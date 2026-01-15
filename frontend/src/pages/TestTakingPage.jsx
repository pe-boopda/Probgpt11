import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import sessionService from '../services/sessionService';
import TestTimer from '../components/test/TestTimer';
import QuestionView from '../components/test/QuestionView';
import TestProgress from '../components/test/TestProgress';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react';

const TestTakingPage = () => {
  const { testId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);
  const [test, setTest] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(null);

  useEffect(() => {
    startTest();
  }, [testId]);

  useEffect(() => {
    if (session && session.time_remaining) {
      setTimeRemaining(session.time_remaining);
    }
  }, [session]);

  // Таймер
  useEffect(() => {
    if (timeRemaining === null || timeRemaining <= 0) return;

    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          handleTimeUp();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeRemaining]);

  const startTest = async () => {
    setLoading(true);
    try {
      // Начать тест
      const sessionData = await sessionService.startTest(testId);
      setSession(sessionData);

      // Получить вопросы
      const testData = await sessionService.getTestQuestions(sessionData.id);
      setTest(testData);
    } catch (error) {
      alert(error.response?.data?.detail || 'Ошибка при загрузке теста');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (questionId, answerData) => {
    try {
      await sessionService.submitAnswer(session.id, questionId, answerData);
      setAnswers({ ...answers, [questionId]: answerData });
    } catch (error) {
      console.error('Error submitting answer:', error);
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex < test.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = async () => {
    const answeredCount = Object.keys(answers).length;
    const totalQuestions = test.questions.length;

    if (answeredCount < totalQuestions) {
      if (
        !confirm(
          `Вы ответили на ${answeredCount} из ${totalQuestions} вопросов. Завершить тест?`
        )
      ) {
        return;
      }
    }

    setSubmitting(true);
    try {
      const result = await sessionService.submitTest(session.id);
      navigate(`/tests/results/${session.id}`);
    } catch (error) {
      alert('Ошибка при отправке теста');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTimeUp = async () => {
    alert('Время вышло! Тест будет автоматически завершен.');
    await handleSubmit();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!test || !session) return null;

  const currentQuestion = test.questions[currentQuestionIndex];
  const isAnswered = answers.hasOwnProperty(currentQuestion.id);
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex-1">
              <h1 className="text-xl font-bold text-gray-900">{test.title}</h1>
              <p className="text-sm text-gray-600 mt-1">
                Вопрос {currentQuestionIndex + 1} из {test.questions.length}
              </p>
            </div>

            {/* Timer */}
            {timeRemaining !== null && (
              <TestTimer
                timeRemaining={timeRemaining}
                totalTime={test.time_limit * 60}
              />
            )}
          </div>

          {/* Progress Bar */}
          <TestProgress
            current={currentQuestionIndex + 1}
            total={test.questions.length}
            answered={answeredCount}
          />
        </div>
      </div>

      {/* Question */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <QuestionView
          question={currentQuestion}
          answer={answers[currentQuestion.id]}
          onAnswer={(answerData) => handleAnswer(currentQuestion.id, answerData)}
        />

        {/* Navigation */}
        <div className="mt-8 flex justify-between items-center">
          <button
            onClick={handlePrevious}
            disabled={currentQuestionIndex === 0}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Назад
          </button>

          <div className="flex gap-3">
            {currentQuestionIndex < test.questions.length - 1 ? (
              <button
                onClick={handleNext}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Далее →
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 flex items-center gap-2"
              >
                {submitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Отправка...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    Завершить тест
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Info */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex gap-3 items-start">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-900">
              <p className="font-medium mb-1">Совет:</p>
              <p>
                Ваши ответы сохраняются автоматически. Вы можете вернуться к
                предыдущим вопросам и изменить ответы до завершения теста.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestTakingPage;