import pandas as pd
import mysql.connector
import os
from db_config import DB_CONFIG

def export_latest_panel():
    print("🚀 Đang trích xuất Dataset Panel (38 biến + Snapshot mới nhất)...")
    
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        
        # Truy vấn trực tiếp từ View vw_firm_panel_latest
        query = "SELECT * FROM vw_firm_panel_latest ORDER BY ticker, fiscal_year"
        
        # Đọc dữ liệu
        df = pd.read_sql(query, conn)
        
        if df.empty:
            print("❌ LỖI: Không có dữ liệu để xuất! Tùng kiểm tra lại xem đã chạy import_panel.py chưa?")
            return

        # Kiểm tra số lượng cột
        expected_cols = 40 # 38 biến + ticker + fiscal_year
        if len(df.columns) < expected_cols:
            print(f"⚠️ CẢNH BÁO: Chỉ tìm thấy {len(df.columns)} cột. Có thể thiếu biến tài chính.")

        # Xuất file
        output_dir = '../outputs'
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        output_path = os.path.join(output_dir, 'panel_latest.csv')
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ THÀNH CÔNG: Đã xuất {len(df)} dòng vào {output_path}")
        print(f"📊 Dataset chuẩn: {len(df.columns)} cột (biến).")

    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    export_latest_panel()