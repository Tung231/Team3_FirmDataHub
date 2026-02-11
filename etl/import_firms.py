# etl/import_firms.py
import mysql.connector
try:
    from db_config import DB_CONFIG
except ImportError:
    print("❌ Lỗi: Bạn chưa tạo file db_config.py từ file template!")
    exit()

def verify_firm_list():
    # Danh sách 20 mã cổ phiếu chuẩn của nhóm
    target_tickers = [
        'VGS', 'CLH', 'LBM', 'QHD', 'MVB', 'BCF', 'HAP', 'MCP', 
        'IDI', 'LGC', 'THG', 'CDC', 'LHC', 'LCG', 'TV2', 'TCL', 
        'ILB', 'STG', 'PVB', 'VNT'
    ]
    
    conn = None
    try:
        # 1. Kết nối Database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"--- Đang kiểm tra danh mục công ty trong '{DB_CONFIG['database']}' ---")
        
        # 2. Truy vấn lấy danh sách ticker hiện có trong dim_firm
        query = "SELECT ticker FROM dim_firm"
        cursor.execute(query)
        existing_tickers = [row[0] for row in cursor.fetchall()]
        
        # 3. So sánh
        found = []
        missing = []
        for t in target_tickers:
            if t in existing_tickers:
                found.append(t)
            else:
                missing.append(t)
        
        # 4. Xuất kết quả
        print(f"✅ Đã tìm thấy: {len(found)}/{len(target_tickers)} mã.")
        
        if missing:
            print(f"⚠️ Cảnh báo: Thiếu {len(missing)} mã: {', '.join(missing)}")
            print("👉 Vui lòng chạy lại phần SEED DATA trong file SQL!")
        else:
            print("🚀 Tuyệt vời! Tất cả 20 mã đã sẵn sàng để nạp dữ liệu tài chính.")

    except mysql.connector.Error as err:
        print(f"❌ Lỗi kết nối MySQL: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    verify_firm_list()