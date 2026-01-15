import { create } from 'zustand';
import authService from '../services/authService';

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  // Инициализация - проверка токена и загрузка пользователя
  initialize: async () => {
    set({ isLoading: true });
    
    if (authService.isAuthenticated()) {
      try {
        const user = await authService.getCurrentUser();
        set({ user, isAuthenticated: true, isLoading: false });
      } catch (error) {
        set({ user: null, isAuthenticated: false, isLoading: false });
        authService.logout();
      }
    } else {
      set({ isLoading: false });
    }
  },

  // Вход
  login: async (username, password) => {
    await authService.login(username, password);
    const user = await authService.getCurrentUser();
    set({ user, isAuthenticated: true });
    return user;
  },

  // Выход
  logout: () => {
    authService.logout();
    set({ user: null, isAuthenticated: false });
  },

  // Регистрация
  register: async (userData) => {
    const user = await authService.register(userData);
    return user;
  },

  // Обновление данных пользователя
  updateUser: (userData) => {
    set((state) => ({
      user: { ...state.user, ...userData },
    }));
  },
}));

export default useAuthStore;