import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import useAuthStore from './store/authStore';

// Pages
import LoginPage from './pages/LoginPage';
import StudentDashboard from './pages/StudentDashboard';
import AdminDashboard from './pages/AdminDashboard';

// Components
import ProtectedRoute from './components/common/ProtectedRoute';
import LoadingScreen from './components/common/LoadingScreen';

function App() {
  const { initialize, isLoading, isAuthenticated } = useAuthStore();

  useEffect(() => {
    initialize();
  }, [initialize]);

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Публичные маршруты */}
        <Route
          path="/login"
          element={
            isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage />
          }
        />

        {/* Защищённые маршруты для студентов */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <StudentDashboard />
            </ProtectedRoute>
          }
        />

        {/* Защищённые маршруты для админов/преподавателей */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute roles={['admin', 'teacher']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        {/* Перенаправление */}
        <Route
          path="/"
          element={
            <Navigate to={isAuthenticated ? '/dashboard' : '/login'} />
          }
        />

        {/* 404 */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;