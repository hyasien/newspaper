// Mock data for Arabic breaking news
export const mockBreakingNews = [
  {
    id: 1,
    title: "عاجل: اتفاقية تجارية جديدة بين الدول العربية",
    description: "وقعت عدة دول عربية على اتفاقية تجارية جديدة تهدف إلى تعزيز التبادل التجاري وتقوية الاقتصاد العربي المشترك",
    source: "الجزيرة",
    publishedAt: "2025-01-27T10:30:00Z",
    category: "اقتصاد",
    isBreaking: true
  },
  {
    id: 2,
    title: "تطورات هامة في قمة المناخ العالمية",
    description: "شهدت قمة المناخ العالمية اليوم تطورات هامة حول التزامات الدول بخفض الانبعاثات الكربونية والاستثمار في الطاقة المتجددة",
    source: "العربية",
    publishedAt: "2025-01-27T09:15:00Z",
    category: "بيئة",
    isBreaking: true
  },
  {
    id: 3,
    title: "إنجاز علمي: اكتشاف جديد في مجال الطب",
    description: "تمكن فريق من الباحثين العرب من اكتشاف علاج جديد لمرض نادر، مما يفتح آفاق جديدة في مجال الطب الحديث",
    source: "سكاي نيوز عربية",
    publishedAt: "2025-01-27T08:45:00Z",
    category: "علوم",
    isBreaking: false
  },
  {
    id: 4,
    title: "عاجل: انطلاق مؤتمر التكنولوجيا العربي",
    description: "انطلق اليوم المؤتمر السنوي للتكنولوجيا العربي بحضور خبراء ومختصين من جميع أنحاء المنطقة لمناقشة أحدث التطورات التقنية",
    source: "تك عرب",
    publishedAt: "2025-01-27T07:20:00Z",
    category: "تكنولوجيا",
    isBreaking: true
  },
  {
    id: 5,
    title: "تحديث: نتائج البطولة الرياضية العربية",
    description: "شهدت البطولة الرياضية العربية منافسات قوية اليوم مع تحقيق عدة أرقام قياسية جديدة في مختلف الألعاب الرياضية",
    source: "الرياضية",
    publishedAt: "2025-01-27T06:10:00Z",
    category: "رياضة",
    isBreaking: false
  }
];

export const addNewBreakingNews = (news) => {
  const newNews = {
    id: Date.now(),
    ...news,
    publishedAt: new Date().toISOString(),
    isBreaking: true
  };
  mockBreakingNews.unshift(newNews);
  return newNews;
};