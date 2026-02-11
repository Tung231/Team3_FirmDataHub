import mysql.connector
from datetime import datetime
try:
    from db_config import DB_CONFIG
except ImportError:
    print("❌ Lỗi: Bạn chưa tạo file db_config.py!")
    exit()

def create_snapshot(source_name, fiscal_year, snapshot_date=None, version_tag="v1.0"):
    # Nếu không nhập ngày, lấy ngày hôm nay
    if snapshot_date is None:
        snapshot_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Câu lệnh Insert đúng theo yêu cầu của thầy
        query = """
        INSERT INTO fact_data_snapshot (source_name, fiscal_year, snapshot_date, version_tag)
        VALUES (%s, %s, %s, %s)
        """
        data = (source_name, fiscal_year, snapshot_date, version_tag)
        
        cursor.execute(query, data)
        conn.commit()
        
        snapshot_id = cursor.lastrowid
        print(f"✅ Đã tạo Snapshot thành công!")
        print(f"🆔 SNAPSHOT_ID: {snapshot_id}")
        print(f"📋 Chi tiết: Nguồn: {source_name} | Năm tài chính: {fiscal_year} | Phiên bản: {version_tag}")
        
        return snapshot_id

    except mysql.connector.Error as err:
        print(f"❌ Lỗi SQL: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # Tùng có thể thay đổi thông tin ở đây trước khi chạy
    create_snapshot(
        source_name="Vietstock_Excel_Group3", 
        fiscal_year=2024, 
        version_tag="Final_Draft"
    )