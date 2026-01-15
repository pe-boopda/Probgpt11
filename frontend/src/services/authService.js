import api from './api';

const authService = {
  // Регистрация
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  // Вход
  login: async (username, password) => {
    const response = await api.post('/api/auth/login', {
      username,
      password,
    });
    
    const { access_token, refresh_token } = response.data;
    
    // Сохранение токенов
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    return response.data;
  },

  // Выход
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  // Получение текущего пользователя
  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  // Проверка авторизации
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  // Смена пароля
  changePassword: async (oldPassword, newPassword) => {
    const response = await api.post('/api/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};

export default authService;