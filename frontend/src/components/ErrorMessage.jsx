import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';

const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 bg-red-50 rounded-lg border border-red-200">
      <AlertTriangle className="w-12 h-12 text-red-500 mb-3" />
      <h3 className="text-lg font-semibold text-red-800 mb-2">حدث خطأ</h3>
      <p className="text-red-600 text-center mb-4 max-w-md">{message}</p>
      {onRetry && (
        <Button 
          onClick={onRetry}
          variant="outline"
          className="flex items-center gap-2 border-red-300 text-red-700 hover:bg-red-100"
        >
          <RefreshCw className="w-4 h-4" />
          إعادة المحاولة
        </Button>
      )}
    </div>
  );
};

export default ErrorMessage;