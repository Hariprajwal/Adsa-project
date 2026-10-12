import time
import socket
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def run_test():
    port = find_free_port()
    print(f"Starting uvicorn on port {port}...")
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.web.app:app", "--port", str(port), "--host", "127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--window-size=1920,1080')
    driver = None
    
    try:
        # Wait for server to be responsive
        time.sleep(2.5)
        driver = webdriver.Chrome(options=opts)
        
        print(f"[1/6] Loading http://127.0.0.1:{port}...")
        driver.get(f'http://127.0.0.1:{port}')
        time.sleep(1.5)
        
        # 1. Verify Dropdown Button
        dropdown_toggle = driver.find_element(By.ID, 'btnSimulateDropdownToggle')
        dropdown_menu = driver.find_element(By.ID, 'simulateDropdownMenu')
        main_sim_btn = driver.find_element(By.ID, 'btnSimulateStream')
        
        print("[2/6] Verifying Dropdown toggle...")
        dropdown_toggle.click()
        time.sleep(0.5)
        assert "show" in dropdown_menu.get_attribute("class"), "Dropdown menu should be visible"
        
        items = driver.find_elements(By.CLASS_NAME, 'dropdown-item')
        print(f"Found {len(items)} policy options in dropdown menu.")
        assert len(items) == 6, f"Expected 6 policies, found {len(items)}"
        
        # 2. Select Round-Robin from Dropdown
        rr_item = driver.find_element(By.CSS_SELECTOR, '.dropdown-item[data-policy="round_robin"]')
        print("[3/6] Clicking Round-Robin in Dropdown...")
        rr_item.click()
        time.sleep(2.0) # Wait for 20 chunks to simulate
        
        # 3. Verify Real-Time Policy Comparison Table Card
        table_card = driver.find_element(By.ID, 'policyComparisonCard')
        assert table_card is not None, "Policy Comparison Card should exist below dispatch feed"
        
        rows = driver.find_elements(By.CSS_SELECTOR, '#policyTableBody tr')
        print(f"[4/6] Verifying Comparison Table: found {len(rows)} rows.")
        assert len(rows) == 6, f"Expected 6 rows in comparison table, found {len(rows)}"
        
        # Check active row is Round-Robin
        rr_row = driver.find_element(By.ID, 'row-round_robin')
        assert "row-active" in rr_row.get_attribute("class"), "Round-Robin row should be active"
        
        # 4. Click 'Run Pure' for Least-Loaded Node
        lln_run_btn = driver.find_element(By.CSS_SELECTOR, '#row-least_loaded .btn-pure-run')
        print(f"[5/6] Clicking 'Run Pure' for Least-Loaded Node (LLN)...")
        lln_run_btn.click()
        time.sleep(2.0)
        
        lln_row = driver.find_element(By.ID, 'row-least_loaded')
        assert "row-active" in lln_row.get_attribute("class"), "LLN row should be active"
        
        # Save screenshot
        driver.save_screenshot('tests/policy_dropdown_comparison_screenshot.png')
        print("[6/6] Saved screenshot to tests/policy_dropdown_comparison_screenshot.png")
        print("ALL UI DROPDOWN & REAL-TIME COMPARISON TABLE TESTS PASSED!")
        
    finally:
        if driver:
            driver.quit()
        server.terminate()
        server.wait()

if __name__ == "__main__":
    run_test()
