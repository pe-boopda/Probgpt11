import { Navigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

const ProtectedRoute = ({ children, roles = [] }) => {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  // Проверка ролей, если указаны
  if (roles.length > 0 && !roles.includes(user?.role)) {
    return <Navigate to="/dashboard" />;
  }

  return children;
};

export default ProtectedRoute;