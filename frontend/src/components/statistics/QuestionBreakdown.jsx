import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const QuestionBreakdown = ({ questions }) => {
  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyLabel = (difficulty) => {
    switch (difficulty) {
      case 'easy':
        return 'Легкий';
      case 'medium':
        return 'Средний';
      case 'hard':
        return 'Сложный';
      default:
        return '-';
    }
  };

  return (
    <div className="space-y-4">
      {questions.map((question, index) => (
        <div key={question.question_id} className="border border-gray-200 rounded-lg p-4">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-sm font-medium text-gray-600">
                  Вопрос {index + 1}
                </span>
                <span
                  className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(
                    question.difficulty
                  )}`}
                >
                  {getDifficultyLabel(question.difficulty)}
                </span>
                <span className="text-xs text-gray-600">
                  {question.points} балл(а)
                </span>
              </div>
              <p className="text-gray-900">{question.question_text}</p>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {question.total_answers}
              </div>
              <div className="text-xs text-gray-600">Всего ответов</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-green-600 flex items-center justify-center gap-1">
                <CheckCircle className="w-5 h-5" />
                {question.correct_answers}
              </div>
              <div className="text-xs text-gray-600">Правильных</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-red-600 flex items-center justify-center gap-1">
                <XCircle className="w-5 h-5" />
                {question.incorrect_answers}
              </div>
              <div className="text-xs text-gray-600">Неправильных</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {question.correct_rate.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-600">% правильных</div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 transition-all"
                style={{ width: `${question.correct_rate}%` }}
              />
            </div>
          </div>

          {/* Warning if too hard or too easy */}
          {(question.correct_rate < 30 || question.correct_rate > 95) && (
            <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-yellow-800">
                {question.correct_rate < 30
                  ? 'Этот вопрос очень сложный - возможно, стоит его переформулировать или упростить'
                  : 'Этот вопрос слишком простой - рассмотрите возможность усложнить его'}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default QuestionBreakdown;