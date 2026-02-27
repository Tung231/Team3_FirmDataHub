USE vn_firm_panel;

-- 1. Thêm cột giá cổ phiếu vào bảng Market
ALTER TABLE fact_market_year ADD COLUMN share_price decimal(20,4) DEFAULT NULL;

-- 2. Cập nhật lại View để nhận diện cột mới (giúp bước Export không bị lỗi)
CREATE OR REPLACE VIEW vw_firm_panel_latest AS
WITH LatestSnapshots AS (
    SELECT firm_id, fiscal_year, MAX(snapshot_id) as max_sid
    FROM fact_financial_year
    GROUP BY firm_id, fiscal_year
)
SELECT 
    f.ticker, fin.fiscal_year,
    -- 38 biến tài chính, thị trường...
    fin.net_sales, fin.total_assets, fin.selling_expenses, fin.general_admin_expenses, 
    fin.intangible_assets_net, fin.manufacturing_overhead, fin.net_operating_income, 
    fin.raw_material_consumption, fin.merchandise_purchase_year, fin.wip_goods_purchase, 
    fin.outside_manufacturing_expenses, fin.production_cost, fin.rnd_expenses, 
    fin.net_income, fin.total_equity, fin.total_liabilities, fin.cash_and_equivalents, 
    fin.long_term_debt, fin.current_assets, fin.current_liabilities, fin.growth_ratio, 
    fin.inventory, fin.net_ppe,
    mkt.shares_outstanding, mkt.share_price, mkt.market_value_equity, mkt.dividend_cash_paid, mkt.eps_basic,
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

SELECT COUNT(*) FROM vn_firm_panel.fact_financial_year;