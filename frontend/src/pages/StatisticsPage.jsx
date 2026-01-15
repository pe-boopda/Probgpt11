import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Users,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  BarChart3,
  Target,
} from 'lucide-react';
import api from '../services/api';
import TestStatsChart from '../components/statistics/TestStatsChart';
import QuestionBreakdown from '../components/statistics/QuestionBreakdown';
import Leaderboard from '../components/statistics/Leaderboard';

const StatisticsPage = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [questionStats, setQuestionStats] = useState(null);
  const [test, setTest] = useState(null);

  useEffect(() => {
    loadStatistics();
  }, [testId]);

  const loadStatistics = async () => {
    setLoading(true);
    try {
      const [statsRes, questionsRes, testRes] = await Promise.all([
        api.get(`/api/statistics/tests/${testId}`),
        api.get(`/api/statistics/tests/${testId}/questions`),
        api.get(`/api/tests/${testId}`),
      ]);

      setStats(statsRes.data);
      setQuestionStats(questionsRes.data);
      setTest(testRes.data);
    } catch (error) {
      console.error('Failed to load statistics:', error);
      alert('Ошибка при загрузке статистики');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/admin')}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Статистика теста
              </h1>
              <p className="text-sm text-gray-600 mt-1">{test?.title}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <Users className="w-8 h-8 text-blue-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900">
              {stats.completed_attempts}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Завершенных попыток
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Всего: {stats.total_attempts}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <Target className="w-8 h-8 text-green-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900">
              {stats.average_score.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Средний балл</div>
            <div className="text-xs text-gray-500 mt-2">
              Медиана: {stats.median_score.toFixed(1)}%
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <CheckCircle className="w-8 h-8 text-purple-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900">
              {stats.pass_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Процент прохождения
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Проходной: {test?.passing_score}%
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <Clock className="w-8 h-8 text-orange-600" />
            </div>
            <div className="text-3xl font-bold text-gray-900">
              {stats.average_time_minutes.toFixed(0)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Среднее время (мин)</div>
            <div className="text-xs text-gray-500 mt-2">
              Мин: {stats.min_time_minutes.toFixed(0)} / Макс:{' '}
              {stats.max_time_minutes.toFixed(0)}
            </div>
          </div>
        </div>

        {/* Score Distribution */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Распределение баллов
          </h2>
          <TestStatsChart testId={testId} />
        </div>

        {/* Question Breakdown */}
        {questionStats && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Статистика по вопросам
            </h2>
            <QuestionBreakdown questions={questionStats.questions} />
          </div>
        )}

        {/* Leaderboard */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Топ студентов
          </h2>
          <Leaderboard testId={testId} />
        </div>
      </div>
    </div>
  );
};

export default StatisticsPage;