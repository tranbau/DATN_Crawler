import os
import string
import re
import numpy as np
import pandas as pd
from unidecode import unidecode
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from itertools import product
from handle_functions import get_special_value_groups, divide_df
from io_functions import export_csv_list_dfs, write_log
from mapper import location_mapper, provenance_id_mapper

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
website = "https://www.gso.gov.vn/"
driver.get(website)
data_dir = "data"
special_log_file = "logs\\special.log"

# Biến toàn cục lưu tên biến đã có


if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Xử lí df sau khi craw được
def handle_place(df, folder_name, file_name):
    # Chuyển đổi tên cột thành dạng viết thường và loại bỏ dấu tiếng Việt
    normalized_columns = df.columns.str.lower()

    # Tìm các cột có tên chứa các từ quan tâm
    place_columns = df.columns[normalized_columns.str.contains(
        'địa phương|(tỉnh.*thành phố)|(phường.*xã)|vùng')]

    if len(place_columns) == 0:
        # Nếu không có cột nào thỏa điều kiện, thêm cột "Địa phương" với giá trị id của Viet Nam
        df.insert(0, "dia phuong", "geoId-VNM")
        
    else:
        for col in place_columns:
            if df[col].dtype == 'object':
                # Chuyển đổi giá trị trong cột thành dạng không dấu
                df[col] = df[col].apply(lambda x: unidecode(x) if pd.notnull(x) else x)
                # Kiểm tra nếu giá trị chứa "ca nuoc" thì đổi thành "viet nam"
                df[col] = df[col].apply(
                    lambda x: "Viet Nam" if "CA NUOC" in x else x)
                # Chuyển thành id địa điểm tương ứng
                location_mapper_lower = {key.lower(): value for key, value in location_mapper.items()}
                # Chuyển thành id địa điểm tương ứng
                def map_location(x):
                    x_lower = x.lower()
                    if x_lower in location_mapper_lower:
                        return location_mapper_lower[x_lower]
                    else:
                        # Ghi log để xử lí
                        content = f"{folder_name}/{file_name}: {x}"
                        write_log(special_log_file, content)
                        
                        # Chuyển giá trị đó thành 1 cột place_special
                        
                        return None
                df[col] = df[col].apply(map_location)
                
    return df

# Xử lí các cột địa điểm
def handle_date(df, file_name, folder_name):
    # Chuyển đổi tên cột thành dạng viết thường \
    normalized_columns = df.columns.str.lower().str.replace(',', '')

    # Kiểm tra có cột năm
    if (any(normalized_columns == 'năm')):
        # Lọc các cột là "năm"
        year_columns = df.columns[normalized_columns == 'năm']
        # Chỉ giữ lại kí tự số
        # df[year_columns] = df[year_columns].applymap(lambda x: re.sub(r'\D', '', str(x)) if pd.notnull(x) else x)
    else:
        # Kiểm tra nhiều cột năm
        date_columns = normalized_columns[normalized_columns.str.contains(
            r'\b\d{4}\b')]
        if (len(date_columns) >= 2):
            pass
            # Chỉ giữ lại kí tự số
            # df.columns = df.columns.to_series().apply(lambda x: re.sub(r'\D', '', x) if any(col in x for col in date_columns) else x)
        else:
            # Thêm 1 cột năm sau cột địa điểm với giá trị lấy trong title
            match = re.search(r'\b\d{4}\b', file_name)
            if match:
                df.insert(1, "năm", match.group())
            else:
                # Không có -> trường hợp đặc biệt
                content = f"{folder_name}/{file_name}"
                write_log(special_log_file, content)
                return None
                
    return df

# Xử lí các cột không phải địa điểm, thời gian, dữ liệu (các cột tiêu chí xét)
def handle_special_columns(df):
    unique_values_dict = get_special_value_groups(df)

    dfs_with_details = divide_df(df, unique_values_dict)

    return dfs_with_details


# Xử lí chung
def handle_common(df):
    # Loại bỏ các kí tự không mong muốn từ tất cả các cell
    df = df.applymap(lambda x: str(x).replace(',', '.').replace(
        '(', '').replace(')', '').replace('*', '') if pd.notnull(x) else x)

    # Thay thế '..' bằng rỗng
    df.replace('..', '', inplace=True)

    # Xử lý các giá trị dạng chuỗi
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace('"', '', regex=False)
    return df

# Xử lí dataframe
def handle_df(df, folder_name, file_name,provenance_id ):
    # Xử lí cột địa điểm
    df = handle_place(df, folder_name, file_name)

    # TH đặc biệt -> dừng xử lí
    if(df is None):
        return
    
    # Xử lí thời gian
    df = handle_date(df, file_name, folder_name)
    
    # TH đặc biệt -> dừng xử lí
    if(df is None):
        return

    # Xử lí giá trị
    df = handle_common(df)

    # Xử lí tách df thành các df riêng nếu tồn tại các cột có giá trị khác số
    dfs_with_details = handle_special_columns(df)

    # Xuất file csv
    export_csv_list_dfs(dfs_with_details, data_dir, folder_name, file_name , provenance_id)

# Hàm lấy dữ liệu trong 1 tab
def extractData(folder_name, file_name, provenance_id):
    # Chuyển context vào iframe
    iframe = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.post-content iframe"))
    )
    driver.switch_to.frame(iframe)

    # Tìm tất cả các element có ID kết thúc bằng "VariableValueSelect_VariableValueSelect_SelectAllButton"
    selectAllButtons = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//*[contains(@id, 'VariableValueSelect_VariableValueSelect_SelectAllButton')]"))
    )
    # Click vào mỗi button tìm được
    for button in selectAllButtons:
        button.click()

    # Format
    formatElement = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "variableselector_outputformats_dropdown"))
    )
    formatSelect = Select(formatElement)
    formatSelect.select_by_value("tableViewSorted")

    # Submit
    submitBtn = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.ID, "ctl00_ContentPlaceHolderMain_VariableSelector1_VariableSelector1_ButtonViewTable"))
    )
    submitBtn.click()

    # Get data
    headers = []
    data = []

    # Header
    headerElements = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".tablesorter tr.table-jquerysort-header th.header"))
    )
    headers = [headerElement.text for headerElement in headerElements]

    # Data
    rowElements = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".tablesorter tbody tr"))
    )
    
    for rowElement in rowElements:
        dataElements = rowElement.find_elements(by=By.CSS_SELECTOR, value="td")
        rowData = [td.text for td in dataElements]
        data.append(rowData)

    # Tạo pandas dataframe
    df = pd.DataFrame(data, columns=headers)

    # Xử lí
    handle_df(df, folder_name, file_name, provenance_id)

    driver.switch_to.default_content()
    driver.back()

if __name__ == "__main__":
    # Các tab lĩnh vực
    linkElements = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//nav[@aria-label='Main Menu']//ul[@id='menu-main-menu-vi']//ul[@class='sub-menu']//a[@class='fusion-bar-highlight' and @href != '#']"))
    )

    # Chỉ 13 tab đầu có data
    data_tab = 13
    for index,linkElement in enumerate(linkElements[12:13]):
        try:
            # Tên tab - tên lĩnh vực ứng với tên folder tương ứng
            spanElement = linkElement.find_element(By.XPATH, ".//span")
            
            folder_name = spanElement.get_attribute("textContent")
            
            # Link
            link = linkElement.get_attribute("href")
            driver.get(link)

            # Danh sách link data trong lĩnh vực
            subLinkElements = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@class='tab-pane fade fusion-clearfix in active']//a")))
            
            # Tab lao động : lấy từ index 26 do trùng với dân số
            # if(folder_name == 'Lao động việc làm'):
            #     subLinkElements = subLinkElements[26:]
            for sub_index,subLinkElement in enumerate(subLinkElements):
                try:
                    link = subLinkElement.get_attribute("href")

                    # Lấy tên dataset
                    dataset_name = subLinkElement.text
                    driver.get(link)

                    provenance_id = provenance_id_mapper(folder_name, sub_index)
                    extractData(folder_name=folder_name,
                                file_name=dataset_name, provenance_id=provenance_id)

                    driver.back()
                except StaleElementReferenceException:
                    subLinkElements = WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//div[@class='tab-pane fade fusion-clearfix in active']//a")))
                
            driver.back()
                
        except StaleElementReferenceException:
            print("Stale element, refreshing...")
            linkElements = WebDriverWait(driver, 1500).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//nav[@aria-label='Main Menu']//ul[@id='menu-main-menu-vi']//ul[@class='sub-menu']//a[@class='fusion-bar-highlight' and @href != '#']"))
            )
        finally:
            print("done")
            driver.quit()
