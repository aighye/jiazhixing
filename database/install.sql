-- 汽车4S店维修业务管理系统数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS `auto_4s_system` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `auto_4s_system`;

-- 1. 系统配置表
CREATE TABLE IF NOT EXISTS `system_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `config_key` varchar(100) NOT NULL COMMENT '配置键',
  `config_value` text COMMENT '配置值',
  `config_desc` varchar(255) DEFAULT NULL COMMENT '配置描述',
  `group_name` varchar(50) DEFAULT 'system' COMMENT '分组',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- 2. 角色表
CREATE TABLE IF NOT EXISTS `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) NOT NULL COMMENT '角色名称',
  `role_code` varchar(50) NOT NULL COMMENT '角色代码',
  `description` varchar(255) DEFAULT NULL COMMENT '描述',
  `is_system` tinyint(1) DEFAULT 0 COMMENT '是否系统内置',
  `sort` int(11) DEFAULT 0 COMMENT '排序',
  `status` tinyint(1) DEFAULT 1 COMMENT '状态 1启用 0禁用',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- 3. 权限表
CREATE TABLE IF NOT EXISTS `permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) DEFAULT 0 COMMENT '父级ID',
  `permission_name` varchar(100) NOT NULL COMMENT '权限名称',
  `permission_key` varchar(100) NOT NULL COMMENT '权限标识',
  `type` tinyint(1) DEFAULT 1 COMMENT '类型 1菜单 2按钮',
  `icon` varchar(50) DEFAULT NULL COMMENT '图标',
  `route` varchar(255) DEFAULT NULL COMMENT '路由',
  `sort` int(11) DEFAULT 0 COMMENT '排序',
  `status` tinyint(1) DEFAULT 1 COMMENT '状态',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_permission_key` (`permission_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';

-- 4. 角色权限关联表
CREATE TABLE IF NOT EXISTS `role_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `role_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_role_id` (`role_id`),
  KEY `idx_permission_id` (`permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表';

-- 5. 用户表
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password` varchar(255) NOT NULL COMMENT '密码',
  `real_name` varchar(50) DEFAULT NULL COMMENT '真实姓名',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `role_id` int(11) NOT NULL COMMENT '角色ID',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像',
  `department` varchar(50) DEFAULT NULL COMMENT '部门',
  `status` tinyint(1) DEFAULT 1 COMMENT '状态 1启用 0禁用',
  `last_login_at` datetime DEFAULT NULL COMMENT '最后登录时间',
  `last_login_ip` varchar(50) DEFAULT NULL COMMENT '最后登录IP',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 6. 系统操作日志表
CREATE TABLE IF NOT EXISTS `system_logs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT 0,
  `username` varchar(50) DEFAULT NULL,
  `action` varchar(100) DEFAULT NULL COMMENT '操作',
  `description` text COMMENT '描述',
  `module` varchar(50) DEFAULT 'system' COMMENT '模块',
  `ip_address` varchar(50) DEFAULT NULL,
  `user_agent` varchar(255) DEFAULT NULL,
  `request_data` text COMMENT '请求数据',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统操作日志表';

-- 7. 登录日志表
CREATE TABLE IF NOT EXISTS `login_logs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) DEFAULT NULL,
  `status` tinyint(1) DEFAULT 1 COMMENT '1成功 0失败',
  `ip_address` varchar(50) DEFAULT NULL,
  `user_agent` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表';

-- 8. 客户表
CREATE TABLE IF NOT EXISTS `customers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_no` varchar(50) DEFAULT NULL COMMENT '客户编号',
  `name` varchar(50) NOT NULL COMMENT '姓名',
  `phone` varchar(20) NOT NULL COMMENT '手机号',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `id_card` varchar(20) DEFAULT NULL COMMENT '身份证号',
  `address` varchar(255) DEFAULT NULL COMMENT '地址',
  `member_level` tinyint(1) DEFAULT 1 COMMENT '会员等级 1普通 2银卡 3金卡 4钻石',
  `member_points` int(11) DEFAULT 0 COMMENT '会员积分',
  `balance` decimal(10,2) DEFAULT 0.00 COMMENT '账户余额',
  `source` varchar(50) DEFAULT NULL COMMENT '客户来源',
  `remark` text COMMENT '备注',
  `status` tinyint(1) DEFAULT 1 COMMENT '状态',
  `created_by` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_customer_no` (`customer_no`),
  KEY `idx_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户表';

-- 9. 客户车辆表
CREATE TABLE IF NOT EXISTS `customer_vehicles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_id` int(11) NOT NULL COMMENT '客户ID',
  `plate_number` varchar(20) NOT NULL COMMENT '车牌号',
  `vin` varchar(50) DEFAULT NULL COMMENT '车架号',
  `engine_no` varchar(50) DEFAULT NULL COMMENT '发动机号',
  `brand` varchar(50) DEFAULT NULL COMMENT '品牌',
  `model` varchar(100) DEFAULT NULL COMMENT '车型',
  `color` varchar(20) DEFAULT NULL COMMENT '颜色',
  `displacement` varchar(20) DEFAULT NULL COMMENT '排量',
  `purchase_date` date DEFAULT NULL COMMENT '购车日期',
  `registration_date` date DEFAULT NULL COMMENT '上牌日期',
  `insurance_date` date DEFAULT NULL COMMENT '保险到期日',
  `inspection_date` date DEFAULT NULL COMMENT '年检到期日',
  `mileage` int(11) DEFAULT 0 COMMENT '当前里程',
  `last_service_date` date DEFAULT NULL COMMENT '上次保养日期',
  `remark` text COMMENT '备注',
  `is_default` tinyint(1) DEFAULT 0 COMMENT '是否默认',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_plate_number` (`plate_number`),
  KEY `idx_customer_id` (`customer_id`),
  KEY `idx_vin` (`vin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户车辆表';

-- 10. 配件分类表
CREATE TABLE IF NOT EXISTS `parts_categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) DEFAULT 0,
  `category_name` varchar(100) NOT NULL,
  `category_code` varchar(50) DEFAULT NULL,
  `sort` int(11) DEFAULT 0,
  `remark` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配件分类表';

-- 11. 供应商表
CREATE TABLE IF NOT EXISTS `suppliers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `supplier_name` varchar(100) NOT NULL COMMENT '供应商名称',
  `supplier_code` varchar(50) DEFAULT NULL COMMENT '供应商编码',
  `contact_person` varchar(50) DEFAULT NULL COMMENT '联系人',
  `contact_phone` varchar(20) DEFAULT NULL COMMENT '联系电话',
  `email` varchar(100) DEFAULT NULL COMMENT '邮箱',
  `address` varchar(255) DEFAULT NULL COMMENT '地址',
  `bank_name` varchar(100) DEFAULT NULL COMMENT '开户银行',
  `bank_account` varchar(50) DEFAULT NULL COMMENT '银行账号',
  `remark` text COMMENT '备注',
  `status` tinyint(1) DEFAULT 1,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商表';

-- 12. 配件表
CREATE TABLE IF NOT EXISTS `parts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `part_code` varchar(50) NOT NULL COMMENT '配件编码',
  `part_name` varchar(100) NOT NULL COMMENT '配件名称',
  `category_id` int(11) DEFAULT NULL COMMENT '分类ID',
  `brand` varchar(50) DEFAULT NULL COMMENT '品牌',
  `model` varchar(100) DEFAULT NULL COMMENT '型号',
  `spec` varchar(100) DEFAULT NULL COMMENT '规格',
  `unit` varchar(20) DEFAULT '个' COMMENT '单位',
  `purchase_price` decimal(10,2) DEFAULT 0.00 COMMENT '进价',
  `sale_price` decimal(10,2) DEFAULT 0.00 COMMENT '售价',
  `wholesale_price` decimal(10,2) DEFAULT 0.00 COMMENT '批发价',
  `stock` int(11) DEFAULT 0 COMMENT '库存',
  `min_stock` int(11) DEFAULT 10 COMMENT '最小库存预警',
  `max_stock` int(11) DEFAULT 1000 COMMENT '最大库存',
  `supplier_id` int(11) DEFAULT NULL COMMENT '供应商ID',
  `location` varchar(50) DEFAULT NULL COMMENT '库位',
  `barcode` varchar(100) DEFAULT NULL COMMENT '条码',
  `image` varchar(255) DEFAULT NULL COMMENT '图片',
  `remark` text COMMENT '备注',
  `status` tinyint(1) DEFAULT 1 COMMENT '状态',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_part_code` (`part_code`),
  KEY `idx_category_id` (`category_id`),
  KEY `idx_supplier_id` (`supplier_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配件表';

-- 13. 配件入库单表
CREATE TABLE IF NOT EXISTS `parts_inbound` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `inbound_no` varchar(50) NOT NULL COMMENT '入库单号',
  `supplier_id` int(11) DEFAULT NULL COMMENT '供应商ID',
  `inbound_type` tinyint(1) DEFAULT 1 COMMENT '入库类型 1采购 2退货 3调拨 4其他',
  `total_amount` decimal(12,2) DEFAULT 0.00 COMMENT '总金额',
  `remark` text COMMENT '备注',
  `operator_id` int(11) DEFAULT NULL COMMENT '操作员ID',
  `status` tinyint(1) DEFAULT 1 COMMENT '状态 0草稿 1已确认',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_inbound_no` (`inbound_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配件入库单表';

-- 14. 配件入库明细表
CREATE TABLE IF NOT EXISTS `parts_inbound_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `inbound_id` int(11) NOT NULL,
  `part_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL COMMENT '数量',
  `price` decimal(10,2) DEFAULT 0.00 COMMENT '单价',
  `amount` decimal(10,2) DEFAULT 0.00 COMMENT '金额',
  `remark` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_inbound_id` (`inbound_id`),
  KEY `idx_part_id` (`part_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配件入库明细表';

-- 15. 配件出库单表
CREATE TABLE IF NOT EXISTS `parts_outbound` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `outbound_no` varchar(50) NOT NULL COMMENT '出库单号',
  `outbound_type` tinyint(1) DEFAULT 1 COMMENT '出库类型 1维修 2销售 3调拨 4其他',
  `related_id` int(11) DEFAULT NULL COMMENT '关联ID',
  `total_amount` decimal(12,2) DEFAULT 0.00 COMMENT '总金额',
  `remark` text COMMENT '备注',
  `operator_id` int(11) DEFAULT NULL COMMENT '操作员ID',
  `status` tinyint(1) DEFAULT 1 COMMENT '状态',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_outbound_no` (`outbound_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配件出库单表';

-- 16. 配件出库明细表
CREATE TABLE IF NOT EXISTS `parts_outbound_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `outbound_id` int(11) NOT NULL,
  `part_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL COMMENT '数量',
  `price` decimal(10,2) DEFAULT 0.00 COMMENT '单价',
  `amount` decimal(10,2) DEFAULT 0.00 COMMENT '金额',
  `remark` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_outbound_id` (`outbound_id`),
  KEY `idx_part_id` (`part_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配件出库明细表';

-- 17. 配件库存变动记录表
CREATE TABLE IF NOT EXISTS `parts_stock_logs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `part_id` int(11) NOT NULL,
  `change_type` tinyint(1) NOT NULL COMMENT '变动类型 1入库 2出库 3盘点调整',
  `before_stock` int(11) DEFAULT 0 COMMENT '变动前库存',
  `change_stock` int(11) NOT NULL COMMENT '变动数量',
  `after_stock` int(11) DEFAULT 0 COMMENT '变动后库存',
  `related_no` varchar(50) DEFAULT NULL COMMENT '关联单号',
  `remark` varchar(255) DEFAULT NULL,
  `operator_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_part_id` (`part_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='配件库存变动记录表';

-- 18. 维修工单表
CREATE TABLE IF NOT EXISTS `work_orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_no` varchar(50) NOT NULL COMMENT '工单编号',
  `customer_id` int(11) NOT NULL COMMENT '客户ID',
  `vehicle_id` int(11) NOT NULL COMMENT '车辆ID',
  `order_type` tinyint(1) DEFAULT 1 COMMENT '工单类型 1保养 2维修 3事故 4索赔',
  `source` varchar(50) DEFAULT NULL COMMENT '工单来源',
  `fault_desc` text COMMENT '故障描述',
  `service_request` text COMMENT '服务要求',
  `estimated_amount` decimal(12,2) DEFAULT 0.00 COMMENT '预估金额',
  `actual_amount` decimal(12,2) DEFAULT 0.00 COMMENT '实际金额',
  `discount_amount` decimal(10,2) DEFAULT 0.00 COMMENT '优惠金额',
  `final_amount` decimal(12,2) DEFAULT 0.00 COMMENT '最终金额',
  `receiver_id` int(11) DEFAULT NULL COMMENT '接待员ID',
  `technician_id` int(11) DEFAULT NULL COMMENT '技师ID',
  `status` tinyint(1) DEFAULT 1 COMMENT '状态 1待派工 2维修中 3待质检 4已完成 5已结算 6已关闭',
  `urgent` tinyint(1) DEFAULT 0 COMMENT '是否加急',
  `promise_date` datetime DEFAULT NULL COMMENT '承诺交车时间',
  `actual_finish_date` datetime DEFAULT NULL COMMENT '实际完成时间',
  `settle_date` datetime DEFAULT NULL COMMENT '结算时间',
  `remark` text COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_customer_id` (`customer_id`),
  KEY `idx_vehicle_id` (`vehicle_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='维修工单表';

-- 19. 维修项目表
CREATE TABLE IF NOT EXISTS `work_order_services` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `service_name` varchar(100) NOT NULL COMMENT '服务项目名称',
  `service_type` varchar(50) DEFAULT NULL COMMENT '服务类型',
  `hours` decimal(5,2) DEFAULT 0.00 COMMENT '工时',
  `hour_price` decimal(10,2) DEFAULT 0.00 COMMENT '工时单价',
  `amount` decimal(10,2) DEFAULT 0.00 COMMENT '工时费',
  `technician_id` int(11) DEFAULT NULL COMMENT '技师ID',
  `sort` int(11) DEFAULT 0,
  `remark` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='维修项目表';

-- 20. 工单配件表
CREATE TABLE IF NOT EXISTS `work_order_parts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `part_id` int(11) NOT NULL,
  `part_code` varchar(50) DEFAULT NULL,
  `part_name` varchar(100) DEFAULT NULL,
  `spec` varchar(100) DEFAULT NULL,
  `unit` varchar(20) DEFAULT NULL,
  `quantity` int(11) NOT NULL COMMENT '数量',
  `price` decimal(10,2) DEFAULT 0.00 COMMENT '单价',
  `amount` decimal(10,2) DEFAULT 0.00 COMMENT '金额',
  `outbound_id` int(11) DEFAULT NULL COMMENT '出库单ID',
  `remark` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_part_id` (`part_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单配件表';

-- 21. 工单进度记录表
CREATE TABLE IF NOT EXISTS `work_order_logs` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `status` tinyint(1) DEFAULT NULL COMMENT '状态',
  `operator_id` int(11) DEFAULT NULL,
  `operator_name` varchar(50) DEFAULT NULL,
  `content` text COMMENT '操作内容',
  `remark` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单进度记录表';

-- 22. 质检表
CREATE TABLE IF NOT EXISTS `inspections` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `inspector_id` int(11) DEFAULT NULL COMMENT '质检员ID',
  `result` tinyint(1) DEFAULT NULL COMMENT '1合格 0不合格',
  `check_items` text COMMENT '检查项目',
  `defect_desc` text COMMENT '缺陷描述',
  `suggestion` text COMMENT '建议',
  `remark` text COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='质检表';

-- 23. 结算单表
CREATE TABLE IF NOT EXISTS `settlements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `settle_no` varchar(50) NOT NULL COMMENT '结算单号',
  `order_id` int(11) NOT NULL,
  `total_amount` decimal(12,2) DEFAULT 0.00 COMMENT '总金额',
  `discount_amount` decimal(10,2) DEFAULT 0.00 COMMENT '优惠金额',
  `points_deduct` decimal(10,2) DEFAULT 0.00 COMMENT '积分抵扣',
  `balance_deduct` decimal(10,2) DEFAULT 0.00 COMMENT '余额抵扣',
  `payable_amount` decimal(12,2) DEFAULT 0.00 COMMENT '应付金额',
  `paid_amount` decimal(12,2) DEFAULT 0.00 COMMENT '实付金额',
  `payment_method` varchar(50) DEFAULT NULL COMMENT '支付方式',
  `invoice_title` varchar(255) DEFAULT NULL COMMENT '发票抬头',
  `invoice_no` varchar(50) DEFAULT NULL COMMENT '发票号码',
  `remark` text COMMENT '备注',
  `cashier_id` int(11) DEFAULT NULL COMMENT '收银员ID',
  `settle_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_settle_no` (`settle_no`),
  KEY `idx_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='结算单表';

-- 24. 支付记录表
CREATE TABLE IF NOT EXISTS `payment_records` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `settlement_id` int(11) NOT NULL,
  `payment_method` varchar(50) NOT NULL COMMENT '支付方式',
  `amount` decimal(12,2) NOT NULL COMMENT '支付金额',
  `transaction_no` varchar(100) DEFAULT NULL COMMENT '交易流水号',
  `remark` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_settlement_id` (`settlement_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='支付记录表';

-- 25. 客户回访表
CREATE TABLE IF NOT EXISTS `customer_followups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) DEFAULT NULL,
  `customer_id` int(11) NOT NULL,
  `followup_type` tinyint(1) DEFAULT 1 COMMENT '1售后回访 2保养提醒',
  `followup_date` datetime DEFAULT NULL COMMENT '回访时间',
  `followup_user_id` int(11) DEFAULT NULL COMMENT '回访人',
  `satisfaction` tinyint(1) DEFAULT NULL COMMENT '满意度 1-5',
  `content` text COMMENT '回访内容',
  `next_followup_date` date DEFAULT NULL COMMENT '下次回访日期',
  `status` tinyint(1) DEFAULT 0 COMMENT '0待回访 1已回访',
  `remark` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_customer_id` (`customer_id`),
  KEY `idx_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户回访表';

-- 初始化数据

-- 插入角色数据
INSERT INTO `roles` (`role_name`, `role_code`, `description`, `is_system`, `sort`, `status`) VALUES
('超级管理员', 'admin', '系统超级管理员，拥有所有权限', 1, 1, 1),
('前台接待', 'reception', '负责客户接待和工单创建', 1, 2, 1),
('维修技师', 'technician', '负责车辆维修作业', 1, 3, 1),
('财务员', 'finance', '负责结算和财务管理', 1, 4, 1),
('库管员', 'warehouse', '负责配件出入库和库存管理', 1, 5, 1),
('质检员', 'inspector', '负责维修质量检验', 1, 6, 1);

-- 插入默认管理员账号 (密码: admin123, 需要用 password_hash 加密)
INSERT INTO `users` (`username`, `password`, `real_name`, `phone`, `role_id`, `status`) VALUES
('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '系统管理员', '13800138000', 1, 1);

-- 插入系统配置
INSERT INTO `system_config` (`config_key`, `config_value`, `config_desc`, `group_name`) VALUES
('shop_name', 'XX汽车4S店', '店铺名称', 'shop'),
('shop_phone', '400-888-8888', '联系电话', 'shop'),
('shop_address', 'XX市XX区XX路XX号', '店铺地址', 'shop'),
('hour_price', '150.00', '标准工时单价', 'service'),
('invoice_tax_rate', '13.00', '发票税率', 'finance');