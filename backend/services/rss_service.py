import feedparser
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import re
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class RSSService:
    def __init__(self):
        # مصادر RSS للأخبار العاجلة العربية
        self.rss_sources = [
            {
                "name": "الجزيرة",
                "url": "https://www.aljazeera.net/rss/all",
                "breaking_keywords": ["عاجل", "الآن", "فوري", "طارئ", "عذراً"]
            },
            {
                "name": "العربية",
                "url": "https://www.alarabiya.net/arab-and-world.rss",
                "breaking_keywords": ["عاجل", "الآن", "سريع", "فوري"]
            },
            {
                "name": "BBC عربي",
                "url": "https://feeds.bbci.co.uk/arabic/rss.xml",
                "breaking_keywords": ["عاجل", "الآن", "سريع"]
            },
            {
                "name": "سكاي نيوز عربية",
                "url": "https://www.skynewsarabia.com/rss",
                "breaking_keywords": ["عاجل", "فوري", "الآن"]
            }
        ]
        self.session = None

    async def get_session(self):
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    def is_breaking_news(self, title: str, description: str, keywords: List[str]) -> bool:
        """تحديد ما إذا كان الخبر عاجلاً بناءً على الكلمات المفتاحية"""
        text = f"{title} {description}".lower()
        return any(keyword in text for keyword in keywords)

    def categorize_news(self, title: str, description: str) -> str:
        """تصنيف الأخبار بناءً على المحتوى"""
        text = f"{title} {description}".lower()
        
        categories = {
            "سياسة": ["سياسة", "حكومة", "رئيس", "وزير", "برلمان", "انتخابات", "دبلوماسية"],
            "اقتصاد": ["اقتصاد", "تجارة", "استثمار", "أسعار", "تضخم", "بورصة", "شركة"],
            "رياضة": ["رياضة", "كرة", "مباراة", "بطولة", "فريق", "لاعب"],
            "تكنولوجيا": ["تكنولوجيا", "إنترنت", "ذكي", "رقمي", "تقني", "برمجة"],
            "صحة": ["صحة", "طب", "علاج", "مرض", "وباء", "طبيب", "مستشفى"],
            "علوم": ["علم", "اكتشاف", "بحث", "دراسة", "تجربة", "عالم"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "عام"

    async def fetch_rss_feed(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """جلب RSS feed من مصدر واحد"""
        try:
            session = await self.get_session()
            async with session.get(source["url"]) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch RSS from {source['name']}: {response.status}")
                    return []
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries[:20]:  # أخذ آخر 20 خبر فقط
                    try:
                        # تنسيق التاريخ
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_at = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                            published_at = datetime(*entry.updated_parsed[:6])
                        else:
                            published_at = datetime.now()

                        # تنظيف العنوان والوصف
                        title = re.sub(r'<[^>]+>', '', entry.get('title', ''))
                        description = re.sub(r'<[^>]+>', '', entry.get('summary', entry.get('description', '')))
                        
                        # تحديد ما إذا كان الخبر عاجلاً
                        is_breaking = self.is_breaking_news(title, description, source["breaking_keywords"])
                        
                        # التصنيف التلقائي
                        category = self.categorize_news(title, description)
                        
                        # جلب الصورة إذا وجدت
                        image_url = None
                        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                            image_url = entry.media_thumbnail[0].get('url')
                        elif hasattr(entry, 'enclosures') and entry.enclosures:
                            for enclosure in entry.enclosures:
                                if enclosure.type.startswith('image/'):
                                    image_url = enclosure.href
                                    break

                        articles.append({
                            'title': title.strip(),
                            'description': description.strip()[:500],  # قطع الوصف عند 500 حرف
                            'source': source["name"],
                            'published_at': published_at,
                            'category': category,
                            'is_breaking': is_breaking,
                            'url': entry.get('link', ''),
                            'image_url': image_url
                        })
                    except Exception as e:
                        logger.error(f"Error processing entry from {source['name']}: {str(e)}")
                        continue

                logger.info(f"Fetched {len(articles)} articles from {source['name']}")
                return articles

        except Exception as e:
            logger.error(f"Error fetching RSS from {source['name']}: {str(e)}")
            return []

    async def fetch_all_breaking_news(self) -> List[Dict[str, Any]]:
        """جلب جميع الأخبار العاجلة من جميع المصادر"""
        tasks = []
        for source in self.rss_sources:
            tasks.append(self.fetch_rss_feed(source))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"RSS fetch failed: {result}")
                continue
            all_articles.extend(result)
        
        # فلترة الأخبار العاجلة فقط
        breaking_news = [article for article in all_articles if article['is_breaking']]
        
        # ترتيب حسب التاريخ (الأحدث أولاً)
        breaking_news.sort(key=lambda x: x['published_at'], reverse=True)
        
        # إزالة الأخبار المكررة بناءً على العنوان
        seen_titles = set()
        unique_breaking_news = []
        for article in breaking_news:
            title_clean = re.sub(r'[^\w\s]', '', article['title'].lower())
            if title_clean not in seen_titles:
                seen_titles.add(title_clean)
                unique_breaking_news.append(article)
        
        logger.info(f"Fetched {len(unique_breaking_news)} unique breaking news articles")
        return unique_breaking_news[:50]  # أقصى 50 خبر عاجل

    async def close(self):
        """إغلاق الجلسة"""
        if self.session:
            await self.session.close()
            self.session = None