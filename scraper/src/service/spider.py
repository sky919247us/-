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
            "結構補強": ["鋼筋外露", "天花板掉落", "水泥剝落", "樑柱裂縫", "房屋傾斜", "結構加固"],
            "防水抓漏": ["頂樓漏水", "窗框滲水", "壁癌嚴重", "抓漏推薦", "外牆防水", "浴室漏水"]
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
        self.target_urls = [
            "https://m.facebook.com/groups/436329713183204/", # 範例社團 (大里人)
            # 未來可再加入新竹、台北、高雄等地方社團
        ]

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
                    logger.error(f"抓取 {url} 時發生錯誤: {e}")
            
            browser.close()
            
        return posts_data

    def run_spider(self) -> List[Lead]:
        """
        執行爬蟲任務 (整合真實爬蟲 + 關鍵字判斷)
        """
        logger.info("開始執行真實爬蟲腳本...")
        leads = []
        
        raw_posts = self._scrape_facebook_groups()

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
