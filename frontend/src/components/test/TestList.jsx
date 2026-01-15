import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import testService from '../../services/testService';
import useAuthStore from '../../store/authStore';
import {
  FileText,
  Clock,
  Target,
  Users,
  Plus,
  Search,
  Filter,
  Trash2,
  Edit,
  Eye,
  PlayCircle,
} from 'lucide-react';

const TestList = () => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showPublishedOnly, setShowPublishedOnly] = useState(false);
  const [showMyTests, setShowMyTests] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const limit = 20;

  const { user } = useAuthStore();
  const navigate = useNavigate();

  const isTeacherOrAdmin = ['teacher', 'admin'].includes(user?.role);

  useEffect(() => {
    loadTests();
  }, [search, showPublishedOnly, showMyTests, page]);

  const loadTests = async () => {
    setLoading(true);
    try {
      const data = await testService.getTests({
        skip: page * limit,
        limit,
        search,
        publishedOnly: showPublishedOnly,
        myTests: showMyTests,
      });
      setTests(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to load tests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (testId) => {
    if (!confirm('Вы уверены, что хотите удалить этот тест?')) return;

    try {
      await testService.deleteTest(testId);
      loadTests();
    } catch (error) {
      alert('Ошибка при удалении теста');
    }
  };

  const handlePublishToggle = async (testId, currentStatus) => {
    try {
      await testService.publishTest(testId, !currentStatus);
      loadTests();
    } catch (error) {
      alert(error.response?.data?.detail || 'Ошибка при изменении статуса');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Тесты</h2>
          <p className="text-sm text-gray-600 mt-1">
            Всего тестов: {total}
          </p>
        </div>
        {isTeacherOrAdmin && (
          <button
            onClick={() => navigate('/admin/tests/create')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <Plus className="w-4 h-4" />
            Создать тест
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Поиск по названию или описанию..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Filter toggles */}
        <div className="flex gap-4 flex-wrap">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={showPublishedOnly}
              onChange={(e) => {
                setShowPublishedOnly(e.target.checked);
                setPage(0);
              }}
              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">
              Только опубликованные
            </span>
          </label>

          {isTeacherOrAdmin && (
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showMyTests}
                onChange={(e) => {
                  setShowMyTests(e.target.checked);
                  setPage(0);
                }}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Только мои тесты</span>
            </label>
          )}
        </div>
      </div>

      {/* Test List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : tests.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Тесты не найдены</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {tests.map((test) => (
            <div
              key={test.id}
              className="bg-white rounded-lg shadow hover:shadow-md transition p-6"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  {/* Title and status */}
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">
                      {test.title}
                    </h3>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${testService.getStatusColor(
                        test.is_published
                      )}`}
                    >
                      {testService.getStatusText(test.is_published)}
                    </span>
                  </div>

                  {/* Description */}
                  {test.description && (
                    <p className="text-gray-600 mb-4">{test.description}</p>
                  )}

                  {/* Info */}
                  <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      {test.questions_count} вопросов
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      {testService.formatTime(test.time_limit)}
                    </div>
                    <div className="flex items-center gap-2">
                      <Target className="w-4 h-4" />
                      Проходной балл: {test.passing_score}%
                    </div>
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      Автор: {test.creator_name}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 ml-4">
                  {user?.role === 'student' && test.is_published ? (
                    <button
                      onClick={() => navigate(`/tests/${test.id}/take`)}
                      className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition"
                      title="Пройти тест"
                    >
                      <PlayCircle className="w-5 h-5" />
                    </button>
                  ) : (
                    <>
                      <button
                        onClick={() => navigate(`/tests/${test.id}`)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                        title="Просмотр"
                      >
                        <Eye className="w-5 h-5" />
                      </button>
                      {isTeacherOrAdmin && (
                        <>
                          <button
                            onClick={() =>
                              navigate(`/admin/tests/${test.id}/edit`)
                            }
                            className="p-2 text-gray-600 hover:bg-gray-50 rounded-lg transition"
                            title="Редактировать"
                          >
                            <Edit className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() =>
                              handlePublishToggle(test.id, test.is_published)
                            }
                            className={`p-2 rounded-lg transition ${
                              test.is_published
                                ? 'text-orange-600 hover:bg-orange-50'
                                : 'text-green-600 hover:bg-green-50'
                            }`}
                            title={
                              test.is_published
                                ? 'Снять с публикации'
                                : 'Опубликовать'
                            }
                          >
                            {test.is_published ? '📥' : '📤'}
                          </button>
                          <button
                            onClick={() => handleDelete(test.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                            title="Удалить"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > limit && (
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Назад
          </button>
          <span className="px-4 py-2 text-gray-600">
            Страница {page + 1} из {Math.ceil(total / limit)}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={(page + 1) * limit >= total}
            className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Вперед
          </button>
        </div>
      )}
    </div>
  );
};

export default TestList;