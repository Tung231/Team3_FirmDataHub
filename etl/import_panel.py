import pandas as pd
import mysql.connector
from db_config import DB_CONFIG

def clean_decimal(value):
    if pd.isna(value) or value == '': return None
    if isinstance(value, str): value = value.replace(',', '.')
    try: return float(value)
    except: return None

def get_firm_id(cursor, ticker):
    """Tìm firm_id từ ticker trong bảng dim_firm"""
    cursor.execute("SELECT firm_id FROM dim_firm WHERE ticker = %s", (ticker,))
    result = cursor.fetchone()
    return result[0] if result else None

def import_panel_data(file_path, snapshot_id):
    print(f"🚀 Đang nạp dữ liệu vào Database của thầy...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        df = pd.read_excel(file_path, header=2)
        df.columns = [str(c).strip().lower() for c in df.columns]
        if 'stockcode' in df.columns: df.rename(columns={'stockcode': 'ticker'}, inplace=True)

        # Mapping mới theo bảng của thầy
        mapping = {
            'doanh thu thuần': ('fact_financial_year', 'net_sales'),
            'lợi nhuận sau thuế': ('fact_financial_year', 'net_income'),
            'tổng tài sản': ('fact_financial_year', 'total_assets'),
            'nợ phải trả': ('fact_financial_year', 'total_liabilities'),
            'eps': ('fact_market_year', 'eps_basic') # EPS nằm ở bảng Market
        }

        count = 0
        for _, row in df.iterrows():
            ticker = str(row['ticker']).strip().upper()
            year = int(row['year'])
            firm_id = get_firm_id(cursor, ticker)

            if not firm_id:
                print(f"⚠️ Bỏ qua {ticker}: Không tìm thấy ID trong dim_firm")
                continue

            for excel_col, (table, sql_col) in mapping.items():
                val = clean_decimal(row.get(excel_col))
                if val is None: continue

                query = f"""
                    INSERT INTO {table} (firm_id, fiscal_year, {sql_col}, snapshot_id)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE {sql_col} = VALUES({sql_col}), snapshot_id = VALUES(snapshot_id)
                """
                cursor.execute(query, (firm_id, year, val, snapshot_id))
            count += 1
        
        conn.commit()
        print(f"✅ XONG: Đã nạp {count} dòng vào các bảng Fact của thầy!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    sid = input("Nhập Snapshot ID (số 1): ")
    import_panel_data("../data/panel_2020_2024.xlsx", int(sid))