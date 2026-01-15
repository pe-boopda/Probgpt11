import { useState, useEffect } from 'react';
import {
  Save,
  X,
  Plus,
  Trash2,
  CheckCircle,
  Circle,
  Image as ImageIcon,
} from 'lucide-react';
import testService from '../../services/testService';

const QuestionEditor = ({ question, onSave, onCancel, saving }) => {
  const [formData, setFormData] = useState({
    question_type: 'multiple_choice',
    question_text: '',
    order: 0,
    points: 1.0,
    image_id: null,
    metadata: null,
    options: [],
  });

  useEffect(() => {
    if (question) {
      setFormData({ ...question });
      // Ensure options array exists
      if (!question.options || question.options.length === 0) {
        initializeOptions(question.question_type);
      }
    }
  }, [question]);

  const initializeOptions = (type) => {
    let defaultOptions = [];
    
    if (type === 'multiple_choice' || type === 'multiple_select') {
      defaultOptions = [
        { option_text: '', is_correct: false, order: 0 },
        { option_text: '', is_correct: false, order: 1 },
      ];
    } else if (type === 'true_false') {
      defaultOptions = [
        { option_text: 'Правда', is_correct: false, order: 0 },
        { option_text: 'Ложь', is_correct: false, order: 1 },
      ];
    }
    
    setFormData((prev) => ({ ...prev, options: defaultOptions }));
  };

  const handleTypeChange = (type) => {
    setFormData((prev) => ({ ...prev, question_type: type }));
    initializeOptions(type);
  };

  const handleAddOption = () => {
    setFormData((prev) => ({
      ...prev,
      options: [
        ...prev.options,
        {
          option_text: '',
          is_correct: false,
          order: prev.options.length,
        },
      ],
    }));
  };

  const handleRemoveOption = (index) => {
    setFormData((prev) => ({
      ...prev,
      options: prev.options.filter((_, i) => i !== index),
    }));
  };

  const handleOptionChange = (index, field, value) => {
    setFormData((prev) => ({
      ...prev,
      options: prev.options.map((opt, i) =>
        i === index ? { ...opt, [field]: value } : opt
      ),
    }));
  };

  const handleCorrectToggle = (index) => {
    const isSingleChoice = formData.question_type === 'multiple_choice';
    
    setFormData((prev) => ({
      ...prev,
      options: prev.options.map((opt, i) => ({
        ...opt,
        is_correct: isSingleChoice ? i === index : i === index ? !opt.is_correct : opt.is_correct,
      })),
    }));
  };

  const handleSubmit = () => {
    // Validation
    if (!formData.question_text.trim()) {
      alert('Введите текст вопроса');
      return;
    }

    if (
      ['multiple_choice', 'multiple_select', 'true_false'].includes(
        formData.question_type
      )
    ) {
      if (formData.options.length < 2) {
        alert('Добавьте минимум 2 варианта ответа');
        return;
      }

      const hasCorrect = formData.options.some((opt) => opt.is_correct);
      if (!hasCorrect) {
        alert('Отметьте хотя бы один правильный ответ');
        return;
      }

      const allFilled = formData.options.every((opt) => opt.option_text.trim());
      if (!allFilled) {
        alert('Заполните все варианты ответов');
        return;
      }
    }

    onSave(formData);
  };

  const questionTypes = testService.getQuestionTypes();
  const needsOptions = ['multiple_choice', 'multiple_select', 'true_false'].includes(
    formData.question_type
  );

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900">
            {question?.id ? 'Редактирование вопроса' : 'Новый вопрос'}
          </h2>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* Question Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Тип вопроса *
            </label>
            <select
              value={formData.question_type}
              onChange={(e) => handleTypeChange(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {questionTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Question Text */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Текст вопроса *
            </label>
            <textarea
              value={formData.question_text}
              onChange={(e) =>
                setFormData({ ...formData, question_text: e.target.value })
              }
              placeholder="Введите вопрос..."
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Points */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Баллы за вопрос
            </label>
            <input
              type="number"
              value={formData.points}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  points: parseFloat(e.target.value) || 1,
                })
              }
              min="0"
              step="0.5"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Image Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Изображение (опционально)
            </label>
            <div className="flex items-center gap-4">
              <button
                type="button"
                className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                <ImageIcon className="w-4 h-4" />
                Загрузить изображение
              </button>
              {formData.image_id && (
                <span className="text-sm text-green-600">
                  ✓ Изображение прикреплено
                </span>
              )}
            </div>
          </div>

          {/* Options (for choice questions) */}
          {needsOptions && (
            <div>
              <div className="flex justify-between items-center mb-3">
                <label className="block text-sm font-medium text-gray-700">
                  Варианты ответов *
                </label>
                {formData.question_type !== 'true_false' && (
                  <button
                    onClick={handleAddOption}
                    className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                  >
                    <Plus className="w-4 h-4" />
                    Добавить вариант
                  </button>
                )}
              </div>

              <div className="space-y-3">
                {formData.options.map((option, index) => (
                  <div key={index} className="flex items-start gap-3">
                    {/* Correct toggle */}
                    <button
                      type="button"
                      onClick={() => handleCorrectToggle(index)}
                      className="mt-2"
                      title={
                        option.is_correct
                          ? 'Правильный ответ'
                          : 'Отметить как правильный'
                      }
                    >
                      {option.is_correct ? (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      ) : (
                        <Circle className="w-5 h-5 text-gray-400 hover:text-gray-600" />
                      )}
                    </button>

                    {/* Option text */}
                    <input
                      type="text"
                      value={option.option_text}
                      onChange={(e) =>
                        handleOptionChange(index, 'option_text', e.target.value)
                      }
                      placeholder={`Вариант ${index + 1}`}
                      className={`flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                        option.is_correct
                          ? 'border-green-300 bg-green-50'
                          : 'border-gray-300'
                      }`}
                      disabled={formData.question_type === 'true_false'}
                    />

                    {/* Remove button */}
                    {formData.question_type !== 'true_false' &&
                      formData.options.length > 2 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveOption(index)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition mt-1"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                  </div>
                ))}
              </div>

              <p className="mt-2 text-sm text-gray-600">
                {formData.question_type === 'multiple_choice'
                  ? '✓ Нажмите на кружок, чтобы отметить правильный ответ'
                  : '✓ Можно отметить несколько правильных ответов'}
              </p>
            </div>
          )}

          {/* Text Input Info */}
          {formData.question_type === 'text_input' && (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-900">
                ℹ️ Студент введет свой ответ в текстовое поле. Проверка таких
                ответов требует ручной оценки преподавателем или настройки ключевых
                слов.
              </p>
            </div>
          )}

          {/* Image Annotation Info */}
          {formData.question_type === 'image_annotation' && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-900">
                ℹ️ Загрузите изображение выше. Студент сможет рисовать на нем и
                добавлять подписи. Настройка проверки будет доступна после
                загрузки изображения.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onCancel}
            disabled={saving}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
          >
            Отмена
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Сохранение...' : 'Сохранить вопрос'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuestionEditor;