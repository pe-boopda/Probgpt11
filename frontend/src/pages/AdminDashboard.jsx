import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import {
  LogOut,
  FileText,
  Users,
  TrendingUp,
  PlusCircle,
} from 'lucide-react';

const AdminDashboard = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Панель администратора
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {user?.full_name} • {user?.role === 'admin' ? 'Администратор' : 'Преподаватель'}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
            >
              <LogOut className="w-4 h-4" />
              Выйти
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600">Тестов</h3>
            <p className="text-2xl font-bold text-gray-900 mt-1">0</p>
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <Users className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600">Студентов</h3>
            <p className="text-2xl font-bold text-gray-900 mt-1">0</p>
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600">
              Пройдено тестов
            </h3>
            <p className="text-2xl font-bold text-gray-900 mt-1">0</p>
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <Users className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
            <h3 className="text-sm font-medium text-gray-600">Групп</h3>
            <p className="text-2xl font-bold text-gray-900 mt-1">0</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <button className="bg-white rounded-xl shadow p-6 hover:shadow-lg transition text-left">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <PlusCircle className="w-8 h-8 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Создать тест
                </h3>
                <p className="text-sm text-gray-600">
                  Создайте новый тест для студентов
                </p>
              </div>
            </div>
          </button>

          <button className="bg-white rounded-xl shadow p-6 hover:shadow-lg transition text-left">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <Users className="w-8 h-8 text-green-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Управление студентами
                </h3>
                <p className="text-sm text-gray-600">
                  Добавить студентов и группы
                </p>
              </div>
            </div>
          </button>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Последние результаты
            </h2>
          </div>
          <div className="p-6">
            <p className="text-gray-500 text-center py-8">
              Пока нет результатов тестирования
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;