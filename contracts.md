# عقود API لتطبيق الأخبار العاجلة

## نظرة عامة
هذا المستند يحدد عقود API وخطة التكامل بين الواجهة الأمامية والخلفية لتطبيق الأخبار العاجلة.

## البيانات الوهمية الحالية
- **الملف**: `/frontend/src/mock.js`
- **البيانات**: مصفوفة من الأخبار العربية مع خصائص: id, title, description, source, publishedAt, category, isBreaking

## عقود API المطلوبة

### 1. جلب الأخبار
```
GET /api/news
Response: {
  "news": [
    {
      "id": "string",
      "title": "string",
      "description": "string", 
      "source": "string",
      "publishedAt": "ISO_DATE",
      "category": "string",
      "isBreaking": "boolean",
      "url": "string" (optional),
      "imageUrl": "string" (optional)
    }
  ],
  "total": "number",
  "lastUpdated": "ISO_DATE"
}
```

### 2. جلب الأخبار العاجلة فقط
```
GET /api/news/breaking
Response: {
  "breaking_news": [...same_structure],
  "count": "number"
}
```

### 3. تحديث مصادر RSS
```
POST /api/news/refresh
Response: {
  "success": "boolean",
  "message": "string",
  "updated_count": "number"
}
```

### 4. البحث في الأخبار
```
GET /api/news/search?q={search_term}&category={category}
Response: {
  "results": [...same_structure],
  "count": "number"
}
```

## تكامل مصادر RSS

### مصادر مقترحة:
1. الجزيرة RSS
2. العربية RSS  
3. BBC Arabic RSS
4. Sky News Arabic RSS
5. مصادر محلية

### تنفيذ الباك إند:

1. **نموذج قاعدة البيانات**:
   - جدول `news_articles` لحفظ المقالات
   - جدول `rss_sources` لإدارة مصادر RSS
   - جدول `categories` للتصنيفات

2. **مهام الخلفية**:
   - مهمة دورية لجلب RSS كل 5 دقائق
   - معالج لتحليل XML وحفظ الأخبار الجديدة
   - تصنيف تلقائي للأخبار العاجلة

3. **أوقات التحديث**:
   - تحديث تلقائي كل 5 دقائق
   - إشعارات فورية للأخبار العاجلة
   - آلية cache للأداء المحسن

## تعديلات الواجهة الأمامية المطلوبة:

1. **استبدال البيانات الوهمية**:
   - حذف استيراد `mockBreakingNews` من `mock.js`
   - تحديث hooks لاستخدام API calls
   - إضافة معالجة أخطاء الشبكة

2. **تحسينات إضافية**:
   - Loading states أثناء جلب البيانات
   - Error handling للـ API failures
   - إضافة timestamps حقيقية
   - دعم الصور في المقالات

## API Integration Plan:

1. إنشاء ملف `api.js` للتعامل مع HTTP requests
2. تحديث components لاستخدام real data بدلاً من mock
3. إضافة loading spinners و error states
4. تحسين UX مع toast notifications

## الميزات التقنية:

- **RSS Parsing**: مكتبة `feedparser` أو `rss-parser`
- **Background Jobs**: APScheduler لمهام دورية  
- **Caching**: Redis للأداء المحسن
- **Rate Limiting**: تحديد معدل الطلبات لكل IP
- **Logging**: تتبع طلبات RSS والأخطاء