import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

opts = Options()
opts.add_argument('--headless')
opts.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=opts)

try:
    driver.get('http://127.0.0.1:8080')
    time.sleep(1)
    
    btn = driver.find_element(By.ID, 'themeToggleBtn')
    btn.click()
    time.sleep(1)
    
    driver.save_screenshot('tests/light_mode_screenshot.png')
    print('Screenshot saved to tests/light_mode_screenshot.png')

finally:
    driver.quit()
