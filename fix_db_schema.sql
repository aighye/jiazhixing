-- Fix missing columns in existing tables
ALTER TABLE `work_order_flow_logs` ADD COLUMN `operator_no` VARCHAR(30) COMMENT '操作人工号' AFTER operator_name;
ALTER TABLE `work_order_flow_logs` ADD COLUMN `operator_dept` VARCHAR(50) COMMENT '操作人部门' AFTER operator_no;
ALTER TABLE `parts_inbound_details` ADD COLUMN `unit` VARCHAR(20) DEFAULT '' AFTER total_price;
ALTER TABLE `parts_inbound_details` ADD COLUMN `unit_price_with_tax` DECIMAL(12,2) DEFAULT 0 AFTER unit;
ALTER TABLE `parts_inbound_details` ADD COLUMN `location` VARCHAR(50) DEFAULT '' AFTER unit_price_with_tax;
ALTER TABLE `repair_items` ADD COLUMN `discount_rate` DECIMAL(4,2) DEFAULT 1 AFTER labor_amount;
ALTER TABLE `repair_items` ADD COLUMN `charge_type` VARCHAR(20) AFTER discount_rate;
ALTER TABLE `repair_items` ADD COLUMN `repair_category` VARCHAR(20) AFTER charge_type;
ALTER TABLE `parts_inbound` ADD COLUMN `invoice_type` VARCHAR(10) DEFAULT '无发票' AFTER remark;
ALTER TABLE `parts_inbound` ADD COLUMN `tax_rate` DECIMAL(5,2) DEFAULT 0 AFTER invoice_type;
ALTER TABLE `work_orders` ADD COLUMN `insurance_company` VARCHAR(50) COMMENT '保险公司' AFTER remark;
ALTER TABLE `work_orders` ADD COLUMN `claim_manufacturer` VARCHAR(50) COMMENT '索赔厂家' AFTER insurance_company;

-- Create missing tables
CREATE TABLE IF NOT EXISTS `claim_manufacturers` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `code` VARCHAR(50),
    `contact_person` VARCHAR(50),
    `phone` VARCHAR(20),
    `address` VARCHAR(200),
    `status` TINYINT DEFAULT 1,
    `remark` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='索赔厂家表';

CREATE TABLE IF NOT EXISTS `dict_items` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `dict_type` VARCHAR(50) NOT NULL,
    `dict_label` VARCHAR(100) NOT NULL,
    `dict_value` VARCHAR(100),
    `sort` INT DEFAULT 0,
    `status` TINYINT DEFAULT 1,
    `remark` VARCHAR(200),
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_dict_type` (`dict_type`)
) ENGINE=InnoDB COMMENT='字典表';

CREATE TABLE IF NOT EXISTS `work_order_parts` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `order_id` INT NOT NULL COMMENT '工单ID',
    `part_id` INT NOT NULL COMMENT '配件ID',
    `quantity` INT NOT NULL COMMENT '数量',
    `unit_price` DECIMAL(10,2) NOT NULL COMMENT '单价',
    `total_price` DECIMAL(10,2) NOT NULL COMMENT '总价',
    `status` TINYINT DEFAULT 0 COMMENT '状态：0待出库 1已出库',
    `outbound_at` DATETIME COMMENT '出库时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_id`) REFERENCES `work_orders`(`id`),
    FOREIGN KEY (`part_id`) REFERENCES `parts`(`id`)
) ENGINE=InnoDB COMMENT='工单配件关联表';

CREATE TABLE IF NOT EXISTS `insurance_companies` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,
    `code` VARCHAR(50),
    `contact_person` VARCHAR(50),
    `phone` VARCHAR(20),
    `address` VARCHAR(200),
    `cooperation_level` TINYINT DEFAULT 1,
    `status` TINYINT DEFAULT 1,
    `remark` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='保险公司表';

CREATE TABLE IF NOT EXISTS `repair_item_templates` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL COMMENT '模板名称',
    `code` VARCHAR(50) COMMENT '模板编码',
    `category` VARCHAR(50) COMMENT '分类',
    `standard_hours` DECIMAL(8,2) DEFAULT 0 COMMENT '标准工时',
    `standard_price` DECIMAL(10,2) DEFAULT 0 COMMENT '标准价格',
    `description` TEXT COMMENT '描述',
    `status` TINYINT DEFAULT 1,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `idx_code` (`code`)
) ENGINE=InnoDB COMMENT='维修项目模板表';

CREATE TABLE IF NOT EXISTS `repair_item_template_parts` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `template_id` INT NOT NULL COMMENT '模板ID',
    `part_id` INT NOT NULL COMMENT '配件ID',
    `quantity` INT DEFAULT 1 COMMENT '数量',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`template_id`) REFERENCES `repair_item_templates`(`id`),
    FOREIGN KEY (`part_id`) REFERENCES `parts`(`id`)
) ENGINE=InnoDB COMMENT='维修项目模板配件关联表';
