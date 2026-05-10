from dotenv import load_dotenv
load_dotenv()

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate, login_manager
import os

def create_app(config_class=Config):
    # 前端构建文件目录
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'dist')

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    login_manager.login_view = 'auth.login'
    login_manager.session_protection = 'basic'

    # API 请求未认证时返回 401 JSON，而非重定向到登录页
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request as req
        if req.path.startswith('/api/'):
            return jsonify({'code': 401, 'message': '登录已过期，请重新登录', 'data': None}), 401
        return login_manager.login_manager.redirect(login_manager.login_view)

    # 全局异常处理 - 确保所有 API 错误都返回 JSON
    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({'code': 400, 'message': str(e.description) if hasattr(e, 'description') else '请求参数错误', 'data': None}), 400

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({'code': 404, 'message': '请求的资源不存在', 'data': None}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({'code': 405, 'message': '请求方法不允许', 'data': None}), 405

    @app.errorhandler(500)
    def handle_internal_error(e):
        return jsonify({'code': 500, 'message': '服务器内部错误', 'data': None}), 500

    # 用户加载回调
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.customer import customer_bp
    from app.routes.work_order import work_order_bp
    from app.routes.repair_item import repair_item_bp
    from app.routes.parts import parts_bp
    from app.routes.finance import finance_bp
    from app.routes.employee import employee_bp
    from app.routes.report import report_bp
    from app.routes.system import system_bp
    from app.routes.technician import technician_bp
    from app.routes.dict import dict_bp
    from app.routes.supplier import supplier_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(customer_bp, url_prefix='/api/customers')
    app.register_blueprint(work_order_bp, url_prefix='/api/work-orders')
    app.register_blueprint(repair_item_bp, url_prefix='/api/repair-items')
    app.register_blueprint(parts_bp, url_prefix='/api/parts')
    app.register_blueprint(finance_bp, url_prefix='/api/finance')
    app.register_blueprint(employee_bp, url_prefix='/api/employees')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(system_bp, url_prefix='/api/system')
    app.register_blueprint(technician_bp, url_prefix='/api/technicians')
    app.register_blueprint(dict_bp, url_prefix='/api/dict')
    app.register_blueprint(supplier_bp, url_prefix='/api/suppliers')

    # 确保上传目录存在
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    os.makedirs(app.config.get('BACKUP_FOLDER', 'backups'), exist_ok=True)

    # Serve 前端静态文件（Vue SPA）
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        assets_dir = os.path.join(frontend_dist, 'assets')
        if os.path.isdir(assets_dir):
            return send_from_directory(assets_dir, filename)
        return jsonify({'code': 404, 'message': '前端资源未构建，请先执行 npm run build', 'data': None}), 404

    @app.route('/')
    def serve_index():
        if os.path.isfile(os.path.join(frontend_dist, 'index.html')):
            return send_from_directory(frontend_dist, 'index.html')
        return jsonify({'code': 404, 'message': '前端资源未构建，请先执行 npm run build', 'data': None}), 404

    # SPA fallback: 所有非 API、非 assets 的路由都返回 index.html
    @app.route('/<path:path>')
    def serve_spa(path):
        if path.startswith('api/'):
            return jsonify({'code': 404, 'message': '请求的资源不存在', 'data': None}), 404
        file_path = os.path.join(frontend_dist, path)
        if os.path.isfile(file_path):
            return send_from_directory(frontend_dist, path)
        if os.path.isfile(os.path.join(frontend_dist, 'index.html')):
            return send_from_directory(frontend_dist, 'index.html')
        return jsonify({'code': 404, 'message': '前端资源未构建，请先执行 npm run build', 'data': None}), 404

    return app
