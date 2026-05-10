import multiprocessing

bind = '127.0.0.1:5000'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gthread'
threads = 2
timeout = 120
accesslog = '/opt/4s_repair_management/logs/gunicorn_access.log'
errorlog = '/opt/4s_repair_management/logs/gunicorn_error.log'
loglevel = 'info'
