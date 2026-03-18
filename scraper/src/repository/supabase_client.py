import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv
from src.model.lead import Lead

load_dotenv()
logger = logging.getLogger(__name__)

class SupabaseRepository:
    """
    處理 Supabase 資料庫連線與寫入邏輯
    """
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            # 這裡不直接報錯，因為爬蟲可能還在剛測試開發階段
            logger.warning("Supabase URL或KEY未設定，寫入動作將跳過")
            self.client = None
        else:
            self.client: Client = create_client(url, key)

    def insert_lead(self, lead: Lead) -> bool:
        """
        將爬蟲抓到的名單寫入 Supabase
        """
        if not self.client:
            logger.info(f"[模擬寫入] {lead.model_dump()}")
            return True

        try:
            data = self.client.table("leads").insert(lead.model_dump(mode='json')).execute()
            logger.info(f"成功寫入名單: {lead.id}")
            return True
        except Exception as e:
            logger.error(f"寫入名單發生錯誤: {e}")
            return False
