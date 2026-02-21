import pandas as pd
import mysql.connector
from db_config import DB_CONFIG

def clean_val(value):
    """Xử lý số định dạng VN (6.669.719.000) và các khoảng trắng"""
    if pd.isna(value) or value == '': return None
    if isinstance(value, str):
        value = value.strip()
        # Nếu có nhiều dấu chấm (nghìn tỷ) -> Bỏ dấu chấm phân cách
        if value.count('.') > 1:
            value = value.replace('.', '')
        # Đổi dấu phẩy thập phân thành dấu chấm
        value = value.replace(',', '.')
    try:
        return float(value)
    except:
        return None

def import_panel_data(file_path, snapshot_id):
    print(f"🚀 Leader Tùng đang nạp dữ liệu chuẩn 38 biến vào Database...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # Đọc dữ liệu từ dòng 3 (Header=2)
        df = pd.read_excel(file_path, header=2)
        df.columns = [str(c).strip().lower() for c in df.columns]

        # MAPPING CHUẨN XÁC THEO FILE EXCEL CỦA TÙNG
        mapping = {
            # Bảng Sở hữu (Ownership)
            'managerial/inside ownership': ('fact_ownership_year', 'managerial_inside_own'),
            'state ownership': ('fact_ownership_year', 'state_own'),
            'institutional ownership': ('fact_ownership_year', 'institutional_own'),
            'foreign ownership': ('fact_ownership_year', 'foreign_own'),
            
            # Bảng Thị trường (Market)
            'total share outstanding': ('fact_market_year', 'shares_outstanding'),
            'market value of equity': ('fact_market_year', 'market_value_equity'),
            'divident payment': ('fact_market_year', 'dividend_cash_paid'),
            'eps': ('fact_market_year', 'eps_basic'),
            
            # Bảng Tài chính (Financial) - 23 biến
            'net sales revenue': ('fact_financial_year', 'net_sales'),
            'total assets': ('fact_financial_year', 'total_assets'),
            'selling expenses': ('fact_financial_year', 'selling_expenses'),
            'general and administrative expenditure': ('fact_financial_year', 'general_admin_expenses'),
            'value of intangible assets': ('fact_financial_year', 'intangible_assets_net'),
            'manufacturing overhead (indirect cost)': ('fact_financial_year', 'manufacturing_overhead'),
            'net operating income': ('fact_financial_year', 'net_operating_income'),
            'consumption of raw material': ('fact_financial_year', 'raw_material_consumption'),
            'merchandise purchase of the year': ('fact_financial_year', 'merchandise_purchase_year'),
            'work-in-progess goods purchase': ('fact_financial_year', 'wip_goods_purchase'),
            'outside manufacturing expenses': ('fact_financial_year', 'outside_manufacturing_expenses'),
            'production cost': ('fact_financial_year', 'production_cost'),
            'r&d expenditure': ('fact_financial_year', 'rnd_expenses'),
            'net income': ('fact_financial_year', 'net_income'),
            'total shareholders\' equity': ('fact_financial_year', 'total_equity'),
            'total liabilities': ('fact_financial_year', 'total_liabilities'),
            'cash and cash equivalent': ('fact_financial_year', 'cash_and_equivalents'),
            'long-term debt': ('fact_financial_year', 'long_term_debt'),
            'current assets': ('fact_financial_year', 'current_assets'),
            'current liabiltiies': ('fact_financial_year', 'current_liabilities'),
            'growth ratio': ('fact_financial_year', 'growth_ratio'),
            'total inventory': ('fact_financial_year', 'inventory'),
            'net plant, property and equipment': ('fact_financial_year', 'net_ppe'),
            
            # Bảng Nhân sự & Tuổi (Meta)
            'number of employees': ('fact_firm_year_meta', 'employees_count'),
            'firm age': ('fact_firm_year_meta', 'firm_age'),
            
            # Bảng Đổi mới (Innovation)
            'product innovation': ('fact_innovation_year', 'product_innovation'),
            'process innovation': ('fact_innovation_year', 'process_innovation'),
            
            # Bảng Dòng tiền (Cashflow)
            'net cash from operating activities': ('fact_cashflow_year', 'net_cfo'),
            'capital expenditure': ('fact_cashflow_year', 'capex'),
            'cash flows from investing activities': ('fact_cashflow_year', 'net_cfi')
        }

        success_count = 0
        for _, row in df.iterrows():
            ticker = str(row.get('ticker', '')).strip().upper()
            if not ticker: continue
            
            # Lấy firm_id
            cursor.execute("SELECT firm_id FROM dim_firm WHERE ticker = %s", (ticker,))
            res = cursor.fetchone()
            if not res:
                print(f"❌ Ticker '{ticker}' không tồn tại. Bỏ qua.")
                continue
            
            firm_id = res[0]
            year = int(row['year'])
            
            # Gom dữ liệu theo bảng để nạp
            table_payloads = {}
            for excel_col, (table, sql_col) in mapping.items():
                if excel_col in df.columns:
                    val = clean_val(row[excel_col])
                    if val is not None:
                        if table not in table_payloads: table_payloads[table] = {}
                        table_payloads[table][sql_col] = val

            # Ghi vào MySQL
            for table, fields in table_payloads.items():
                cols = ['firm_id', 'fiscal_year', 'snapshot_id'] + list(fields.keys())
                vals = [firm_id, year, snapshot_id] + list(fields.values())
                placeholders = ", ".join(["%s"] * len(vals))
                updates = ", ".join([f"{c} = VALUES({c})" for c in fields.keys()])
                
                query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {updates}, snapshot_id = VALUES(snapshot_id)"
                cursor.execute(query, vals)
            
            success_count += 1

        conn.commit()
        print(f"✅ THÀNH CÔNG: Đã nạp dữ liệu cho {success_count} công ty/năm.")

    except Exception as e:
        conn.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    sid = input("Nhập Snapshot ID: ")
    import_panel_data("../data/panel_2020_2024.xlsx", int(sid))