from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import shutil

# Lấy đường dẫn tới thư mục hiện tại của file Python
current_dir = os.path.dirname(os.path.abspath(__file__))
pcivn_dir = os.path.join(current_dir, "pgi-vn")

# Tạo thư mục pci-vn nếu chưa tồn tại
if not os.path.exists(pcivn_dir):
    os.makedirs(pcivn_dir)

# Khởi tạo trình duyệt
driver = webdriver.Chrome()

driver.get("https://www.pcivietnam.vn/du-lieu-pgi")

wait = WebDriverWait(driver, 10)
download_links = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//tbody[@id='pgi_data_load']//td[@class='td_button']/a")))

download_dir = os.path.expanduser("~/Downloads")

# Tải xuống tất cả các file
for link in download_links:
    link.click()
    time.sleep(5)  # Thời gian chờ để đảm bảo file được tải xuống hoàn toàn

    # Lấy file mới nhất trong thư mục tải về
    latest_file = max([os.path.join(download_dir, f) for f in os.listdir(download_dir) if not f.endswith(".crdownload")], key=os.path.getctime)
    
    # Di chuyển file vào thư mục pci-vn
    shutil.move(latest_file, pcivn_dir)

# Đóng trình duyệt
driver.quit()