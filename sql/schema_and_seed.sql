-- 1. Đoạn giữ nguyên thiết lập môi trường của thầy
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

-- 2. Khởi tạo Database
DROP DATABASE IF EXISTS vn_firm_panel;
CREATE DATABASE vn_firm_panel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE vn_firm_panel;

-- ==========================================================
-- 3. CÁC BẢNG DANH MỤC (DIMENSION TABLES)
-- ==========================================================

CREATE TABLE `dim_data_source` (
  `source_id` smallint NOT NULL AUTO_INCREMENT,
  `source_name` varchar(100) NOT NULL,
  `source_type` enum('market','financial_statement','ownership','text_report','manual') NOT NULL,
  `provider` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`source_id`),
  UNIQUE KEY (`source_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `dim_exchange` (
  `exchange_id` tinyint NOT NULL AUTO_INCREMENT,
  `exchange_code` varchar(10) NOT NULL,
  `exchange_name` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`exchange_id`),
  UNIQUE KEY (`exchange_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `dim_industry_l2` (
  `industry_l2_id` smallint NOT NULL AUTO_INCREMENT,
  `industry_l2_name` varchar(150) NOT NULL,
  PRIMARY KEY (`industry_l2_id`),
  UNIQUE KEY (`industry_l2_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `dim_firm` (
  `firm_id` bigint NOT NULL AUTO_INCREMENT,
  `ticker` varchar(20) NOT NULL,
  `company_name` varchar(255) NOT NULL,
  `exchange_id` tinyint NOT NULL,
  `industry_l2_id` smallint DEFAULT NULL,
  PRIMARY KEY (`firm_id`),
  UNIQUE KEY `uq_ticker` (`ticker`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================================
-- 4. VERSIONING (SNAPSHOT)
-- ==========================================================

CREATE TABLE `fact_data_snapshot` (
  `snapshot_id` bigint NOT NULL AUTO_INCREMENT,
  `snapshot_date` date NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `source_id` smallint NOT NULL,
  `version_tag` varchar(50) DEFAULT 'v1.0',
  PRIMARY KEY (`snapshot_id`),
  CONSTRAINT `fk_snap_source` FOREIGN KEY (`source_id`) REFERENCES `dim_data_source` (`source_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================================
-- 5. CÁC BẢNG DỮ LIỆU CHÍNH (FACT TABLES)
-- ==========================================================

-- FACT: Tài chính (23 biến)
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
  CONSTRAINT `fk_fin_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`),
  CONSTRAINT `fk_fin_snap` FOREIGN KEY (`snapshot_id`) REFERENCES `fact_data_snapshot` (`snapshot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- FACT: Thị trường, Sở hữu, Dòng tiền, Meta, Innovation (Tương tự cấu trúc trên)
CREATE TABLE `fact_market_year` (
  `firm_id` bigint NOT NULL, `fiscal_year` smallint NOT NULL, `snapshot_id` bigint NOT NULL,
  `shares_outstanding` bigint DEFAULT NULL, `market_value_equity` decimal(20,2) DEFAULT NULL,
  `dividend_cash_paid` decimal(20,2) DEFAULT NULL, `eps_basic` decimal(20,6) DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_mkt_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `fact_ownership_year` (
  `firm_id` bigint NOT NULL, `fiscal_year` smallint NOT NULL, `snapshot_id` bigint NOT NULL,
  `managerial_inside_own` decimal(10,6) DEFAULT NULL, `state_own` decimal(10,6) DEFAULT NULL,
  `institutional_own` decimal(10,6) DEFAULT NULL, `foreign_own` decimal(10,6) DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_own_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `fact_cashflow_year` (
  `firm_id` bigint NOT NULL, `fiscal_year` smallint NOT NULL, `snapshot_id` bigint NOT NULL,
  `net_cfo` decimal(20,2) DEFAULT NULL, `capex` decimal(20,2) DEFAULT NULL, `net_cfi` decimal(20,2) DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_cf_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `fact_firm_year_meta` (
  `firm_id` bigint NOT NULL, `fiscal_year` smallint NOT NULL, `snapshot_id` bigint NOT NULL,
  `employees_count` int DEFAULT NULL, `firm_age` smallint DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_meta_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `fact_innovation_year` (
  `firm_id` bigint NOT NULL, `fiscal_year` smallint NOT NULL, `snapshot_id` bigint NOT NULL,
  `product_innovation` tinyint DEFAULT NULL, `process_innovation` tinyint DEFAULT NULL,
  PRIMARY KEY (`firm_id`,`fiscal_year`,`snapshot_id`),
  CONSTRAINT `fk_inn_firm` FOREIGN KEY (`firm_id`) REFERENCES `dim_firm` (`firm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AUDIT: Nhật ký thay đổi
CREATE TABLE `fact_value_override_log` (
  `override_id` bigint NOT NULL AUTO_INCREMENT,
  `firm_id` bigint NOT NULL,
  `fiscal_year` smallint NOT NULL,
  `table_name` varchar(80) NOT NULL,
  `column_name` varchar(80) NOT NULL,
  `old_value` varchar(255) DEFAULT NULL,
  `new_value` varchar(255) DEFAULT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `changed_by` varchar(80) DEFAULT NULL,
  `changed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`override_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================================
-- 6. VIEW: DATASET CUỐI CÙNG (38 BIẾN)
-- ==========================================================

CREATE OR REPLACE VIEW vw_firm_panel_latest AS
WITH LatestSnapshots AS (
    SELECT firm_id, fiscal_year, MAX(snapshot_id) as max_sid
    FROM fact_financial_year
    GROUP BY firm_id, fiscal_year
)
SELECT 
    f.ticker, fin.fiscal_year,
    fin.net_sales, fin.total_assets, fin.selling_expenses, fin.general_admin_expenses, 
    fin.intangible_assets_net, fin.manufacturing_overhead, fin.net_operating_income, 
    fin.raw_material_consumption, fin.merchandise_purchase_year, fin.wip_goods_purchase, 
    fin.outside_manufacturing_expenses, fin.production_cost, fin.rnd_expenses, 
    fin.net_income, fin.total_equity, fin.total_liabilities, fin.cash_and_equivalents, 
    fin.long_term_debt, fin.current_assets, fin.current_liabilities, fin.growth_ratio, 
    fin.inventory, fin.net_ppe,
    mkt.shares_outstanding, mkt.market_value_equity, mkt.dividend_cash_paid, mkt.eps_basic,
    own.managerial_inside_own, own.state_own, own.institutional_own, own.foreign_own,
    meta.employees_count, meta.firm_age,
    inn.product_innovation, inn.process_innovation,
    cf.net_cfo, cf.capex, cf.net_cfi
FROM LatestSnapshots ls
JOIN dim_firm f ON ls.firm_id = f.firm_id
JOIN fact_financial_year fin ON ls.firm_id = fin.firm_id AND ls.fiscal_year = fin.fiscal_year AND ls.max_sid = fin.snapshot_id
LEFT JOIN fact_market_year mkt ON fin.firm_id = mkt.firm_id AND fin.fiscal_year = mkt.fiscal_year AND fin.snapshot_id = mkt.snapshot_id
LEFT JOIN fact_ownership_year own ON fin.firm_id = own.firm_id AND fin.fiscal_year = own.fiscal_year AND fin.snapshot_id = own.snapshot_id
LEFT JOIN fact_firm_year_meta meta ON fin.firm_id = meta.firm_id AND fin.fiscal_year = meta.fiscal_year AND fin.snapshot_id = meta.snapshot_id
LEFT JOIN fact_innovation_year inn ON fin.firm_id = inn.firm_id AND fin.fiscal_year = inn.fiscal_year AND fin.snapshot_id = inn.snapshot_id
LEFT JOIN fact_cashflow_year cf ON fin.firm_id = cf.firm_id AND fin.fiscal_year = cf.fiscal_year AND fin.snapshot_id = cf.snapshot_id;

-- ==========================================================
-- 7. SEED DATA (20 FIRMS)
-- ==========================================================
INSERT INTO `dim_data_source` (source_id, source_name, source_type) VALUES (1, 'Vietstock', 'financial_statement');
INSERT INTO `dim_exchange` (exchange_id, exchange_code) VALUES (1, 'HOSE'), (2, 'HNX');
INSERT INTO `dim_firm` (ticker, company_name, exchange_id) VALUES 
('VGS','Ống thép Việt Đức',2), ('CLH','Xi măng La Hiên',2), ('LBM','Khoáng sản Lâm Đồng',1),
('QHD','Que hàn Việt Đức',2), ('MVB','Mỏ Việt Bắc',2), ('BCF','Thực phẩm Bích Chi',2),
('HAP','Hapaco',1), ('MCP','In Mỹ Châu',1), ('IDI','Đầu tư Đa Quốc Gia',1),
('LGC','Cầu đường CII',1), ('THG','Xây dựng Tiền Giang',1), ('CDC','Chương Dương',1),
('LHC','Thủy lợi Lâm Đồng',2), ('LCG','Lizen',1), ('TV2','Tư vấn điện 2',1),
('TCL','Tân Cảng Logistics',1), ('ILB','Tân Cảng Long Bình',1), ('STG','Kho vận Miền Nam',1),
('PVB','Bọc ống Dầu khí',2), ('VNT','Giao nhận Ngoại thương',2);

-- Bật lại các kiểm tra
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;