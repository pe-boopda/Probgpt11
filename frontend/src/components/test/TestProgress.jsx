const TestProgress = ({ current, total, answered }) => {
  const percentage = (current / total) * 100;
  const answeredPercentage = (answered / total) * 100;

  return (
    <div className="mt-4">
      <div className="flex justify-between text-sm text-gray-600 mb-2">
        <span>Прогресс</span>
        <span>
          {answered} из {total} отвечено
        </span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className="h-full flex">
          {/* Answered portion */}
          <div
            className="bg-green-500 transition-all duration-300"
            style={{ width: `${answeredPercentage}%` }}
          />
          {/* Current position (if not answered) */}
          {current > answered && (
            <div
              className="bg-blue-300 transition-all duration-300"
              style={{ width: `${((current - answered) / total) * 100}%` }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default TestProgress;