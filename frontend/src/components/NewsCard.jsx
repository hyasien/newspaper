import React from 'react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { Clock, ExternalLink, Image } from 'lucide-react';

const NewsCard = ({ news }) => {
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

  const getCategoryColor = (category) => {
    const colors = {
      'اقتصاد': 'bg-blue-100 text-blue-800 border-blue-200',
      'بيئة': 'bg-green-100 text-green-800 border-green-200',
      'علوم': 'bg-purple-100 text-purple-800 border-purple-200',
      'تكنولوجيا': 'bg-gray-100 text-gray-800 border-gray-200',
      'رياضة': 'bg-orange-100 text-orange-800 border-orange-200',
      'سياسة': 'bg-red-100 text-red-800 border-red-200',
      'صحة': 'bg-green-100 text-green-800 border-green-200',
      'عام': 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return colors[category] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const handleExternalLink = () => {
    if (news.url) {
      window.open(news.url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <Card className={`relative mb-4 transition-all duration-300 hover:shadow-lg hover:scale-[1.02] ${
      news.is_breaking ? 'border-r-4 border-r-red-500 bg-red-50/30' : 'border-r-4 border-r-blue-200'
    }`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            {news.is_breaking && (
              <Badge className="mb-2 bg-red-600 text-white animate-pulse">
                عاجل
              </Badge>
            )}
            <h3 className="text-lg font-bold text-gray-900 leading-tight mb-2 hover:text-blue-600 cursor-pointer transition-colors"
                onClick={handleExternalLink}>
              {news.title}
            </h3>
          </div>
          {news.url && (
            <ExternalLink 
              className="w-4 h-4 text-gray-400 hover:text-blue-600 cursor-pointer transition-colors flex-shrink-0" 
              onClick={handleExternalLink}
            />
          )}
        </div>
      </CardHeader>
      <CardContent>
        {news.image_url && (
          <div className="mb-4 overflow-hidden rounded-lg">
            <img 
              src={news.image_url} 
              alt={news.title}
              className="w-full h-48 object-cover hover:scale-105 transition-transform duration-300"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
        )}
        
        <p className="text-gray-700 mb-4 leading-relaxed">
          {news.description}
        </p>
        
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-3">
            <Badge variant="outline" className={getCategoryColor(news.category)}>
              {news.category}
            </Badge>
            <span className="text-sm font-medium text-blue-600">
              {news.source}
            </span>
          </div>
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            <span>{formatTime(news.published_at)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default NewsCard;