import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

opts = Options()
opts.add_argument('--headless')
opts.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=opts)

port = 8080
try:
    print(f"[1/5] Loading http://127.0.0.1:{port}...")
    driver.get(f'http://127.0.0.1:{port}')

    time.sleep(1.5)
    
    # Check initial dispatched count
    cnt_el = driver.find_element(By.ID, 'statDispatchedCount')
    print(f"[2/5] Initial Dispatched Count: {cnt_el.text}")

    # Click Simulate Continuous Stream
    sim_btn = driver.find_element(By.ID, 'btnToggleLiveSim')
    print(f"[3/5] Clicking '{sim_btn.text}'...")
    sim_btn.click()
    
    # Wait for chunks to stream live
    time.sleep(3.5)
    
    # Check dispatched count after streaming
    final_cnt = int(cnt_el.text)
    print(f"[4/5] Dispatched Count after 3.5s: {final_cnt}")
    assert final_cnt >= 2, f"Expected at least 2 dispatched chunks, got {final_cnt}"
    
    # Inspect live algorithm simulation card
    step1 = driver.find_element(By.ID, 'simStep1Text').text
    step2 = driver.find_element(By.ID, 'simStep2Text').text
    step3 = driver.find_element(By.ID, 'simStep3Text').text
    thesis_metric = driver.find_element(By.ID, 'contrastThesisMetric').text
    print(f"Step 1: {step1}")
    print(f"Step 2: {step2}")
    print(f"Step 3: {step3}")
    print(f"Thesis Metric: {thesis_metric}")
    
    driver.save_screenshot('tests/live_simulation_screenshot.png')
    print("[5/5] Screenshot saved to tests/live_simulation_screenshot.png")
    print("LIVE STREAM CHUNK SIMULATION TEST PASSED SUCCESSFULLY!")

finally:
    driver.quit()
