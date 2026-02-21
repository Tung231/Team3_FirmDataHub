-- 1. Xóa sạch Database để xóa bỏ hoàn toàn các ràng buộc cũ bị lỗi
DROP DATABASE IF EXISTS vn_firm_panel;
CREATE DATABASE vn_firm_panel;
USE vn_firm_panel;

-- 2. Tạo bảng Snapshot (Bảng Cha) - Dùng kiểu BIGINT cho đồng bộ
CREATE TABLE `fact_data_snapshot` (
  `snapshot_id` bigint NOT NULL AUTO_INCREMENT,
  `snapshot_date` date NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `source_name` varchar(100) DEFAULT 'Vietstock',
  `version_tag` varchar(50) DEFAULT 'v1.0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Tạo bảng Danh mục Công ty
CREATE TABLE `dim_firm` (
  `firm_id` bigint NOT NULL AUTO_INCREMENT,
  `ticker` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `company_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `exchange_id` tinyint NOT NULL,
  `industry_l2_id` smallint DEFAULT NULL,
  PRIMARY KEY (`firm_id`),
  UNIQUE KEY `ticker` (`ticker`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Tạo bảng Cashflow (Bảng Con) - Giờ snapshot_id đã là BIGINT nên sẽ THÀNH CÔNG
CREATE TABLE `fact_cashflow_year` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `net_cfo` decimal(20,2) DEFAULT NULL,
  `capex` decimal(20,2) DEFAULT NULL,
  `net_cfi` decimal(20,2) DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_cf_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_cf_snapshot` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------

USE vn_firm_panel;

-- 1. Bảng Tài chính năm (Chứa Doanh thu, Lợi nhuận, Tài sản, Nợ...)
CREATE TABLE IF NOT EXISTS `fact_financial_year` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `net_sales` decimal(20,2) DEFAULT NULL,
  `total_assets` decimal(20,2) DEFAULT NULL,
  `total_liabilities` decimal(20,2) DEFAULT NULL,
  `net_income` decimal(20,2) DEFAULT NULL,
  `total_equity` decimal(20,2) DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_fin_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_fin_snap` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Bảng Thị trường (Chứa EPS và giá trị thị trường)
CREATE TABLE IF NOT EXISTS `fact_market_year` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `shares_outstanding` bigint DEFAULT NULL,
  `market_value_equity` decimal(20,2) DEFAULT NULL,
  `dividend_cash_paid` decimal(20,2) DEFAULT NULL, -- Cột vừa thiếu đây
  `eps_basic` decimal(20,6) DEFAULT NULL,
  `share_price` decimal(20,4) DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_mkt_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_mkt_snap` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------
USE vn_firm_panel;

-- Thêm từng cột một cách chắc chắn
ALTER TABLE fact_financial_year 
ADD COLUMN current_liabilities decimal(20,2) DEFAULT NULL,
ADD COLUMN growth_ratio decimal(10,6) DEFAULT NULL;

-- -------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------
USE vn_firm_panel;

-- Thêm từng cột một cách thủ công
ALTER TABLE fact_market_year ADD COLUMN shares_outstanding bigint DEFAULT NULL;
ALTER TABLE fact_market_year ADD COLUMN share_price decimal(20,4) DEFAULT NULL;
ALTER TABLE fact_market_year ADD COLUMN market_value_equity decimal(20,2) DEFAULT NULL;
ALTER TABLE fact_market_year ADD COLUMN eps_basic decimal(20,6) DEFAULT NULL;

-- --------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------
USE vn_firm_panel;

-- 1. Bảng Sở hữu (Cần cho Rule 1: Ownership ratios)
CREATE TABLE IF NOT EXISTS `fact_ownership_year` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `managerial_inside_own` decimal(10,6) DEFAULT NULL,
  `state_own` decimal(10,6) DEFAULT NULL,
  `institutional_own` decimal(10,6) DEFAULT NULL,
  `foreign_own` decimal(10,6) DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_own_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_own_snap` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Bảng Meta (Cần cho Rule về Nhân sự & Tuổi)
CREATE TABLE IF NOT EXISTS `fact_firm_year_meta` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `employees_count` int DEFAULT NULL,
  `firm_age` smallint DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_meta_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Bảng Đổi mới (Innovation)
CREATE TABLE IF NOT EXISTS `fact_innovation_year` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `product_innovation` tinyint DEFAULT NULL,
  `process_innovation` tinyint DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_inn_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- --------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------
USE vn_firm_panel;

-- 1. Xóa bảng cũ để tạo lại bản đầy đủ (Lưu ý: sẽ mất 100 dòng vừa nạp, nhưng nạp lại chỉ mất 1 giây)
DROP TABLE IF EXISTS fact_financial_year;

-- 2. Tạo bảng bản Full 23 biến tài chính
CREATE TABLE `fact_financial_year` (
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `snapshot_id` bigint NOT NULL,
  `net_sales` decimal(20,2) DEFAULT NULL,
  `total_assets` decimal(20,2) DEFAULT NULL,
  `selling_expenses` decimal(20,2) DEFAULT NULL,
  `general_admin_expenses` decimal(20,2) DEFAULT NULL,
  `intangible_assets_net` decimal(20,2) DEFAULT NULL,
  `manufacturing_overhead` decimal(20,2) DEFAULT NULL,
  `net_operating_income` decimal(20,2) DEFAULT NULL,
  `raw_material_consumption` decimal(20,2) DEFAULT NULL,
  `merchandise_purchase_year` decimal(20,2) DEFAULT NULL,
  `wip_goods_purchase` decimal(20,2) DEFAULT NULL,
  `outside_manufacturing_expenses` decimal(20,2) DEFAULT NULL,
  `production_cost` decimal(20,2) DEFAULT NULL,
  `rnd_expenses` decimal(20,2) DEFAULT NULL,
  `net_income` decimal(20,2) DEFAULT NULL,
  `total_equity` decimal(20,2) DEFAULT NULL,
  `total_liabilities` decimal(20,2) DEFAULT NULL,
  `cash_and_equivalents` decimal(20,2) DEFAULT NULL,
  `long_term_debt` decimal(20,2) DEFAULT NULL,
  `current_assets` decimal(20,2) DEFAULT NULL,
  `current_liabilities` decimal(20,2) DEFAULT NULL,
  `growth_ratio` decimal(10,6) DEFAULT NULL,
  `inventory` decimal(20,2) DEFAULT NULL,
  `net_ppe` decimal(20,2) DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_fin_firm_full` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_fin_snap_full` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------
USE vn_firm_panel;

-- 1. Bổ sung cho bảng Market
ALTER TABLE fact_market_year ADD COLUMN dividend_cash_paid decimal(20,2) DEFAULT NULL;
ALTER TABLE fact_market_year ADD COLUMN share_price decimal(20,4) DEFAULT NULL;

-- 2. Bổ sung cho bảng Cashflow (Để không lỗi net_cfi)
ALTER TABLE fact_cashflow_year ADD COLUMN net_cfi decimal(20,2) DEFAULT NULL;

-- 3. Bổ sung cho bảng Meta (Để không lỗi employees_count)
ALTER TABLE fact_firm_year_meta ADD COLUMN employees_count int DEFAULT NULL;
ALTER TABLE fact_firm_year_meta ADD COLUMN firm_age smallint DEFAULT NULL;

SELECT COUNT(*) FROM vn_firm_panel.dim_firm;
SELECT COUNT(*) FROM vn_firm_panel.fact_data_snapshot;
SELECT COUNT(*) FROM vn_firm_panel.fact_financial_year;

-- --------------------------------------------------------------------------------
-- -------------------------------------------------------------------------------
USE vn_firm_panel;

SELECT 
    (SELECT COUNT(*) FROM fact_financial_year) AS count_financial,
    (SELECT COUNT(*) FROM fact_market_year) AS count_market,
    (SELECT COUNT(*) FROM fact_ownership_year) AS count_ownership,
    (SELECT COUNT(*) FROM fact_cashflow_year) AS count_cashflow;