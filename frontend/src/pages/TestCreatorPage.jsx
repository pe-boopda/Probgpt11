import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import testService from '../services/testService';
import TestBasicInfo from '../components/test/TestBasicInfo';
import QuestionList from '../components/test/QuestionList';
import QuestionEditor from '../components/test/QuestionEditor';
import { Save, ArrowLeft, Eye, Upload } from 'lucide-react';

const TestCreatorPage = () => {
  const { testId } = useParams();
  const navigate = useNavigate();
  const isEditMode = !!testId;

  const [test, setTest] = useState({
    title: '',
    description: '',
    time_limit: 30,
    passing_score: 70,
    show_results: true,
    shuffle_questions: false,
    shuffle_options: false,
  });

  const [questions, setQuestions] = useState([]);
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [step, setStep] = useState(1); // 1: Basic Info, 2: Questions

  useEffect(() => {
    if (isEditMode) {
      loadTest();
    }
  }, [testId]);

  const loadTest = async () => {
    setLoading(true);
    try {
      const data = await testService.getTest(testId);
      setTest({
        title: data.title,
        description: data.description,
        time_limit: data.time_limit,
        passing_score: data.passing_score,
        show_results: data.show_results,
        shuffle_questions: data.shuffle_questions,
        shuffle_options: data.shuffle_options,
      });
      setQuestions(data.questions || []);
    } catch (error) {
      alert('Ошибка при загрузке теста');
      navigate('/admin/tests');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveBasicInfo = async () => {
    if (!test.title.trim()) {
      alert('Введите название теста');
      return;
    }

    setSaving(true);
    try {
      if (isEditMode) {
        await testService.updateTest(testId, test);
        alert('Тест обновлен');
      } else {
        const created = await testService.createTest(test);
        navigate(`/admin/tests/${created.id}/edit`);
      }
      setStep(2);
    } catch (error) {
      alert(error.response?.data?.detail || 'Ошибка при сохранении теста');
    } finally {
      setSaving(false);
    }
  };

  const handleAddQuestion = () => {
    setEditingQuestion({
      question_type: 'multiple_choice',
      question_text: '',
      order: questions.length,
      points: 1.0,
      options: [],
    });
  };

  const handleSaveQuestion = async (questionData) => {
    setSaving(true);
    try {
      if (questionData.id) {
        // Update existing
        await testService.updateQuestion(questionData.id, questionData);
        setQuestions(
          questions.map((q) => (q.id === questionData.id ? questionData : q))
        );
      } else {
        // Create new
        const created = await testService.addQuestion(testId, questionData);
        setQuestions([...questions, created]);
      }
      setEditingQuestion(null);
    } catch (error) {
      alert(error.response?.data?.detail || 'Ошибка при сохранении вопроса');
    } finally {
      setSaving(false);
    }
  };

  const handleEditQuestion = (question) => {
    setEditingQuestion(question);
  };

  const handleDeleteQuestion = async (questionId) => {
    if (!confirm('Удалить этот вопрос?')) return;

    setSaving(true);
    try {
      await testService.deleteQuestion(questionId);
      setQuestions(questions.filter((q) => q.id !== questionId));
    } catch (error) {
      alert('Ошибка при удалении вопроса');
    } finally {
      setSaving(false);
    }
  };

  const handlePublish = async () => {
    if (questions.length === 0) {
      alert('Добавьте хотя бы один вопрос перед публикацией');
      return;
    }

    if (!confirm('Опубликовать тест?')) return;

    setSaving(true);
    try {
      await testService.publishTest(testId, true);
      alert('Тест опубликован!');
      navigate('/admin/tests');
    } catch (error) {
      alert(error.response?.data?.detail || 'Ошибка при публикации');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/admin/tests')}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {isEditMode ? 'Редактирование теста' : 'Создание теста'}
                </h1>
                {test.title && (
                  <p className="text-sm text-gray-600 mt-1">{test.title}</p>
                )}
              </div>
            </div>

            <div className="flex gap-2">
              {isEditMode && step === 2 && (
                <>
                  <button
                    onClick={() => navigate(`/tests/${testId}`)}
                    className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                  >
                    <Eye className="w-4 h-4" />
                    Предпросмотр
                  </button>
                  <button
                    onClick={handlePublish}
                    disabled={saving || questions.length === 0}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50"
                  >
                    <Upload className="w-4 h-4" />
                    Опубликовать
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Steps */}
          <div className="flex gap-4 mt-6">
            <button
              onClick={() => setStep(1)}
              className={`pb-2 border-b-2 transition ${
                step === 1
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              1. Основная информация
            </button>
            <button
              onClick={() => isEditMode && setStep(2)}
              disabled={!isEditMode}
              className={`pb-2 border-b-2 transition ${
                step === 2
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              2. Вопросы ({questions.length})
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {step === 1 ? (
          <div className="max-w-3xl">
            <TestBasicInfo
              test={test}
              onChange={setTest}
              onSave={handleSaveBasicInfo}
              saving={saving}
              isEditMode={isEditMode}
            />
          </div>
        ) : editingQuestion ? (
          <QuestionEditor
            question={editingQuestion}
            onSave={handleSaveQuestion}
            onCancel={() => setEditingQuestion(null)}
            saving={saving}
          />
        ) : (
          <QuestionList
            questions={questions}
            onAdd={handleAddQuestion}
            onEdit={handleEditQuestion}
            onDelete={handleDeleteQuestion}
            loading={saving}
          />
        )}
      </div>
    </div>
  );
};

export default TestCreatorPage;