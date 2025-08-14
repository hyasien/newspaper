import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { mockBreakingNews } from "./mock";
import NewsCard from "./components/NewsCard";
import NewsHeader from "./components/NewsHeader";
import BreakingNewsBanner from "./components/BreakingNewsBanner";
import { Toaster } from "./components/ui/toaster";

const Home = () => {
  const [news, setNews] = useState(mockBreakingNews);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("الكل");

  // Filter news based on search and category
  const filteredNews = news.filter((item) => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "الكل" || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Get breaking news for banner
  const breakingNews = news.filter(item => item.isBreaking);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call delay
    setTimeout(() => {
      // In real implementation, this would fetch from RSS feeds
      const shuffledNews = [...mockBreakingNews].sort(() => Math.random() - 0.5);
      setNews(shuffledNews);
      setIsRefreshing(false);
    }, 1000);
  };

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      handleRefresh();
    }, 300000);
    return () => clearInterval(interval);
  }, []);

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
        />
        
        <BreakingNewsBanner breakingNews={breakingNews} />
        
        <div className="grid gap-4">
          {filteredNews.length > 0 ? (
            filteredNews.map((newsItem) => (
              <div key={newsItem.id} className="w-full">
                <NewsCard news={newsItem} />
              </div>
            ))
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">لا توجد أخبار تطابق البحث</p>
            </div>
          )}
        </div>
        
        {filteredNews.length > 0 && (
          <div className="text-center mt-8">
            <p className="text-gray-500 text-sm">
              تم عرض {filteredNews.length} خبر من أصل {news.length}
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