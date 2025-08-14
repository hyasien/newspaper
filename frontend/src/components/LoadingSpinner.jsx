import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ message = "جاري تحميل الأخبار العاجلة..." }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-3" />
      <p className="text-gray-600 text-lg">{message}</p>
    </div>
  );
};

export default LoadingSpinner;