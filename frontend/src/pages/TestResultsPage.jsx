import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import sessionService from '../services/sessionService';
import {
  CheckCircle,
  XCircle,
  Clock,
  Target,
  TrendingUp,
  Home,
  Circle,
  AlertCircle,
} from 'lucide-react';

const TestResultsPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadResults();
  }, [sessionId]);

  const loadResults = async () => {
    setLoading(true);
    try {
      const data = await sessionService.getResult(sessionId);
      setResult(data);
    } catch (error) {
      alert('Ошибка при загрузке результатов');
      navigate('/dashboard');
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

  if (!result) return null;

  const scoreColor = sessionService.getScoreColor(result.score, 70);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <div className="mb-4">
              {result.passed ? (
                <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full">
                  <CheckCircle className="w-12 h-12 text-green-600" />
                </div>
              ) : (
                <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full">
                  <XCircle className="w-12 h-12 text-red-600" />
                </div>
              )}
            </div>
            <h1 className="text-3xl font-bold text-gray-900">
              {result.passed ? 'Тест пройден!' : 'Тест не пройден'}
            </h1>
            <p className="text-lg text-gray-600 mt-2">{result.test_title}</p>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {/* Score */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <Target className="w-8 h-8 text-blue-600" />
            </div>
            <div className="text-3xl font-bold text-blue-600">
              {result.score.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Итоговый балл</div>
          </div>

          {/* Correct Answers */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <div className="text-3xl font-bold text-green-600">
              {result.correct_answers}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Из {result.total_questions}
            </div>
          </div>

          {/* Points */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="w-8 h-8 text-purple-600" />
            </div>
            <div className="text-3xl font-bold text-purple-600">
              {result.points_earned.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Из {result.max_points} баллов
            </div>
          </div>

          {/* Time */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <Clock className="w-8 h-8 text-orange-600" />
            </div>
            <div className="text-3xl font-bold text-orange-600">
              {result.time_taken_minutes
                ? result.time_taken_minutes.toFixed(0)
                : '-'}
            </div>
            <div className="text-sm text-gray-600 mt-1">Минут затрачено</div>
          </div>
        </div>

        {/* Status Banner */}
        <div
          className={`p-6 rounded-lg mb-8 ${
            result.passed
              ? 'bg-green-50 border border-green-200'
              : 'bg-red-50 border border-red-200'
          }`}
        >
          <div className="flex items-start gap-4">
            {result.passed ? (
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
            ) : (
              <XCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
            )}
            <div>
              <h3
                className={`text-lg font-semibold ${
                  result.passed ? 'text-green-900' : 'text-red-900'
                }`}
              >
                {result.passed
                  ? 'Поздравляем! Вы успешно прошли тест'
                  : 'К сожалению, тест не пройден'}
              </h3>
              <p
                className={`mt-1 ${
                  result.passed ? 'text-green-800' : 'text-red-800'
                }`}
              >
                {result.passed
                  ? `Вы набрали ${result.score.toFixed(1)}%, что превышает проходной балл.`
                  : `Вы набрали ${result.score.toFixed(1)}%. Для прохождения нужно минимум 70%.`}
              </p>
            </div>
          </div>
        </div>

        {/* Question Details */}
        {result.questions_details && result.questions_details.length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">
                Детали по вопросам
              </h2>
            </div>
            <div className="p-6 space-y-6">
              {result.questions_details.map((detail, index) => (
                <div
                  key={detail.question_id}
                  className={`p-4 rounded-lg border-2 ${
                    detail.is_correct === true
                      ? 'border-green-300 bg-green-50'
                      : detail.is_correct === false
                      ? 'border-red-300 bg-red-50'
                      : 'border-gray-300 bg-gray-50'
                  }`}
                >
                  {/* Question Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm font-medium text-gray-600">
                          Вопрос {index + 1}
                        </span>
                        {detail.is_correct === true && (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        )}
                        {detail.is_correct === false && (
                          <XCircle className="w-5 h-5 text-red-600" />
                        )}
                        {detail.is_correct === null && (
                          <AlertCircle className="w-5 h-5 text-yellow-600" />
                        )}
                      </div>
                      <h4 className="font-medium text-gray-900">
                        {detail.question_text}
                      </h4>
                    </div>
                    <span className="text-sm text-gray-600 ml-4">
                      {detail.points_awarded?.toFixed(1) || 0} /{' '}
                      {detail.points} балл(а)
                    </span>
                  </div>

                  {/* Answer Info */}
                  <div className="mt-3 space-y-2">
                    {detail.question_type !== 'text_input' && (
                      <>
                        <div className="text-sm">
                          <span className="font-medium text-gray-700">
                            Ваш ответ:
                          </span>
                          <span className="ml-2 text-gray-900">
                            {detail.your_answer?.selected_option_id ||
                              detail.your_answer?.selected_option_ids?.join(
                                ', '
                              ) ||
                              'Нет ответа'}
                          </span>
                        </div>
                        {detail.correct_answer && (
                          <div className="text-sm">
                            <span className="font-medium text-gray-700">
                              Правильный ответ:
                            </span>
                            <span className="ml-2 text-green-700">
                              {Array.isArray(detail.correct_answer)
                                ? detail.correct_answer.join(', ')
                                : detail.correct_answer}
                            </span>
                          </div>
                        )}
                      </>
                    )}

                    {detail.question_type === 'text_input' && (
                      <div className="text-sm">
                        <span className="font-medium text-gray-700">
                          Ваш ответ:
                        </span>
                        <p className="mt-1 p-3 bg-white rounded border border-gray-200">
                          {detail.your_answer?.text || 'Нет ответа'}
                        </p>
                        {detail.is_correct === null && (
                          <p className="mt-2 text-yellow-700">
                            ⏳ Требуется проверка преподавателем
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="mt-8 flex justify-center">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <Home className="w-4 h-4" />
            Вернуться на главную
          </button>
        </div>
      </div>
    </div>
  );
};

export default TestResultsPage;