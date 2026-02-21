import pandas as pd
import mysql.connector
import os
from db_config import DB_CONFIG

def export_latest_panel():
    print("🚀 Đang tiến hành trích xuất Dataset Panel sạch...")
    conn = mysql.connector.connect(**DB_CONFIG)
    
    # Câu truy vấn SQL "Vạn năng": 
    # 1. Tìm Snapshot ID lớn nhất cho mỗi (firm_id, fiscal_year)
    # 2. JOIN với tất cả các bảng Fact để lấy đủ 38 biến
    query = """
    WITH LatestSnapshots AS (
        SELECT firm_id, fiscal_year, MAX(snapshot_id) as max_sid
        FROM fact_financial_year
        GROUP BY firm_id, fiscal_year
    )
    SELECT 
        f.ticker, 
        fin.fiscal_year,
        -- Nhóm Tài chính (Financial)
        fin.net_sales, fin.total_assets, fin.selling_expenses, fin.general_admin_expenses, 
        fin.intangible_assets_net, fin.manufacturing_overhead, fin.net_operating_income, 
        fin.raw_material_consumption, fin.merchandise_purchase_year, fin.wip_goods_purchase, 
        fin.outside_manufacturing_expenses, fin.production_cost, fin.rnd_expenses, 
        fin.net_income, fin.total_equity, fin.total_liabilities, fin.cash_and_equivalents, 
        fin.long_term_debt, fin.current_assets, fin.current_liabilities, fin.growth_ratio, 
        fin.inventory, fin.net_ppe,
        -- Nhóm Thị trường (Market)
        mkt.shares_outstanding, mkt.market_value_equity, mkt.dividend_cash_paid, mkt.eps_basic,
        -- Nhóm Sở hữu (Ownership)
        own.managerial_inside_own, own.state_own, own.institutional_own, own.foreign_own,
        -- Nhóm Nhân sự & Tuổi (Meta)
        meta.employees_count, meta.firm_age,
        -- Nhóm Đổi mới (Innovation)
        inn.product_innovation, inn.process_innovation,
        -- Nhóm Dòng tiền (Cashflow)
        cf.net_cfo, cf.capex, cf.net_cfi
    FROM LatestSnapshots ls
    JOIN dim_firm f ON ls.firm_id = f.firm_id
    JOIN fact_financial_year fin ON ls.firm_id = fin.firm_id AND ls.fiscal_year = fin.fiscal_year AND ls.max_sid = fin.snapshot_id
    LEFT JOIN fact_market_year mkt ON fin.firm_id = mkt.firm_id AND fin.fiscal_year = mkt.fiscal_year AND fin.snapshot_id = mkt.snapshot_id
    LEFT JOIN fact_ownership_year own ON fin.firm_id = own.firm_id AND fin.fiscal_year = own.fiscal_year AND fin.snapshot_id = own.snapshot_id
    LEFT JOIN fact_firm_year_meta meta ON fin.firm_id = meta.firm_id AND fin.fiscal_year = meta.fiscal_year AND fin.snapshot_id = meta.snapshot_id
    LEFT JOIN fact_innovation_year inn ON fin.firm_id = inn.firm_id AND fin.fiscal_year = inn.fiscal_year AND fin.snapshot_id = inn.snapshot_id
    LEFT JOIN fact_cashflow_year cf ON fin.firm_id = cf.firm_id AND fin.fiscal_year = cf.fiscal_year AND fin.snapshot_id = cf.snapshot_id
    ORDER BY f.ticker, fin.fiscal_year;
    """

    try:
        df = pd.read_sql(query, conn)
        
        # Tạo thư mục outputs nếu chưa có
        output_dir = '../outputs'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_path = os.path.join(output_dir, 'panel_latest.csv')
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ THÀNH CÔNG: Đã xuất {len(df)} dòng dữ liệu vào {output_path}")
        print(f"📊 Tổng số cột (biến): {len(df.columns)}")

    except Exception as e:
        print(f"❌ Lỗi khi xuất dữ liệu: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    export_latest_panel()