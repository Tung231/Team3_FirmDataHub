import pandas as pd
import mysql.connector
import os
from db_config import DB_CONFIG

def export_latest_panel():
    print("🚀 Đang trích xuất Dataset Panel chuẩn theo thứ tự của thầy...")
    
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        
        # Truy vấn từ View đã sắp xếp
        query = "SELECT * FROM vw_firm_panel_latest ORDER BY ticker, fiscal_year"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            print("❌ LỖI: Không có dữ liệu! Hãy chạy import_panel.py trước.")
            return

        # Đổi tên cột sang đúng yêu cầu của thầy (Professional Labels)
        column_mapping = {
            'ticker': 'Ticker',
            'fiscal_year': 'Fiscal_Year',
            'managerial_inside_own': 'Managerial Ownership',
            'state_own': 'State Ownership',
            'institutional_own': 'Institutional Ownership',
            'foreign_own': 'Foreign Ownership',
            'shares_outstanding': 'Total share outstanding',
            'total_sales_revenue': 'Total sales revenue',
            'net_sales_revenue': 'Net sales revenue',
            'total_assets': 'Total assets',
            'selling_expenses': 'Selling expenses',
            'general_admin_expenses': 'General and administrative expenditure',
            'intangible_assets_net': 'Value of intangible assets',
            'manufacturing_overhead': 'Manufacturing overhead',
            'net_operating_income': 'Net operating income',
            'raw_material_consumption': 'Consumption of raw material',
            'merchandise_purchase_year': 'Merchandise purchase',
            'wip_goods_purchase': 'Work-in-progress goods',
            'outside_manufacturing_expenses': 'Outside manufacturing expenses',
            'production_cost': 'Production cost',
            'rnd_expenses': 'R&D expenditure',
            'product_innovation': 'Product innovation',
            'process_innovation': 'Process innovation',
            'net_income': 'Net Income',
            'total_equity': "Total shareholders' equity",
            'market_value_equity': 'Market value of equity',
            'total_liabilities': 'Total liabilities',
            'net_cfo': 'Net cash from operating activities',
            'capex': 'Capital expenditure',
            'net_cfi': 'Cash flows from investing activities',
            'cash_and_equivalents': 'Cash and cash equivalent',
            'long_term_debt': 'Long-term debt',
            'current_assets': 'Current assets',
            'current_liabilities': 'Current liabilities',
            'growth_ratio': 'Growth ratio',
            'inventory': 'Total inventory',
            'dividend_cash_paid': 'Dividend payment',
            'eps_basic': 'EPS',
            'employees_count': 'Number of employees',
            'net_ppe': 'Net plant, property and equipment',
            'firm_age': 'Firm age'
        }

        # Áp dụng đổi tên
        df = df.rename(columns=column_mapping)

        # Xuất file
        output_dir = '../outputs'
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        output_path = os.path.join(output_dir, 'panel_latest.csv')
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ THÀNH CÔNG: Đã xuất {len(df)} dòng vào {output_path}")
        print(f"📊 Tổng số cột: {len(df.columns)} (Ticker, Year + 39 biến)")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    export_latest_panel()