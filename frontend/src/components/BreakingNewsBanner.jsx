import React, { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';

const BreakingNewsBanner = ({ breakingNews }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (breakingNews.length > 1) {
      const interval = setInterval(() => {
        setCurrentIndex((prev) => (prev + 1) % breakingNews.length);
      }, 4000);
      return () => clearInterval(interval);
    }
  }, [breakingNews.length]);

  if (breakingNews.length === 0) return null;

  return (
    <div className="bg-gradient-to-r from-red-600 to-red-700 text-white p-4 mb-6 rounded-lg shadow-lg">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 flex-shrink-0">
          <AlertTriangle className="w-5 h-5 animate-pulse" />
          <span className="font-bold text-sm bg-white text-red-600 px-2 py-1 rounded">
            عاجل
          </span>
        </div>
        <div className="flex-1 overflow-hidden">
          <p className="text-sm font-medium animate-fadeIn">
            {breakingNews[currentIndex]?.title}
          </p>
        </div>
        {breakingNews.length > 1 && (
          <div className="flex gap-1">
            {breakingNews.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  index === currentIndex ? 'bg-white' : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BreakingNewsBanner;