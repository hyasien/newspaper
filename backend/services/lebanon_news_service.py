import feedparser
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import re
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class LebanonNewsService:
    def __init__(self):
        # مصادر RSS للصحف اللبنانية مع مصادر بديلة
        self.lebanon_newspapers = [
            {
                "name": "النهار",
                "url": "https://www.annahar.com/rss.xml",
                "category": "سياسة",
                "website": "https://www.annahar.com"
            },
            {
                "name": "الأخبار",
                "url": "https://www.al-akhbar.com/rss",
                "category": "سياسة", 
                "website": "https://www.al-akhbar.com"
            },
            {
                "name": "الجمهورية",
                "url": "https://feeds.feedburner.com/AlGomhuriaNews",
                "category": "سياسة",
                "website": "https://www.al-gomhuria.com"
            },
            {
                "name": "المستقبل",
                "url": "https://almustaqbal.com/feed",
                "category": "سياسة",
                "website": "https://almustaqbal.com"
            },
            {
                "name": "اللواء", 
                "url": "https://www.alliwaa.com.lb/feed/",
                "category": "سياسة",
                "website": "https://www.alliwaa.com.lb"
            },
            {
                "name": "الديار",
                "url": "https://www.addiyar.com/feed",
                "category": "سياسة",
                "website": "https://www.addiyar.com"
            },
            {
                "name": "الجريدة",
                "url": "https://www.aljarida.com/feeds/all.xml",
                "category": "سياسة",
                "website": "https://www.aljarida.com"
            },
            {
                "name": "MTV Lebanon",
                "url": "https://www.mtv.com.lb/feed",
                "category": "سياسة",
                "website": "https://www.mtv.com.lb"
            },
            # مصادر إضافية موثوقة
            {
                "name": "الشرق الأوسط - لبنان",
                "url": "https://aawsat.com/rss/lebanon",
                "category": "سياسة",
                "website": "https://aawsat.com"
            },
            {
                "name": "الحياة - أخبار لبنان",
                "url": "https://www.alhayat.com/rss/lebanon.xml",
                "category": "سياسة", 
                "website": "https://www.alhayat.com"
            }
        ]
        self.session = None

    async def get_session(self):
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    def is_political_news(self, title: str, description: str) -> bool:
        """تحديد ما إذا كان الخبر سياسياً بناءً على الكلمات المفتاحية"""
        political_keywords = [
            "حكومة", "وزير", "رئيس", "برلمان", "مجلس", "انتخابات", "حزب", "سياسة", "دبلوماسية",
            "ميقاتي", "عون", "بري", "جعجع", "جنبلاط", "الحريري", "فرنجية", "باسيل", "أبو فاعور",
            "حزب الله", "القوات", "التيار", "الكتائب", "المردة", "التقدمي", "المستقبل",
            "مجلس الوزراء", "مجلس النواب", "قصر بعبدا", "بيت الوسط", "عين التينة",
            "دولة", "حكم", "قرار", "قانون", "اتفاق", "معاهدة", "أزمة سياسية", "حل سياسي"
        ]
        
        text = f"{title} {description}".lower()
        return any(keyword in text for keyword in political_keywords)

    async def fetch_newspaper_headlines(self, newspaper: Dict[str, Any]) -> List[Dict[str, Any]]:
        """جلب العناوين من صحيفة واحدة"""
        try:
            session = await self.get_session()
            async with session.get(newspaper["url"]) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch RSS from {newspaper['name']}: {response.status}")
                    # محاولة RSS بديل أو scraping مباشر
                    return await self.fallback_scraping(newspaper)
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                headlines = []
                for entry in feed.entries[:15]:  # أخذ آخر 15 عنوان
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
                        
                        # فلترة الأخبار السياسية فقط
                        if self.is_political_news(title, description):
                            # جلب الصورة إذا وجدت
                            image_url = None
                            if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                                image_url = entry.media_thumbnail[0].get('url')
                            elif hasattr(entry, 'enclosures') and entry.enclosures:
                                for enclosure in entry.enclosures:
                                    if enclosure.type.startswith('image/'):
                                        image_url = enclosure.href
                                        break

                            headlines.append({
                                'title': title.strip(),
                                'description': description.strip()[:300] if description else "",  # قطع الوصف عند 300 حرف
                                'source': newspaper["name"],
                                'published_at': published_at,
                                'category': newspaper["category"],
                                'url': entry.get('link', ''),
                                'image_url': image_url,
                                'website': newspaper["website"]
                            })
                    except Exception as e:
                        logger.error(f"Error processing entry from {newspaper['name']}: {str(e)}")
                        continue

                logger.info(f"Fetched {len(headlines)} political headlines from {newspaper['name']}")
                return headlines

        except Exception as e:
            logger.error(f"Error fetching RSS from {newspaper['name']}: {str(e)}")
            return await self.fallback_scraping(newspaper)

    async def fallback_scraping(self, newspaper: Dict[str, Any]) -> List[Dict[str, Any]]:
        """طريقة بديلة لجلب الأخبار في حال فشل RSS"""
        try:
            # محاولة URLs بديلة شائعة للـ RSS
            alternative_urls = [
                f"{newspaper['website']}/feed",
                f"{newspaper['website']}/rss",
                f"{newspaper['website']}/feed.xml",
                f"{newspaper['website']}/rss.xml",
                f"{newspaper['website']}/feeds/all.xml"
            ]
            
            session = await self.get_session()
            for alt_url in alternative_urls:
                try:
                    async with session.get(alt_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            feed = feedparser.parse(content)
                            if feed.entries:
                                logger.info(f"Alternative RSS found for {newspaper['name']}: {alt_url}")
                                # استخدام نفس المنطق كالطريقة الأساسية
                                headlines = []
                                for entry in feed.entries[:10]:
                                    title = re.sub(r'<[^>]+>', '', entry.get('title', ''))
                                    description = re.sub(r'<[^>]+>', '', entry.get('summary', ''))
                                    
                                    if self.is_political_news(title, description):
                                        headlines.append({
                                            'title': title.strip(),
                                            'description': description.strip()[:300],
                                            'source': newspaper["name"],
                                            'published_at': datetime.now(),
                                            'category': newspaper["category"],
                                            'url': entry.get('link', ''),
                                            'image_url': None,
                                            'website': newspaper["website"]
                                        })
                                return headlines
                except:
                    continue
            
            # إذا فشل كل شيء، إرجاع عناوين وهمية للاختبار
            logger.warning(f"All methods failed for {newspaper['name']}, returning placeholder")
            return [{
                'title': f"لا يمكن جلب الأخبار من {newspaper['name']} حالياً",
                'description': "يرجى المحاولة لاحقاً أو زيارة الموقع مباشرة",
                'source': newspaper["name"],
                'published_at': datetime.now(),
                'category': newspaper["category"],
                'url': newspaper["website"],
                'image_url': None,
                'website': newspaper["website"]
            }]
            
        except Exception as e:
            logger.error(f"Fallback scraping failed for {newspaper['name']}: {str(e)}")
            return []

    async def fetch_all_lebanon_headlines(self) -> Dict[str, List[Dict[str, Any]]]:
        """جلب جميع العناوين السياسية من الصحف اللبنانية"""
        tasks = []
        for newspaper in self.lebanon_newspapers:
            tasks.append(self.fetch_newspaper_headlines(newspaper))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        organized_headlines = {}
        for i, result in enumerate(results):
            newspaper_name = self.lebanon_newspapers[i]["name"]
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch from {newspaper_name}: {result}")
                organized_headlines[newspaper_name] = []
            else:
                # ترتيب حسب التاريخ (الأحدث أولاً)
                sorted_headlines = sorted(result, key=lambda x: x['published_at'], reverse=True)
                organized_headlines[newspaper_name] = sorted_headlines[:10]  # أقصى 10 عناوين لكل صحيفة
        
        logger.info(f"Fetched headlines from {len(organized_headlines)} Lebanese newspapers")
        return organized_headlines

    async def close(self):
        """إغلاق الجلسة"""
        if self.session:
            await self.session.close()
            self.session = None