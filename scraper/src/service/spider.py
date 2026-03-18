import logging
from typing import List
from datetime import datetime
from src.model.lead import Lead

logger = logging.getLogger(__name__)

class RegexEngine:
    """
    處理關鍵字比對的引擎
    """
    def __init__(self):
        self.triggers = {
            "結構補強": ["鋼筋外露", "天花板", "水泥剝落", "裂縫", "房屋傾斜", "結構加固"],
            "防水抓漏": ["漏水", "滲水", "壁癌", "抓漏", "防水", "積水"]
        }
        # 移除地區限制，改為全台適用。負面詞條維持。
        self.negatives = ["售屋", "仲介", "五金買賣", "誠徵學徒", "缺工", "找人代工"]

    def analyze_content(self, content: str) -> str:
        """
        初步過濾內容，返回對應的業務分類，若都不符合或觸發負面字則返回空字串。
        """
        # 排除字檢查
        for neg in self.negatives:
            if neg in content:
                return ""

        # 觸發詞檢查
        for category, triggers in self.triggers.items():
            for trigger in triggers:
                if trigger in content:
                    return category
        
        return ""

class ScraperService:
    """
    主爬蟲服務，包含 Playwright 的呼叫邏輯。
    針對 Facebook / Threads 進行真實 DOM 爬取。
    """
    def __init__(self):
        self.engine = RegexEngine()
        # 擴展至全台灣 FB 相關修繕 / 地方社團清單 (可隨時擴充)
        # 擴展至全台灣 FB 相關修繕 / 地方社團清單
        self.target_urls = [
            "https://m.facebook.com/groups/436329713183204/", # 大里人聊天室
            "https://m.facebook.com/groups/109311415779075/", # 台中大小事
            "https://m.facebook.com/groups/176558112958742/", # 高雄五四三
            "https://m.facebook.com/groups/337463513076135/", # 台北人
            "https://m.facebook.com/groups/712345678901234/"  # 這裡可繼續手動加入更多的公開社團網址
        ]
        # 設定 Threads 的搜尋字串清單
        self.threads_keywords = ["抓漏", "房屋修繕", "壁癌"]

    def _scrape_facebook_groups(self) -> List[dict]:
        from playwright.sync_api import sync_playwright
        import os
        logger.info("啟動 Playwright 無頭瀏覽器抓取 FB 社團...")
        
        posts_data = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # 建立行動版 Context 並掛載通行證 (若存在)
            state_path = "state.json"
            context_kwargs = {
                "user_agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
                "viewport": {'width': 390, 'height': 844}
            }
            if os.path.exists(state_path):
                logger.info("找到 state.json 登入通行證，套用至爬蟲環境...")
                context_kwargs["storage_state"] = state_path
            
            context = browser.new_context(**context_kwargs)
            
            page = context.new_page()
            
            for url in self.target_urls:
                try:
                    logger.info(f"正在前往: {url}")
                    page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    page.wait_for_timeout(3000) # 等待內容渲染
                    
                    # 擷取文章文字塊 (納入多種可能的 FB Mobile 結構)
                    elements = page.locator('article, div[data-mcomponent="MContainer"], div[data-sigil="m-feed-voice"]').all()
                    logger.info(f"在 {url} 找到 {len(elements)} 個潛在貼文區塊")
                    for el in elements[:10]: # 增加掃描數量
                        text = el.inner_text().strip()
                        if len(text) > 20: # 過濾掉太短的無效字串
                            posts_data.append({
                                "platform": "Facebook",
                                "content": text,
                                "url": url 
                            })
                except Exception as e:
                    logger.error(f"抓取 FB {url} 時發生錯誤: {e}")
            
            browser.close()
            
        return posts_data

    def _scrape_threads(self) -> List[dict]:
        from playwright.sync_api import sync_playwright
        import urllib.parse
        import os
        logger.info("啟動 Playwright 無頭瀏覽器抓取 Threads...")
        
        posts_data = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            state_path = "threads_state.json"
            context_kwargs = {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "viewport": {'width': 1280, 'height': 800}
            }
            if os.path.exists(state_path):
                logger.info("找到 threads_state.json 登入通行證，套用至 Threads 爬蟲環境...")
                context_kwargs["storage_state"] = state_path
            
            context = browser.new_context(**context_kwargs)
            page = context.new_page()
            
            for keyword in self.threads_keywords:
                url = f"https://www.threads.net/search?q={urllib.parse.quote(keyword)}"
                try:
                    logger.info(f"正在前往 Threads 搜尋: {keyword}")
                    page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    page.wait_for_timeout(5000)
                    
                    elements = page.locator("div[role='article']").all()
                    if not elements:
                        elements = page.locator("div[data-pressable-container='true']").all()
                        
                    logger.info(f"在 Threads ({keyword}) 找到 {len(elements)} 篇潛在貼文")
                    for el in elements[:10]:
                        text = el.inner_text().strip()
                        if len(text) > 20: 
                            posts_data.append({
                                "platform": "Threads",
                                "content": text,
                                "url": url 
                            })
                except Exception as e:
                    logger.error(f"抓取 Threads {keyword} 時發生錯誤: {e}")
            
            browser.close()
            
        return posts_data

    def run_spider(self) -> List[Lead]:
        """
        執行爬蟲任務 (整合真實爬蟲 + 關鍵字判斷)
        """
        logger.info("開始執行真實爬蟲腳本...")
        leads = []
        
        raw_posts = self._scrape_facebook_groups() + self._scrape_threads()

        for idx, post in enumerate(raw_posts):
            logger.info(f"檢測貼文 {idx+1} [長度 {len(post['content'])}]: {post['content'][:50]}...")
            category = self.engine.analyze_content(post["content"])
            if category:
                lead = Lead(
                    id=f"POST-{datetime.now().strftime('%Y%m%d%H%M')}-{idx+1}",
                    platform=post["platform"],
                    post_date=datetime.now(),
                    category=category,
                    content_summary=post["content"][:150],
                    image_url=None,
                    ai_tags=None,
                    url=post["url"],
                    status="未處理"
                )
                leads.append(lead)

        logger.info(f"爬蟲執行完畢，共解析出 {len(leads)} 筆有效貼文。")
        return leads
