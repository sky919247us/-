import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def login_threads():
    phone = "0930118237"
    password = "Feat940940"
    
    with sync_playwright() as p:
        logger.info("啟動無頭瀏覽器準備登入 Threads...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        logger.info("前往 Threads 登入頁面...")
        page.goto("https://www.threads.net/login")
        page.wait_for_timeout(3000)
        
        try:
            logger.info("尋找使用者與密碼輸入框...")
            # Instagram/Threads login fields usually have name "username" and "password"
            page.fill("input[type='text'], input[name='username']", phone)
            page.fill("input[type='password'], input[name='password']", password)
            
            logger.info("點擊登入按鈕...")
            # Look for button containing 'Log in' or '登入'
            page.locator("button[type='submit'], div[role='button']:has-text('登入'), div[role='button']:has-text('Log in')").first.click()
            
            logger.info("等待登入驗證 (15秒)...")
            page.wait_for_timeout(15000)
            
            context.storage_state(path="threads_state.json")
            logger.info("✅ 成功將 Threads 登入通行證儲存為 threads_state.json！")
            
            page.screenshot(path="threads_login_result.png")
            
        except Exception as e:
            logger.error(f"登入 Threads 過程發生錯誤: {e}")
            page.screenshot(path="threads_login_error.png")
            
        finally:
            browser.close()

if __name__ == "__main__":
    login_threads()
