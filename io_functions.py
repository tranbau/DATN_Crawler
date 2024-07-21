
import os
import re
from unidecode import unidecode
import json
from ultis import remove_accents, build_json_content
from pathlib import Path

# Xử lí tên file
def format_file_name(file_name):
    # Loại bỏ các kí tự không hợp lệ 
    sanitized_title = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', file_name)
    
    # Loại bỏ khoảng trắng ở đầu và cuối chuỗi và thay thế khoảng trắng nếu có bằng dấu gạch dưới
    sanitized_title = sanitized_title.strip()

    return sanitized_title

# Xử lí tên folder
def format_folder_name(folder_name):    
    folder_name =  folder_name.strip()
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', folder_name)
        
def export_csv_list_dfs(dfs_with_details, data_dir, folder_name, file_name, provenance_id, error_log_file = 'logs\\errors.log' ):
    dfs = dfs_with_details['dfs']
    details = dfs_with_details['details']
    
    if len(dfs) != len(details):
        return
    
    # Format the file and folder names
    formatted_file_name = format_file_name(file_name)
    formatted_folder_name = format_folder_name(folder_name)
    
    # Open the error log file in append mode
    with open(error_log_file, 'a', encoding='utf-8') as log_file:
        for i, df in enumerate(dfs):  
            try:
                # Create a new file name with the index appended
                new_file_name = f"{formatted_file_name}_{i}"

                dir_path = os.path.join(data_dir, formatted_folder_name, format_folder_name(file_name))
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                            
                # Write the DataFrame to a CSV file
                full_path = os.path.join(dir_path, f"{new_file_name}.csv")
                
                # Kiểm tra độ dài full_path, nếu quá 216
                max_len = 216
                if(len(full_path) > max_len):
                    dir_len = len(dir_path)
                    file_new_len = max_len - dir_len - len('.csv') - 1
                    new_file_name = new_file_name[-file_new_len:]
                    full_path = os.path.join(dir_path, f"{new_file_name}.csv")
                            
                df.to_csv(full_path, index=False)
                
                # Tạo nội dung theo template 
                json_content = build_json_content(df,details[i], formatted_file_name, provenance_id)
                
                # Ghi file json 
                write_json_file(json_content, dir_path, new_file_name)
                
            except Exception as e:
                # If an error occurs, write the file name to the log file
                log_file.write(f"{full_path}: {str(e)}\n")
                
# Ghi dữ liệu từ từ điển vào file JSON
def write_json_file(json_content, dir_path, file_name):    
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        # Tạo đường dẫn đầy đủ cho file JSON
        file_path = os.path.join(dir_path, f"{file_name}.json")
    

        with open(file_path, 'w', encoding='utf-8') as json_file:
             json.dump(json_content, json_file, ensure_ascii=False)
    except Exception as e:
        print(f"Lỗi xuất file CSV: {str(e)}. Bỏ qua không xuất file nữa.")
        
# Ghi log cần thiết 
def write_log(file_log, content):
    with open(file_log, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{content}\n")
