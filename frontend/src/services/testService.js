import api from './api';

const testService = {
  // ============ Tests CRUD ============

  // Получить список тестов
  getTests: async (params = {}) => {
    const {
      skip = 0,
      limit = 20,
      search = '',
      publishedOnly = false,
      myTests = false,
    } = params;

    const response = await api.get('/api/tests', {
      params: {
        skip,
        limit,
        search,
        published_only: publishedOnly,
        my_tests: myTests,
      },
    });
    return response.data;
  },

  // Получить детальную информацию о тесте
  getTest: async (testId) => {
    const response = await api.get(`/api/tests/${testId}`);
    return response.data;
  },

  // Создать новый тест
  createTest: async (testData) => {
    const response = await api.post('/api/tests', testData);
    return response.data;
  },

  // Обновить тест
  updateTest: async (testId, testData) => {
    const response = await api.put(`/api/tests/${testId}`, testData);
    return response.data;
  },

  // Удалить тест
  deleteTest: async (testId) => {
    await api.delete(`/api/tests/${testId}`);
  },

  // Опубликовать/снять с публикации
  publishTest: async (testId, isPublished) => {
    const response = await api.post(`/api/tests/${testId}/publish`, {
      is_published: isPublished,
    });
    return response.data;
  },

  // ============ Questions Management ============

  // Добавить вопрос
  addQuestion: async (testId, questionData) => {
    const response = await api.post(
      `/api/tests/${testId}/questions`,
      questionData
    );
    return response.data;
  },

  // Обновить вопрос
  updateQuestion: async (questionId, questionData) => {
    const response = await api.put(
      `/api/tests/questions/${questionId}`,
      questionData
    );
    return response.data;
  },

  // Удалить вопрос
  deleteQuestion: async (questionId) => {
    await api.delete(`/api/tests/questions/${questionId}`);
  },

  // ============ Statistics ============

  // Получить статистику по тесту
  getTestStatistics: async (testId) => {
    const response = await api.get(`/api/tests/${testId}/statistics`);
    return response.data;
  },

  // ============ Bulk Operations ============

  // Массовое удаление тестов
  bulkDeleteTests: async (testIds) => {
    const response = await api.post('/api/tests/bulk/delete', {
      test_ids: testIds,
    });
    return response.data;
  },

  // ============ Helper Functions ============

  // Получить типы вопросов
  getQuestionTypes: () => {
    return [
      { value: 'multiple_choice', label: 'Один правильный ответ' },
      { value: 'multiple_select', label: 'Несколько правильных ответов' },
      { value: 'true_false', label: 'Правда/Ложь' },
      { value: 'text_input', label: 'Текстовый ответ' },
      { value: 'image_annotation', label: 'Аннотация изображения' },
      { value: 'matching', label: 'Соответствия' },
      { value: 'ordering', label: 'Упорядочивание' },
      { value: 'hotspot', label: 'Выбор области на изображении' },
      { value: 'fill_blanks', label: 'Заполнение пропусков' },
    ];
  },

  // Форматировать время
  formatTime: (minutes) => {
    if (!minutes) return 'Без ограничения';
    if (minutes < 60) return `${minutes} мин`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}ч ${mins}мин` : `${hours}ч`;
  },

  // Получить цвет статуса
  getStatusColor: (isPublished) => {
    return isPublished
      ? 'bg-green-100 text-green-800'
      : 'bg-gray-100 text-gray-800';
  },

  // Получить текст статуса
  getStatusText: (isPublished) => {
    return isPublished ? 'Опубликован' : 'Черновик';
  },
};

export default testService;