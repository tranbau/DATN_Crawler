import re

s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
def remove_accents(input_str):
	s = ''
	for c in input_str:
		if c in s1:
			s += s0[s1.index(c)]
		else:
			s += c
	return s

# Lấy tên biến từ tên file
# file_name: Tên file đã bỏ các kí tự đặc biệt
def get_statvar_by_file_name(file_name):
    # Tìm trước cụm từ "phân theo"
    parts = file_name.split("phân theo", 1)
    
    # Lấy phần đầu tiên của danh sách hoặc toàn bộ chuỗi nếu không có cụm từ "phân theo"
    if len(parts) > 1:
        result = parts[0].strip()
    else:
        result = file_name.strip()
        
    # Loại bỏ chuỗi trong dấu ngoặc đơn ()
    result = re.sub(r'\(.*?\)', '', result)
    
    # Loại bỏ các ký tự đặc biệt và chỉ giữ lại số , chữ cái và dấu ,
    result = re.sub(r"[^\w\s,]", "", result)
    
    # Cắt bỏ khoảng trắng ở đầu và cuối chuỗi
    result = result.strip()
    
    return result

# Đổi tên các biến 
def build_name_with_dict(stat_var_name_in_file, column_name, factor_dict):
    stat_var_name_in_file_lower = stat_var_name_in_file.lower()
    column_name_lower = column_name.lower()

    # Kiểm tra tên cột đã có trong tên biến ở tên file
    if column_name_lower not in stat_var_name_in_file_lower:  
        column_name = f"{stat_var_name_in_file}_{column_name}"
        
    if not factor_dict:
        return column_name
    for key, value in factor_dict.items():
        column_name  += f"_{value}"
    return column_name

template_onevar_multidate = {
    "facets": [
            {
                "id": 1,
                "mapper": "facet1",
                "provenance_url": "https://example.com/provenance1",
                "measurement_method": "method1",
                "observation_period": "period1",
                "scaling_factor": "factor1",
                "unit": "unit1"
            }
        ],
        "place_col": 1,
        "stat_var": "var1",
        "date_col_from": 2
    } 

template_multivar_onedate = {
    "facets": [
            {
                "id": 1,
                "mapper": "facet1",
                "provenance_url": "https://example.com/provenance1",
                "measurement_method": "method1",
                "observation_period": "period1",
                "scaling_factor": "factor1",
                "unit": "unit1"
            }
        ],
    "place_col": 1,
    "date_col": 2,
    "var_col_from": 3
    } 

def build_template(template, stat_var_columns, stat_var_names, provenance_id):
    # FIXME: cần sửa đổi facet + provenance_id về sau
    data = {}
    # 1 biến - nhiều ngày
    if template == 1:
        data = template_onevar_multidate
    else:
        data = template_multivar_onedate
                
    # Tạo đối tượng vars
    vars_list = []
    
    for index, name in enumerate(stat_var_names):
        mapper = 'var1' if template == 1 else stat_var_columns[index]
        var = {
            "id": 0,  
            "mapper": mapper,
            "name": name,
            "provenance_id": provenance_id,
            "definition": name,
            "facet": "facet1"
        }
        vars_list.append(var)
        
    data["vars"] = vars_list
    return data

# Phân loại template của df
def category_template(df):
    # 1 biến - nhiều cột Kiểm tra nhiều cột năm
    # Lấy danh sách cột
    normalized_columns = df.columns.str.lower()
    
    pattern = re.compile(r'^(sơ bộ \d+|\d+)$')
    
    # Lọc danh sách các cột thỏa mãn điều kiện
    date_columns = normalized_columns[normalized_columns.str.match(pattern)]
    
    if(len(date_columns) >= 2):
        return 1
    
    return 2

# Tạo file json tương ứng
def build_json_content(df, factor_dict , file_name, provenance_id):
    template = category_template(df)
    
    # Một biến - nhiều năm
    if(template == 1):
        # Lấy tên biến
        stat_var_name_in_file = get_statvar_by_file_name(file_name)
        
        # Đổi tên biến nào là trường hợp phân theo tiêu chí đặc biệt
        stat_var_name = build_name_with_dict(stat_var_name_in_file, stat_var_name_in_file, factor_dict)
        
        # Tạo đối tượng để ghi json theo template
        stat_var_names = []
        stat_var_names.append(stat_var_name)
        stat_var_columns = []
        stat_var_columns.append(stat_var_name_in_file)
        
        json_content = build_template(template ,stat_var_columns, stat_var_names, provenance_id)
        
        return json_content
        
    # Nhiều biến - 1 năm
    else :
        # Từ cột thứ 3
        stat_var_columns = df.columns[2:].tolist()
        
        # Lấy tên biến trong tên file
        stat_var_name_in_file = get_statvar_by_file_name(file_name)
        
        # Đổi tên biến
        stat_var_names = [build_name_with_dict(stat_var_name_in_file, col, factor_dict) for col in stat_var_columns]

        # Tạo đối tượng để ghi json theo template 
        json_content = build_template(template, stat_var_columns, stat_var_names, provenance_id)
        
        return json_content