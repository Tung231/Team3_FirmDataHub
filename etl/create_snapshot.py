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
        
        # BƯỚC 1: Tìm source_id từ bảng dim_data_source dựa trên source_name
        cursor.execute("SELECT source_id FROM dim_data_source WHERE source_name = %s", (source_name,))
        result = cursor.fetchone()
        
        if result:
            source_id = result[0]
        else:
            # Nếu chưa có nguồn này, tự động nạp mới vào bảng DIM
            print(f"⚠️ Nguồn '{source_name}' chưa có trong danh mục. Đang tự động thêm...")
            cursor.execute(
                "INSERT INTO dim_data_source (source_name, source_type, provider) VALUES (%s, 'manual', 'Group3')",
                (source_name,)
            )
            source_id = cursor.lastrowid

        # BƯỚC 2: Insert vào bảng fact_data_snapshot dùng source_id (Đúng ý thầy)
        query = """
        INSERT INTO fact_data_snapshot (source_id, fiscal_year, snapshot_date, version_tag)
        VALUES (%s, %s, %s, %s)
        """
        data = (source_id, fiscal_year, snapshot_date, version_tag)
        
        cursor.execute(query, data)
        conn.commit()
        
        snapshot_id = cursor.lastrowid
        print(f"✅ Đã tạo Snapshot thành công!")
        print(f"🆔 SNAPSHOT_ID: {snapshot_id}")
        print(f"📋 Chi tiết: Nguồn: {source_name} (ID: {source_id}) | Năm: {fiscal_year}")
        
        return snapshot_id

    except mysql.connector.Error as err:
        print(f"❌ Lỗi SQL: {err}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # Tùng chạy thử với nguồn Vietstock
    create_snapshot(
        source_name="Vietstock", 
        fiscal_year=2024, 
        version_tag="Final_Group3"
    )