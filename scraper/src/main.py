import logging
import sys
import os

# 確保可正確 import src 模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.service.spider import ScraperService
from src.repository.supabase_client import SupabaseRepository

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logger()
    logger = logging.getLogger("main")
    logger.info("=== 獵漏雷達爬蟲任務啟動 ===")

    # 1. 初始化爬蟲服務與資料庫服務
    spider = ScraperService()
    db = SupabaseRepository()

    # 2. 爬取資料
    leads = spider.run_spider()

    # 3. 寫入資料庫
    if not leads:
        logger.info("沒有找到新的潛在名單。")
        return

    success_count = 0
    for lead in leads:
        if db.insert_lead(lead):
            success_count += 1
    
    logger.info(f"=== 任務結束：總共嘗試寫入 {len(leads)} 筆，成功 {success_count} 筆 ===")

if __name__ == "__main__":
    main()
