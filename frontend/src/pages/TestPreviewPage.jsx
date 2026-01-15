import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import testService from '../services/testService';
import {
  ArrowLeft,
  Clock,
  Target,
  FileText,
  AlertCircle,
  CheckCircle,
  Circle,
} from 'lucide-react';

const TestPreviewPage = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const [test, setTest] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTest();
  }, [testId]);

  const loadTest = async () => {
    setLoading(true);
    try {
      const data = await testService.getTest(testId);
      setTest(data);
    } catch (error) {
      alert('Ошибка при загрузке теста');
      navigate('/admin/tests');
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

  if (!test) return null;

  const getQuestionTypeLabel = (type) => {
    const types = {
      multiple_choice: 'Один правильный ответ',
      multiple_select: 'Несколько правильных',
      true_false: 'Правда/Ложь',
      text_input: 'Текстовый ответ',
      image_annotation: 'Аннотация изображения',
      matching: 'Соответствия',
      ordering: 'Упорядочивание',
      hotspot: 'Области на изображении',
      fill_blanks: 'Заполнение пропусков',
    };
    return types[type] || type;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-gray-900">
                  {test.title}
                </h1>
                <span
                  className={`px-2 py-1 text-xs font-medium rounded-full ${
                    test.is_published
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {test.is_published ? 'Опубликован' : 'Черновик'}
                </span>
              </div>
              {test.description && (
                <p className="text-sm text-gray-600 mt-1">{test.description}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Test Info */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Информация о тесте
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Вопросов</p>
                <p className="font-semibold text-gray-900">
                  {test.questions_count}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Clock className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Время</p>
                <p className="font-semibold text-gray-900">
                  {testService.formatTime(test.time_limit)}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Target className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Проходной балл</p>
                <p className="font-semibold text-gray-900">
                  {test.passing_score}%
                </p>
              </div>
            </div>
          </div>

          {/* Settings */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-3">
              Настройки
            </h3>
            <div className="flex flex-wrap gap-3">
              <span
                className={`px-3 py-1 rounded-full text-sm ${
                  test.show_results
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {test.show_results
                  ? '✓ Показывать результаты'
                  : '✗ Не показывать результаты'}
              </span>
              <span
                className={`px-3 py-1 rounded-full text-sm ${
                  test.shuffle_questions
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {test.shuffle_questions
                  ? '🔀 Случайный порядок вопросов'
                  : '📋 Фиксированный порядок'}
              </span>
              <span
                className={`px-3 py-1 rounded-full text-sm ${
                  test.shuffle_options
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {test.shuffle_options
                  ? '🔀 Перемешивать варианты'
                  : '📋 Не перемешивать'}
              </span>
            </div>
          </div>
        </div>

        {/* Questions */}
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-gray-900">
            Вопросы ({test.questions?.length || 0})
          </h2>

          {test.questions && test.questions.length > 0 ? (
            test.questions.map((question, index) => (
              <div key={question.id} className="bg-white rounded-lg shadow p-6">
                {/* Question Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-sm font-medium text-gray-500">
                        Вопрос {index + 1}
                      </span>
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                        {getQuestionTypeLabel(question.question_type)}
                      </span>
                      <span className="text-sm text-gray-600">
                        {question.points}{' '}
                        {question.points === 1 ? 'балл' : 'балла'}
                      </span>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {question.question_text}
                    </h3>
                  </div>
                </div>

                {/* Options */}
                {question.options && question.options.length > 0 && (
                  <div className="space-y-2 mt-4">
                    {question.options.map((option, optIdx) => (
                      <div
                        key={option.id || optIdx}
                        className={`flex items-center gap-3 p-3 rounded-lg border-2 transition ${
                          option.is_correct
                            ? 'border-green-300 bg-green-50'
                            : 'border-gray-200 bg-gray-50'
                        }`}
                      >
                        {option.is_correct ? (
                          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                        ) : (
                          <Circle className="w-5 h-5 text-gray-400 flex-shrink-0" />
                        )}
                        <span
                          className={
                            option.is_correct
                              ? 'text-green-900 font-medium'
                              : 'text-gray-700'
                          }
                        >
                          {option.option_text}
                        </span>
                        {option.is_correct && (
                          <span className="ml-auto text-xs text-green-700 bg-green-100 px-2 py-1 rounded">
                            Правильный ответ
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Text Input Placeholder */}
                {question.question_type === 'text_input' && (
                  <div className="mt-4">
                    <textarea
                      placeholder="Здесь студент введет свой ответ..."
                      disabled
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
                    />
                  </div>
                )}

                {/* Image Indicator */}
                {question.image_id && (
                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-900">
                      📷 К этому вопросу прикреплено изображение
                    </p>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">В тесте пока нет вопросов</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TestPreviewPage;