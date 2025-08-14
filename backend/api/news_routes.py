from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from typing import List, Optional
import logging
from ..services.rss_service import RSSService
from ..models.news import NewsArticle, BreakingNewsResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/news", tags=["news"])

# خدمة RSS عامة
rss_service = RSSService()

@router.get("/breaking", response_model=BreakingNewsResponse)
async def get_breaking_news():
    """جلب الأخبار العاجلة من مصادر RSS"""
    try:
        breaking_news_data = await rss_service.fetch_all_breaking_news()
        
        news_articles = []
        for article_data in breaking_news_data:
            article = NewsArticle(
                title=article_data['title'],
                description=article_data['description'],
                source=article_data['source'],
                published_at=article_data['published_at'],
                category=article_data['category'],
                is_breaking=article_data['is_breaking'],
                url=article_data.get('url'),
                image_url=article_data.get('image_url')
            )
            news_articles.append(article)
        
        return BreakingNewsResponse(
            breaking_news=news_articles,
            count=len(news_articles),
            last_updated=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error fetching breaking news: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في جلب الأخبار العاجلة")

@router.post("/refresh")
async def refresh_breaking_news(background_tasks: BackgroundTasks):
    """تحديث الأخبار العاجلة"""
    try:
        # تحديث في الخلفية لعدم إبطاء الاستجابة
        background_tasks.add_task(rss_service.fetch_all_breaking_news)
        
        return {
            "success": True,
            "message": "تم بدء تحديث الأخبار العاجلة",
            "timestamp": datetime.now()
        }
    
    except Exception as e:
        logger.error(f"Error refreshing news: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في تحديث الأخبار")

@router.get("/search")
async def search_breaking_news(q: Optional[str] = None, category: Optional[str] = None):
    """البحث في الأخبار العاجلة"""
    try:
        breaking_news_data = await rss_service.fetch_all_breaking_news()
        
        filtered_news = breaking_news_data
        
        if q:
            filtered_news = [
                article for article in filtered_news
                if q.lower() in article['title'].lower() or q.lower() in article['description'].lower()
            ]
        
        if category and category != "الكل":
            filtered_news = [
                article for article in filtered_news
                if article['category'] == category
            ]
        
        news_articles = []
        for article_data in filtered_news:
            article = NewsArticle(
                title=article_data['title'],
                description=article_data['description'],
                source=article_data['source'],
                published_at=article_data['published_at'],
                category=article_data['category'],
                is_breaking=article_data['is_breaking'],
                url=article_data.get('url'),
                image_url=article_data.get('image_url')
            )
            news_articles.append(article)
        
        return {
            "results": news_articles,
            "count": len(news_articles),
            "search_query": q,
            "category": category
        }
    
    except Exception as e:
        logger.error(f"Error searching news: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في البحث")