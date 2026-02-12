import pandas as pd
import mysql.connector
import os
import csv
from db_config import DB_CONFIG

# --- CẤU HÌNH RULES ---
GROWTH_MIN = -0.95
GROWTH_MAX = 5.0
MKT_VAL_TOLERANCE = 0.01  # Sai số 1% cho kiểm tra vốn hóa

def run_qc():
    print("🔍 Đang bắt đầu kiểm tra chất lượng dữ liệu (Quality Control)...")
    
    # 1. Kết nối Database
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True) # Trả về dạng dict cho dễ truy cập

    # 2. Lấy dữ liệu tổng hợp để kiểm tra
    # Chúng ta JOIN các bảng Fact lại để check chéo
    query = """
    SELECT f.ticker, fin.fiscal_year, 
           fin.total_assets, fin.current_liabilities, fin.growth_ratio,
           mkt.shares_outstanding, mkt.share_price, mkt.market_value_equity,
           own.managerial_inside_own, own.state_own, own.institutional_own, own.foreign_own
    FROM dim_firm f
    JOIN fact_financial_year fin ON f.firm_id = fin.firm_id
    LEFT JOIN fact_market_year mkt ON fin.firm_id = mkt.firm_id AND fin.fiscal_year = mkt.fiscal_year
    LEFT JOIN fact_ownership_year own ON fin.firm_id = own.firm_id AND fin.fiscal_year = own.fiscal_year
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    qc_results = []

    for row in rows:
        t = row['ticker']
        y = row['fiscal_year']

        # Rule 1: Ownership ratios nằm trong [0,1]
        own_fields = ['managerial_inside_own', 'state_own', 'institutional_own', 'foreign_own']
        for field in own_fields:
            val = row[field]
            if val is not None and not (0 <= float(val) <= 1):
                qc_results.append([t, y, field, 'OUT_OF_RANGE', f'Giá trị {val} nằm ngoài khoảng [0,1]'])

        # Rule 2: Shares outstanding > 0
        shares = row['shares_outstanding']
        if shares is not None and float(shares) <= 0:
            qc_results.append([t, y, 'shares_outstanding', 'INVALID_VALUE', f'Số lượng cổ phiếu ({shares}) phải > 0'])

        # Rule 3: Total assets >= 0
        assets = row['total_assets']
        if assets is not None and float(assets) < 0:
            qc_results.append([t, y, 'total_assets', 'NEGATIVE_VALUE', f'Tổng tài sản ({assets}) không được âm'])

        # Rule 4: Current liabilities >= 0
        liabilities = row['current_liabilities']
        if liabilities is not None and float(liabilities) < 0:
            qc_results.append([t, y, 'current_liabilities', 'NEGATIVE_VALUE', f'Nợ ngắn hạn ({liabilities}) không được âm'])

        # Rule 5: Growth ratio nằm trong khoảng cấu hình
        growth = row['growth_ratio']
        if growth is not None:
            if not (GROWTH_MIN <= float(growth) <= GROWTH_MAX):
                qc_results.append([t, y, 'growth_ratio', 'OUT_OF_RANGE', f'Tỷ lệ tăng trưởng {growth} bất thường (Range: {GROWTH_MIN} to {GROWTH_MAX})'])

        # Rule 6: Market Value ≈ Shares * Price
        mkt_val = row['market_value_equity']
        price = row['share_price']
        if all(v is not None for v in [mkt_val, shares, price]):
            expected_val = float(shares) * float(price)
            diff = abs(float(mkt_val) - expected_val)
            if diff > (expected_val * MKT_VAL_TOLERANCE):
                qc_results.append([t, y, 'market_value_equity', 'CALCULATION_ERROR', f'Vốn hóa ({mkt_val}) lệch so với Shares * Price ({expected_val})'])

    # 3. Xuất file báo cáo
    output_dir = '../outputs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    report_path = os.path.join(output_dir, 'qc_report.csv')
    with open(report_path, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['ticker', 'fiscal_year', 'field_name', 'error_type', 'message'])
        writer.writerows(qc_results)

    print(f"✅ Đã hoàn thành kiểm tra. Tìm thấy {len(qc_results)} cảnh báo.")
    print(f"📊 Báo cáo chi tiết tại: {report_path}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_qc()