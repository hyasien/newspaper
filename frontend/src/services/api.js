import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// إنشاء instance لـ axios مع إعدادات افتراضية
const apiClient = axios.create({
  baseURL: API,
  timeout: 30000, // 30 ثانية
  headers: {
    'Content-Type': 'application/json',
  }
});

// معالج الأخطاء
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// وظائف API
export const newsAPI = {
  // جلب الأخبار العاجلة
  getBreakingNews: async () => {
    try {
      const response = await apiClient.get('/news/breaking');
      return response.data;
    } catch (error) {
      throw new Error('فشل في جلب الأخبار العاجلة: ' + (error.response?.data?.detail || error.message));
    }
  },

  // تحديث الأخبار
  refreshNews: async () => {
    try {
      const response = await apiClient.post('/news/refresh');
      return response.data;
    } catch (error) {
      throw new Error('فشل في تحديث الأخبار: ' + (error.response?.data?.detail || error.message));
    }
  },

  // البحث في الأخبار
  searchNews: async (query, category) => {
    try {
      const params = new URLSearchParams();
      if (query) params.append('q', query);
      if (category && category !== 'الكل') params.append('category', category);
      
      const response = await apiClient.get(`/news/search?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw new Error('فشل في البحث: ' + (error.response?.data?.detail || error.message));
    }
  },

  // فحص حالة الخدمة
  healthCheck: async () => {
    try {
      const response = await apiClient.get('/');
      return response.data;
    } catch (error) {
      throw new Error('الخدمة غير متاحة حالياً');
    }
  }
};

export default apiClient;