-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: 4s_repair_db
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `appointments`
--

DROP TABLE IF EXISTS `appointments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appointments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `appointment_no` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '预约编号',
  `customer_id` int NOT NULL COMMENT '客户ID',
  `vehicle_id` int NOT NULL COMMENT '车辆ID',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '联系电话',
  `appointment_date` date NOT NULL COMMENT '预约日期',
  `appointment_time` time NOT NULL COMMENT '预约时间',
  `service_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '服务类型',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '问题描述',
  `status` tinyint DEFAULT '0' COMMENT '状态：0待确认 1已确认 2已完成 3已取消',
  `confirm_by` int DEFAULT NULL COMMENT '确认人ID',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appointment_no` (`appointment_no`),
  KEY `customer_id` (`customer_id`),
  KEY `vehicle_id` (`vehicle_id`),
  KEY `idx_appointment_date` (`appointment_date`),
  CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `appointments_ibfk_2` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预约表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointments`
--

LOCK TABLES `appointments` WRITE;
/*!40000 ALTER TABLE `appointments` DISABLE KEYS */;
/*!40000 ALTER TABLE `appointments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `backup_records`
--

DROP TABLE IF EXISTS `backup_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `backup_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `backup_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '备份名称',
  `backup_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'full' COMMENT '备份类型：full全量 incremental增量',
  `file_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '文件路径',
  `file_size` bigint DEFAULT NULL COMMENT '文件大小(字节)',
  `status` tinyint DEFAULT '0' COMMENT '状态：0进行中 1成功 2失败',
  `created_by` int DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据备份记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `backup_records`
--

LOCK TABLES `backup_records` WRITE;
/*!40000 ALTER TABLE `backup_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `backup_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `claim_manufacturers`
--

DROP TABLE IF EXISTS `claim_manufacturers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `claim_manufacturers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact_person` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` tinyint DEFAULT '1',
  `remark` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='索赔厂家表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `claim_manufacturers`
--

LOCK TABLES `claim_manufacturers` WRITE;
/*!40000 ALTER TABLE `claim_manufacturers` DISABLE KEYS */;
INSERT INTO `claim_manufacturers` VALUES (1,'一汽-大众汽车有限公司','CLM-FAW-VW','孙索赔',NULL,NULL,1,'大众品牌索赔','2026-05-10 07:18:13','2026-05-10 07:18:13','0431-85990000'),(2,'广汽本田汽车有限公司','CLM-GHAC','周保修',NULL,NULL,1,'本田品牌索赔','2026-05-10 07:18:13','2026-05-10 07:18:13','020-82218888'),(3,'上汽通用汽车有限公司','CLM-SGM','吴质保',NULL,NULL,1,'别克/雪佛兰品牌索赔','2026-05-10 07:18:13','2026-05-10 07:18:13','021-28902888'),(4,'北京奔驰汽车有限公司','CLM-BBAC','郑保修',NULL,NULL,1,'奔驰品牌索赔','2026-05-10 07:18:13','2026-05-10 07:18:13','010-67828888');
/*!40000 ALTER TABLE `claim_manufacturers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_no` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '客户编号',
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '客户姓名',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '联系电话',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '邮箱',
  `gender` tinyint DEFAULT '0' COMMENT '性别：0未知 1男 2女',
  `birthday` date DEFAULT NULL COMMENT '生日',
  `id_card` varchar(18) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '身份证号',
  `address` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '地址',
  `customer_type` tinyint DEFAULT '1' COMMENT '客户类型：1个人 2企业',
  `company_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '公司名称',
  `vip_level` tinyint DEFAULT '0' COMMENT 'VIP等级',
  `total_spending` decimal(12,2) DEFAULT '0.00' COMMENT '累计消费金额',
  `points` int DEFAULT '0' COMMENT '积分',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `status` tinyint DEFAULT '1' COMMENT '状态：1正常 0禁用',
  `created_by` int DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `customer_no` (`customer_no`),
  KEY `idx_phone` (`phone`),
  KEY `idx_customer_no` (`customer_no`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (1,'CUS-2024-001','张伟','13901001001','zhangwei@qq.com',1,'1985-03-15',NULL,'北京市朝阳区建国路88号',1,NULL,2,12580.00,1258,'老客户，定期保养',1,1,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(2,'CUS-2024-002','李娜','13901001002','lina@163.com',2,'1990-07-22',NULL,'北京市海淀区中关村大街1号',1,NULL,1,5680.00,568,'',1,1,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(3,'CUS-2024-003','王强','13901001003','wangqiang@gmail.com',1,'1978-11-08',NULL,'北京市丰台区南三环西路16号',2,'北京万达科技有限公司',3,38900.00,3890,'公司车队客户，多台车辆',1,1,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(4,'CUS-2024-004','陈芳','13901001004','chenfang@qq.com',2,'1995-01-30',NULL,'北京市西城区金融街9号',1,NULL,0,1280.00,128,'新客户',1,1,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(5,'CUS-2024-005','刘洋','13901001005','liuyang@outlook.com',1,'1982-05-18',NULL,'北京市东城区东直门内大街',1,NULL,2,18760.00,1876,'推荐客户3位',1,1,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(6,'CUS-2024-006','赵敏','13901001006','zhaomin@126.com',2,'1988-09-12',NULL,'北京市昌平区回龙观',1,NULL,1,7350.00,735,'',1,1,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(7,'CUS-2024-007','孙鹏','13901001007','sunpeng@qq.com',1,'1975-12-25',NULL,'北京市通州区新华大街',2,'顺达物流有限公司',3,52300.00,5230,'物流公司，维修频繁',1,1,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(8,'CUS-2024-008','周婷','13901001008','zhouting@sina.com',2,'1992-04-06',NULL,'北京市大兴区黄村',1,NULL,0,0.00,0,'首次到店',1,1,'2026-05-10 07:18:14','2026-05-10 07:18:14');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dict_items`
--

DROP TABLE IF EXISTS `dict_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dict_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `dict_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dict_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dict_value` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sort` int DEFAULT '0',
  `status` tinyint DEFAULT '1',
  `remark` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_dict_type` (`dict_type`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='字典表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dict_items`
--

LOCK TABLES `dict_items` WRITE;
/*!40000 ALTER TABLE `dict_items` DISABLE KEYS */;
INSERT INTO `dict_items` VALUES (1,'service_type','常规保养','常规保养',1,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(2,'service_type','故障维修','故障维修',2,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(3,'service_type','事故维修','事故维修',3,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(4,'service_type','索赔维修','索赔维修',4,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(5,'service_type','年检','年检',5,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(6,'payment_method','现金','cash',1,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(7,'payment_method','微信','wechat',2,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(8,'payment_method','支付宝','alipay',3,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(9,'payment_method','银行卡','bank_card',4,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(10,'payment_method','保险理赔','insurance',5,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(11,'vehicle_brand','大众','大众',1,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(12,'vehicle_brand','本田','本田',2,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(13,'vehicle_brand','别克','别克',3,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(14,'vehicle_brand','奔驰','奔驰',4,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(15,'vehicle_brand','宝马','宝马',5,1,NULL,'2026-05-10 07:18:14',NULL,NULL),(16,'vehicle_brand','丰田','丰田',6,1,NULL,'2026-05-10 07:18:14',NULL,NULL);
/*!40000 ALTER TABLE `dict_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employee_labor_stats`
--

DROP TABLE IF EXISTS `employee_labor_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee_labor_stats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int NOT NULL COMMENT '员工ID',
  `stat_date` date NOT NULL COMMENT '统计日期',
  `stat_month` varchar(7) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '统计月份',
  `total_hours` decimal(8,2) DEFAULT '0.00' COMMENT '总工时',
  `total_amount` decimal(12,2) DEFAULT '0.00' COMMENT '总工时金额',
  `order_count` int DEFAULT '0' COMMENT '完成工单数',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_emp_date` (`employee_id`,`stat_date`),
  KEY `idx_stat_month` (`stat_month`),
  CONSTRAINT `employee_labor_stats_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='员工工时统计表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employee_labor_stats`
--

LOCK TABLES `employee_labor_stats` WRITE;
/*!40000 ALTER TABLE `employee_labor_stats` DISABLE KEYS */;
/*!40000 ALTER TABLE `employee_labor_stats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees` (
  `id` int NOT NULL AUTO_INCREMENT,
  `employee_no` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '员工工号',
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '姓名',
  `gender` tinyint DEFAULT '0' COMMENT '性别',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系电话',
  `id_card` varchar(18) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '身份证号',
  `department` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '部门',
  `position` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '职位',
  `employee_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '员工类型：technician技术员 service服务顾问 manager管理',
  `level` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '级别',
  `entry_date` date DEFAULT NULL COMMENT '入职日期',
  `base_salary` decimal(10,2) DEFAULT '0.00' COMMENT '基本工资',
  `hourly_rate` decimal(8,2) DEFAULT '0.00' COMMENT '工时单价',
  `user_id` int DEFAULT NULL COMMENT '关联用户ID',
  `status` tinyint DEFAULT '1' COMMENT '状态：1在职 0离职',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_no` (`employee_no`),
  KEY `user_id` (`user_id`),
  KEY `idx_employee_no` (`employee_no`),
  CONSTRAINT `employees_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='员工表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insurance_companies`
--

DROP TABLE IF EXISTS `insurance_companies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insurance_companies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact_person` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cooperation_level` tinyint DEFAULT '1',
  `status` tinyint DEFAULT '1',
  `remark` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='保险公司表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insurance_companies`
--

LOCK TABLES `insurance_companies` WRITE;
/*!40000 ALTER TABLE `insurance_companies` DISABLE KEYS */;
INSERT INTO `insurance_companies` VALUES (1,'中国人民财产保险','INS-PICC','刘保险',NULL,NULL,1,1,'人保财险，合作紧密','2026-05-10 07:18:13','2026-05-10 07:18:13','95518'),(2,'中国平安财产保险','INS-PINGAN','张理赔',NULL,NULL,1,1,'平安产险','2026-05-10 07:18:13','2026-05-10 07:18:13','95511'),(3,'中国太平洋财产保险','INS-CPIC','王定损',NULL,NULL,1,1,'太保产险','2026-05-10 07:18:13','2026-05-10 07:18:13','95500'),(4,'中国人寿财产保险','INS-CLIC','赵服务',NULL,NULL,1,1,'国寿财险','2026-05-10 07:18:13','2026-05-10 07:18:13','95519');
/*!40000 ALTER TABLE `insurance_companies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoices`
--

DROP TABLE IF EXISTS `invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_no` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '发票号',
  `order_id` int DEFAULT NULL COMMENT '工单ID',
  `customer_id` int DEFAULT NULL COMMENT '客户ID',
  `invoice_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'normal' COMMENT '发票类型：normal普通 special专用',
  `title` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '发票抬头',
  `tax_no` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '税号',
  `amount` decimal(12,2) NOT NULL COMMENT '发票金额',
  `tax_amount` decimal(12,2) DEFAULT '0.00' COMMENT '税额',
  `status` tinyint DEFAULT '0' COMMENT '状态：0待开票 1已开票 2已作废',
  `issued_by` int DEFAULT NULL COMMENT '开票人ID',
  `issued_at` datetime DEFAULT NULL COMMENT '开票时间',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_no` (`invoice_no`),
  KEY `order_id` (`order_id`),
  KEY `idx_invoice_no` (`invoice_no`),
  CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `work_orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='发票表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoices`
--

LOCK TABLES `invoices` WRITE;
/*!40000 ALTER TABLE `invoices` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `operation_logs`
--

DROP TABLE IF EXISTS `operation_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `operation_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL COMMENT '操作用户ID',
  `username` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '用户名',
  `action` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '操作类型',
  `module` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属模块',
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '操作描述',
  `ip_address` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'IP地址',
  `request_data` json DEFAULT NULL COMMENT '请求数据',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `operation_logs`
--

LOCK TABLES `operation_logs` WRITE;
/*!40000 ALTER TABLE `operation_logs` DISABLE KEYS */;
INSERT INTO `operation_logs` VALUES (1,1,'admin','login','auth','用户登录','127.0.0.1',NULL,'2026-05-10 07:18:59'),(2,1,'admin','login','auth','用户登录','127.0.0.1',NULL,'2026-05-10 07:25:23'),(3,1,'admin','login','auth','用户登录','127.0.0.1',NULL,'2026-05-10 07:32:26'),(4,1,'admin','login','auth','用户登录','127.0.0.1',NULL,'2026-05-10 07:33:24'),(5,1,'admin','login','auth','用户登录','127.0.0.1',NULL,'2026-05-10 07:34:58');
/*!40000 ALTER TABLE `operation_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parts`
--

DROP TABLE IF EXISTS `parts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `part_no` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配件编号',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配件名称',
  `pinyin_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category_id` int DEFAULT NULL COMMENT '分类ID',
  `brand` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '品牌',
  `model` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '规格型号',
  `specification` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unit` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '个' COMMENT '单位',
  `purchase_price` decimal(10,2) DEFAULT '0.00' COMMENT '采购价(加权平均)',
  `selling_price` decimal(10,2) DEFAULT '0.00' COMMENT '销售价',
  `network_price` decimal(10,2) DEFAULT '0.00',
  `stock_quantity` int DEFAULT '0' COMMENT '当前库存',
  `min_stock` int DEFAULT '0' COMMENT '最低库存预警',
  `safety_stock` int DEFAULT '0',
  `min_package_qty` int DEFAULT '0',
  `max_stock` int DEFAULT '0' COMMENT '最高库存',
  `warehouse` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '默认仓库' COMMENT '仓库',
  `location` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '库位',
  `boutique_location` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `spare_location` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `factory_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `origin` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `replaceable_part` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `warehouse_location` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `applicable_vehicles` text COLLATE utf8mb4_unicode_ci,
  `applicable_vehicle` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category1` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category2` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `discontinued` tinyint(1) DEFAULT '0',
  `archive_remark` text COLLATE utf8mb4_unicode_ci,
  `status` tinyint DEFAULT '1' COMMENT '状态',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `part_no` (`part_no`),
  KEY `idx_part_no` (`part_no`),
  KEY `idx_category_id` (`category_id`),
  CONSTRAINT `parts_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `parts_categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='配件库存表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parts`
--

LOCK TABLES `parts` WRITE;
/*!40000 ALTER TABLE `parts` DISABLE KEYS */;
INSERT INTO `parts` VALUES (1,'PJ-ENG-001','机油滤清器','JYLQ',1,'博世',NULL,'F026407005','个',18.00,35.00,30.00,120,20,15,10,200,'备件库','A-01-01',NULL,NULL,'W914/4','国产',NULL,NULL,NULL,NULL,'通用','油液滤芯','滤清器',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(2,'PJ-ENG-002','空气滤清器','KQLQ',11,'曼牌',NULL,'C27030','个',35.00,68.00,58.00,80,15,10,5,150,'备件库','A-01-02',NULL,NULL,'1H0129620','进口',NULL,NULL,NULL,NULL,'大众系列','油液滤芯','滤清器',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(3,'PJ-ENG-003','火花塞','HHS',12,'NGK',NULL,'PFR7S8EG','支',28.00,55.00,48.00,200,40,30,4,400,'备件库','A-02-01',NULL,NULL,'SILZKR8B8S','日本',NULL,NULL,NULL,NULL,'本田系列','发动机配件','点火系统',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(4,'PJ-BRK-001','前刹车片','QSC',2,'博世',NULL,'BC956','套',120.00,240.00,210.00,45,10,8,1,80,'备件库','B-01-01',NULL,NULL,'06D698151F','国产',NULL,NULL,NULL,NULL,'大众系列','制动系统','刹车片',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(5,'PJ-BRK-002','后刹车片','HSC',4,'博世',NULL,'BC905','套',95.00,190.00,165.00,38,10,8,1,60,'备件库','B-01-02',NULL,NULL,'06D698521','国产',NULL,NULL,NULL,NULL,'大众系列','制动系统','刹车片',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(6,'PJ-BRK-003','刹车盘（前）','QSCP',13,'TRW',NULL,'DF4391','个',180.00,360.00,320.00,22,5,4,1,40,'备件库','B-02-01',NULL,NULL,'5C0615301A','国产',NULL,NULL,NULL,NULL,'大众系列','制动系统','刹车盘',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(7,'PJ-ELC-001','蓄电池','XDC',14,'风帆',NULL,'6-QW-60','个',280.00,520.00,460.00,15,5,3,1,30,'备件库','C-01-01',NULL,NULL,'12V60Ah','国产',NULL,NULL,NULL,NULL,'通用','电气系统','蓄电池',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(8,'PJ-ELC-002','远光灯泡','YGDP',15,'飞利浦',NULL,'H7 12V55W','个',15.00,30.00,25.00,150,30,20,10,300,'备件库','C-02-01',NULL,NULL,'12972PRC','国产',NULL,NULL,NULL,NULL,'通用','电气系统','灯泡',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(9,'PJ-CHS-001','减震器（前）','QJZQ',15,'萨克斯',NULL,'313421','支',320.00,620.00,550.00,12,4,3,1,20,'备件库','D-01-01',NULL,NULL,'5C0413023B','德国',NULL,NULL,NULL,NULL,'大众系列','底盘悬挂','减震器',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(10,'PJ-FLR-001','5W-30全合成机油','JY',15,'嘉实多',NULL,'4L装','桶',168.00,328.00,288.00,60,15,10,6,100,'油液库','E-01-01',NULL,NULL,'EDGE5W30','进口',NULL,NULL,NULL,NULL,'通用','油液滤芯','机油',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(11,'PJ-FLR-002','防冻液','FDY',15,'百适通',NULL,'4L装','桶',65.00,128.00,108.00,40,10,8,4,80,'油液库','E-01-02',NULL,NULL,'P-OAT','进口',NULL,NULL,NULL,NULL,'通用','油液滤芯','防冻液',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(12,'PJ-FLR-003','变速箱油','BSXY',15,'爱信',NULL,'1L装','瓶',55.00,108.00,95.00,50,10,8,12,100,'油液库','E-02-01',NULL,NULL,'AFW+','日本',NULL,NULL,NULL,NULL,'通用','油液滤芯','变速箱油',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(13,'PJ-BDY-001','前保险杠','QBXG',15,'原厂',NULL,'喷漆件','个',680.00,1380.00,1200.00,5,2,1,1,10,'车身库','F-01-01',NULL,NULL,'5C0807221A','国产',NULL,NULL,NULL,NULL,'大众系列','车身外观','保险杠',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(14,'PJ-AC-001','空调滤清器','KTLQ',15,'曼牌',NULL,'CUK2202','个',42.00,85.00,72.00,90,20,15,5,150,'备件库','A-01-03',NULL,NULL,'5Q0129620','进口',NULL,NULL,NULL,NULL,'大众系列','空调系统','滤清器',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13'),(15,'PJ-INT-001','车载空气净化器','KJHQ',15,'3M',NULL,'PN38803','台',180.00,368.00,320.00,8,3,2,1,20,'精品库',NULL,'G-01-01',NULL,NULL,'国产',NULL,NULL,NULL,NULL,'通用','内饰精品','净化器',0,NULL,1,'2026-05-10 07:18:13','2026-05-10 07:18:13');
/*!40000 ALTER TABLE `parts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parts_categories`
--

DROP TABLE IF EXISTS `parts_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parts_categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '分类名称',
  `code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '分类编码',
  `parent_id` int DEFAULT '0' COMMENT '父分类ID',
  `level` tinyint DEFAULT '1' COMMENT '层级',
  `sort` int DEFAULT '0' COMMENT '排序',
  `status` tinyint DEFAULT '1' COMMENT '状态',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='配件分类表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parts_categories`
--

LOCK TABLES `parts_categories` WRITE;
/*!40000 ALTER TABLE `parts_categories` DISABLE KEYS */;
INSERT INTO `parts_categories` VALUES (1,'发动机配件','ENGINE',0,1,0,1,'2026-05-10 07:15:16'),(2,'底盘配件','CHASSIS',0,1,0,1,'2026-05-10 07:15:16'),(3,'电气系统','ELECTRICAL',0,1,0,1,'2026-05-10 07:15:16'),(4,'车身配件','BODY',0,1,0,1,'2026-05-10 07:15:16'),(5,'保养件','MAINTENANCE',0,1,0,1,'2026-05-10 07:15:16'),(11,'制动系统','BRAKE',0,1,2,1,'2026-05-10 07:18:13'),(12,'电气系统','ELECTRIC',0,1,3,1,'2026-05-10 07:18:13'),(13,'内饰精品','INTERIOR',0,1,6,1,'2026-05-10 07:18:13'),(14,'油液滤芯','FILTER',0,1,7,1,'2026-05-10 07:18:13'),(15,'空调系统','AC',0,1,8,1,'2026-05-10 07:18:13');
/*!40000 ALTER TABLE `parts_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parts_inbound`
--

DROP TABLE IF EXISTS `parts_inbound`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parts_inbound` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inbound_no` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '入库单号',
  `supplier_id` int DEFAULT NULL COMMENT '供应商ID',
  `total_amount` decimal(12,2) DEFAULT '0.00' COMMENT '总金额',
  `total_quantity` int DEFAULT '0' COMMENT '总数量',
  `status` tinyint DEFAULT '0' COMMENT '状态：0待入库 1已入库 2已取消',
  `inbound_by` int DEFAULT NULL COMMENT '入库人ID',
  `inbound_at` datetime DEFAULT NULL COMMENT '入库时间',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_by` int DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `invoice_type` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT '无发票',
  `tax_rate` decimal(5,2) DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `inbound_no` (`inbound_no`),
  KEY `supplier_id` (`supplier_id`),
  KEY `idx_inbound_no` (`inbound_no`),
  CONSTRAINT `parts_inbound_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='配件入库记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parts_inbound`
--

LOCK TABLES `parts_inbound` WRITE;
/*!40000 ALTER TABLE `parts_inbound` DISABLE KEYS */;
/*!40000 ALTER TABLE `parts_inbound` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parts_inbound_details`
--

DROP TABLE IF EXISTS `parts_inbound_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parts_inbound_details` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inbound_id` int NOT NULL COMMENT '入库单ID',
  `part_id` int NOT NULL COMMENT '配件ID',
  `quantity` int NOT NULL COMMENT '数量',
  `unit_price` decimal(10,2) NOT NULL COMMENT '单价',
  `total_price` decimal(10,2) NOT NULL COMMENT '小计',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `unit` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `unit_price_with_tax` decimal(12,2) DEFAULT '0.00',
  `location` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `inbound_id` (`inbound_id`),
  KEY `part_id` (`part_id`),
  CONSTRAINT `parts_inbound_details_ibfk_1` FOREIGN KEY (`inbound_id`) REFERENCES `parts_inbound` (`id`),
  CONSTRAINT `parts_inbound_details_ibfk_2` FOREIGN KEY (`part_id`) REFERENCES `parts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='入库明细表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parts_inbound_details`
--

LOCK TABLES `parts_inbound_details` WRITE;
/*!40000 ALTER TABLE `parts_inbound_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `parts_inbound_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parts_outbound`
--

DROP TABLE IF EXISTS `parts_outbound`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parts_outbound` (
  `id` int NOT NULL AUTO_INCREMENT,
  `outbound_no` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '出库单号',
  `order_id` int DEFAULT NULL COMMENT '关联工单ID',
  `outbound_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'repair' COMMENT '出库类型：repair维修 return退库 scrap报废',
  `total_amount` decimal(12,2) DEFAULT '0.00' COMMENT '总金额',
  `total_quantity` int DEFAULT '0' COMMENT '总数量',
  `status` tinyint DEFAULT '0' COMMENT '状态：0待出库 1已出库 2已取消',
  `outbound_by` int DEFAULT NULL COMMENT '出库人ID',
  `outbound_at` datetime DEFAULT NULL COMMENT '出库时间',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_by` int DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `outbound_no` (`outbound_no`),
  KEY `idx_outbound_no` (`outbound_no`),
  KEY `idx_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='配件出库记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parts_outbound`
--

LOCK TABLES `parts_outbound` WRITE;
/*!40000 ALTER TABLE `parts_outbound` DISABLE KEYS */;
/*!40000 ALTER TABLE `parts_outbound` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parts_outbound_details`
--

DROP TABLE IF EXISTS `parts_outbound_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parts_outbound_details` (
  `id` int NOT NULL AUTO_INCREMENT,
  `outbound_id` int NOT NULL COMMENT '出库单ID',
  `part_id` int NOT NULL COMMENT '配件ID',
  `quantity` int NOT NULL COMMENT '数量',
  `unit_price` decimal(10,2) NOT NULL COMMENT '单价(加权平均)',
  `total_price` decimal(10,2) NOT NULL COMMENT '小计',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `outbound_id` (`outbound_id`),
  KEY `part_id` (`part_id`),
  CONSTRAINT `parts_outbound_details_ibfk_1` FOREIGN KEY (`outbound_id`) REFERENCES `parts_outbound` (`id`),
  CONSTRAINT `parts_outbound_details_ibfk_2` FOREIGN KEY (`part_id`) REFERENCES `parts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='出库明细表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parts_outbound_details`
--

LOCK TABLES `parts_outbound_details` WRITE;
/*!40000 ALTER TABLE `parts_outbound_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `parts_outbound_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `payment_no` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '收款单号',
  `order_id` int DEFAULT NULL COMMENT '工单ID',
  `customer_id` int DEFAULT NULL COMMENT '客户ID',
  `amount` decimal(12,2) NOT NULL COMMENT '收款金额',
  `payment_method` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '支付方式：cash微信支付宝bank',
  `payment_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'repair' COMMENT '收款类型：repair维修 deposit定金 other其他',
  `transaction_no` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易流水号',
  `payer_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '付款人',
  `status` tinyint DEFAULT '1' COMMENT '状态：1已支付 2已退款 3已取消',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `received_by` int DEFAULT NULL COMMENT '收款人ID',
  `received_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '收款时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `payment_no` (`payment_no`),
  KEY `customer_id` (`customer_id`),
  KEY `idx_payment_no` (`payment_no`),
  KEY `idx_order_id` (`order_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `work_orders` (`id`),
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收款记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repair_item_template_parts`
--

DROP TABLE IF EXISTS `repair_item_template_parts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repair_item_template_parts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `template_id` int NOT NULL COMMENT '模板ID',
  `part_id` int NOT NULL COMMENT '配件ID',
  `quantity` int DEFAULT '1' COMMENT '数量',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `sort_order` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `template_id` (`template_id`),
  KEY `part_id` (`part_id`),
  CONSTRAINT `repair_item_template_parts_ibfk_1` FOREIGN KEY (`template_id`) REFERENCES `repair_item_templates` (`id`),
  CONSTRAINT `repair_item_template_parts_ibfk_2` FOREIGN KEY (`part_id`) REFERENCES `parts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='维修项目模板配件关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repair_item_template_parts`
--

LOCK TABLES `repair_item_template_parts` WRITE;
/*!40000 ALTER TABLE `repair_item_template_parts` DISABLE KEYS */;
/*!40000 ALTER TABLE `repair_item_template_parts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repair_item_templates`
--

DROP TABLE IF EXISTS `repair_item_templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repair_item_templates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模板名称',
  `code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '模板编码',
  `category` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '分类',
  `standard_hours` decimal(8,2) DEFAULT '0.00' COMMENT '标准工时',
  `standard_price` decimal(10,2) DEFAULT '0.00' COMMENT '标准价格',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '描述',
  `status` tinyint DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `repair_category` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `item_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `charge_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `labor_price` decimal(10,2) DEFAULT '0.00',
  `remark` text COLLATE utf8mb4_unicode_ci,
  `labor_hours` decimal(6,2) DEFAULT '0.00',
  `sort_order` int DEFAULT '0',
  `item_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='维修项目模板表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repair_item_templates`
--

LOCK TABLES `repair_item_templates` WRITE;
/*!40000 ALTER TABLE `repair_item_templates` DISABLE KEYS */;
INSERT INTO `repair_item_templates` VALUES (1,'小保养（更换机油机滤）',NULL,'保养',0.00,0.00,'更换机油、机油滤清器，全车检查',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','常规保养',1,'WX-001','工时',120.00,NULL,1.00,1,'小保养（更换机油机滤）'),(2,'大保养（更换机油三滤）',NULL,'保养',0.00,0.00,'更换机油、机滤、空滤、空调滤，全车检查',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','常规保养',1,'WX-002','工时',240.00,NULL,2.00,2,'大保养（更换机油三滤）'),(3,'更换刹车片（前）',NULL,'制动',0.00,0.00,'更换前轮刹车片',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','制动维修',1,'WX-003','工时',180.00,NULL,1.50,3,'更换刹车片（前）'),(4,'更换刹车片（后）',NULL,'制动',0.00,0.00,'更换后轮刹车片',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','制动维修',1,'WX-004','工时',180.00,NULL,1.50,4,'更换刹车片（后）'),(5,'更换刹车盘（前）',NULL,'制动',0.00,0.00,'更换前轮刹车盘',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','制动维修',1,'WX-005','工时',280.00,NULL,2.00,5,'更换刹车盘（前）'),(6,'更换蓄电池',NULL,'电气',0.00,0.00,'更换蓄电池，检测充电系统',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','电气维修',1,'WX-006','工时',60.00,NULL,0.50,6,'更换蓄电池'),(7,'更换火花塞',NULL,'发动机',0.00,0.00,'更换全部火花塞',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','发动机维修',1,'WX-007','工时',120.00,NULL,1.00,7,'更换火花塞'),(8,'更换减震器（前单侧）',NULL,'底盘',0.00,0.00,'更换前减震器',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','底盘维修',1,'WX-008','工时',300.00,NULL,2.00,8,'更换减震器（前单侧）'),(9,'更换防冻液',NULL,'保养',0.00,0.00,'更换防冻液，排气检查',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','常规保养',1,'WX-009','工时',100.00,NULL,1.00,9,'更换防冻液'),(10,'更换变速箱油',NULL,'保养',0.00,0.00,'更换变速箱油，检查变速箱',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','常规保养',1,'WX-010','工时',200.00,NULL,1.50,10,'更换变速箱油'),(11,'空调系统清洗',NULL,'空调',0.00,0.00,'空调管路清洗、杀菌、除味',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','空调维修',1,'WX-011','工时',150.00,NULL,1.00,11,'空调系统清洗'),(12,'更换前保险杠',NULL,'钣金',0.00,0.00,'拆卸更换前保险杠，喷漆',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','钣金喷漆',1,'WX-012','工时',600.00,NULL,4.00,12,'更换前保险杠'),(13,'四轮定位',NULL,'底盘',0.00,0.00,'四轮定位检测调整',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','底盘维修',1,'WX-013','工时',200.00,NULL,1.00,13,'四轮定位'),(14,'电脑诊断',NULL,'电气',0.00,0.00,'OBD电脑诊断，故障码读取',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','电气维修',1,'WX-014','工时',80.00,NULL,0.50,14,'电脑诊断'),(15,'更换轮胎（单条）',NULL,'轮胎',0.00,0.00,'更换轮胎，动平衡',1,'2026-05-10 07:18:14','2026-05-10 07:18:14','轮胎服务',1,'WX-015','工时',50.00,NULL,0.50,15,'更换轮胎（单条）');
/*!40000 ALTER TABLE `repair_item_templates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repair_items`
--

DROP TABLE IF EXISTS `repair_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repair_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL COMMENT '工单ID',
  `item_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '项目名称',
  `item_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '项目编码',
  `category` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '项目类别',
  `labor_hours` decimal(6,2) DEFAULT '0.00' COMMENT '工时',
  `labor_price` decimal(10,2) DEFAULT '0.00' COMMENT '工时单价',
  `labor_amount` decimal(10,2) DEFAULT '0.00' COMMENT '工时金额',
  `technician_id` int DEFAULT NULL COMMENT '维修技师ID',
  `technician_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '技师姓名',
  `status` tinyint DEFAULT '0' COMMENT '状态：0待处理 1进行中 2已完成',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `discount_rate` decimal(4,2) DEFAULT '1.00',
  `charge_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `repair_category` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_order_id` (`order_id`),
  CONSTRAINT `repair_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `work_orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='维修项目表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repair_items`
--

LOCK TABLES `repair_items` WRITE;
/*!40000 ALTER TABLE `repair_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `repair_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色名称',
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色编码',
  `description` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '角色描述',
  `permissions` json DEFAULT NULL COMMENT '权限配置',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'系统管理员','admin','系统超级管理员，拥有所有权限','[\"*\"]','2026-05-10 07:15:16','2026-05-10 07:15:16'),(2,'服务经理','manager','服务部门经理','[\"customer:*\", \"work_order:*\", \"parts:*\", \"finance:*\", \"report:*\"]','2026-05-10 07:15:16','2026-05-10 07:15:16'),(3,'服务顾问','advisor','接待客户，创建工单','[\"customer:read\", \"customer:create\", \"work_order:create\", \"work_order:read\", \"work_order:update\"]','2026-05-10 07:15:16','2026-05-10 07:15:16'),(4,'维修技师','technician','执行维修工作','[\"work_order:read\", \"work_order:repair\"]','2026-05-10 07:15:16','2026-05-10 07:15:16'),(5,'配件管理员','parts_manager','管理配件库存','[\"parts:*\"]','2026-05-10 07:15:16','2026-05-10 07:15:16'),(6,'财务人员','finance','处理财务事务','[\"finance:*\", \"report:finance\"]','2026-05-10 07:15:16','2026-05-10 07:15:16');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_movements`
--

DROP TABLE IF EXISTS `stock_movements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock_movements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `part_id` int NOT NULL COMMENT '配件ID',
  `movement_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '变动类型：in入库 out出库 adjust调整',
  `reference_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '关联类型：inbound outbound order',
  `reference_id` int DEFAULT NULL COMMENT '关联ID',
  `quantity_before` int NOT NULL COMMENT '变动前数量',
  `quantity_change` int NOT NULL COMMENT '变动数量',
  `quantity_after` int NOT NULL COMMENT '变动后数量',
  `price_before` decimal(10,2) DEFAULT NULL COMMENT '变动前单价',
  `price_after` decimal(10,2) DEFAULT NULL COMMENT '变动后单价',
  `operator_id` int DEFAULT NULL COMMENT '操作人ID',
  `remark` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_part_id` (`part_id`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `stock_movements_ibfk_1` FOREIGN KEY (`part_id`) REFERENCES `parts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='库存变动记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_movements`
--

LOCK TABLES `stock_movements` WRITE;
/*!40000 ALTER TABLE `stock_movements` DISABLE KEYS */;
/*!40000 ALTER TABLE `stock_movements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suppliers`
--

DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suppliers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '供应商名称',
  `code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '供应商编码',
  `contact_person` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系人',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '联系电话',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '邮箱',
  `address` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '地址',
  `bank_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '开户银行',
  `bank_account` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '银行账号',
  `credit_level` tinyint DEFAULT '1' COMMENT '信用等级',
  `status` tinyint DEFAULT '1' COMMENT '状态',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='供应商表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suppliers`
--

LOCK TABLES `suppliers` WRITE;
/*!40000 ALTER TABLE `suppliers` DISABLE KEYS */;
INSERT INTO `suppliers` VALUES (6,'博世贸易（上海）有限公司','SUP-BOSCH','王建国','021-61806000','sales@bosch.com.cn','上海市浦东新区陆家嘴','中国银行上海分行','6228480031234567890',5,1,'全球知名汽车零部件供应商','2026-05-10 07:18:13','2026-05-10 07:18:13'),(7,'电装（中国）投资有限公司','SUP-DENSO','李明辉','010-65908888','info@denso.com.cn','北京市朝阳区建国路','工商银行北京分行','6222021234567890123',5,1,'日本电装中国总部','2026-05-10 07:18:13','2026-05-10 07:18:13'),(8,'广州本田汽车零部件有限公司','SUP-HONDA','陈伟强','020-82218888','parts@honda-guangzhou.com','广州市黄埔区','建设银行广州分行','6227001234567890456',4,1,'本田原厂件供应商','2026-05-10 07:18:13','2026-05-10 07:18:13'),(9,'一汽大众零部件供应中心','SUP-FAW-VW','张志远','0431-85998888','parts@faw-vw.com','长春市汽车产业开发区','农业银行长春分行','6228481234567890789',4,1,'大众原厂件供应','2026-05-10 07:18:13','2026-05-10 07:18:13'),(10,'浙江万向精工有限公司','SUP-WANXIANG','赵德明','0571-82888888','sales@wanxiang.com','杭州市萧山区','招商银行杭州分行','6225881234567890123',3,1,'底盘件专业供应商','2026-05-10 07:18:13','2026-05-10 07:18:13');
/*!40000 ALTER TABLE `suppliers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_configs`
--

DROP TABLE IF EXISTS `system_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `config_key` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置键',
  `config_value` text COLLATE utf8mb4_unicode_ci COMMENT '配置值',
  `config_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'string' COMMENT '类型：string number boolean json',
  `description` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '描述',
  `group` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'general' COMMENT '分组',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `group_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'general',
  PRIMARY KEY (`id`),
  UNIQUE KEY `config_key` (`config_key`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_configs`
--

LOCK TABLES `system_configs` WRITE;
/*!40000 ALTER TABLE `system_configs` DISABLE KEYS */;
INSERT INTO `system_configs` VALUES (1,'shop_name','XX汽车4S店','string','店铺名称','basic','2026-05-10 07:15:16','general'),(2,'shop_address','XX市XX区XX路XX号','string','店铺地址','basic','2026-05-10 07:15:16','general'),(3,'shop_phone','400-xxx-xxxx','string','联系电话','basic','2026-05-10 07:15:16','general'),(4,'default_labor_rate','200','number','默认工时单价','price','2026-05-10 07:15:16','general'),(5,'tax_rate','0.13','number','税率','price','2026-05-10 07:15:16','general'),(6,'stock_warning_enabled','true','boolean','是否启用库存预警','stock','2026-05-10 07:15:16','general'),(7,'backup_retention_days','30','number','备份保留天数','system','2026-05-10 07:15:16','general');
/*!40000 ALTER TABLE `system_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码哈希',
  `real_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '真实姓名',
  `gender` smallint DEFAULT '0' COMMENT '性别：0未知 1男 2女',
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '手机号',
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '邮箱',
  `id_card` varchar(18) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '身份证号',
  `avatar` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像',
  `role_id` int NOT NULL COMMENT '角色ID',
  `department` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '部门',
  `position` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '职位',
  `employee_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '员工类型',
  `employee_no` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '员工工号',
  `level` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '级别',
  `title` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '职称',
  `entry_date` date DEFAULT NULL COMMENT '入职日期',
  `base_salary` decimal(10,2) DEFAULT '0.00' COMMENT '基本工资',
  `hourly_rate` decimal(8,2) DEFAULT '0.00' COMMENT '工时单价',
  `status` tinyint DEFAULT '1' COMMENT '状态：1启用 0禁用',
  `last_login` datetime DEFAULT NULL COMMENT '最后登录时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','scrypt:32768:8:1$0nd9RsME2gFwbngo$4ea6cc2366f0f7ddabf9f2733824472326849e836d2e8a549995f1dfae709f20718e6c1342a07a0ca55d93b65930574789e79866d842b8c81ea36014bbac5f8c','系统管理员',0,'13800000000','admin@jzx.com',NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0.00,0.00,1,'2026-05-10 07:34:58','2026-05-10 07:15:37','2026-05-10 07:34:58'),(2,'manager','scrypt:32768:8:1$z3wej1El3lgyCm8x$102a4af70d85b458fefa2daa7bb6345d4f6ae38dee6a39d6348a31294d3111c87a81bb310c77e19894b98861444132ed03dc584b8822e91e546f6b01402e1965','李经理',1,'13800000001','manager@jzx.com',NULL,NULL,2,'售后服务部','服务经理','正式','EMP001','高级','服务经理','2024-01-01',0.00,0.00,1,NULL,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(3,'advisor1','scrypt:32768:8:1$LyMzhrBluIygh6sg$3e47f29ac441a28eefd2c486a207cf9201a3f68e83d3915c719e5119aea7465fd2a6a2382eb8090d7d752a9af0e6a9f54b25a7735b81657e4637ff52f313a070','王顾问',1,'13800000002','advisor1@jzx.com',NULL,NULL,3,'售后服务部','服务顾问','正式','EMP002','中级','服务顾问','2024-01-01',0.00,0.00,1,NULL,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(4,'advisor2','scrypt:32768:8:1$4f9BNvuBDo79MJxH$b25de89a8088396f553de5d314f07f23908b2186a942b0f01f065e0128e71496ba7a1cf333f80d6feb54fd997e2e91debc2eb684d22d5e03782ddcd6c395dc2d','陈顾问',1,'13800000003','advisor2@jzx.com',NULL,NULL,3,'售后服务部','服务顾问','正式','EMP003','初级','服务顾问','2024-01-01',0.00,0.00,1,NULL,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(5,'tech1','scrypt:32768:8:1$BdlePOEZwuTmt7h3$2e50e9bef1989feaaeaa22d8eb34106a228991769da0e38505511f0036c11dd1136a0976e99a60d752ae10e041c6c1d3e05d234edc940d976ecda62f3d658f7a','张师傅',1,'13800000004','tech1@jzx.com',NULL,NULL,4,'维修车间','主修技师','正式','EMP004','高级','技师组长','2024-01-01',0.00,0.00,1,NULL,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(6,'tech2','scrypt:32768:8:1$qsKY65ApAKgiF5Ld$2c4121b89e89bf005e75f0c6110a3695735aaf0908a6f03e3c7bcc31269247c586b84dd8529b96966129434566fd332dc22e93ff1a6344a3ba8e995483dd113c','刘师傅',1,'13800000005','tech2@jzx.com',NULL,NULL,4,'维修车间','维修技师','正式','EMP005','中级','维修技师','2024-01-01',0.00,0.00,1,NULL,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(7,'tech3','scrypt:32768:8:1$b1jFYCJLdwJLBIse$b9ffe6934d42cc78a6238dbf3fa00578cbf3c0c845f16f439f45959f109befcebc84e90706a8dc181148a33a12a3c191706f4e93cceade03981d5fcff80e2e6c','黄师傅',1,'13800000006','tech3@jzx.com',NULL,NULL,4,'维修车间','维修技师','合同','EMP006','初级','维修技师','2024-01-01',0.00,0.00,1,NULL,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(8,'parts_mgr','scrypt:32768:8:1$MAb4Hch80ywqr8yI$845007ed6f27ae7c5093b7bffa7142aa882566f4b72f1269b2e91c3b813a25f49331dd26c7ac8fc704b6fcd9bc43d4dd7dc4460b3000f888d8d3ed4280f9c6dd','赵仓管',1,'13800000007','parts@jzx.com',NULL,NULL,5,'配件部','配件主管','正式','EMP007','高级','配件主管','2024-01-01',0.00,0.00,1,NULL,'2026-05-10 07:18:14','2026-05-10 07:18:14'),(9,'finance1','scrypt:32768:8:1$EFMDvm3d7i632Iur$28dab68e582d4c1627e55b50f5c0ad5326c9b1fec2eb8a14b56d7ed2d8bf95440a4d6884d9faa45a880eeac28b0eaf324730bb9a3e43b3dc6a89bd18d69fbf58','孙会计',1,'13800000008','finance@jzx.com',NULL,NULL,6,'财务部','财务专员','正式','EMP008','中级','会计','2024-01-01',0.00,0.00,1,NULL,'2026-05-10 07:18:14','2026-05-10 07:18:14');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vehicles`
--

DROP TABLE IF EXISTS `vehicles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehicles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vehicle_no` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '车辆编号',
  `customer_id` int NOT NULL COMMENT '客户ID',
  `plate_number` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '车牌号',
  `vin` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '车架号',
  `brand` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '品牌',
  `model` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '车型',
  `year` int DEFAULT NULL COMMENT '年款',
  `color` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '颜色',
  `engine_no` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '发动机号',
  `purchase_date` date DEFAULT NULL COMMENT '购车日期',
  `mileage` int DEFAULT '0' COMMENT '当前里程(km)',
  `insurance_date` date DEFAULT NULL COMMENT '保险到期日期',
  `inspection_date` date DEFAULT NULL COMMENT '年检到期日期',
  `photo` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '车辆照片',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `status` tinyint DEFAULT '1' COMMENT '状态：1正常 0删除',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `vehicle_no` (`vehicle_no`),
  KEY `idx_plate_number` (`plate_number`),
  KEY `idx_customer_id` (`customer_id`),
  CONSTRAINT `vehicles_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='车辆表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehicles`
--

LOCK TABLES `vehicles` WRITE;
/*!40000 ALTER TABLE `vehicles` DISABLE KEYS */;
INSERT INTO `vehicles` VALUES (1,'VCL-2024-001',1,'京A·88888','LFV2A21K9G3010001','大众','迈腾 380TSI',2023,'极地白','EA888G0123','2023-03-15',28000,'2025-03-14','2027-03-14',NULL,'定期保养客户',1,'2026-05-10 07:18:14','2026-05-10 07:18:14',1),(2,'VCL-2024-002',2,'京B·66666','LHGCM8869G200002','本田','雅阁 260TURBO',2022,'星曜黑','L15BN3002','2022-06-20',35000,'2025-06-19','2026-06-19',NULL,'',1,'2026-05-10 07:18:14','2026-05-10 07:18:14',1),(3,'VCL-2024-003',3,'京C·12345','LFV3A28C0G3030003','大众','帕萨特 330TSI',2021,'钛金灰','EA888G0456','2021-08-10',52000,'2025-08-09','2025-08-09',NULL,'公司用车',1,'2026-05-10 07:18:14','2026-05-10 07:18:14',1),(4,'VCL-2024-004',4,'京D·77777','LSGPC54U9GF100004','别克','君威 552T',2023,'墨玉黑','LFV00789','2023-11-01',12000,'2025-10-31','2027-10-31',NULL,'新车主',1,'2026-05-10 07:18:14','2026-05-10 07:18:14',1),(5,'VCL-2024-005',5,'京E·99999','WVWZZZ3CZWE005005','大众','途观L 380TSI',2020,'玄武灰','EA888G0789','2020-02-28',68000,'2025-02-27','2025-02-27',NULL,'出保车辆',1,'2026-05-10 07:18:14','2026-05-10 07:18:14',1),(6,'VCL-2024-006',6,'京F·33333','LHGGM6660G0600006','本田','CR-V 240TURBO',2022,'彩晶黑','L15BL006','2022-12-15',22000,'2025-12-14','2026-12-14',NULL,'',1,'2026-05-10 07:18:14','2026-05-10 07:18:14',1),(7,'VCL-2024-007',7,'京G·55555','LFV2A21K5K3070007','大众','速腾 280TSI',2024,'海贝金','EA211G011','2024-05-08',5000,'2026-05-07','2028-05-07',NULL,'新车首保',1,'2026-05-10 07:18:14','2026-05-10 07:18:14',1),(8,'VCL-2024-008',8,'京H·11111','WBAJB1105CJ800008','奔驰','C260L',2021,'曜岩黑','M2648008','2021-04-22',45000,'2025-04-21','2025-04-21',NULL,'高端客户',1,'2026-05-10 07:18:14','2026-05-10 07:18:14',1),(9,'VCL-2024-009',8,'京J·22222','LSVAU2180N2090009','大众','朗逸 1.5L',2023,'谦雅紫','EA211G022','2023-07-10',18000,'2025-07-09','2027-07-09',NULL,'',1,'2026-05-10 07:18:14','2026-05-10 07:18:14',1),(10,'VCL-2024-010',8,'京K·44444','LHGCM6660L0100010','本田','思域 240TURBO',2024,'闪烈黄','L15C8010','2024-09-05',3000,'2026-09-04','2028-09-04',NULL,'首保未做',1,'2026-05-10 07:18:14','2026-05-10 07:18:14',1);
/*!40000 ALTER TABLE `vehicles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `work_order_flow_logs`
--

DROP TABLE IF EXISTS `work_order_flow_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `work_order_flow_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL COMMENT '工单ID',
  `from_status` tinyint DEFAULT NULL COMMENT '原状态',
  `to_status` tinyint NOT NULL COMMENT '新状态',
  `operator_id` int DEFAULT NULL COMMENT '操作人ID',
  `operator_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '操作人姓名',
  `operator_no` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `operator_dept` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `operation` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '操作类型',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_order_id` (`order_id`),
  CONSTRAINT `work_order_flow_logs_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `work_orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工单状态流转记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `work_order_flow_logs`
--

LOCK TABLES `work_order_flow_logs` WRITE;
/*!40000 ALTER TABLE `work_order_flow_logs` DISABLE KEYS */;
INSERT INTO `work_order_flow_logs` VALUES (1,4,NULL,0,1,'系统管理员','','','create','创建工单','2026-05-10 07:36:40');
/*!40000 ALTER TABLE `work_order_flow_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `work_order_parts`
--

DROP TABLE IF EXISTS `work_order_parts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `work_order_parts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL COMMENT '工单ID',
  `part_id` int NOT NULL COMMENT '配件ID',
  `quantity` int NOT NULL COMMENT '数量',
  `unit_price` decimal(10,2) NOT NULL COMMENT '单价',
  `total_price` decimal(10,2) NOT NULL COMMENT '总价',
  `status` tinyint DEFAULT '0' COMMENT '状态：0待出库 1已出库',
  `outbound_at` datetime DEFAULT NULL COMMENT '出库时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `repair_category` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `charge_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `repair_item_id` int DEFAULT NULL,
  `remark` text COLLATE utf8mb4_unicode_ci,
  `outbound_status` tinyint DEFAULT '0',
  `discount_rate` decimal(4,2) DEFAULT '1.00',
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `part_id` (`part_id`),
  CONSTRAINT `work_order_parts_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `work_orders` (`id`),
  CONSTRAINT `work_order_parts_ibfk_2` FOREIGN KEY (`part_id`) REFERENCES `parts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工单配件关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `work_order_parts`
--

LOCK TABLES `work_order_parts` WRITE;
/*!40000 ALTER TABLE `work_order_parts` DISABLE KEYS */;
/*!40000 ALTER TABLE `work_order_parts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `work_order_technicians`
--

DROP TABLE IF EXISTS `work_order_technicians`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `work_order_technicians` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL COMMENT '工单ID',
  `repair_item_id` int DEFAULT NULL COMMENT '维修项目ID',
  `technician_id` int NOT NULL COMMENT '技师ID',
  `technician_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '技师姓名',
  `assign_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'primary' COMMENT '分配类型：primary主修 auxiliary辅修',
  `labor_hours` decimal(6,2) DEFAULT '0.00' COMMENT '分配工时',
  `labor_amount` decimal(10,2) DEFAULT '0.00' COMMENT '工时金额',
  `assigned_by` int DEFAULT NULL COMMENT '分配人ID',
  `assigned_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '分配时间',
  `status` tinyint DEFAULT '0' COMMENT '状态：0待处理 1进行中 2已完成',
  `completed_at` datetime DEFAULT NULL COMMENT '完成时间',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_technician_id` (`technician_id`),
  CONSTRAINT `work_order_technicians_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `work_orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='维修技师分配表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `work_order_technicians`
--

LOCK TABLES `work_order_technicians` WRITE;
/*!40000 ALTER TABLE `work_order_technicians` DISABLE KEYS */;
/*!40000 ALTER TABLE `work_order_technicians` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `work_orders`
--

DROP TABLE IF EXISTS `work_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `work_orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_no` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '工单编号',
  `customer_id` int NOT NULL COMMENT '客户ID',
  `vehicle_id` int NOT NULL COMMENT '车辆ID',
  `mileage` int DEFAULT NULL COMMENT '进厂里程(km)',
  `status` tinyint DEFAULT '0' COMMENT '状态：0新建 1确认 2派工 3维修中 4检验 5完工 6结算 7已完成',
  `service_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '服务类型',
  `fault_description` text COLLATE utf8mb4_unicode_ci COMMENT '故障描述',
  `repair_suggestion` text COLLATE utf8mb4_unicode_ci COMMENT '维修建议',
  `estimated_cost` decimal(10,2) DEFAULT '0.00' COMMENT '预估费用',
  `actual_cost` decimal(10,2) DEFAULT '0.00' COMMENT '实际费用',
  `parts_cost` decimal(10,2) DEFAULT '0.00' COMMENT '配件费用',
  `labor_cost` decimal(10,2) DEFAULT '0.00' COMMENT '工时费用',
  `other_cost` decimal(10,2) DEFAULT '0.00' COMMENT '其他费用',
  `discount_rate` decimal(4,2) DEFAULT '1.00' COMMENT '折扣率',
  `discount_amount` decimal(10,2) DEFAULT '0.00' COMMENT '优惠金额',
  `total_amount` decimal(10,2) DEFAULT '0.00' COMMENT '总金额',
  `received_amount` decimal(10,2) DEFAULT '0.00' COMMENT '已收金额',
  `is_paid` tinyint DEFAULT '0' COMMENT '是否已付款',
  `repair_confirmed` tinyint DEFAULT '0' COMMENT '维修确认完成',
  `parts_outbound_confirmed` tinyint DEFAULT '0' COMMENT '备件出库确认完成',
  `created_by` int DEFAULT NULL COMMENT '创建人ID',
  `confirmed_by` int DEFAULT NULL COMMENT '确认人ID',
  `confirmed_at` datetime DEFAULT NULL COMMENT '确认时间',
  `assigned_by` int DEFAULT NULL COMMENT '派工人ID',
  `assigned_at` datetime DEFAULT NULL COMMENT '派工时间',
  `inspected_by` int DEFAULT NULL COMMENT '检验人ID',
  `inspected_at` datetime DEFAULT NULL COMMENT '检验时间',
  `completed_by` int DEFAULT NULL COMMENT '完工人ID',
  `completed_at` datetime DEFAULT NULL COMMENT '完工时间',
  `settled_by` int DEFAULT NULL COMMENT '结算人ID',
  `settled_at` datetime DEFAULT NULL COMMENT '结算时间',
  `delivery_at` datetime DEFAULT NULL COMMENT '交车时间',
  `remark` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `insurance_company` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `claim_manufacturer` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_no` (`order_no`),
  KEY `customer_id` (`customer_id`),
  KEY `vehicle_id` (`vehicle_id`),
  KEY `idx_order_no` (`order_no`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `work_orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `work_orders_ibfk_2` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='维修工单表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `work_orders`
--

LOCK TABLES `work_orders` WRITE;
/*!40000 ALTER TABLE `work_orders` DISABLE KEYS */;
INSERT INTO `work_orders` VALUES (4,'G202605100001',1,1,15000,0,'常规保养','定期保养','',0.00,0.00,0.00,0.00,0.00,1.00,0.00,0.00,0.00,0,0,0,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2026-05-10 07:36:40','2026-05-10 07:36:40',NULL,NULL);
/*!40000 ALTER TABLE `work_orders` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-10  7:36:47
