import { Save, Info } from 'lucide-react';

const TestBasicInfo = ({ test, onChange, onSave, saving, isEditMode }) => {
  const handleChange = (field, value) => {
    onChange({ ...test, [field]: value });
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Основная информация о тесте
        </h2>

        {/* Title */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Название теста *
          </label>
          <input
            type="text"
            value={test.title}
            onChange={(e) => handleChange('title', e.target.value)}
            placeholder="Введите название теста"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        {/* Description */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Описание
          </label>
          <textarea
            value={test.description || ''}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Описание теста, инструкции для студентов..."
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Time Limit */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ограничение по времени (минуты)
          </label>
          <input
            type="number"
            value={test.time_limit || ''}
            onChange={(e) =>
              handleChange('time_limit', parseInt(e.target.value) || null)
            }
            placeholder="Оставьте пустым для неограниченного времени"
            min="1"
            max="300"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="text-sm text-gray-500 mt-1">
            Оставьте пустым, если тест без ограничения по времени
          </p>
        </div>

        {/* Passing Score */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Проходной балл (%)
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              value={test.passing_score}
              onChange={(e) =>
                handleChange('passing_score', parseInt(e.target.value))
              }
              min="0"
              max="100"
              step="5"
              className="flex-1"
            />
            <span className="text-2xl font-bold text-blue-600 w-16 text-center">
              {test.passing_score}%
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Минимальный процент правильных ответов для прохождения теста
          </p>
        </div>

        {/* Settings */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Дополнительные настройки
          </h3>

          <div className="space-y-4">
            {/* Show Results */}
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={test.show_results}
                onChange={(e) => handleChange('show_results', e.target.checked)}
                className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <div>
                <div className="font-medium text-gray-900">
                  Показывать результаты
                </div>
                <div className="text-sm text-gray-600">
                  Студенты увидят результаты сразу после завершения теста
                </div>
              </div>
            </label>

            {/* Shuffle Questions */}
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={test.shuffle_questions}
                onChange={(e) =>
                  handleChange('shuffle_questions', e.target.checked)
                }
                className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <div>
                <div className="font-medium text-gray-900">
                  Случайный порядок вопросов
                </div>
                <div className="text-sm text-gray-600">
                  Вопросы будут показываться в случайном порядке для каждого
                  студента
                </div>
              </div>
            </label>

            {/* Shuffle Options */}
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={test.shuffle_options}
                onChange={(e) =>
                  handleChange('shuffle_options', e.target.checked)
                }
                className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <div>
                <div className="font-medium text-gray-900">
                  Перемешивать варианты ответов
                </div>
                <div className="text-sm text-gray-600">
                  Варианты ответов будут показываться в случайном порядке
                </div>
              </div>
            </label>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex gap-3">
            <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-900">
              <p className="font-medium mb-1">Совет:</p>
              <p>
                После сохранения основной информации вы сможете добавить вопросы
                к тесту. Тест можно опубликовать только после добавления хотя бы
                одного вопроса.
              </p>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={onSave}
            disabled={saving || !test.title.trim()}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="w-4 h-4" />
            {saving
              ? 'Сохранение...'
              : isEditMode
              ? 'Сохранить изменения'
              : 'Создать тест'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TestBasicInfo;