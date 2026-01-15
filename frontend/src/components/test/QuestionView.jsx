import { CheckCircle, Circle, Square, CheckSquare } from 'lucide-react';

const QuestionView = ({ question, answer, onAnswer }) => {
  const handleMultipleChoice = (optionId) => {
    onAnswer({ selected_option_id: optionId });
  };

  const handleMultipleSelect = (optionId) => {
    const currentIds = answer?.selected_option_ids || [];
    const newIds = currentIds.includes(optionId)
      ? currentIds.filter((id) => id !== optionId)
      : [...currentIds, optionId];
    onAnswer({ selected_option_ids: newIds });
  };

  const handleTextInput = (text) => {
    onAnswer({ text });
  };

  const renderMultipleChoice = () => {
    const selectedId = answer?.selected_option_id;

    return (
      <div className="space-y-3">
        {question.options.map((option) => {
          const isSelected = selectedId === option.id;
          return (
            <button
              key={option.id}
              onClick={() => handleMultipleChoice(option.id)}
              className={`w-full p-4 rounded-lg border-2 transition text-left flex items-center gap-3 ${
                isSelected
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400 bg-white'
              }`}
            >
              {isSelected ? (
                <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0" />
              ) : (
                <Circle className="w-5 h-5 text-gray-400 flex-shrink-0" />
              )}
              <span
                className={isSelected ? 'text-blue-900 font-medium' : 'text-gray-700'}
              >
                {option.option_text}
              </span>
            </button>
          );
        })}
      </div>
    );
  };

  const renderMultipleSelect = () => {
    const selectedIds = answer?.selected_option_ids || [];

    return (
      <div className="space-y-3">
        {question.options.map((option) => {
          const isSelected = selectedIds.includes(option.id);
          return (
            <button
              key={option.id}
              onClick={() => handleMultipleSelect(option.id)}
              className={`w-full p-4 rounded-lg border-2 transition text-left flex items-center gap-3 ${
                isSelected
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400 bg-white'
              }`}
            >
              {isSelected ? (
                <CheckSquare className="w-5 h-5 text-blue-600 flex-shrink-0" />
              ) : (
                <Square className="w-5 h-5 text-gray-400 flex-shrink-0" />
              )}
              <span
                className={isSelected ? 'text-blue-900 font-medium' : 'text-gray-700'}
              >
                {option.option_text}
              </span>
            </button>
          );
        })}
        <p className="text-sm text-gray-600 mt-2">
          💡 Можно выбрать несколько вариантов
        </p>
      </div>
    );
  };

  const renderTextInput = () => {
    return (
      <div>
        <textarea
          value={answer?.text || ''}
          onChange={(e) => handleTextInput(e.target.value)}
          placeholder="Введите ваш ответ..."
          rows={6}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="text-sm text-gray-600 mt-2">
          Введите развернутый ответ на вопрос
        </p>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {/* Question Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-3">
          <span className="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
            {question.question_type === 'multiple_choice' && 'Один правильный ответ'}
            {question.question_type === 'multiple_select' && 'Несколько правильных'}
            {question.question_type === 'true_false' && 'Правда/Ложь'}
            {question.question_type === 'text_input' && 'Текстовый ответ'}
          </span>
          <span className="text-sm text-gray-600">{question.points} балл(а)</span>
        </div>
        <h2 className="text-xl font-semibold text-gray-900">
          {question.question_text}
        </h2>
      </div>

      {/* Question Body */}
      <div>
        {(question.question_type === 'multiple_choice' ||
          question.question_type === 'true_false') &&
          renderMultipleChoice()}
        {question.question_type === 'multiple_select' && renderMultipleSelect()}
        {question.question_type === 'text_input' && renderTextInput()}
      </div>

      {/* Image */}
      {question.image_id && (
        <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <p className="text-sm text-gray-600">
            📷 К этому вопросу прикреплено изображение
          </p>
        </div>
      )}
    </div>
  );
};

export default QuestionView;