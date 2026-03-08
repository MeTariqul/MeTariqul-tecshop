-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: techshop_db
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `admin_dashboard_activitylog`
--

DROP TABLE IF EXISTS `admin_dashboard_activitylog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_dashboard_activitylog` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `action` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `object_id` int unsigned DEFAULT NULL,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `changes` json NOT NULL,
  `ip_address` char(39) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `timestamp` datetime(6) NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_dashb_timesta_1223ee_idx` (`timestamp` DESC),
  KEY `admin_dashb_user_id_b4d50d_idx` (`user_id`,`timestamp` DESC),
  KEY `admin_dashb_model_n_20dff8_idx` (`model_name`,`timestamp` DESC),
  CONSTRAINT `admin_dashboard_activitylog_user_id_7d161df3_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `admin_dashboard_activitylog_chk_1` CHECK ((`object_id` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_dashboard_activitylog`
--

LOCK TABLES `admin_dashboard_activitylog` WRITE;
/*!40000 ALTER TABLE `admin_dashboard_activitylog` DISABLE KEYS */;
INSERT INTO `admin_dashboard_activitylog` VALUES (1,'update','WebOrder',1,'Order ORD-F45EF76E -  ','{}',NULL,'','Updated order status to: delivered','2026-02-14 21:19:18.504663',1),(2,'update','StaffProfile',1,'admin - Super Admin','{}',NULL,'','Updated permissions for admin','2026-02-14 21:33:18.031752',1),(3,'create','StaffProfile',2,'manager - Manager','{}',NULL,'','Created new staff member: manager with role manager','2026-02-15 14:50:38.287826',1),(4,'update','WebOrder',1,'Order ORD-F45EF76E -  ','{}',NULL,'','Updated order status to: cancelled','2026-02-16 10:06:17.485421',1),(5,'update','WebOrder',1,'Order ORD-F45EF76E -  ','{}',NULL,'','Updated order status to: confirmed','2026-02-16 10:06:25.733215',1),(6,'update','WebOrder',1,'Order ORD-F45EF76E -  ','{}',NULL,'','Updated order status to: confirmed','2026-02-16 10:16:11.467180',1),(7,'update','WebOrder',2,'Order ORD-05D1F36E - Tariful  Islam','{}',NULL,'','Updated order status to: confirmed','2026-02-16 11:21:56.822501',1),(8,'delete','WebCustomer',2,' ','{}',NULL,'','Deleted customer: tarif','2026-02-16 12:01:10.913639',1),(9,'update','Product',4,'Gaming Console 5 (GMG-C5-001)','{}',NULL,'','Updated product: Gaming Console 5','2026-02-16 20:15:39.704201',1),(10,'update','WebOrder',2,'Order ORD-05D1F36E - Tariful  Islam','{}',NULL,'','Updated order status to: cancelled','2026-02-19 10:17:08.027148',1),(11,'update','WebOrder',3,'Order ORD-A50987DE - Tariful  Islam','{}',NULL,'','Updated order status to: confirmed','2026-02-19 11:42:02.612456',1),(12,'update','WebOrder',4,'Order ORD-D7F9A42C - Tariful  Islam','{}',NULL,'','Updated order status to: delivered','2026-02-20 09:31:31.672307',1),(13,'update','WebOrder',3,'Order ORD-A50987DE - Tariful  Islam','{}',NULL,'','Updated order status to: delivered','2026-02-20 09:31:58.052930',1),(14,'update','SiteConfiguration',1,'TechShop','{}',NULL,'','Updated site configuration','2026-02-20 10:17:05.316343',1),(15,'update','SiteConfiguration',1,'TechShop','{}',NULL,'','Updated site configuration','2026-02-20 10:17:20.210798',1),(16,'update','SiteConfiguration',1,'TechShop','{}',NULL,'','Updated site configuration','2026-02-20 10:17:26.312010',1);
/*!40000 ALTER TABLE `admin_dashboard_activitylog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_dashboard_inventorymovement`
--

DROP TABLE IF EXISTS `admin_dashboard_inventorymovement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_dashboard_inventorymovement` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `movement_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantity` int NOT NULL,
  `reference_number` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `performed_by_id` int DEFAULT NULL,
  `product_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_dashboard_inve_performed_by_id_8de886fb_fk_auth_user` (`performed_by_id`),
  KEY `admin_dashboard_inve_product_id_29e8958e_fk_products_` (`product_id`),
  CONSTRAINT `admin_dashboard_inve_performed_by_id_8de886fb_fk_auth_user` FOREIGN KEY (`performed_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `admin_dashboard_inve_product_id_29e8958e_fk_products_` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_dashboard_inventorymovement`
--

LOCK TABLES `admin_dashboard_inventorymovement` WRITE;
/*!40000 ALTER TABLE `admin_dashboard_inventorymovement` DISABLE KEYS */;
INSERT INTO `admin_dashboard_inventorymovement` VALUES (1,'sold',-1,'Order #5','','2026-02-20 10:22:02.284273',1,3);
/*!40000 ALTER TABLE `admin_dashboard_inventorymovement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_dashboard_purchaseorder`
--

DROP TABLE IF EXISTS `admin_dashboard_purchaseorder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_dashboard_purchaseorder` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `po_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order_date` date DEFAULT NULL,
  `expected_delivery` date DEFAULT NULL,
  `received_date` date DEFAULT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_amount` decimal(12,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int DEFAULT NULL,
  `supplier_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `po_number` (`po_number`),
  KEY `admin_dashboard_purc_created_by_id_cad219e2_fk_auth_user` (`created_by_id`),
  KEY `admin_dashboard_purc_supplier_id_33d53844_fk_admin_das` (`supplier_id`),
  CONSTRAINT `admin_dashboard_purc_created_by_id_cad219e2_fk_auth_user` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `admin_dashboard_purc_supplier_id_33d53844_fk_admin_das` FOREIGN KEY (`supplier_id`) REFERENCES `admin_dashboard_supplier` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_dashboard_purchaseorder`
--

LOCK TABLES `admin_dashboard_purchaseorder` WRITE;
/*!40000 ALTER TABLE `admin_dashboard_purchaseorder` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_dashboard_purchaseorder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_dashboard_purchaseorderitem`
--

DROP TABLE IF EXISTS `admin_dashboard_purchaseorderitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_dashboard_purchaseorderitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantity_ordered` int NOT NULL,
  `quantity_received` int NOT NULL,
  `unit_cost` decimal(10,2) NOT NULL,
  `product_id` bigint NOT NULL,
  `purchase_order_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_dashboard_purc_product_id_aaf7012a_fk_products_` (`product_id`),
  KEY `admin_dashboard_purc_purchase_order_id_10bdb228_fk_admin_das` (`purchase_order_id`),
  CONSTRAINT `admin_dashboard_purc_product_id_aaf7012a_fk_products_` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `admin_dashboard_purc_purchase_order_id_10bdb228_fk_admin_das` FOREIGN KEY (`purchase_order_id`) REFERENCES `admin_dashboard_purchaseorder` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_dashboard_purchaseorderitem`
--

LOCK TABLES `admin_dashboard_purchaseorderitem` WRITE;
/*!40000 ALTER TABLE `admin_dashboard_purchaseorderitem` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_dashboard_purchaseorderitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_dashboard_siteconfiguration`
--

DROP TABLE IF EXISTS `admin_dashboard_siteconfiguration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_dashboard_siteconfiguration` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `site_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `site_logo` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `favicon` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contact_email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_address` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `facebook_url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `twitter_url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `instagram_url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `youtube_url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `meta_title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `meta_description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `meta_keywords` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `maintenance_mode` tinyint(1) NOT NULL,
  `maintenance_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `tax_rate` decimal(5,2) NOT NULL,
  `free_shipping_threshold` decimal(10,2) NOT NULL,
  `default_shipping_cost` decimal(10,2) NOT NULL,
  `low_stock_threshold` int NOT NULL,
  `enable_backorders` tinyint(1) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `tax_enabled` tinyint(1) NOT NULL,
  `currency_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `currency_short_form` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `auto_cancel_hours` int NOT NULL,
  `auto_cancel_unpaid_orders` tinyint(1) NOT NULL,
  `default_order_status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email_notifications_enabled` tinyint(1) NOT NULL,
  `enable_database_backup` tinyint(1) NOT NULL,
  `notification_email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notify_low_stock` tinyint(1) NOT NULL,
  `notify_new_order` tinyint(1) NOT NULL,
  `notify_new_review` tinyint(1) NOT NULL,
  `notify_order_status_change` tinyint(1) NOT NULL,
  `require_approval_for_reviews` tinyint(1) NOT NULL,
  `reviews_enabled` tinyint(1) NOT NULL,
  `show_database_status` tinyint(1) NOT NULL,
  `show_system_health` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_dashboard_siteconfiguration`
--

LOCK TABLES `admin_dashboard_siteconfiguration` WRITE;
/*!40000 ALTER TABLE `admin_dashboard_siteconfiguration` DISABLE KEYS */;
INSERT INTO `admin_dashboard_siteconfiguration` VALUES (1,'TechShop','','','info@techshop.com','(555) 123-4567','123 Tech Street, Dhaka, Bangladesh','','','','','','','',0,'',8.00,50.00,5.99,10,0,'2026-02-20 10:17:26.309240',0,'Bangladeshi Taka','BDT',48,0,'confirmed',1,1,'admin@techshop.com',1,1,1,1,1,1,1,1);
/*!40000 ALTER TABLE `admin_dashboard_siteconfiguration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_dashboard_staffprofile`
--

DROP TABLE IF EXISTS `admin_dashboard_staffprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_dashboard_staffprofile` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `department` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `employee_id` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `hire_date` date DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `can_manage_products` tinyint(1) NOT NULL,
  `can_manage_orders` tinyint(1) NOT NULL,
  `can_manage_inventory` tinyint(1) NOT NULL,
  `can_manage_customers` tinyint(1) NOT NULL,
  `can_manage_staff` tinyint(1) NOT NULL,
  `can_view_reports` tinyint(1) NOT NULL,
  `can_manage_settings` tinyint(1) NOT NULL,
  `user_id` int NOT NULL,
  `can_manage_delivery` tinyint(1) NOT NULL,
  `can_manage_finance` tinyint(1) NOT NULL,
  `can_manage_sellers` tinyint(1) NOT NULL,
  `can_view_all_orders` tinyint(1) NOT NULL,
  `can_view_own_orders` tinyint(1) NOT NULL,
  `is_switched` tinyint(1) NOT NULL,
  `original_role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `employee_id` (`employee_id`),
  CONSTRAINT `admin_dashboard_staffprofile_user_id_c8bcb458_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_dashboard_staffprofile`
--

LOCK TABLES `admin_dashboard_staffprofile` WRITE;
/*!40000 ALTER TABLE `admin_dashboard_staffprofile` DISABLE KEYS */;
INSERT INTO `admin_dashboard_staffprofile` VALUES (1,'super_admin','Administration','EMP-91668F','','',NULL,1,'2026-02-14 18:24:39.112204','2026-02-17 17:06:26.120533',1,1,1,1,1,1,1,1,1,1,1,1,1,0,''),(2,'manager','','EMP-B14590','','',NULL,1,'2026-02-15 14:50:38.284996','2026-02-16 12:02:28.091600',1,1,1,1,0,1,1,4,0,0,0,0,1,1,'manager'),(3,'super_admin','','EMP-784FCF','','',NULL,1,'2026-02-16 09:44:28.080272','2026-02-16 09:44:28.080295',0,0,0,0,0,0,0,5,0,0,0,0,1,0,'');
/*!40000 ALTER TABLE `admin_dashboard_staffprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_dashboard_supplier`
--

DROP TABLE IF EXISTS `admin_dashboard_supplier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_dashboard_supplier` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_person` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_dashboard_supplier`
--

LOCK TABLES `admin_dashboard_supplier` WRITE;
/*!40000 ALTER TABLE `admin_dashboard_supplier` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_dashboard_supplier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_dashboard_systemsettings`
--

DROP TABLE IF EXISTS `admin_dashboard_systemsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_dashboard_systemsettings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `category` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_public` tinyint(1) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`),
  KEY `admin_dashboard_syst_updated_by_id_e329c90c_fk_auth_user` (`updated_by_id`),
  CONSTRAINT `admin_dashboard_syst_updated_by_id_e329c90c_fk_auth_user` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_dashboard_systemsettings`
--

LOCK TABLES `admin_dashboard_systemsettings` WRITE;
/*!40000 ALTER TABLE `admin_dashboard_systemsettings` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_dashboard_systemsettings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_dashboard_userpermission`
--

DROP TABLE IF EXISTS `admin_dashboard_userpermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_dashboard_userpermission` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `permission` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `granted_at` datetime(6) NOT NULL,
  `can_grant` tinyint(1) NOT NULL,
  `granted_by_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_dashboard_userpermission_user_id_permission_9fb5f49a_uniq` (`user_id`,`permission`),
  KEY `admin_dashboard_user_granted_by_id_84314ed1_fk_auth_user` (`granted_by_id`),
  CONSTRAINT `admin_dashboard_user_granted_by_id_84314ed1_fk_auth_user` FOREIGN KEY (`granted_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `admin_dashboard_userpermission_user_id_371751a5_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_dashboard_userpermission`
--

LOCK TABLES `admin_dashboard_userpermission` WRITE;
/*!40000 ALTER TABLE `admin_dashboard_userpermission` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_dashboard_userpermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=137 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add category',7,'add_category'),(26,'Can change category',7,'change_category'),(27,'Can delete category',7,'delete_category'),(28,'Can view category',7,'view_category'),(29,'Can add supplier',8,'add_supplier'),(30,'Can change supplier',8,'change_supplier'),(31,'Can delete supplier',8,'delete_supplier'),(32,'Can view supplier',8,'view_supplier'),(33,'Can add product',9,'add_product'),(34,'Can change product',9,'change_product'),(35,'Can delete product',9,'delete_product'),(36,'Can view product',9,'view_product'),(37,'Can add inventory',10,'add_inventory'),(38,'Can change inventory',10,'change_inventory'),(39,'Can delete inventory',10,'delete_inventory'),(40,'Can view inventory',10,'view_inventory'),(41,'Can add product image',11,'add_productimage'),(42,'Can change product image',11,'change_productimage'),(43,'Can delete product image',11,'delete_productimage'),(44,'Can view product image',11,'view_productimage'),(45,'Can add review',12,'add_review'),(46,'Can change review',12,'change_review'),(47,'Can delete review',12,'delete_review'),(48,'Can view review',12,'view_review'),(49,'Can add shopping cart',13,'add_shoppingcart'),(50,'Can change shopping cart',13,'change_shoppingcart'),(51,'Can delete shopping cart',13,'delete_shoppingcart'),(52,'Can view shopping cart',13,'view_shoppingcart'),(53,'Can add cart item',14,'add_cartitem'),(54,'Can change cart item',14,'change_cartitem'),(55,'Can delete cart item',14,'delete_cartitem'),(56,'Can view cart item',14,'view_cartitem'),(57,'Can add web customer',15,'add_webcustomer'),(58,'Can change web customer',15,'change_webcustomer'),(59,'Can delete web customer',15,'delete_webcustomer'),(60,'Can view web customer',15,'view_webcustomer'),(61,'Can add web order',16,'add_weborder'),(62,'Can change web order',16,'change_weborder'),(63,'Can delete web order',16,'delete_weborder'),(64,'Can view web order',16,'view_weborder'),(65,'Can add payment transaction',17,'add_paymenttransaction'),(66,'Can change payment transaction',17,'change_paymenttransaction'),(67,'Can delete payment transaction',17,'delete_paymenttransaction'),(68,'Can view payment transaction',17,'view_paymenttransaction'),(69,'Can add order item',18,'add_orderitem'),(70,'Can change order item',18,'change_orderitem'),(71,'Can delete order item',18,'delete_orderitem'),(72,'Can view order item',18,'view_orderitem'),(73,'Can add wishlist item',19,'add_wishlistitem'),(74,'Can change wishlist item',19,'change_wishlistitem'),(75,'Can delete wishlist item',19,'delete_wishlistitem'),(76,'Can view wishlist item',19,'view_wishlistitem'),(77,'Can add attribute value',20,'add_attributevalue'),(78,'Can change attribute value',20,'change_attributevalue'),(79,'Can delete attribute value',20,'delete_attributevalue'),(80,'Can view attribute value',20,'view_attributevalue'),(81,'Can add brand',21,'add_brand'),(82,'Can change brand',21,'change_brand'),(83,'Can delete brand',21,'delete_brand'),(84,'Can view brand',21,'view_brand'),(85,'Can add product attribute',22,'add_productattribute'),(86,'Can change product attribute',22,'change_productattribute'),(87,'Can delete product attribute',22,'delete_productattribute'),(88,'Can view product attribute',22,'view_productattribute'),(89,'Can add product variation',23,'add_productvariation'),(90,'Can change product variation',23,'change_productvariation'),(91,'Can delete product variation',23,'delete_productvariation'),(92,'Can view product variation',23,'view_productvariation'),(93,'Can add address',24,'add_address'),(94,'Can change address',24,'change_address'),(95,'Can delete address',24,'delete_address'),(96,'Can view address',24,'view_address'),(97,'Can add Site Configuration',26,'add_siteconfiguration'),(98,'Can change Site Configuration',26,'change_siteconfiguration'),(99,'Can delete Site Configuration',26,'delete_siteconfiguration'),(100,'Can view Site Configuration',26,'view_siteconfiguration'),(101,'Can add System Setting',28,'add_systemsettings'),(102,'Can change System Setting',28,'change_systemsettings'),(103,'Can delete System Setting',28,'delete_systemsettings'),(104,'Can view System Setting',28,'view_systemsettings'),(105,'Can add Staff Profile',27,'add_staffprofile'),(106,'Can change Staff Profile',27,'change_staffprofile'),(107,'Can delete Staff Profile',27,'delete_staffprofile'),(108,'Can view Staff Profile',27,'view_staffprofile'),(109,'Can add Activity Log',25,'add_activitylog'),(110,'Can change Activity Log',25,'change_activitylog'),(111,'Can delete Activity Log',25,'delete_activitylog'),(112,'Can view Activity Log',25,'view_activitylog'),(113,'Can add user permission',29,'add_userpermission'),(114,'Can change user permission',29,'change_userpermission'),(115,'Can delete user permission',29,'delete_userpermission'),(116,'Can view user permission',29,'view_userpermission'),(117,'Can add purchase order',31,'add_purchaseorder'),(118,'Can change purchase order',31,'change_purchaseorder'),(119,'Can delete purchase order',31,'delete_purchaseorder'),(120,'Can view purchase order',31,'view_purchaseorder'),(121,'Can add purchase order item',32,'add_purchaseorderitem'),(122,'Can change purchase order item',32,'change_purchaseorderitem'),(123,'Can delete purchase order item',32,'delete_purchaseorderitem'),(124,'Can view purchase order item',32,'view_purchaseorderitem'),(125,'Can add supplier',33,'add_supplier'),(126,'Can change supplier',33,'change_supplier'),(127,'Can delete supplier',33,'delete_supplier'),(128,'Can view supplier',33,'view_supplier'),(129,'Can add inventory movement',30,'add_inventorymovement'),(130,'Can change inventory movement',30,'change_inventorymovement'),(131,'Can delete inventory movement',30,'delete_inventorymovement'),(132,'Can view inventory movement',30,'view_inventorymovement'),(133,'Can add product variant',34,'add_productvariant'),(134,'Can change product variant',34,'change_productvariant'),(135,'Can delete product variant',34,'delete_productvariant'),(136,'Can view product variant',34,'view_productvariant');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1200000$WKbt0GiVQdBKODJBnfydBM$GE6x50bXn+OQaoVAkj8a/fKxdAtBEIgogNREFNUJag0=','2026-02-17 19:27:41.216611',1,'admin','Tariful ','Islam','admin@example.com',1,1,'2026-02-14 09:47:25.434597'),(4,'pbkdf2_sha256$1200000$Idnrxj4RBbtA96JeugAqoZ$9oDRfKN/TJFWaHDafHHrnSNgKkdvpA7SIjVpQT39oAU=',NULL,0,'manager','Tariful','Islam','tarifulislam2544@gmail.com',0,1,'2026-02-15 14:50:37.260369'),(5,'pbkdf2_sha256$1200000$rbiEzwN99hisA1arcaMKqB$VD2pcaV6lt1DraKALD19U/0A19a6ZCgnv1LXdE2BFMw=','2026-02-16 09:59:01.245678',1,'test_admin_debug','','','admin@example.com',1,1,'2026-02-16 09:44:27.304421');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_cartitem`
--

DROP TABLE IF EXISTS `cart_cartitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_cartitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantity` int unsigned NOT NULL,
  `added_at` datetime(6) NOT NULL,
  `product_id` bigint NOT NULL,
  `cart_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cart_cartitem_cart_id_product_id_53cce7c3_uniq` (`cart_id`,`product_id`),
  KEY `cart_cartitem_product_id_b24e265a_fk_products_id` (`product_id`),
  CONSTRAINT `cart_cartitem_cart_id_370ad265_fk_cart_shoppingcart_id` FOREIGN KEY (`cart_id`) REFERENCES `cart_shoppingcart` (`id`),
  CONSTRAINT `cart_cartitem_product_id_b24e265a_fk_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `cart_cartitem_chk_1` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_cartitem`
--

LOCK TABLES `cart_cartitem` WRITE;
/*!40000 ALTER TABLE `cart_cartitem` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart_cartitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_shoppingcart`
--

DROP TABLE IF EXISTS `cart_shoppingcart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_shoppingcart` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `customer_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cart_shoppingcart_customer_id_56fe164a_fk_orders_webcustomer_id` (`customer_id`),
  CONSTRAINT `cart_shoppingcart_customer_id_56fe164a_fk_orders_webcustomer_id` FOREIGN KEY (`customer_id`) REFERENCES `orders_webcustomer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_shoppingcart`
--

LOCK TABLES `cart_shoppingcart` WRITE;
/*!40000 ALTER TABLE `cart_shoppingcart` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart_shoppingcart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `categories_name_09afee77_uniq` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Laptops','','2026-02-14 09:47:26.139375','2026-02-14 09:47:26.139394'),(2,'Smartphones','','2026-02-14 09:47:26.142012','2026-02-14 09:47:26.142034'),(3,'Accessories','','2026-02-14 09:47:26.145013','2026-02-14 09:47:26.145028'),(4,'Audio','','2026-02-14 09:47:26.147541','2026-02-14 09:47:26.147566'),(5,'Gaming','','2026-02-14 09:47:26.150093','2026-02-14 09:47:26.150111');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(25,'admin_dashboard','activitylog'),(30,'admin_dashboard','inventorymovement'),(31,'admin_dashboard','purchaseorder'),(32,'admin_dashboard','purchaseorderitem'),(26,'admin_dashboard','siteconfiguration'),(27,'admin_dashboard','staffprofile'),(33,'admin_dashboard','supplier'),(28,'admin_dashboard','systemsettings'),(29,'admin_dashboard','userpermission'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(14,'cart','cartitem'),(13,'cart','shoppingcart'),(5,'contenttypes','contenttype'),(24,'orders','address'),(18,'orders','orderitem'),(17,'orders','paymenttransaction'),(15,'orders','webcustomer'),(16,'orders','weborder'),(6,'sessions','session'),(20,'store','attributevalue'),(21,'store','brand'),(7,'store','category'),(10,'store','inventory'),(9,'store','product'),(22,'store','productattribute'),(11,'store','productimage'),(34,'store','productvariant'),(23,'store','productvariation'),(12,'store','review'),(8,'store','supplier'),(19,'wishlist','wishlistitem');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-02-14 09:47:04.679922'),(2,'auth','0001_initial','2026-02-14 09:47:05.239087'),(3,'admin','0001_initial','2026-02-14 09:47:05.362261'),(4,'admin','0002_logentry_remove_auto_add','2026-02-14 09:47:05.369997'),(5,'admin','0003_logentry_add_action_flag_choices','2026-02-14 09:47:05.377314'),(6,'contenttypes','0002_remove_content_type_name','2026-02-14 09:47:05.486697'),(7,'auth','0002_alter_permission_name_max_length','2026-02-14 09:47:05.544159'),(8,'auth','0003_alter_user_email_max_length','2026-02-14 09:47:05.573698'),(9,'auth','0004_alter_user_username_opts','2026-02-14 09:47:05.581389'),(10,'auth','0005_alter_user_last_login_null','2026-02-14 09:47:05.643254'),(11,'auth','0006_require_contenttypes_0002','2026-02-14 09:47:05.646419'),(12,'auth','0007_alter_validators_add_error_messages','2026-02-14 09:47:05.653568'),(13,'auth','0008_alter_user_username_max_length','2026-02-14 09:47:05.717266'),(14,'auth','0009_alter_user_last_name_max_length','2026-02-14 09:47:05.777804'),(15,'auth','0010_alter_group_name_max_length','2026-02-14 09:47:05.797363'),(16,'auth','0011_update_proxy_permissions','2026-02-14 09:47:05.804541'),(17,'auth','0012_alter_user_first_name_max_length','2026-02-14 09:47:05.868852'),(18,'store','0001_initial','2026-02-14 09:47:06.125217'),(19,'orders','0001_initial','2026-02-14 09:47:06.535950'),(20,'cart','0001_initial','2026-02-14 09:47:06.735612'),(21,'sessions','0001_initial','2026-02-14 09:47:06.775659'),(22,'store','0002_productimage_review','2026-02-14 09:47:06.985940'),(23,'wishlist','0001_initial','2026-02-14 09:47:07.122286'),(24,'store','0003_attributevalue_brand_productattribute_category_image_and_more','2026-02-14 09:47:56.084400'),(25,'orders','0002_remove_webcustomer_address_remove_webcustomer_city_and_more','2026-02-14 09:51:05.071348'),(26,'orders','0003_remove_webcustomer_birthday_and_more','2026-02-14 11:00:07.779165'),(27,'store','0004_alter_attributevalue_unique_together_and_more','2026-02-14 11:00:08.395091'),(28,'admin_dashboard','0001_initial','2026-02-14 18:17:51.020621'),(29,'admin_dashboard','0002_staffprofile_can_manage_delivery_and_more','2026-02-14 19:20:27.850622'),(30,'orders','0004_webcustomer_profile_picture','2026-02-16 08:43:04.400819'),(31,'admin_dashboard','0003_siteconfiguration_tax_enabled','2026-02-16 09:00:52.891398'),(32,'store','0005_product_discount_label_product_discount_percentage_and_more','2026-02-16 09:00:53.066226'),(33,'admin_dashboard','0004_siteconfiguration_currency_name_and_more','2026-02-16 17:37:15.151198'),(34,'admin_dashboard','0005_siteconfiguration_auto_cancel_hours_and_more','2026-02-16 20:54:43.306601'),(35,'admin_dashboard','0006_supplier_inventorymovement_purchaseorder_and_more','2026-02-17 17:04:44.038416'),(36,'store','0006_productvariant_product_products_name_6f9890_idx_and_more','2026-02-17 19:38:03.107404'),(37,'admin_dashboard','0007_remove_siteconfiguration_currency_code_and_more','2026-02-17 20:17:40.926161'),(38,'store','0007_review','2026-02-19 11:16:16.756469'),(39,'store','0008_product_tax_exempt_product_tax_rate','2026-02-19 11:45:18.246469'),(40,'orders','0005_orderitem_tax_rate','2026-02-19 11:52:16.630390'),(41,'store','0009_review_admin_response_review_admin_response_at_and_more','2026-02-20 09:36:07.406971');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('1w0dvc80i9zyx780hf0f7x6ox54u7rg0','.eJxVjMsOgjAQAP9lz6ahr5Vy9M43kN1ua1FTEgon478bEg56nZnMGybatzLtLa3TLDCAhssvY4rPVA8hD6r3RcWlbuvM6kjUaZsaF0mv29n-DQq1AgP0dPUYnDaROUQ0aDsUZO116Mg5YZcMiSbsrWBgE6zPJrNmbzPanODzBcowN50:1vtNaD:lFXuvUwjzY_eAg2GWT6171aDSIVd81y97Cvl2FKRBJM','2026-03-06 10:18:01.444743'),('4lisjk3n02upcgrlyovb2j4htjlbapu6','.eJxVjDkKwzAQAP-ydRA6Vgcu0-cNZldaRU6CDD6qkL8Hg4uknRnmDSPtWxv3VZZxKjCAh8svY8pP6YcoD-r3WeW5b8vE6kjUaVd1m4u8rmf7N2i0NhgAdXXEGnMiSZhsJA4OszOpIOoStZcYHEv1pupA0WgUHzkYtrF46-HzBdYsNzQ:1vrv9z:56xkAYaaVGg9Uyge9rAWod7D0LuTYFTk2uNy_UUGbk0','2026-03-02 09:44:55.038345'),('8fm7yx056wsvjxfgvle6bz0az27r2w8i','.eJxVjDkKwzAQAP-ydRA6Vgcu0-cNZldaRU6CDD6qkL8Hg4uknRnmDSPtWxv3VZZxKjCAh8svY8pP6YcoD-r3WeW5b8vE6kjUaVd1m4u8rmf7N2i0NhgAdXXEGnMiSZhsJA4OszOpIOoStZcYHEv1pupA0WgUHzkYtrF46-HzBdYsNzQ:1vrv9Y:9jDBQlNrYD4NarW4cgtKq12LewDRtRCU8YBO6Av0x54','2026-03-02 09:44:28.769783'),('asoi9owss9bfzxli43sd3gw4ou4y82r4','.eJxVjDkKwzAQAP-ydRA6Vgcu0-cNZldaRU6CDD6qkL8Hg4uknRnmDSPtWxv3VZZxKjCAh8svY8pP6YcoD-r3WeW5b8vE6kjUaVd1m4u8rmf7N2i0NhgAdXXEGnMiSZhsJA4OszOpIOoStZcYHEv1pupA0WgUHzkYtrF46-HzBdYsNzQ:1vrvAT:57stvWqhuirVJ2cBC12jMuFygOmteaTtohWhorpCfu0','2026-03-02 09:45:25.898041'),('g9oj5npgd31yp5c3wg829nfylu9xa987','.eJxVjDkKwzAQAP-ydRA6Vgcu0-cNZldaRU6CDD6qkL8Hg4uknRnmDSPtWxv3VZZxKjCAh8svY8pP6YcoD-r3WeW5b8vE6kjUaVd1m4u8rmf7N2i0NhgAdXXEGnMiSZhsJA4OszOpIOoStZcYHEv1pupA0WgUHzkYtrF46-HzBdYsNzQ:1vrvNd:y_abELfV8UnjC64-K83f3eosgXJRTP9NWKyVHXEy6Es','2026-03-02 09:59:01.247872'),('ikt09o21xmuprs1iziix2l5h3gifui6l','.eJxVjDkKwzAQAP-ydRA6Vgcu0-cNZldaRU6CDD6qkL8Hg4uknRnmDSPtWxv3VZZxKjCAh8svY8pP6YcoD-r3WeW5b8vE6kjUaVd1m4u8rmf7N2i0NhgAdXXEGnMiSZhsJA4OszOpIOoStZcYHEv1pupA0WgUHzkYtrF46-HzBdYsNzQ:1vrvE7:6i2M9rfHETMe3irUb-X1w4EM_cZb0wckVysWeQORwJ0','2026-03-02 09:49:11.855134'),('n8l1mj450quw0o4exnn11cg06m2b4f6q','.eJxVjDkKwzAQAP-ydRA6Vgcu0-cNZldaRU6CDD6qkL8Hg4uknRnmDSPtWxv3VZZxKjCAh8svY8pP6YcoD-r3WeW5b8vE6kjUaVd1m4u8rmf7N2i0NhgAdXXEGnMiSZhsJA4OszOpIOoStZcYHEv1pupA0WgUHzkYtrF46-HzBdYsNzQ:1vrvBL:tFYrnjClPxyVDANAy2K5blbtMDRB5FU7FAR2YABGFpM','2026-03-02 09:46:19.881314'),('og2stdrieii0vnt3dyh2z5p22m3b1vwj','.eJxVjMsOgjAQAP9lz6ahr5Vy9M43kN1ua1FTEgon478bEg56nZnMGybatzLtLa3TLDCAhssvY4rPVA8hD6r3RcWlbuvM6kjUaZsaF0mv29n-DQq1AgP0dPUYnDaROUQ0aDsUZO116Mg5YZcMiSbsrWBgE6zPJrNmbzPanODzBcowN50:1vsOWo:XeupWiDHf5UqsqybETHxsDcm0Pd6ldmJjOaHcHsXZTA','2026-03-03 17:06:26.126424');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantity_on_hand` int NOT NULL,
  `reorder_level` int NOT NULL,
  `location` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_updated` datetime(6) NOT NULL,
  `product_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_id` (`product_id`),
  CONSTRAINT `inventory_product_id_7c50457a_fk_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory`
--

LOCK TABLES `inventory` WRITE;
/*!40000 ALTER TABLE `inventory` DISABLE KEYS */;
INSERT INTO `inventory` VALUES (1,0,5,'Warehouse A','2026-02-15 17:29:27.583153',1),(2,0,5,'Warehouse A','2026-02-20 09:28:00.833805',2),(3,10,5,'Warehouse A','2026-02-20 10:22:02.281211',3),(4,43,5,'Warehouse A','2026-02-19 11:24:38.063629',4);
/*!40000 ALTER TABLE `inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders_orderitem`
--

DROP TABLE IF EXISTS `orders_orderitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders_orderitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantity` int unsigned NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `product_id` bigint NOT NULL,
  `order_id` bigint NOT NULL,
  `tax_rate` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `orders_orderitem_product_id_afe4254a_fk_products_id` (`product_id`),
  KEY `orders_orderitem_order_id_fe61a34d_fk_orders_weborder_id` (`order_id`),
  CONSTRAINT `orders_orderitem_order_id_fe61a34d_fk_orders_weborder_id` FOREIGN KEY (`order_id`) REFERENCES `orders_weborder` (`id`),
  CONSTRAINT `orders_orderitem_product_id_afe4254a_fk_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `orders_orderitem_chk_1` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders_orderitem`
--

LOCK TABLES `orders_orderitem` WRITE;
/*!40000 ALTER TABLE `orders_orderitem` DISABLE KEYS */;
INSERT INTO `orders_orderitem` VALUES (2,37,1200.00,1,2,NULL),(3,5,474.05,4,3,NULL),(4,20,999.00,2,4,8.00),(5,1,299.00,3,5,8.00);
/*!40000 ALTER TABLE `orders_orderitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders_paymenttransaction`
--

DROP TABLE IF EXISTS `orders_paymenttransaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders_paymenttransaction` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `transaction_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `payment_method` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `processed_at` datetime(6) NOT NULL,
  `order_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transaction_id` (`transaction_id`),
  UNIQUE KEY `order_id` (`order_id`),
  CONSTRAINT `orders_paymenttransa_order_id_63cdfa20_fk_orders_we` FOREIGN KEY (`order_id`) REFERENCES `orders_weborder` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders_paymenttransaction`
--

LOCK TABLES `orders_paymenttransaction` WRITE;
/*!40000 ALTER TABLE `orders_paymenttransaction` DISABLE KEYS */;
INSERT INTO `orders_paymenttransaction` VALUES (2,'TXN-B54721719E72','Credit Card',47952.00,'completed','2026-02-15 17:29:27.585865',2),(3,'TXN-727A1034A987','Credit Card',2559.87,'completed','2026-02-19 11:24:38.065870',3),(4,'TXN-9EB6047534D0','Credit Card',21578.40,'completed','2026-02-20 09:28:00.836425',4),(5,'TXN-49694A994EE7','Credit Card',299.00,'completed','2026-02-20 10:18:01.440926',5);
/*!40000 ALTER TABLE `orders_paymenttransaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders_webcustomer`
--

DROP TABLE IF EXISTS `orders_webcustomer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders_webcustomer` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int NOT NULL,
  `address` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `city` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `state` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `zip_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `profile_picture` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `orders_webcustomer_user_id_313fca91_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders_webcustomer`
--

LOCK TABLES `orders_webcustomer` WRITE;
/*!40000 ALTER TABLE `orders_webcustomer` DISABLE KEYS */;
INSERT INTO `orders_webcustomer` VALUES (1,'','2026-02-14 18:24:51.136699','2026-02-16 09:02:04.201131',1,'','','','','profile_pics/IMG_3716-removebg-preview.png');
/*!40000 ALTER TABLE `orders_webcustomer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders_weborder`
--

DROP TABLE IF EXISTS `orders_weborder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders_weborder` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_number` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `tax_amount` decimal(10,2) NOT NULL,
  `shipping_cost` decimal(10,2) NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `shipping_address` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `shipping_city` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shipping_state` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shipping_zip` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `shipped_at` datetime(6) DEFAULT NULL,
  `delivered_at` datetime(6) DEFAULT NULL,
  `customer_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_number` (`order_number`),
  KEY `orders_weborder_customer_id_602c59b6_fk_orders_webcustomer_id` (`customer_id`),
  CONSTRAINT `orders_weborder_customer_id_602c59b6_fk_orders_webcustomer_id` FOREIGN KEY (`customer_id`) REFERENCES `orders_webcustomer` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders_weborder`
--

LOCK TABLES `orders_weborder` WRITE;
/*!40000 ALTER TABLE `orders_weborder` DISABLE KEYS */;
INSERT INTO `orders_weborder` VALUES (2,'ORD-05D1F36E','cancelled',44400.00,3552.00,0.00,47952.00,'Savar,Dhaka.','Dhaka','Bd','1349','2026-02-15 17:29:27.580145','2026-02-19 10:17:08.011859',NULL,NULL,1),(3,'ORD-A50987DE','delivered',2370.25,189.62,0.00,2559.87,'3456 DEANS LANE PLEASANTVILLE, NY 10570','PLEASANTVILLE','New York','10570','2026-02-19 11:24:38.060740','2026-02-20 09:31:58.035102',NULL,NULL,1),(4,'ORD-D7F9A42C','delivered',19980.00,1598.40,0.00,21578.40,'3456 DEANS LANE PLEASANTVILLE, NY 10570','PLEASANTVILLE','Bd','10570','2026-02-20 09:28:00.826905','2026-02-20 09:31:31.666876',NULL,NULL,1),(5,'ORD-33286588','shipped',299.00,0.00,0.00,299.00,'Savar,Dhaka.','Dhaka','Bd','1349','2026-02-20 10:18:01.435078','2026-02-20 10:22:02.273116','2026-02-20 10:22:02.273011',NULL,1);
/*!40000 ALTER TABLE `orders_weborder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_reviews`
--

DROP TABLE IF EXISTS `product_reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_reviews` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rating` int unsigned NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `comment` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_verified_purchase` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `product_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `admin_response` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `admin_response_at` datetime(6) DEFAULT NULL,
  `admin_response_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_reviews_product_id_user_id_d808f9a4_uniq` (`product_id`,`user_id`),
  KEY `product_reviews_user_id_4a2266e2_fk_orders_webcustomer_id` (`user_id`),
  KEY `product_reviews_admin_response_by_id_4fb410fd_fk_auth_user_id` (`admin_response_by_id`),
  CONSTRAINT `product_reviews_admin_response_by_id_4fb410fd_fk_auth_user_id` FOREIGN KEY (`admin_response_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `product_reviews_product_id_9059f243_fk_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `product_reviews_user_id_4a2266e2_fk_orders_webcustomer_id` FOREIGN KEY (`user_id`) REFERENCES `orders_webcustomer` (`id`),
  CONSTRAINT `product_reviews_chk_1` CHECK ((`rating` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_reviews`
--

LOCK TABLES `product_reviews` WRITE;
/*!40000 ALTER TABLE `product_reviews` DISABLE KEYS */;
INSERT INTO `product_reviews` VALUES (1,5,'Good','',1,'2026-02-20 10:31:04.162415','2026-02-20 10:31:04.162445',4,1,'',NULL,NULL);
/*!40000 ALTER TABLE `product_reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_variants`
--

DROP TABLE IF EXISTS `product_variants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_variants` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `size` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `color` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sku_suffix` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `price_adjustment` decimal(10,2) NOT NULL,
  `stock_quantity` int NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `product_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_variants_product_id_size_color_52f9365c_uniq` (`product_id`,`size`,`color`),
  CONSTRAINT `product_variants_product_id_019d9f04_fk_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_variants`
--

LOCK TABLES `product_variants` WRITE;
/*!40000 ALTER TABLE `product_variants` DISABLE KEYS */;
/*!40000 ALTER TABLE `product_variants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `SKU` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `cost_price` decimal(10,2) NOT NULL,
  `selling_price` decimal(10,2) NOT NULL,
  `is_available_online` tinyint(1) NOT NULL,
  `featured_image` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `category_id` bigint DEFAULT NULL,
  `supplier_id` bigint DEFAULT NULL,
  `discount_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `discount_percentage` decimal(5,2) NOT NULL,
  `tax_exempt` tinyint(1) NOT NULL,
  `tax_rate` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `SKU` (`SKU`),
  KEY `products_supplier_id_ae23c972_fk_suppliers_id` (`supplier_id`),
  KEY `products_name_6f9890_idx` (`name`),
  KEY `products_categor_ce828c_idx` (`category_id`,`is_available_online`),
  CONSTRAINT `products_category_id_a7a3a156_fk_categories_id` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `products_supplier_id_ae23c972_fk_suppliers_id` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'LAP-X1-001','Pro Laptop X1','High performance laptop for professionals.',800.00,1200.00,1,'','2026-02-14 09:47:26.158851','2026-02-14 09:47:26.158871',1,1,'',0.00,0,NULL),(2,'PHN-S24-001','Galaxy Phone S24','Latest flagship smartphone with AI features.',600.00,999.00,1,'','2026-02-14 09:47:26.164314','2026-02-14 09:47:26.164333',2,1,'',0.00,0,NULL),(3,'AUD-NC-001','Noise Cancelling Headphones','Premium wireless headphones with ANC.',150.00,299.00,1,'','2026-02-14 09:47:26.169156','2026-02-14 09:47:26.169173',4,1,'',0.00,0,NULL),(4,'GMG-C5-001','Gaming Console 5','Next-gen gaming console.',350.00,499.00,1,'','2026-02-14 09:47:26.173881','2026-02-16 20:15:39.695684',5,1,'',5.00,0,NULL);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `store_productimage`
--

DROP TABLE IF EXISTS `store_productimage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `store_productimage` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `image` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `alt_text` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_order` int unsigned NOT NULL,
  `product_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `store_productimage_product_id_e50e4046_fk_products_id` (`product_id`),
  CONSTRAINT `store_productimage_product_id_e50e4046_fk_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `store_productimage_chk_1` CHECK ((`sort_order` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `store_productimage`
--

LOCK TABLES `store_productimage` WRITE;
/*!40000 ALTER TABLE `store_productimage` DISABLE KEYS */;
/*!40000 ALTER TABLE `store_productimage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suppliers`
--

DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suppliers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_person` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suppliers`
--

LOCK TABLES `suppliers` WRITE;
/*!40000 ALTER TABLE `suppliers` DISABLE KEYS */;
INSERT INTO `suppliers` VALUES (1,'TechDistributor Inc.','','contact@techdist.com','555-0101','','2026-02-14 09:47:26.154528','2026-02-14 09:47:26.154558');
/*!40000 ALTER TABLE `suppliers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wishlist_wishlistitem`
--

DROP TABLE IF EXISTS `wishlist_wishlistitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `wishlist_wishlistitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `added_at` datetime(6) NOT NULL,
  `product_id` bigint NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wishlist_wishlistitem_user_id_product_id_fc088002_uniq` (`user_id`,`product_id`),
  KEY `wishlist_wishlistitem_product_id_8309716a_fk_products_id` (`product_id`),
  CONSTRAINT `wishlist_wishlistitem_product_id_8309716a_fk_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `wishlist_wishlistitem_user_id_e2483288_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wishlist_wishlistitem`
--

LOCK TABLES `wishlist_wishlistitem` WRITE;
/*!40000 ALTER TABLE `wishlist_wishlistitem` DISABLE KEYS */;
/*!40000 ALTER TABLE `wishlist_wishlistitem` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-20 17:56:27
