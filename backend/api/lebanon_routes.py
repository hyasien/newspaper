from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from typing import Dict, List, Optional
import logging
from services.lebanon_news_service import LebanonNewsService
from models.news import NewsArticle

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lebanon", tags=["lebanon"])

# خدمة الأخبار اللبنانية
lebanon_service = LebanonNewsService()

@router.get("/headlines")
async def get_lebanon_headlines():
    """جلب أبرز العناوين السياسية من الصحف اللبنانية"""
    try:
        headlines_data = await lebanon_service.fetch_all_lebanon_headlines()
        
        # تنظيم البيانات بتنسيق مناسب للعرض
        organized_data = {}
        total_count = 0
        
        for newspaper_name, headlines in headlines_data.items():
            news_articles = []
            for headline_data in headlines:
                article = NewsArticle(
                    title=headline_data['title'],
                    description=headline_data['description'],
                    source=headline_data['source'],
                    published_at=headline_data['published_at'],
                    category=headline_data['category'],
                    is_breaking=False,  # العناوين العادية ليست عاجلة
                    url=headline_data.get('url'),
                    image_url=headline_data.get('image_url')
                )
                news_articles.append(article)
            
            organized_data[newspaper_name] = {
                "headlines": news_articles,
                "count": len(news_articles),
                "website": headlines[0]["website"] if headlines else ""
            }
            total_count += len(news_articles)
        
        return {
            "newspapers": organized_data,
            "total_newspapers": len(organized_data),
            "total_headlines": total_count,
            "last_updated": datetime.now(),
            "country": "لبنان"
        }
    
    except Exception as e:
        logger.error(f"Error fetching Lebanon headlines: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في جلب عناوين الصحف اللبنانية")

@router.get("/newspapers")
async def get_lebanon_newspapers_list():
    """قائمة بأسماء الصحف اللبنانية المتاحة"""
    try:
        newspapers_info = []
        for newspaper in lebanon_service.lebanon_newspapers:
            newspapers_info.append({
                "name": newspaper["name"],
                "website": newspaper["website"],
                "category": newspaper["category"]
            })
        
        return {
            "newspapers": newspapers_info,
            "count": len(newspapers_info),
            "country": "لبنان"
        }
    
    except Exception as e:
        logger.error(f"Error fetching newspapers list: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في جلب قائمة الصحف")

@router.post("/refresh")
async def refresh_lebanon_headlines(background_tasks: BackgroundTasks):
    """تحديث عناوين الصحف اللبنانية"""
    try:
        # تحديث في الخلفية لعدم إبطاء الاستجابة
        background_tasks.add_task(lebanon_service.fetch_all_lebanon_headlines)
        
        return {
            "success": True,
            "message": "تم بدء تحديث عناوين الصحف اللبنانية",
            "timestamp": datetime.now()
        }
    
    except Exception as e:
        logger.error(f"Error refreshing Lebanon headlines: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في تحديث العناوين")

@router.get("/newspaper/{newspaper_name}")
async def get_specific_newspaper_headlines(newspaper_name: str):
    """جلب عناوين صحيفة محددة"""
    try:
        # البحث عن الصحيفة في القائمة
        newspaper_info = None
        for newspaper in lebanon_service.lebanon_newspapers:
            if newspaper["name"] == newspaper_name:
                newspaper_info = newspaper
                break
        
        if not newspaper_info:
            raise HTTPException(status_code=404, detail="الصحيفة غير موجودة")
        
        headlines = await lebanon_service.fetch_newspaper_headlines(newspaper_info)
        
        news_articles = []
        for headline_data in headlines:
            article = NewsArticle(
                title=headline_data['title'],
                description=headline_data['description'],
                source=headline_data['source'],
                published_at=headline_data['published_at'],
                category=headline_data['category'],
                is_breaking=False,
                url=headline_data.get('url'),
                image_url=headline_data.get('image_url')
            )
            news_articles.append(article)
        
        return {
            "newspaper": newspaper_name,
            "headlines": news_articles,
            "count": len(news_articles),
            "website": newspaper_info["website"],
            "last_updated": datetime.now()
        }
    
    except Exception as e:
        logger.error(f"Error fetching headlines for {newspaper_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في جلب عناوين الصحيفة")