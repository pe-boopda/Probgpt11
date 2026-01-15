import api from './api';

const sessionService = {
  // Начать тест
  startTest: async (testId) => {
    const response = await api.post(`/api/tests/${testId}/start`);
    return response.data;
  },

  // Получить информацию о сессии
  getSession: async (sessionId) => {
    const response = await api.get(`/api/sessions/${sessionId}`);
    return response.data;
  },

  // Получить вопросы теста
  getTestQuestions: async (sessionId) => {
    const response = await api.get(`/api/sessions/${sessionId}/test`);
    return response.data;
  },

  // Отправить ответ
  submitAnswer: async (sessionId, questionId, answerData) => {
    const response = await api.post(`/api/sessions/${sessionId}/answer`, {
      question_id: questionId,
      answer_data: answerData,
    });
    return response.data;
  },

  // Завершить тест
  submitTest: async (sessionId) => {
    const response = await api.post(`/api/sessions/${sessionId}/submit`);
    return response.data;
  },

  // Получить результаты
  getResult: async (sessionId) => {
    const response = await api.get(`/api/sessions/${sessionId}/result`);
    return response.data;
  },

  // Получить прогресс
  getProgress: async (sessionId) => {
    const response = await api.get(`/api/sessions/${sessionId}/progress`);
    return response.data;
  },

  // Форматировать время
  formatTime: (seconds) => {
    if (!seconds) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  },

  // Получить цвет результата
  getScoreColor: (score, passingScore) => {
    if (score >= passingScore + 20) return 'text-green-600';
    if (score >= passingScore) return 'text-blue-600';
    if (score >= passingScore - 10) return 'text-yellow-600';
    return 'text-red-600';
  },
};

export default sessionService;