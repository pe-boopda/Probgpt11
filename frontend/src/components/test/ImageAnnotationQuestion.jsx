import { useState } from 'react';
import CanvasEditor from '../canvas/CanvasEditor';
import { Info } from 'lucide-react';

const ImageAnnotationQuestion = ({ question, answer, onAnswer }) => {
  const imageUrl = question.image_id
    ? `/uploads/${question.image_id}`
    : null;

  const handleSave = (canvasData) => {
    onAnswer({
      annotations: canvasData,
      timestamp: new Date().toISOString(),
    });
  };

  if (!imageUrl) {
    return (
      <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex gap-3">
          <Info className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-yellow-900">
              Изображение не прикреплено
            </p>
            <p className="text-sm text-yellow-800 mt-1">
              Обратитесь к преподавателю - к этому вопросу должно быть
              прикреплено изображение.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex gap-3">
          <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-900">
            <p className="font-medium mb-1">Инструкция:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Используйте инструменты для добавления аннотаций</li>
              <li>Рисуйте карандашом для свободных линий</li>
              <li>Добавляйте фигуры и текст для обозначений</li>
              <li>Выберите подходящий цвет для ваших аннотаций</li>
              <li>Ваша работа сохраняется автоматически</li>
            </ul>
          </div>
        </div>
      </div>

      <CanvasEditor
        imageUrl={imageUrl}
        initialData={answer?.annotations}
        onSave={handleSave}
      />

      {answer && (
        <div className="text-sm text-green-600 flex items-center gap-2">
          <span className="w-2 h-2 bg-green-600 rounded-full"></span>
          Аннотации сохранены
        </div>
      )}
    </div>
  );
};

export default ImageAnnotationQuestion;