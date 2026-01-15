import { useState, useEffect } from 'react';
import { GripVertical, ArrowUp, ArrowDown, RefreshCw } from 'lucide-react';

const OrderingQuestion = ({ question, answer, onAnswer }) => {
  const [items, setItems] = useState([]);
  const [draggedItem, setDraggedItem] = useState(null);

  useEffect(() => {
    if (answer?.order) {
      // Восстановить порядок из ответа
      const orderedItems = answer.order.map((id) =>
        question.options.find((opt) => opt.id === id)
      ).filter(Boolean);
      setItems(orderedItems);
    } else {
      // Начальный порядок - перемешанный
      const shuffled = [...question.options].sort(() => Math.random() - 0.5);
      setItems(shuffled);
    }
  }, [question, answer]);

  const handleDragStart = (e, index) => {
    setDraggedItem(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e, index) => {
    e.preventDefault();
    
    if (draggedItem === null || draggedItem === index) return;

    const newItems = [...items];
    const draggedElement = newItems[draggedItem];
    
    newItems.splice(draggedItem, 1);
    newItems.splice(index, 0, draggedElement);
    
    setItems(newItems);
    setDraggedItem(index);
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
    saveOrder();
  };

  const handleMoveUp = (index) => {
    if (index === 0) return;
    
    const newItems = [...items];
    [newItems[index - 1], newItems[index]] = [newItems[index], newItems[index - 1]];
    
    setItems(newItems);
    saveOrder(newItems);
  };

  const handleMoveDown = (index) => {
    if (index === items.length - 1) return;
    
    const newItems = [...items];
    [newItems[index], newItems[index + 1]] = [newItems[index + 1], newItems[index]];
    
    setItems(newItems);
    saveOrder(newItems);
  };

  const handleReset = () => {
    const shuffled = [...question.options].sort(() => Math.random() - 0.5);
    setItems(shuffled);
    onAnswer({ order: shuffled.map((item) => item.id) });
  };

  const saveOrder = (itemsToSave = items) => {
    onAnswer({ order: itemsToSave.map((item) => item.id) });
  };

  return (
    <div className="space-y-4">
      {/* Instructions */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-900">
          💡 Перетаскивайте элементы или используйте стрелки для изменения порядка
        </p>
      </div>

      {/* Ordering Interface */}
      <div className="space-y-2">
        {items.map((item, index) => (
          <div
            key={item.id}
            draggable
            onDragStart={(e) => handleDragStart(e, index)}
            onDragOver={(e) => handleDragOver(e, index)}
            onDragEnd={handleDragEnd}
            className={`flex items-center gap-3 p-4 bg-white border-2 rounded-lg transition ${
              draggedItem === index
                ? 'border-blue-500 shadow-lg opacity-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            {/* Drag Handle */}
            <div className="cursor-move text-gray-400 hover:text-gray-600">
              <GripVertical className="w-5 h-5" />
            </div>

            {/* Order Number */}
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold">
              {index + 1}
            </div>

            {/* Item Text */}
            <div className="flex-1 font-medium text-gray-900">
              {item.option_text}
            </div>

            {/* Move Buttons */}
            <div className="flex gap-1">
              <button
                onClick={() => handleMoveUp(index)}
                disabled={index === 0}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded transition disabled:opacity-30 disabled:cursor-not-allowed"
                title="Переместить вверх"
              >
                <ArrowUp className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleMoveDown(index)}
                disabled={index === items.length - 1}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded transition disabled:opacity-30 disabled:cursor-not-allowed"
                title="Переместить вниз"
              >
                <ArrowDown className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Reset Button */}
      <div className="flex justify-end">
        <button
          onClick={handleReset}
          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
        >
          <RefreshCw className="w-4 h-4" />
          Перемешать заново
        </button>
      </div>

      {/* Hint */}
      <div className="text-sm text-gray-600 text-center">
        {items.length} элементов для упорядочивания
      </div>
    </div>
  );
};

export default OrderingQuestion;