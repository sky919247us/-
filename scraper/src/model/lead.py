from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class Lead(BaseModel):
    """
    潛在客戶名單實體
    對應 Supabase 中的 `leads` 資料表
    """
    id: str                 # 系統唯一識別碼 (流水號)
    platform: str           # 來源出處 (例：FB - 大里人聊天室)
    post_date: datetime      # 發文日期
    category: str           # 業務分類 (例：防水抓漏)
    content_summary: str    # 對方留言摘要
    image_url: Optional[str] # 照片預覽
    ai_tags: Optional[str]  # AI 標籤 (🔥 緊急求救 / 👁️ 競業已留言)
    url: str                # 貼文網址
    status: str = "未處理"   # 處理狀態 (未處理 / 已回覆 / 略過)
