import { useState, useEffect } from 'react';
import { ArrowRight, RefreshCw } from 'lucide-react';

const MatchingQuestion = ({ question, answer, onAnswer }) => {
  const [matches, setMatches] = useState({});
  const [selectedLeft, setSelectedLeft] = useState(null);

  useEffect(() => {
    if (answer?.matches) {
      setMatches(answer.matches);
    }
  }, [answer]);

  // Разделение вариантов на левую и правую колонки
  const leftItems = question.options.filter((opt) => opt.match_id?.startsWith('left_'));
  const rightItems = question.options.filter((opt) => opt.match_id?.startsWith('right_'));

  const handleLeftClick = (leftId) => {
    if (selectedLeft === leftId) {
      setSelectedLeft(null);
    } else {
      setSelectedLeft(leftId);
    }
  };

  const handleRightClick = (rightId) => {
    if (!selectedLeft) return;

    const newMatches = { ...matches };
    
    // Удалить предыдущее соответствие этого правого элемента
    Object.keys(newMatches).forEach((key) => {
      if (newMatches[key] === rightId) {
        delete newMatches[key];
      }
    });

    // Создать новое соответствие
    newMatches[selectedLeft] = rightId;
    
    setMatches(newMatches);
    setSelectedLeft(null);
    onAnswer({ matches: newMatches });
  };

  const handleRemoveMatch = (leftId) => {
    const newMatches = { ...matches };
    delete newMatches[leftId];
    setMatches(newMatches);
    onAnswer({ matches: newMatches });
  };

  const handleReset = () => {
    setMatches({});
    setSelectedLeft(null);
    onAnswer({ matches: {} });
  };

  const getRightItemById = (rightId) => {
    return rightItems.find((item) => item.match_id === rightId);
  };

  const isRightItemUsed = (rightId) => {
    return Object.values(matches).includes(rightId);
  };

  return (
    <div className="space-y-4">
      {/* Instructions */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-900">
          💡 Кликните на элемент слева, затем на соответствующий элемент справа для создания пары
        </p>
      </div>

      {/* Matching Interface */}
      <div className="grid grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Элементы:</h3>
          {leftItems.map((item) => {
            const isSelected = selectedLeft === item.match_id;
            const hasMatch = matches[item.match_id];
            const matchedRight = hasMatch ? getRightItemById(matches[item.match_id]) : null;

            return (
              <div key={item.match_id}>
                <button
                  onClick={() => handleLeftClick(item.match_id)}
                  className={`w-full p-4 rounded-lg border-2 text-left transition ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50 shadow-md'
                      : hasMatch
                      ? 'border-green-300 bg-green-50'
                      : 'border-gray-300 bg-white hover:border-gray-400'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{item.option_text}</span>
                    {hasMatch && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemoveMatch(item.match_id);
                        }}
                        className="text-red-600 hover:text-red-700"
                        title="Удалить пару"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </button>
                
                {/* Show match */}
                {matchedRight && (
                  <div className="mt-2 flex items-center gap-2 text-sm text-green-700">
                    <ArrowRight className="w-4 h-4" />
                    <span>{matchedRight.option_text}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Right Column */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Соответствия:</h3>
          {rightItems.map((item) => {
            const isUsed = isRightItemUsed(item.match_id);
            const canSelect = selectedLeft !== null;

            return (
              <button
                key={item.match_id}
                onClick={() => handleRightClick(item.match_id)}
                disabled={!canSelect}
                className={`w-full p-4 rounded-lg border-2 text-left transition ${
                  isUsed
                    ? 'border-green-300 bg-green-50 opacity-50'
                    : canSelect
                    ? 'border-gray-300 bg-white hover:border-blue-400 hover:bg-blue-50'
                    : 'border-gray-200 bg-gray-50 cursor-not-allowed'
                }`}
              >
                <span className={isUsed ? 'line-through' : ''}>
                  {item.option_text}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Progress */}
      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
        <div className="text-sm text-gray-600">
          Сопоставлено: {Object.keys(matches).length} из {leftItems.length}
        </div>
        <button
          onClick={handleReset}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
        >
          <RefreshCw className="w-4 h-4" />
          Сбросить все
        </button>
      </div>

      {/* Progress Bar */}
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 transition-all duration-300"
          style={{
            width: `${(Object.keys(matches).length / leftItems.length) * 100}%`,
          }}
        />
      </div>
    </div>
  );
};

export default MatchingQuestion;