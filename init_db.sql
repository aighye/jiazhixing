-- init_db.sql
-- 汽车4S店维修管理系统数据库初始化脚本
-- MySQL 5.7+

CREATE DATABASE IF NOT EXISTS `4s_repair_db`
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_unicode_ci;

USE `4s_repair_db`;

-- ==================== 用户与权限模块 ====================

CREATE TABLE `roles` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名称',
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT '角色编码',
    `description` VARCHAR(200) COMMENT '角色描述',
    `permissions` JSON COMMENT '权限配置',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='角色表';

CREATE TABLE `users` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `real_name` VARCHAR(50) NOT NULL COMMENT '真实姓名',
    `gender` SMALLINT DEFAULT 0 COMMENT '性别：0未知 1男 2女',
    `phone` VARCHAR(20) COMMENT '手机号',
    `email` VARCHAR(100) COMMENT '邮箱',
    `id_card` VARCHAR(18) COMMENT '身份证号',
    `avatar` VARCHAR(255) COMMENT '头像',
    `role_id` INT NOT NULL COMMENT '角色ID',
    `department` VARCHAR(50) COMMENT '部门',
    `position` VARCHAR(50) COMMENT '职位',
    `employee_type` VARCHAR(20) COMMENT '员工类型',
    `employee_no` VARCHAR(30) COMMENT '员工工号',
    `level` VARCHAR(20) COMMENT '级别',
    `title` VARCHAR(50) COMMENT '职称',
    `entry_date` DATE COMMENT '入职日期',
    `base_salary` DECIMAL(10,2) DEFAULT 0 COMMENT '基本工资',
    `hourly_rate` DECIMAL(8,2) DEFAULT 0 COMMENT '工时单价',
    `status` TINYINT DEFAULT 1 COMMENT '状态：1启用 0禁用',
    `last_login` DATETIME COMMENT '最后登录时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`)
) ENGINE=InnoDB COMMENT='用户表';

CREATE TABLE `operation_logs` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `user_id` INT COMMENT '操作用户ID',
    `username` VARCHAR(50) COMMENT '用户名',
    `action` VARCHAR(50) NOT NULL COMMENT '操作类型',
    `module` VARCHAR(50) COMMENT '所属模块',
    `description` VARCHAR(500) COMMENT '操作描述',
    `ip_address` VARCHAR(50) COMMENT 'IP地址',
    `request_data` JSON COMMENT '请求数据',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB COMMENT='操作日志表';

-- ==================== 客户管理模块 ====================

CREATE TABLE `customers` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `customer_no` VARCHAR(30) NOT NULL UNIQUE COMMENT '客户编号',
    `name` VARCHAR(50) NOT NULL COMMENT '客户姓名',
    `phone` VARCHAR(20) NOT NULL COMMENT '联系电话',
    `email` VARCHAR(100) COMMENT '邮箱',
    `gender` TINYINT DEFAULT 0 COMMENT '性别：0未知 1男 2女',
    `birthday` DATE COMMENT '生日',
    `id_card` VARCHAR(18) COMMENT '身份证号',
    `address` VARCHAR(200) COMMENT '地址',
    `customer_type` TINYINT DEFAULT 1 COMMENT '客户类型：1个人 2企业',
    `company_name` VARCHAR(100) COMMENT '公司名称',
    `vip_level` TINYINT DEFAULT 0 COMMENT 'VIP等级',
    `total_spending` DECIMAL(12,2) DEFAULT 0 COMMENT '累计消费金额',
    `points` INT DEFAULT 0 COMMENT '积分',
    `remark` TEXT COMMENT '备注',
    `status` TINYINT DEFAULT 1 COMMENT '状态：1正常 0禁用',
    `created_by` INT COMMENT '创建人ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_phone` (`phone`),
    INDEX `idx_customer_no` (`customer_no`)
) ENGINE=InnoDB COMMENT='客户表';

CREATE TABLE `vehicles` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `vehicle_no` VARCHAR(30) NOT NULL UNIQUE COMMENT '车辆编号',
    `customer_id` INT NOT NULL COMMENT '客户ID',
    `plate_number` VARCHAR(20) NOT NULL COMMENT '车牌号',
    `vin` VARCHAR(30) COMMENT '车架号',
    `brand` VARCHAR(50) COMMENT '品牌',
    `model` VARCHAR(50) COMMENT '车型',
    `year` INT COMMENT '年款',
    `color` VARCHAR(20) COMMENT '颜色',
    `engine_no` VARCHAR(30) COMMENT '发动机号',
    `purchase_date` DATE COMMENT '购车日期',
    `mileage` INT DEFAULT 0 COMMENT '当前里程(km)',
    `insurance_date` DATE COMMENT '保险到期日期',
    `inspection_date` DATE COMMENT '年检到期日期',
    `photo` VARCHAR(255) COMMENT '车辆照片',
    `remark` TEXT COMMENT '备注',
    `status` TINYINT DEFAULT 1 COMMENT '状态：1正常 0删除',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`),
    INDEX `idx_plate_number` (`plate_number`),
    INDEX `idx_customer_id` (`customer_id`)
) ENGINE=InnoDB COMMENT='车辆表';

CREATE TABLE `appointments` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `appointment_no` VARCHAR(30) NOT NULL UNIQUE COMMENT '预约编号',
    `customer_id` INT NOT NULL COMMENT '客户ID',
    `vehicle_id` INT NOT NULL COMMENT '车辆ID',
    `phone` VARCHAR(20) NOT NULL COMMENT '联系电话',
    `appointment_date` DATE NOT NULL COMMENT '预约日期',
    `appointment_time` TIME NOT NULL COMMENT '预约时间',
    `service_type` VARCHAR(50) COMMENT '服务类型',
    `description` TEXT COMMENT '问题描述',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0待确认 1已确认 2已完成 3已取消',
    `confirm_by` INT COMMENT '确认人ID',
    `remark` TEXT COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`),
    FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles`(`id`),
    INDEX `idx_appointment_date` (`appointment_date`)
) ENGINE=InnoDB COMMENT='预约表';

-- ==================== 维修管理模块 ====================

CREATE TABLE `work_orders` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `order_no` VARCHAR(30) NOT NULL UNIQUE COMMENT '工单编号',
    `customer_id` INT NOT NULL COMMENT '客户ID',
    `vehicle_id` INT NOT NULL COMMENT '车辆ID',
    `mileage` INT COMMENT '进厂里程(km)',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0新建 1确认 2派工 3维修中 4检验 5完工 6结算 7已完成',
    `service_type` VARCHAR(50) COMMENT '服务类型',
    `fault_description` TEXT COMMENT '故障描述',
    `repair_suggestion` TEXT COMMENT '维修建议',
    `estimated_cost` DECIMAL(10,2) DEFAULT 0 COMMENT '预估费用',
    `actual_cost` DECIMAL(10,2) DEFAULT 0 COMMENT '实际费用',
    `parts_cost` DECIMAL(10,2) DEFAULT 0 COMMENT '配件费用',
    `labor_cost` DECIMAL(10,2) DEFAULT 0 COMMENT '工时费用',
    `other_cost` DECIMAL(10,2) DEFAULT 0 COMMENT '其他费用',
    `discount_rate` DECIMAL(4,2) DEFAULT 1 COMMENT '折扣率',
    `discount_amount` DECIMAL(10,2) DEFAULT 0 COMMENT '优惠金额',
    `total_amount` DECIMAL(10,2) DEFAULT 0 COMMENT '总金额',
    `received_amount` DECIMAL(10,2) DEFAULT 0 COMMENT '已收金额',
    `is_paid` TINYINT DEFAULT 0 COMMENT '是否已付款',
    `created_by` INT COMMENT '创建人ID',
    `confirmed_by` INT COMMENT '确认人ID',
    `confirmed_at` DATETIME COMMENT '确认时间',
    `assigned_by` INT COMMENT '派工人ID',
    `assigned_at` DATETIME COMMENT '派工时间',
    `inspected_by` INT COMMENT '检验人ID',
    `inspected_at` DATETIME COMMENT '检验时间',
    `completed_by` INT COMMENT '完工人ID',
    `completed_at` DATETIME COMMENT '完工时间',
    `settled_by` INT COMMENT '结算人ID',
    `settled_at` DATETIME COMMENT '结算时间',
    `delivery_at` DATETIME COMMENT '交车时间',
    `remark` TEXT COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`),
    FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles`(`id`),
    INDEX `idx_order_no` (`order_no`),
    INDEX `idx_status` (`status`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB COMMENT='维修工单表';

CREATE TABLE `work_order_flow_logs` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `order_id` INT NOT NULL COMMENT '工单ID',
    `from_status` TINYINT COMMENT '原状态',
    `to_status` TINYINT NOT NULL COMMENT '新状态',
    `operator_id` INT COMMENT '操作人ID',
    `operator_name` VARCHAR(50) COMMENT '操作人姓名',
    `operation` VARCHAR(50) COMMENT '操作类型',
    `remark` TEXT COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_id`) REFERENCES `work_orders`(`id`),
    INDEX `idx_order_id` (`order_id`)
) ENGINE=InnoDB COMMENT='工单状态流转记录表';

CREATE TABLE `repair_items` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `order_id` INT NOT NULL COMMENT '工单ID',
    `item_name` VARCHAR(100) NOT NULL COMMENT '项目名称',
    `item_code` VARCHAR(50) COMMENT '项目编码',
    `category` VARCHAR(50) COMMENT '项目类别',
    `labor_hours` DECIMAL(6,2) DEFAULT 0 COMMENT '工时',
    `labor_price` DECIMAL(10,2) DEFAULT 0 COMMENT '工时单价',
    `labor_amount` DECIMAL(10,2) DEFAULT 0 COMMENT '工时金额',
    `technician_id` INT COMMENT '维修技师ID',
    `technician_name` VARCHAR(50) COMMENT '技师姓名',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0待处理 1进行中 2已完成',
    `start_time` DATETIME COMMENT '开始时间',
    `end_time` DATETIME COMMENT '结束时间',
    `remark` TEXT COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_id`) REFERENCES `work_orders`(`id`),
    INDEX `idx_order_id` (`order_id`)
) ENGINE=InnoDB COMMENT='维修项目表';

CREATE TABLE `work_order_technicians` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `order_id` INT NOT NULL COMMENT '工单ID',
    `repair_item_id` INT COMMENT '维修项目ID',
    `technician_id` INT NOT NULL COMMENT '技师ID',
    `technician_name` VARCHAR(50) COMMENT '技师姓名',
    `assign_type` VARCHAR(20) DEFAULT 'primary' COMMENT '分配类型：primary主修 auxiliary辅修',
    `labor_hours` DECIMAL(6,2) DEFAULT 0 COMMENT '分配工时',
    `labor_amount` DECIMAL(10,2) DEFAULT 0 COMMENT '工时金额',
    `assigned_by` INT COMMENT '分配人ID',
    `assigned_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '分配时间',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0待处理 1进行中 2已完成',
    `completed_at` DATETIME COMMENT '完成时间',
    `remark` TEXT COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_id`) REFERENCES `work_orders`(`id`),
    INDEX `idx_order_id` (`order_id`),
    INDEX `idx_technician_id` (`technician_id`)
) ENGINE=InnoDB COMMENT='维修技师分配表';

-- ==================== 配件管理模块 ====================

CREATE TABLE `parts_categories` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL COMMENT '分类名称',
    `code` VARCHAR(50) COMMENT '分类编码',
    `parent_id` INT DEFAULT 0 COMMENT '父分类ID',
    `level` TINYINT DEFAULT 1 COMMENT '层级',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `status` TINYINT DEFAULT 1 COMMENT '状态',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='配件分类表';

CREATE TABLE `suppliers` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL COMMENT '供应商名称',
    `code` VARCHAR(50) UNIQUE COMMENT '供应商编码',
    `contact_person` VARCHAR(50) COMMENT '联系人',
    `phone` VARCHAR(20) COMMENT '联系电话',
    `email` VARCHAR(100) COMMENT '邮箱',
    `address` VARCHAR(200) COMMENT '地址',
    `bank_name` VARCHAR(100) COMMENT '开户银行',
    `bank_account` VARCHAR(50) COMMENT '银行账号',
    `credit_level` TINYINT DEFAULT 1 COMMENT '信用等级',
    `status` TINYINT DEFAULT 1 COMMENT '状态',
    `remark` TEXT COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='供应商表';

CREATE TABLE `parts` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `part_no` VARCHAR(50) NOT NULL UNIQUE COMMENT '配件编号',
    `name` VARCHAR(100) NOT NULL COMMENT '配件名称',
    `category_id` INT COMMENT '分类ID',
    `brand` VARCHAR(50) COMMENT '品牌',
    `model` VARCHAR(100) COMMENT '规格型号',
    `unit` VARCHAR(20) DEFAULT '个' COMMENT '单位',
    `purchase_price` DECIMAL(10,2) DEFAULT 0 COMMENT '采购价(加权平均)',
    `selling_price` DECIMAL(10,2) DEFAULT 0 COMMENT '销售价',
    `stock_quantity` INT DEFAULT 0 COMMENT '当前库存',
    `min_stock` INT DEFAULT 0 COMMENT '最低库存预警',
    `max_stock` INT DEFAULT 0 COMMENT '最高库存',
    `warehouse` VARCHAR(50) DEFAULT '默认仓库' COMMENT '仓库',
    `location` VARCHAR(50) COMMENT '库位',
    `status` TINYINT DEFAULT 1 COMMENT '状态',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`category_id`) REFERENCES `parts_categories`(`id`),
    INDEX `idx_part_no` (`part_no`),
    INDEX `idx_category_id` (`category_id`)
) ENGINE=InnoDB COMMENT='配件库存表';

CREATE TABLE `parts_inbound` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `inbound_no` VARCHAR(30) NOT NULL UNIQUE COMMENT '入库单号',
    `supplier_id` INT COMMENT '供应商ID',
    `total_amount` DECIMAL(12,2) DEFAULT 0 COMMENT '总金额',
    `total_quantity` INT DEFAULT 0 COMMENT '总数量',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0待入库 1已入库 2已取消',
    `inbound_by` INT COMMENT '入库人ID',
    `inbound_at` DATETIME COMMENT '入库时间',
    `remark` TEXT COMMENT '备注',
    `created_by` INT COMMENT '创建人ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`supplier_id`) REFERENCES `suppliers`(`id`),
    INDEX `idx_inbound_no` (`inbound_no`)
) ENGINE=InnoDB COMMENT='配件入库记录表';

CREATE TABLE `parts_inbound_details` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `inbound_id` INT NOT NULL COMMENT '入库单ID',
    `part_id` INT NOT NULL COMMENT '配件ID',
    `quantity` INT NOT NULL COMMENT '数量',
    `unit_price` DECIMAL(10,2) NOT NULL COMMENT '单价',
    `total_price` DECIMAL(10,2) NOT NULL COMMENT '小计',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`inbound_id`) REFERENCES `parts_inbound`(`id`),
    FOREIGN KEY (`part_id`) REFERENCES `parts`(`id`)
) ENGINE=InnoDB COMMENT='入库明细表';

CREATE TABLE `parts_outbound` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `outbound_no` VARCHAR(30) NOT NULL UNIQUE COMMENT '出库单号',
    `order_id` INT COMMENT '关联工单ID',
    `outbound_type` VARCHAR(20) DEFAULT 'repair' COMMENT '出库类型：repair维修 return退库 scrap报废',
    `total_amount` DECIMAL(12,2) DEFAULT 0 COMMENT '总金额',
    `total_quantity` INT DEFAULT 0 COMMENT '总数量',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0待出库 1已出库 2已取消',
    `outbound_by` INT COMMENT '出库人ID',
    `outbound_at` DATETIME COMMENT '出库时间',
    `remark` TEXT COMMENT '备注',
    `created_by` INT COMMENT '创建人ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_outbound_no` (`outbound_no`),
    INDEX `idx_order_id` (`order_id`)
) ENGINE=InnoDB COMMENT='配件出库记录表';

CREATE TABLE `parts_outbound_details` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `outbound_id` INT NOT NULL COMMENT '出库单ID',
    `part_id` INT NOT NULL COMMENT '配件ID',
    `quantity` INT NOT NULL COMMENT '数量',
    `unit_price` DECIMAL(10,2) NOT NULL COMMENT '单价(加权平均)',
    `total_price` DECIMAL(10,2) NOT NULL COMMENT '小计',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`outbound_id`) REFERENCES `parts_outbound`(`id`),
    FOREIGN KEY (`part_id`) REFERENCES `parts`(`id`)
) ENGINE=InnoDB COMMENT='出库明细表';

CREATE TABLE `stock_movements` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `part_id` INT NOT NULL COMMENT '配件ID',
    `movement_type` VARCHAR(20) NOT NULL COMMENT '变动类型：in入库 out出库 adjust调整',
    `reference_type` VARCHAR(20) COMMENT '关联类型：inbound outbound order',
    `reference_id` INT COMMENT '关联ID',
    `quantity_before` INT NOT NULL COMMENT '变动前数量',
    `quantity_change` INT NOT NULL COMMENT '变动数量',
    `quantity_after` INT NOT NULL COMMENT '变动后数量',
    `price_before` DECIMAL(10,2) COMMENT '变动前单价',
    `price_after` DECIMAL(10,2) COMMENT '变动后单价',
    `operator_id` INT COMMENT '操作人ID',
    `remark` VARCHAR(200) COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`part_id`) REFERENCES `parts`(`id`),
    INDEX `idx_part_id` (`part_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB COMMENT='库存变动记录表';

-- ==================== 财务管理模块 ====================

CREATE TABLE `payments` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `payment_no` VARCHAR(30) NOT NULL UNIQUE COMMENT '收款单号',
    `order_id` INT COMMENT '工单ID',
    `customer_id` INT COMMENT '客户ID',
    `amount` DECIMAL(12,2) NOT NULL COMMENT '收款金额',
    `payment_method` VARCHAR(20) COMMENT '支付方式：cash微信支付宝bank',
    `payment_type` VARCHAR(20) DEFAULT 'repair' COMMENT '收款类型：repair维修 deposit定金 other其他',
    `transaction_no` VARCHAR(50) COMMENT '交易流水号',
    `payer_name` VARCHAR(50) COMMENT '付款人',
    `status` TINYINT DEFAULT 1 COMMENT '状态：1已支付 2已退款 3已取消',
    `remark` TEXT COMMENT '备注',
    `received_by` INT COMMENT '收款人ID',
    `received_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收款时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_id`) REFERENCES `work_orders`(`id`),
    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`),
    INDEX `idx_payment_no` (`payment_no`),
    INDEX `idx_order_id` (`order_id`)
) ENGINE=InnoDB COMMENT='收款记录表';

CREATE TABLE `invoices` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `invoice_no` VARCHAR(30) NOT NULL UNIQUE COMMENT '发票号',
    `order_id` INT COMMENT '工单ID',
    `customer_id` INT COMMENT '客户ID',
    `invoice_type` VARCHAR(20) DEFAULT 'normal' COMMENT '发票类型：normal普通 special专用',
    `title` VARCHAR(100) NOT NULL COMMENT '发票抬头',
    `tax_no` VARCHAR(30) COMMENT '税号',
    `amount` DECIMAL(12,2) NOT NULL COMMENT '发票金额',
    `tax_amount` DECIMAL(12,2) DEFAULT 0 COMMENT '税额',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0待开票 1已开票 2已作废',
    `issued_by` INT COMMENT '开票人ID',
    `issued_at` DATETIME COMMENT '开票时间',
    `remark` TEXT COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_id`) REFERENCES `work_orders`(`id`),
    INDEX `idx_invoice_no` (`invoice_no`)
) ENGINE=InnoDB COMMENT='发票表';

-- ==================== 人员管理模块 ====================

CREATE TABLE `employees` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `employee_no` VARCHAR(30) NOT NULL UNIQUE COMMENT '员工工号',
    `name` VARCHAR(50) NOT NULL COMMENT '姓名',
    `gender` TINYINT DEFAULT 0 COMMENT '性别',
    `phone` VARCHAR(20) COMMENT '联系电话',
    `id_card` VARCHAR(18) COMMENT '身份证号',
    `department` VARCHAR(50) COMMENT '部门',
    `position` VARCHAR(50) COMMENT '职位',
    `employee_type` VARCHAR(20) COMMENT '员工类型：technician技术员 service服务顾问 manager管理',
    `level` VARCHAR(20) COMMENT '级别',
    `entry_date` DATE COMMENT '入职日期',
    `base_salary` DECIMAL(10,2) DEFAULT 0 COMMENT '基本工资',
    `hourly_rate` DECIMAL(8,2) DEFAULT 0 COMMENT '工时单价',
    `user_id` INT COMMENT '关联用户ID',
    `status` TINYINT DEFAULT 1 COMMENT '状态：1在职 0离职',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`),
    INDEX `idx_employee_no` (`employee_no`)
) ENGINE=InnoDB COMMENT='员工表';

CREATE TABLE `employee_labor_stats` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `employee_id` INT NOT NULL COMMENT '员工ID',
    `stat_date` DATE NOT NULL COMMENT '统计日期',
    `stat_month` VARCHAR(7) NOT NULL COMMENT '统计月份',
    `total_hours` DECIMAL(8,2) DEFAULT 0 COMMENT '总工时',
    `total_amount` DECIMAL(12,2) DEFAULT 0 COMMENT '总工时金额',
    `order_count` INT DEFAULT 0 COMMENT '完成工单数',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`employee_id`) REFERENCES `employees`(`id`),
    UNIQUE KEY `uk_emp_date` (`employee_id`, `stat_date`),
    INDEX `idx_stat_month` (`stat_month`)
) ENGINE=InnoDB COMMENT='员工工时统计表';

-- ==================== 系统配置模块 ====================

CREATE TABLE `system_configs` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `config_key` VARCHAR(50) NOT NULL UNIQUE COMMENT '配置键',
    `config_value` TEXT COMMENT '配置值',
    `config_type` VARCHAR(20) DEFAULT 'string' COMMENT '类型：string number boolean json',
    `description` VARCHAR(200) COMMENT '描述',
    `group` VARCHAR(50) DEFAULT 'general' COMMENT '分组',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='系统配置表';

CREATE TABLE `backup_records` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `backup_name` VARCHAR(100) NOT NULL COMMENT '备份名称',
    `backup_type` VARCHAR(20) DEFAULT 'full' COMMENT '备份类型：full全量 incremental增量',
    `file_path` VARCHAR(255) COMMENT '文件路径',
    `file_size` BIGINT COMMENT '文件大小(字节)',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0进行中 1成功 2失败',
    `created_by` INT COMMENT '创建人ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='数据备份记录表';

-- ==================== 初始化数据 ====================

INSERT INTO `roles` (`name`, `code`, `description`, `permissions`) VALUES
('系统管理员', 'admin', '系统超级管理员，拥有所有权限', '["*"]'),
('服务经理', 'manager', '服务部门经理', '["customer:*", "work_order:*", "parts:*", "finance:*", "report:*"]'),
('服务顾问', 'advisor', '接待客户，创建工单', '["customer:read", "customer:create", "work_order:create", "work_order:read", "work_order:update"]'),
('维修技师', 'technician', '执行维修工作', '["work_order:read", "work_order:repair"]'),
('配件管理员', 'parts_manager', '管理配件库存', '["parts:*"]'),
('财务人员', 'finance', '处理财务事务', '["finance:*", "report:finance"]');

-- 初始化配件分类
INSERT INTO `parts_categories` (`name`, `code`, `parent_id`, `level`) VALUES
('发动机配件', 'ENGINE', 0, 1),
('底盘配件', 'CHASSIS', 0, 1),
('电气系统', 'ELECTRICAL', 0, 1),
('车身配件', 'BODY', 0, 1),
('保养件', 'MAINTENANCE', 0, 1);

-- 初始化系统配置
INSERT INTO `system_configs` (`config_key`, `config_value`, `config_type`, `description`, `group`) VALUES
('shop_name', 'XX汽车4S店', 'string', '店铺名称', 'basic'),
('shop_address', 'XX市XX区XX路XX号', 'string', '店铺地址', 'basic'),
('shop_phone', '400-xxx-xxxx', 'string', '联系电话', 'basic'),
('default_labor_rate', '200', 'number', '默认工时单价', 'price'),
('tax_rate', '0.13', 'number', '税率', 'price'),
('stock_warning_enabled', 'true', 'boolean', '是否启用库存预警', 'stock'),
('backup_retention_days', '30', 'number', '备份保留天数', 'system');
