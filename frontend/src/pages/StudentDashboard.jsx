import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { LogOut, BookOpen, User, BarChart3 } from 'lucide-react';

const StudentDashboard = () => {
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
                Панель студента
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Добро пожаловать, {user?.full_name}!
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Card 1 */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <BookOpen className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Доступные тесты
            </h3>
            <p className="text-3xl font-bold text-blue-600 mt-2">0</p>
          </div>

          {/* Card 2 */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <BarChart3 className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Пройдено тестов
            </h3>
            <p className="text-3xl font-bold text-green-600 mt-2">0</p>
          </div>

          {/* Card 3 */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <User className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Средний балл
            </h3>
            <p className="text-3xl font-bold text-purple-600 mt-2">-</p>
          </div>
        </div>

        {/* Tests List */}
        <div className="bg-white rounded-xl shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Мои тесты
            </h2>
          </div>
          <div className="p-6">
            <p className="text-gray-500 text-center py-8">
              У вас пока нет доступных тестов
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default StudentDashboard;