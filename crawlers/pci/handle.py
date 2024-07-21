import os
import pandas as pd
import re
import unicodedata
from mapper import normalized_location_mapper

# Đường dẫn tới thư mục hiện tại của file Python
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "data")
handled_data_dir = os.path.join(current_dir, "handled_data")
notfound_file = os.path.join(current_dir, "notfound.txt")

# Tạo thư mục handled_data nếu chưa tồn tại
if not os.path.exists(handled_data_dir):
    os.makedirs(handled_data_dir)

# Hàm để loại bỏ dấu tiếng Việt và chuyển về viết thường
def normalize_location(location):
    if not isinstance(location, str):
        return location
    location = ''.join(
        c for c in unicodedata.normalize('NFD', location) if unicodedata.category(c) != 'Mn'
    )
    return location.lower()

# Hàm để xử lý DataFrame và thêm cột thời gian
def process_dataframe(df, year, notfound_file):
    notfound_values = []

    # Bỏ cột 'Vùng' nếu có
    if 'Vùng' in df.columns:
        df = df.drop(columns=['Vùng'])

    # Thêm cột thời gian vào vị trí thứ 2
    df.insert(1, 'Thời gian', year)

    # Xử lý các cột khác
    for col in df.columns:
        if df[col].dtype == 'object':
            # Bỏ ký tự % và bỏ khoảng trắng
            df[col] = df[col].str.replace('%', '').str.strip()
            
            # Chuyển đổi chuỗi phần trăm thành số nguyên và nhân lên 100 lần
            df[col] = df[col].apply(lambda x: int(float(x) * 100) if x.replace('.', '', 1).isdigit() else x)
            
            if col == df.columns[0]:
                # Áp dụng mapper cho cột đầu tiên
                df[col] = df[col].apply(lambda x: map_location(x, notfound_values))
    
    # Ghi các giá trị không tìm thấy vào file với mã hóa UTF-8
    with open(notfound_file, 'a', encoding='utf-8') as f:
        for value in notfound_values:
            f.write(f"{value}\n")

    return df

# Hàm để map location và lưu các giá trị không tìm thấy
def map_location(value, notfound_values):
    if not isinstance(value, str):
        return value
    normalized_value = normalize_location(value)
    if normalized_value in normalized_location_mapper:
        return normalized_location_mapper[normalized_value]
    else:
        notfound_values.append(value)
        return value

# Hàm để xử lý file Excel
def process_excel_file(input_file_path, output_dir, year):
    # Đọc tất cả các sheet từ file Excel
    xls = pd.ExcelFile(input_file_path)
    
    for sheet_name in xls.sheet_names:
        # Bỏ qua sheet "Tổng hợp"
        if sheet_name == "Tổng hợp":
            continue

        # Đọc dữ liệu từ sheet hiện tại
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Chỉ xử lý tối đa 64 hàng
        df = df.iloc[:63]

        # Gọi hàm xử lý dataframe
        df = process_dataframe(df, year, notfound_file)
        
        # Tạo tên file đầu ra cho sheet hiện tại (dùng tên sheet và năm)
        output_file_path = os.path.join(output_dir, f"{sheet_name}_{year}.csv")
        df.to_csv(output_file_path, index=False)

# Hàm để trích xuất năm từ tên file
def extract_year_from_filename(filename):
    match = re.search(r'(PCI|PGI)(\d{4})', filename)
    if match:
        return match.group(2)
    else:
        return None

# Xóa nội dung cũ của file notfound.txt nếu có
if os.path.exists(notfound_file):
    os.remove(notfound_file)

# Duyệt qua thư mục data và tạo cấu trúc tương ứng trong handled_data
for root, dirs, files in os.walk(data_dir):
    relative_path = os.path.relpath(root, data_dir)
    output_dir = os.path.join(handled_data_dir, relative_path)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in files:
        if file.endswith('.xlsx'):
            input_file_path = os.path.join(root, file)
            year = extract_year_from_filename(file)
            if year:
                process_excel_file(input_file_path, output_dir, year)
