import React, { useState, useEffect, useCallback } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import { newsAPI } from "./services/api";
import NewsCard from "./components/NewsCard";
import NewsHeader from "./components/NewsHeader";
import BreakingNewsBanner from "./components/BreakingNewsBanner";
import LoadingSpinner from "./components/LoadingSpinner";
import ErrorMessage from "./components/ErrorMessage";
import { Toaster } from "./components/ui/toaster";
import { useToast } from "./hooks/use-toast";
import LebanonNews from "./pages/LebanonNews";
import { Button } from "./components/ui/button";
import { Globe, Zap } from "lucide-react";

// Navigation Component
const Navigation = () => {
  const location = useLocation();
  
  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-3 max-w-7xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Globe className="w-6 h-6 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-900">مركز الأخبار العربي</h1>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/">
              <Button 
                variant={location.pathname === '/' ? 'default' : 'ghost'}
                className="flex items-center gap-2"
              >
                <Zap className="w-4 h-4" />
                الأخبار العاجلة
              </Button>
            </Link>
            <Link to="/lebanon">
              <Button 
                variant={location.pathname === '/lebanon' ? 'default' : 'ghost'}
                className="flex items-center gap-2"
              >
                <Globe className="w-4 h-4" />
                الصحف اللبنانية
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

const Home = () => {
  const [news, setNews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("الكل");
  const [lastUpdated, setLastUpdated] = useState(null);
  const { toast } = useToast();

  // جلب الأخبار العاجلة
  const fetchBreakingNews = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) setIsLoading(true);
      setError(null);
      
      const response = await newsAPI.getBreakingNews();
      setNews(response.breaking_news || []);
      setLastUpdated(new Date(response.last_updated));
      
      if (!showLoading && response.breaking_news?.length > 0) {
        toast({
          title: "تم تحديث الأخبار",
          description: `تم جلب ${response.breaking_news.length} خبر عاجل`,
          duration: 3000,
        });
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching breaking news:', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [toast]);

  // البحث في الأخبار
  const searchNews = useCallback(async (query, category) => {
    try {
      if (!query && category === "الكل") {
        // إذا لم يكن هناك بحث أو فلترة، اعرض جميع الأخبار
        return;
      }
      
      const response = await newsAPI.searchNews(query, category);
      return response.results || [];
    } catch (err) {
      console.error('Error searching news:', err);
      toast({
        title: "خطأ في البحث",
        description: err.message,
        variant: "destructive",
        duration: 5000,
      });
      return news; // إرجاع الأخبار الحالية في حالة الخطأ
    }
  }, [news, toast]);

  // فلترة الأخبار محلياً
  const filteredNews = React.useMemo(() => {
    let filtered = news;
    
    if (searchTerm) {
      filtered = filtered.filter((item) =>
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (selectedCategory !== "الكل") {
      filtered = filtered.filter((item) => item.category === selectedCategory);
    }
    
    return filtered;
  }, [news, searchTerm, selectedCategory]);

  // تحديث الأخبار
  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchBreakingNews(false);
  };

  // إعادة المحاولة عند حدوث خطأ
  const handleRetry = () => {
    fetchBreakingNews(true);
  };

  // تحميل الأخبار عند بدء التطبيق
  useEffect(() => {
    fetchBreakingNews(true);
  }, [fetchBreakingNews]);

  // تحديث تلقائي كل 5 دقائق
  useEffect(() => {
    const interval = setInterval(() => {
      fetchBreakingNews(false);
    }, 300000); // 5 دقائق
    
    return () => clearInterval(interval);
  }, [fetchBreakingNews]);

  // جميع الأخبار عاجلة (لأننا نجلب العاجل فقط)
  const breakingNews = filteredNews;

  if (isLoading && news.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error && news.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <ErrorMessage message={error} onRetry={handleRetry} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-6 max-w-4xl">
        <NewsHeader
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          lastUpdated={lastUpdated}
        />
        
        <BreakingNewsBanner breakingNews={breakingNews.slice(0, 3)} />
        
        {error && (
          <div className="mb-4">
            <ErrorMessage 
              message={`تحذير: ${error}`} 
              onRetry={() => fetchBreakingNews(false)} 
            />
          </div>
        )}
        
        <div className="grid gap-4">
          {filteredNews.length > 0 ? (
            filteredNews.map((newsItem) => (
              <div key={newsItem.id} className="w-full">
                <NewsCard news={newsItem} />
              </div>
            ))
          ) : (
            <div className="text-center py-12">
              {searchTerm || selectedCategory !== "الكل" ? (
                <p className="text-gray-500 text-lg">لا توجد أخبار تطابق البحث</p>
              ) : (
                <p className="text-gray-500 text-lg">لا توجد أخبار عاجلة متاحة حالياً</p>
              )}
            </div>
          )}
        </div>
        
        {filteredNews.length > 0 && (
          <div className="text-center mt-8">
            <p className="text-gray-500 text-sm">
              تم عرض {filteredNews.length} خبر عاجل من أصل {news.length}
              {lastUpdated && (
                <span className="block mt-1">
                  آخر تحديث: {lastUpdated.toLocaleString('ar-EG')}
                </span>
              )}
            </p>
          </div>
        )}
      </div>
      <Toaster />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;