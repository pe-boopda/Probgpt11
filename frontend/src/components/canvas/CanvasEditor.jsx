import { useEffect, useRef, useState } from 'react';
import { fabric } from 'fabric';
import {
  Pencil,
  Circle,
  Square,
  Type,
  Eraser,
  Undo,
  Redo,
  Trash2,
  Download,
  Palette,
  Move,
} from 'lucide-react';

const CanvasEditor = ({ imageUrl, initialData, onSave, readOnly = false }) => {
  const canvasRef = useRef(null);
  const [canvas, setCanvas] = useState(null);
  const [tool, setTool] = useState('select'); // select, draw, circle, rect, text, erase
  const [color, setColor] = useState('#FF0000');
  const [brushWidth, setBrushWidth] = useState(3);
  const [isDrawing, setIsDrawing] = useState(false);

  // Инициализация canvas
  useEffect(() => {
    if (!canvasRef.current) return;

    const fabricCanvas = new fabric.Canvas(canvasRef.current, {
      width: 800,
      height: 600,
      backgroundColor: '#f3f4f6',
    });

    // Загрузка изображения
    if (imageUrl) {
      fabric.Image.fromURL(imageUrl, (img) => {
        const scale = Math.min(
          fabricCanvas.width / img.width,
          fabricCanvas.height / img.height
        );
        
        img.scale(scale);
        img.set({
          selectable: false,
          evented: false,
        });
        
        fabricCanvas.setBackgroundImage(img, fabricCanvas.renderAll.bind(fabricCanvas));
      });
    }

    // Загрузка сохраненных данных
    if (initialData) {
      fabricCanvas.loadFromJSON(initialData, () => {
        fabricCanvas.renderAll();
      });
    }

    setCanvas(fabricCanvas);

    return () => {
      fabricCanvas.dispose();
    };
  }, [imageUrl]);

  // Установка режима рисования
  useEffect(() => {
    if (!canvas) return;

    // Сброс всех режимов
    canvas.isDrawingMode = false;
    canvas.selection = true;

    switch (tool) {
      case 'draw':
        canvas.isDrawingMode = true;
        canvas.freeDrawingBrush.color = color;
        canvas.freeDrawingBrush.width = brushWidth;
        break;

      case 'erase':
        canvas.isDrawingMode = true;
        canvas.freeDrawingBrush.color = '#ffffff';
        canvas.freeDrawingBrush.width = brushWidth * 2;
        break;

      case 'select':
        canvas.selection = true;
        break;

      default:
        canvas.selection = false;
    }

    canvas.renderAll();
  }, [tool, canvas, color, brushWidth]);

  // Обработчики инструментов
  const handleAddCircle = () => {
    if (!canvas) return;
    
    const circle = new fabric.Circle({
      radius: 30,
      fill: 'transparent',
      stroke: color,
      strokeWidth: brushWidth,
      left: 100,
      top: 100,
    });
    
    canvas.add(circle);
    setTool('select');
  };

  const handleAddRect = () => {
    if (!canvas) return;
    
    const rect = new fabric.Rect({
      width: 100,
      height: 60,
      fill: 'transparent',
      stroke: color,
      strokeWidth: brushWidth,
      left: 100,
      top: 100,
    });
    
    canvas.add(rect);
    setTool('select');
  };

  const handleAddText = () => {
    if (!canvas) return;
    
    const text = new fabric.IText('Текст', {
      left: 100,
      top: 100,
      fill: color,
      fontSize: 20,
      fontFamily: 'Arial',
    });
    
    canvas.add(text);
    setTool('select');
  };

  const handleUndo = () => {
    if (!canvas) return;
    const objects = canvas.getObjects();
    if (objects.length > 0) {
      canvas.remove(objects[objects.length - 1]);
    }
  };

  const handleClear = () => {
    if (!canvas) return;
    if (confirm('Очистить все аннотации?')) {
      const objects = canvas.getObjects();
      objects.forEach((obj) => canvas.remove(obj));
    }
  };

  const handleSave = () => {
    if (!canvas) return;
    const data = canvas.toJSON();
    onSave && onSave(data);
  };

  const handleExport = () => {
    if (!canvas) return;
    const dataURL = canvas.toDataURL({
      format: 'png',
      quality: 1,
    });
    
    const link = document.createElement('a');
    link.download = 'annotation.png';
    link.href = dataURL;
    link.click();
  };

  const colors = [
    '#FF0000', // Красный
    '#00FF00', // Зеленый
    '#0000FF', // Синий
    '#FFFF00', // Желтый
    '#FF00FF', // Пурпурный
    '#00FFFF', // Голубой
    '#FFA500', // Оранжевый
    '#800080', // Фиолетовый
    '#000000', // Черный
    '#FFFFFF', // Белый
  ];

  if (readOnly) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <canvas ref={canvasRef} />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap gap-2">
          {/* Tools */}
          <div className="flex gap-2 border-r pr-2">
            <button
              onClick={() => setTool('select')}
              className={`p-2 rounded transition ${
                tool === 'select'
                  ? 'bg-blue-100 text-blue-600'
                  : 'hover:bg-gray-100'
              }`}
              title="Выбор (V)"
            >
              <Move className="w-5 h-5" />
            </button>
            <button
              onClick={() => setTool('draw')}
              className={`p-2 rounded transition ${
                tool === 'draw'
                  ? 'bg-blue-100 text-blue-600'
                  : 'hover:bg-gray-100'
              }`}
              title="Карандаш (P)"
            >
              <Pencil className="w-5 h-5" />
            </button>
            <button
              onClick={() => setTool('erase')}
              className={`p-2 rounded transition ${
                tool === 'erase'
                  ? 'bg-blue-100 text-blue-600'
                  : 'hover:bg-gray-100'
              }`}
              title="Ластик (E)"
            >
              <Eraser className="w-5 h-5" />
            </button>
          </div>

          {/* Shapes */}
          <div className="flex gap-2 border-r pr-2">
            <button
              onClick={handleAddCircle}
              className="p-2 rounded hover:bg-gray-100 transition"
              title="Круг (C)"
            >
              <Circle className="w-5 h-5" />
            </button>
            <button
              onClick={handleAddRect}
              className="p-2 rounded hover:bg-gray-100 transition"
              title="Прямоугольник (R)"
            >
              <Square className="w-5 h-5" />
            </button>
            <button
              onClick={handleAddText}
              className="p-2 rounded hover:bg-gray-100 transition"
              title="Текст (T)"
            >
              <Type className="w-5 h-5" />
            </button>
          </div>

          {/* Color Picker */}
          <div className="flex items-center gap-2 border-r pr-2">
            <Palette className="w-5 h-5 text-gray-600" />
            <div className="flex gap-1">
              {colors.map((c) => (
                <button
                  key={c}
                  onClick={() => setColor(c)}
                  className={`w-6 h-6 rounded border-2 transition ${
                    color === c ? 'border-gray-900 scale-110' : 'border-gray-300'
                  }`}
                  style={{ backgroundColor: c }}
                  title={c}
                />
              ))}
            </div>
          </div>

          {/* Brush Width */}
          <div className="flex items-center gap-2 border-r pr-2">
            <span className="text-sm text-gray-600">Толщина:</span>
            <input
              type="range"
              min="1"
              max="20"
              value={brushWidth}
              onChange={(e) => setBrushWidth(parseInt(e.target.value))}
              className="w-24"
            />
            <span className="text-sm font-medium w-6">{brushWidth}</span>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={handleUndo}
              className="p-2 rounded hover:bg-gray-100 transition"
              title="Отменить (Ctrl+Z)"
            >
              <Undo className="w-5 h-5" />
            </button>
            <button
              onClick={handleClear}
              className="p-2 rounded hover:bg-gray-100 transition text-red-600"
              title="Очистить"
            >
              <Trash2 className="w-5 h-5" />
            </button>
            <button
              onClick={handleExport}
              className="p-2 rounded hover:bg-gray-100 transition"
              title="Скачать"
            >
              <Download className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Hints */}
        <div className="mt-3 text-xs text-gray-600 flex gap-4">
          <span>💡 Используйте Delete для удаления выбранного объекта</span>
          <span>💡 Двойной клик на текст для редактирования</span>
        </div>
      </div>

      {/* Canvas */}
      <div className="bg-white rounded-lg shadow p-4">
        <canvas ref={canvasRef} className="border border-gray-300 rounded" />
      </div>

      {/* Save Button */}
      {onSave && (
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Сохранить аннотации
          </button>
        </div>
      )}
    </div>
  );
};

export default CanvasEditor;