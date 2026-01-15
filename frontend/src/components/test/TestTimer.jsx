import { Clock } from 'lucide-react';
import sessionService from '../../services/sessionService';

const TestTimer = ({ timeRemaining, totalTime }) => {
  const percentage = (timeRemaining / totalTime) * 100;
  
  const getColorClass = () => {
    if (percentage > 50) return 'text-green-600';
    if (percentage > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getBarColor = () => {
    if (percentage > 50) return 'bg-green-500';
    if (percentage > 20) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="flex items-center gap-3">
      <div className="text-right">
        <div className={`text-2xl font-bold ${getColorClass()}`}>
          {sessionService.formatTime(timeRemaining)}
        </div>
        <div className="text-xs text-gray-600">осталось</div>
      </div>
      <div className="w-32">
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full ${getBarColor()} transition-all duration-1000`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default TestTimer;