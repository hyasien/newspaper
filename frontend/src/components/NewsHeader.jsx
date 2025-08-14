import React from 'react';
import { Button } from './ui/button';
import { RefreshCw, Filter, Search } from 'lucide-react';
import { Input } from './ui/input';

const NewsHeader = ({ onRefresh, isRefreshing, searchTerm, onSearchChange, selectedCategory, onCategoryChange }) => {
  const categories = ['الكل', 'اقتصاد', 'بيئة', 'علوم', 'تكنولوجيا', 'رياضة', 'سياسة'];

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            الأخبار العاجلة
          </h1>
          <p className="text-gray-600">
            آخر الأخبار والتحديثات العاجلة من مصادر موثوقة
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3 lg:w-auto w-full">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              type="text"
              placeholder="ابحث في الأخبار..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pr-10 w-full sm:w-64"
            />
          </div>
          
          <Button
            onClick={onRefresh}
            disabled={isRefreshing}
            variant="outline"
            className="flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            تحديث
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mt-4">
        {categories.map((category) => (
          <Button
            key={category}
            variant={selectedCategory === category ? 'default' : 'outline'}
            size="sm"
            onClick={() => onCategoryChange(category)}
            className="text-sm"
          >
            {category}
          </Button>
        ))}
      </div>
    </div>
  );
};

export default NewsHeader;