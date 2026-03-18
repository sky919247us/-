import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def login_and_save_cookies():
    phone = "0930118237"
    password = "Feat940940"
    
    with sync_playwright() as p:
        logger.info("啟動無頭瀏覽器準備登入 FB...")
        browser = p.chromium.launch(headless=True)
        # 使用行動版 User-Agent 較不容易被判為機器人
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
            viewport={'width': 390, 'height': 844}
        )
        page = context.new_page()
        
        logger.info("前往 Facebook 行動版登入頁面...")
        page.goto("https://m.facebook.com/")
        
        page.wait_for_timeout(2000)
        
        # 填寫帳號密碼
        try:
            logger.info("正在填寫帳號與密碼...")
            page.fill("input[name='email'], input[type='email']", phone)
            page.fill("input[name='pass'], input[type='password']", password)
            page.locator("button[name='login'], input[name='login'], button[type='submit'], div[role='button']:has-text('登入')").first.click()
            
            logger.info("已提交登入，等待驗證 (10秒)...")
            page.wait_for_timeout(10000)
            
            # 檢查是否成功登入 (藉由網址是否離開首頁或出現登入後的物件判斷)
            current_url = page.url
            if "login/save-device" in current_url or "home.php" in current_url or "?" in current_url:
                 logger.info("登入似乎成功！")
            
            # 儲存登入狀態 (Cookies、LocalStorage)
            context.storage_state(path="state.json")
            logger.info("✅ 成功將登入通行證儲存為 state.json！")
            
            # 測試截圖存檔，確認畫面
            page.screenshot(path="login_result.png")
            logger.info("登入後畫面已截圖至 login_result.png")
            
        except Exception as e:
            logger.error(f"登入過程發生錯誤: {e}")
            page.screenshot(path="login_error.png")
            
        finally:
            browser.close()

if __name__ == "__main__":
    login_and_save_cookies()
