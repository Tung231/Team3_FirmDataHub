import pandas as pd
import mysql.connector
from mysql.connector import Error
try:
    from db_config import DB_CONFIG
except ImportError:
    print("❌ Lỗi: Bạn chưa tạo file db_config.py!")
    exit()

def import_firms_from_excel(file_path):
    print(f"--- Đang bắt đầu Pipeline Import: {file_path} ---")
    conn = None
    
    try:
        df = pd.read_excel(file_path)
        # Chuẩn hóa tên cột: xóa khoảng trắng, viết thường
        df.columns = [c.strip().lower() for c in df.columns]

        # --- BỘ LỌC THÔNG MINH CẬP NHẬT ---
        # 1. Map Sàn chứng khoán
        exchange_map = {
            'hose': 1, 'hnx': 2, 'upcom': 3
        }

        # 2. Map Ngành (Dựa trên 20 mã của nhóm Tùng)
        industry_map = {
            'khai khoáng và vật liệu': 1,
            'khai khoáng': 1,
            'thực phẩm': 2,
            'thực phẩm và đồ uống': 2,
            'dầu khí': 4,
            'thiết bị điện': 5,
            'hàng và dịch vụ công nghiệp': 5,
            'xây dựng và vật liệu': 7,
            'xây dựng': 7
        }

        # Hàm chuyển đổi an toàn
        def map_value(val, mapping):
            if pd.isna(val): return 1
            val_clean = str(val).strip().lower()
            return mapping.get(val_clean, 1) # Nếu không tìm thấy thì mặc định để ID 1

        # Thực hiện chuyển đổi chữ -> số
        if 'exchange_id' in df.columns:
            df['exchange_id'] = df['exchange_id'].apply(lambda x: map_value(x, exchange_map))
        
        if 'industry_l2_id' in df.columns:
            df['industry_l2_id'] = df['industry_l2_id'].apply(lambda x: map_value(x, industry_map))

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        upsert_query = """
        INSERT INTO dim_firm (ticker, company_name, exchange_id, industry_l2_id)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            company_name = VALUES(company_name),
            exchange_id = VALUES(exchange_id),
            industry_l2_id = VALUES(industry_l2_id);
        """

        records_count = 0
        for index, row in df.iterrows():
            # Ép kiểu về int để đảm bảo SQL nhận đúng
            data = (
                str(row['ticker']).strip().upper(), 
                row['company_name'], 
                int(row['exchange_id']), 
                int(row['industry_l2_id'])
            )
            cursor.execute(upsert_query, data)
            records_count += 1

        conn.commit()
        print(f"✅ Thành công: Đã xử lý {records_count} doanh nghiệp.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    path = "../data/firms.xlsx" 
    import_firms_from_excel(path)