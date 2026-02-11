# etl/db_config_template.py

# File này là mẫu cấu hình kết nối Database
# LƯU Ý: Tuyệt đối không sửa trực tiếp file này. 
# Hãy tạo file mới tên 'db_config.py' (không có chữ template) để sử dụng local.

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD_HERE",  # Thay mật khẩu MySQL của bạn vào đây
    "database": "vn_firm_panel",      # Tên Database của nhóm
    "port": 3306                      # Cổng mặc định của MySQL
}