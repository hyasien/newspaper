import React, { useState, useEffect, useCallback } from 'react';
import { newsAPI } from '../services/api';
import { Card, CardContent, CardHeader } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Separator } from '../components/ui/separator';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useToast } from '../hooks/use-toast';
import { Clock, ExternalLink, RefreshCw, Newspaper, Globe } from 'lucide-react';

const LebanonNews = () => {
  const [newspapersData, setNewspapersData] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [totalHeadlines, setTotalHeadlines] = useState(0);
  const { toast } = useToast();

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffHours > 24) {
      return date.toLocaleDateString('ar-EG', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } else if (diffHours > 0) {
      return `منذ ${diffHours} ساعة`;
    } else if (diffMins > 0) {
      return `منذ ${diffMins} دقيقة`;
    } else {
      return 'الآن';
    }
  };

  // جلب عناوين الصحف اللبنانية
  const fetchLebanonHeadlines = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) setIsLoading(true);
      setError(null);
      
      const response = await newsAPI.getLebanonHeadlines();
      setNewspapersData(response.newspapers || {});
      setTotalHeadlines(response.total_headlines || 0);
      setLastUpdated(new Date(response.last_updated));
      
      if (!showLoading && response.total_headlines > 0) {
        toast({
          title: "تم تحديث العناوين",
          description: `تم جلب ${response.total_headlines} عنوان من ${response.total_newspapers} صحيفة لبنانية`,
          duration: 3000,
        });
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching Lebanon headlines:', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [toast]);

  // تحديث العناوين
  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchLebanonHeadlines(false);
  };

  // إعادة المحاولة عند حدوث خطأ
  const handleRetry = () => {
    fetchLebanonHeadlines(true);
  };

  // تحميل العناوين عند بدء التطبيق
  useEffect(() => {
    fetchLebanonHeadlines(true);
  }, [fetchLebanonHeadlines]);

  // تحديث تلقائي كل 10 دقائق
  useEffect(() => {
    const interval = setInterval(() => {
      fetchLebanonHeadlines(false);
    }, 600000); // 10 دقائق
    
    return () => clearInterval(interval);
  }, [fetchLebanonHeadlines]);

  const handleExternalLink = (url, newspaperWebsite) => {
    const finalUrl = url || newspaperWebsite;
    if (finalUrl) {
      window.open(finalUrl, '_blank', 'noopener,noreferrer');
    }
  };

  if (isLoading && Object.keys(newspapersData).length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="container mx-auto px-4 py-6 max-w-7xl">
          <LoadingSpinner message="جاري تحميل عناوين الصحف اللبنانية..." />
        </div>
      </div>
    );
  }

  if (error && Object.keys(newspapersData).length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="container mx-auto px-4 py-6 max-w-7xl">
          <ErrorMessage message={error} onRetry={handleRetry} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-6 max-w-7xl">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <Newspaper className="w-8 h-8 text-green-600" />
                <h1 className="text-3xl font-bold text-gray-900">
                  عناوين الصحف اللبنانية
                </h1>
              </div>
              <div className="flex items-center gap-4">
                <p className="text-gray-600">
                  أبرز العناوين السياسية اليومية
                </p>
                {lastUpdated && (
                  <div className="flex items-center gap-1 text-sm text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span>آخر تحديث: {formatTime(lastUpdated)}</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="text-sm text-gray-600 text-center">
                <div className="font-semibold text-lg text-green-600">{totalHeadlines}</div>
                <div>عنوان إجمالي</div>
              </div>
              <Separator orientation="vertical" className="h-12" />
              <div className="text-sm text-gray-600 text-center">
                <div className="font-semibold text-lg text-blue-600">{Object.keys(newspapersData).length}</div>
                <div>صحيفة</div>
              </div>
              <Separator orientation="vertical" className="h-12" />
              <Button
                onClick={handleRefresh}
                disabled={isRefreshing}
                variant="outline"
                className="flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                {isRefreshing ? 'جاري التحديث...' : 'تحديث'}
              </Button>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-4">
            <ErrorMessage 
              message={`تحذير: ${error}`} 
              onRetry={() => fetchLebanonHeadlines(false)} 
            />
          </div>
        )}

        {/* Newspapers Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {Object.entries(newspapersData).map(([newspaperName, data]) => (
            <Card key={newspaperName} className="bg-white shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader className="border-b border-gray-100 pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Globe className="w-6 h-6 text-blue-600" />
                    <h2 className="text-xl font-bold text-gray-900">{newspaperName}</h2>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="bg-green-100 text-green-800 border-green-200">
                      {data.count} عنوان
                    </Badge>
                    {data.website && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleExternalLink(null, data.website)}
                        className="p-2"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="p-0">
                <div className="max-h-96 overflow-y-auto">
                  {data.headlines && data.headlines.length > 0 ? (
                    data.headlines.map((headline, index) => (
                      <div
                        key={index}
                        className="p-4 border-b border-gray-50 hover:bg-gray-50 cursor-pointer transition-colors duration-200"
                        onClick={() => handleExternalLink(headline.url, data.website)}
                      >
                        <h3 className="text-sm font-semibold text-gray-900 mb-2 leading-relaxed hover:text-blue-600 transition-colors">
                          {headline.title}
                        </h3>
                        {headline.description && (
                          <p className="text-xs text-gray-600 mb-2 line-clamp-2">
                            {headline.description}
                          </p>
                        )}
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>{formatTime(headline.published_at)}</span>
                          <ExternalLink className="w-3 h-3" />
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-4 text-center text-gray-500">
                      <Newspaper className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p>لا توجد عناوين متاحة حالياً</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {Object.keys(newspapersData).length === 0 && !isLoading && (
          <div className="text-center py-12">
            <Newspaper className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-500 text-lg">لا توجد صحف متاحة حالياً</p>
          </div>
        )}

        {/* Footer Info */}
        {totalHeadlines > 0 && (
          <div className="text-center mt-8 p-4 bg-white rounded-lg shadow-sm">
            <p className="text-gray-500 text-sm">
              تم عرض {totalHeadlines} عنوان سياسي من {Object.keys(newspapersData).length} صحيفة لبنانية
              {lastUpdated && (
                <span className="block mt-1">
                  آخر تحديث: {lastUpdated.toLocaleString('ar-EG')}
                </span>
              )}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LebanonNews;