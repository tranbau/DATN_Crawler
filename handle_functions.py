import pandas as pd
from itertools import product

# Hàm để tạo các DataFrame mới từ DataFrame ban đầu và unique_values_dict
def divide_df(df, unique_values_dict):
    # Tạo tất cả các khả năng của các giá trị duy nhất
    all_combinations = list(product(*unique_values_dict.values()))
    
    spec_columns = unique_values_dict.keys()
    # Tạo DataFrame mới cho mỗi khả năng
    dfs = []
    details = []
    for combination in all_combinations:
        conditions = {}
        for col, val in zip( spec_columns, combination):
            conditions[col] = val
        # Lọc DataFrame ban đầu dựa trên điều kiện
        new_df = df.copy()
       
        for col, val in conditions.items():
            new_df = new_df[new_df[col] == val]
        # Loại bỏ các cột là key trong unique_values_dict
        new_df = new_df.drop( spec_columns, axis=1, errors='ignore')
        # Thêm DataFrame mới vào danh sách nếu có dữ liệu
        if not new_df.empty:
            details.append(conditions)
            dfs.append(new_df)
            
    return {'dfs': dfs, 'details': details}

# 
def get_special_value_groups(df):
    special_keywords = ["địa phương", "phường", "xã", "tỉnh", "thành phố", "dia phuong", "vùng", "vung", "năm"]
    special_columns = []
    
    # Tìm các cột đặc biệt
    for column in df.columns:
        if any(keyword in column.lower() for keyword in special_keywords):
            pass
        else:
            try:
                # Kiểm tra xem tất cả các giá trị trong cột có thể chuyển đổi thành số không
                df[column] = pd.to_numeric(df[column])
            except ValueError:
                # Nếu không thể chuyển đổi, thêm cột vào danh sách các cột đặc biệt
                special_columns.append(column)
                
    # Tạo một dictionary để lưu trữ các giá trị khác nhau của các cột đặc biệt
    unique_values_dict = {}
    
    # Duyệt qua từng cột đặc biệt và lưu mảng giá trị khác nhau của mỗi cột 
    for col in special_columns:
        # Tìm các giá trị duy nhất của cột đặc biệt
        unique_values = df[col].unique()
        # Lưu trữ các giá trị duy nhất vào dictionary mới
        unique_values_dict[col] = unique_values
    
    return unique_values_dict