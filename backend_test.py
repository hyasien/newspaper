#!/usr/bin/env python3
"""
اختبار شامل لتطبيق الأخبار العاجلة العربية
Comprehensive tests for Arabic Breaking News API
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import sys
import os

# إضافة مسار المشروع
sys.path.append('/app/backend')

class BreakingNewsAPITester:
    def __init__(self):
        # استخدام الـ URL من متغيرات البيئة
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    self.base_url = line.split('=')[1].strip()
                    break
        
        self.api_url = f"{self.base_url}/api"
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """إعداد جلسة HTTP"""
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def cleanup(self):
        """تنظيف الموارد"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name, success, details="", response_data=None):
        """تسجيل نتائج الاختبار"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if response_data:
            result["response_sample"] = response_data
        self.test_results.append(result)
        
        status = "✅ نجح" if success else "❌ فشل"
        print(f"{status} - {test_name}")
        if details:
            print(f"   التفاصيل: {details}")
        print()
        
    async def test_health_check(self):
        """اختبار health check endpoint"""
        try:
            async with self.session.get(f"{self.api_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("message") == "Breaking News API is running":
                        self.log_test(
                            "Health Check API", 
                            True, 
                            f"API يعمل بشكل صحيح - الحالة: {data.get('status', 'unknown')}",
                            data
                        )
                        return True
                    else:
                        self.log_test("Health Check API", False, f"رسالة غير متوقعة: {data}")
                        return False
                else:
                    self.log_test("Health Check API", False, f"HTTP Status: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Health Check API", False, f"خطأ في الاتصال: {str(e)}")
            return False
            
    async def test_breaking_news_endpoint(self):
        """اختبار endpoint الأخبار العاجلة الأساسي"""
        try:
            async with self.session.get(f"{self.api_url}/news/breaking") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # التحقق من البنية الأساسية
                    required_fields = ["breaking_news", "count", "last_updated"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test(
                            "Breaking News API - البنية", 
                            False, 
                            f"حقول مفقودة: {missing_fields}"
                        )
                        return False
                    
                    breaking_news = data.get("breaking_news", [])
                    count = data.get("count", 0)
                    
                    # التحقق من تطابق العدد
                    if len(breaking_news) != count:
                        self.log_test(
                            "Breaking News API - العدد", 
                            False, 
                            f"عدم تطابق: العدد المعلن {count} والعدد الفعلي {len(breaking_news)}"
                        )
                        return False
                    
                    # التحقق من وجود أخبار
                    if count == 0:
                        self.log_test(
                            "Breaking News API - المحتوى", 
                            True, 
                            "لا توجد أخبار عاجلة حالياً (هذا طبيعي)"
                        )
                        return True
                    
                    # التحقق من بنية الأخبار
                    sample_news = breaking_news[0]
                    required_news_fields = ["title", "description", "source", "published_at", "category", "is_breaking"]
                    missing_news_fields = [field for field in required_news_fields if field not in sample_news]
                    
                    if missing_news_fields:
                        self.log_test(
                            "Breaking News API - بنية الخبر", 
                            False, 
                            f"حقول مفقودة في الخبر: {missing_news_fields}"
                        )
                        return False
                    
                    # التحقق من أن الأخبار عاجلة فعلاً
                    non_breaking = [news for news in breaking_news if not news.get("is_breaking")]
                    if non_breaking:
                        self.log_test(
                            "Breaking News API - فلترة الأخبار العاجلة", 
                            False, 
                            f"وجدت {len(non_breaking)} أخبار غير عاجلة في النتائج"
                        )
                        return False
                    
                    # التحقق من المصادر العربية
                    arabic_sources = ["الجزيرة", "العربية", "BBC عربي", "سكاي نيوز عربية"]
                    found_sources = list(set([news.get("source") for news in breaking_news]))
                    valid_sources = [source for source in found_sources if source in arabic_sources]
                    
                    if not valid_sources:
                        self.log_test(
                            "Breaking News API - المصادر العربية", 
                            False, 
                            f"لم توجد مصادر عربية معروفة. المصادر الموجودة: {found_sources}"
                        )
                        return False
                    
                    # التحقق من تنسيق التاريخ
                    try:
                        datetime.fromisoformat(sample_news["published_at"].replace('Z', '+00:00'))
                        date_format_valid = True
                    except:
                        date_format_valid = False
                    
                    if not date_format_valid:
                        self.log_test(
                            "Breaking News API - تنسيق التاريخ", 
                            False, 
                            f"تنسيق تاريخ غير صحيح: {sample_news['published_at']}"
                        )
                        return False
                    
                    self.log_test(
                        "Breaking News API - شامل", 
                        True, 
                        f"تم جلب {count} خبر عاجل من المصادر: {', '.join(valid_sources)}",
                        {
                            "sample_news": sample_news,
                            "total_count": count,
                            "sources": found_sources
                        }
                    )
                    return True
                    
                else:
                    self.log_test("Breaking News API", False, f"HTTP Status: {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Breaking News API", False, f"خطأ في الاتصال: {str(e)}")
            return False
            
    async def test_refresh_endpoint(self):
        """اختبار endpoint تحديث الأخبار"""
        try:
            async with self.session.post(f"{self.api_url}/news/refresh") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    required_fields = ["success", "message", "timestamp"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test(
                            "Refresh News API", 
                            False, 
                            f"حقول مفقودة: {missing_fields}"
                        )
                        return False
                    
                    if data.get("success") != True:
                        self.log_test(
                            "Refresh News API", 
                            False, 
                            f"فشل التحديث: {data.get('message')}"
                        )
                        return False
                    
                    self.log_test(
                        "Refresh News API", 
                        True, 
                        f"تم بدء التحديث بنجاح: {data.get('message')}",
                        data
                    )
                    return True
                    
                else:
                    self.log_test("Refresh News API", False, f"HTTP Status: {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Refresh News API", False, f"خطأ في الاتصال: {str(e)}")
            return False
            
    async def test_search_endpoint(self):
        """اختبار endpoint البحث والفلترة"""
        test_cases = [
            {
                "name": "البحث بكلمة 'سودان'",
                "params": {"q": "سودان"},
                "expected_behavior": "should_filter_by_keyword"
            },
            {
                "name": "الفلترة بفئة 'سياسة'",
                "params": {"category": "سياسة"},
                "expected_behavior": "should_filter_by_category"
            },
            {
                "name": "البحث الفارغ",
                "params": {},
                "expected_behavior": "should_return_all"
            },
            {
                "name": "البحث المركب",
                "params": {"q": "رئيس", "category": "سياسة"},
                "expected_behavior": "should_filter_both"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                params = test_case["params"]
                url = f"{self.api_url}/news/search"
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        required_fields = ["results", "count", "search_query", "category"]
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if missing_fields:
                            self.log_test(
                                f"Search API - {test_case['name']}", 
                                False, 
                                f"حقول مفقودة: {missing_fields}"
                            )
                            all_passed = False
                            continue
                        
                        results = data.get("results", [])
                        count = data.get("count", 0)
                        
                        # التحقق من تطابق العدد
                        if len(results) != count:
                            self.log_test(
                                f"Search API - {test_case['name']}", 
                                False, 
                                f"عدم تطابق العدد: المعلن {count} والفعلي {len(results)}"
                            )
                            all_passed = False
                            continue
                        
                        # التحقق من صحة الفلترة
                        if test_case["expected_behavior"] == "should_filter_by_keyword" and params.get("q"):
                            keyword = params["q"].lower()
                            invalid_results = [
                                r for r in results 
                                if keyword not in r.get("title", "").lower() and keyword not in r.get("description", "").lower()
                            ]
                            if invalid_results:
                                self.log_test(
                                    f"Search API - {test_case['name']}", 
                                    False, 
                                    f"وجدت {len(invalid_results)} نتائج لا تحتوي على الكلمة المفتاحية"
                                )
                                all_passed = False
                                continue
                        
                        elif test_case["expected_behavior"] == "should_filter_by_category" and params.get("category"):
                            category = params["category"]
                            invalid_results = [r for r in results if r.get("category") != category]
                            if invalid_results:
                                self.log_test(
                                    f"Search API - {test_case['name']}", 
                                    False, 
                                    f"وجدت {len(invalid_results)} نتائج من فئات أخرى"
                                )
                                all_passed = False
                                continue
                        
                        self.log_test(
                            f"Search API - {test_case['name']}", 
                            True, 
                            f"تم العثور على {count} نتيجة",
                            {
                                "params": params,
                                "count": count,
                                "sample_result": results[0] if results else None
                            }
                        )
                        
                    else:
                        self.log_test(
                            f"Search API - {test_case['name']}", 
                            False, 
                            f"HTTP Status: {response.status}"
                        )
                        all_passed = False
                        
            except Exception as e:
                self.log_test(
                    f"Search API - {test_case['name']}", 
                    False, 
                    f"خطأ في الاتصال: {str(e)}"
                )
                all_passed = False
        
        return all_passed
        
    async def test_error_handling(self):
        """اختبار التعامل مع الأخطاء"""
        try:
            # اختبار endpoint غير موجود
            async with self.session.get(f"{self.api_url}/news/nonexistent") as response:
                if response.status == 404:
                    self.log_test(
                        "Error Handling - 404", 
                        True, 
                        "تم التعامل مع الـ endpoint غير الموجود بشكل صحيح"
                    )
                    return True
                else:
                    self.log_test(
                        "Error Handling - 404", 
                        False, 
                        f"متوقع 404 لكن حصلت على: {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Error Handling", False, f"خطأ غير متوقع: {str(e)}")
            return False
            
    async def test_performance_and_timeout(self):
        """اختبار الأداء والـ timeout"""
        try:
            start_time = datetime.now()
            
            async with self.session.get(f"{self.api_url}/news/breaking") as response:
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                if response.status == 200:
                    if response_time < 30:  # أقل من 30 ثانية
                        self.log_test(
                            "Performance Test", 
                            True, 
                            f"وقت الاستجابة: {response_time:.2f} ثانية"
                        )
                        return True
                    else:
                        self.log_test(
                            "Performance Test", 
                            False, 
                            f"وقت الاستجابة بطيء: {response_time:.2f} ثانية"
                        )
                        return False
                else:
                    self.log_test("Performance Test", False, f"HTTP Status: {response.status}")
                    return False
                    
        except asyncio.TimeoutError:
            self.log_test("Performance Test", False, "انتهت مهلة الاتصال (timeout)")
            return False
        except Exception as e:
            self.log_test("Performance Test", False, f"خطأ في اختبار الأداء: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🚀 بدء اختبار تطبيق الأخبار العاجلة العربية")
        print("=" * 60)
        print(f"🌐 API URL: {self.api_url}")
        print("=" * 60)
        print()
        
        await self.setup()
        
        # تشغيل الاختبارات بالترتيب
        tests = [
            ("Health Check", self.test_health_check),
            ("Breaking News API", self.test_breaking_news_endpoint),
            ("Refresh News API", self.test_refresh_endpoint),
            ("Search & Filter API", self.test_search_endpoint),
            ("Error Handling", self.test_error_handling),
            ("Performance Test", self.test_performance_and_timeout)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"🧪 تشغيل اختبار: {test_name}")
            print("-" * 40)
            
            try:
                result = await test_func()
                if result:
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"خطأ غير متوقع: {str(e)}")
            
            print()
        
        await self.cleanup()
        
        # تقرير النتائج النهائية
        print("=" * 60)
        print("📊 تقرير النتائج النهائية")
        print("=" * 60)
        print(f"✅ اختبارات نجحت: {passed_tests}")
        print(f"❌ اختبارات فشلت: {total_tests - passed_tests}")
        print(f"📈 معدل النجاح: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # تفاصيل الاختبارات الفاشلة
        failed_tests = [test for test in self.test_results if not test["success"]]
        if failed_tests:
            print("❌ الاختبارات الفاشلة:")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
            print()
        
        # حفظ النتائج في ملف
        with open('/app/test_results_backend.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 تم حفظ النتائج التفصيلية في: /app/test_results_backend.json")
        print()
        
        return passed_tests == total_tests

async def main():
    """الدالة الرئيسية"""
    tester = BreakingNewsAPITester()
    success = await tester.run_all_tests()
    
    if success:
        print("🎉 جميع الاختبارات نجحت!")
        return 0
    else:
        print("⚠️  بعض الاختبارات فشلت. راجع التفاصيل أعلاه.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)