from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import uuid

class NewsArticle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    source: str
    published_at: datetime
    category: str
    is_breaking: bool = False
    url: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NewsResponse(BaseModel):
    news: List[NewsArticle]
    total: int
    last_updated: datetime

class BreakingNewsResponse(BaseModel):
    breaking_news: List[NewsArticle]
    count: int
    last_updated: datetime