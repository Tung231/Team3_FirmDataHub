import pandas as pd
import mysql.connector
from db_config import DB_CONFIG

def import_panel_data(file_path, snapshot_id):
    print(f"🚀 Đang bắt đầu nạp dữ liệu từ {file_path} (Bắt đầu từ dòng 3)...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # --- FIX: header=2 nghĩa là lấy dòng 3 trong Excel làm tiêu đề ---
        df = pd.read_excel(file_path, header=2) 
        
        # 1. Dọn dẹp tên cột
        df.columns = [str(c).strip().lower() for c in df.columns]

        # 2. Đổi tên stockcode thành ticker để khớp với Database
        if 'stockcode' in df.columns:
            df.rename(columns={'stockcode': 'ticker'}, inplace=True)
            print("💡 Đã nhận diện cột 'stockcode' ở dòng 3 và chuyển thành 'ticker'.")

        # 3. Kiểm tra xem đã thấy ticker và year chưa
        if 'ticker' not in df.columns or 'year' not in df.columns:
            print(f"❌ Vẫn không tìm thấy cột 'ticker'/'year' ở dòng 3!")
            print(f"Các cột máy thấy là: {list(df.columns)}")
            return

        # 4. MAPPING: Tên cột Excel -> {Bảng SQL, Cột SQL}
        # Tùng dặn Thành viên 2 điền nốt các biến còn lại vào đây nhé
        mapping = {
            'doanh thu thuần': ('fact_financial_statement', 'net_revenue'),
            'lợi nhuận sau thuế': ('fact_financial_statement', 'net_profit'),
            'tổng tài sản': ('fact_balance_sheet', 'total_assets'),
            'nợ phải trả': ('fact_balance_sheet', 'total_liabilities'),
            'roa': ('fact_financial_ratios', 'roa'),
            'roe': ('fact_financial_ratios', 'roe'),
            'eps': ('fact_financial_ratios', 'eps')
        }

        count = 0
        for index, row in df.iterrows():
            ticker = str(row['ticker']).strip().upper()
            year = int(row['year'])

            for excel_col, (table, sql_col) in mapping.items():
                if excel_col in df.columns:
                    val = row[excel_col]
                    if pd.isna(val): continue

                    query = f"""
                        INSERT INTO {table} (ticker, year, {sql_col}, snapshot_id)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE {sql_col} = VALUES({sql_col}), snapshot_id = VALUES(snapshot_id)
                    """
                    cursor.execute(query, (ticker, year, val, snapshot_id))
            count += 1
        
        conn.commit()
        print(f"✅ THÀNH CÔNG RỰC RỠ: Đã nạp xong {count} dòng dữ liệu!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    sid = input("Nhập Snapshot ID của Tùng (số 1): ")
    path = "../data/panel_2020_2024.xlsx"
    import_panel_data(path, int(sid))