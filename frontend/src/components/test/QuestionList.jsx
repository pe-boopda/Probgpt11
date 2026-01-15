import { Plus, Edit, Trash2, GripVertical, CheckCircle } from 'lucide-react';

const QuestionList = ({ questions, onAdd, onEdit, onDelete, loading }) => {
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

  const getQuestionTypeColor = (type) => {
    const colors = {
      multiple_choice: 'bg-blue-100 text-blue-800',
      multiple_select: 'bg-purple-100 text-purple-800',
      true_false: 'bg-green-100 text-green-800',
      text_input: 'bg-yellow-100 text-yellow-800',
      image_annotation: 'bg-pink-100 text-pink-800',
      matching: 'bg-indigo-100 text-indigo-800',
      ordering: 'bg-orange-100 text-orange-800',
      hotspot: 'bg-red-100 text-red-800',
      fill_blanks: 'bg-teal-100 text-teal-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Вопросы теста</h2>
          <p className="text-sm text-gray-600 mt-1">
            Всего вопросов: {questions.length} • Общий балл:{' '}
            {questions.reduce((sum, q) => sum + (q.points || 0), 0)}
          </p>
        </div>
        <button
          onClick={onAdd}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          Добавить вопрос
        </button>
      </div>

      {/* Questions List */}
      {questions.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Plus className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Нет вопросов
          </h3>
          <p className="text-gray-600 mb-4">
            Добавьте первый вопрос к этому тесту
          </p>
          <button
            onClick={onAdd}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <Plus className="w-4 h-4" />
            Добавить вопрос
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {questions.map((question, index) => (
            <div
              key={question.id}
              className="bg-white rounded-lg shadow hover:shadow-md transition p-6"
            >
              <div className="flex gap-4">
                {/* Drag Handle */}
                <div className="flex items-start pt-1">
                  <GripVertical className="w-5 h-5 text-gray-400 cursor-move" />
                </div>

                {/* Question Content */}
                <div className="flex-1">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm font-medium text-gray-500">
                          Вопрос {index + 1}
                        </span>
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${getQuestionTypeColor(
                            question.question_type
                          )}`}
                        >
                          {getQuestionTypeLabel(question.question_type)}
                        </span>
                        <span className="text-sm text-gray-600">
                          {question.points} {question.points === 1 ? 'балл' : 'балла'}
                        </span>
                      </div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {question.question_text}
                      </h3>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={() => onEdit(question)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                        title="Редактировать"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => onDelete(question.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Options Preview */}
                  {question.options && question.options.length > 0 && (
                    <div className="mt-4 space-y-2">
                      {question.options.slice(0, 3).map((option, idx) => (
                        <div
                          key={option.id || idx}
                          className="flex items-center gap-2 text-sm"
                        >
                          {option.is_correct ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : (
                            <div className="w-4 h-4 border-2 border-gray-300 rounded-full" />
                          )}
                          <span
                            className={
                              option.is_correct
                                ? 'text-green-700 font-medium'
                                : 'text-gray-700'
                            }
                          >
                            {option.option_text}
                          </span>
                        </div>
                      ))}
                      {question.options.length > 3 && (
                        <p className="text-sm text-gray-500 ml-6">
                          И ещё {question.options.length - 3} вариантов...
                        </p>
                      )}
                    </div>
                  )}

                  {/* Image indicator */}
                  {question.image_id && (
                    <div className="mt-3 text-sm text-gray-600 flex items-center gap-2">
                      <span className="px-2 py-1 bg-gray-100 rounded">
                        📷 Изображение прикреплено
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info */}
      {questions.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-900">
            💡 <strong>Совет:</strong> Вы можете перетаскивать вопросы для
            изменения их порядка. Изменения сохраняются автоматически.
          </p>
        </div>
      )}
    </div>
  );
};

export default QuestionList;