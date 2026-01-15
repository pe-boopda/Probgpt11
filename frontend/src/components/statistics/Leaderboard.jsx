import { useState, useEffect } from 'react';
import { Trophy, Medal } from 'lucide-react';
import api from '../../services/api';

const Leaderboard = ({ testId, groupId, limit = 10 }) => {
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    loadLeaderboard();
  }, [testId, groupId, limit]);

  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (testId) params.append('test_id', testId);
      if (groupId) params.append('group_id', groupId);
      params.append('limit', limit);

      const response = await api.get(`/api/statistics/leaderboard?${params}`);
      setEntries(response.data.entries);
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank) => {
    switch (rank) {
      case 1:
        return <Trophy className="w-6 h-6 text-yellow-500" />;
      case 2:
        return <Medal className="w-6 h-6 text-gray-400" />;
      case 3:
        return <Medal className="w-6 h-6 text-orange-600" />;
      default:
        return (
          <div className="w-6 h-6 flex items-center justify-center text-gray-600 font-semibold">
            {rank}
          </div>
        );
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        Пока нет данных для отображения
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {entries.map((entry) => (
        <div
          key={entry.student_id}
          className={`flex items-center gap-4 p-4 rounded-lg border-2 transition ${
            entry.rank <= 3
              ? 'border-blue-200 bg-blue-50'
              : 'border-gray-200 bg-white hover:bg-gray-50'
          }`}
        >
          {/* Rank */}
          <div className="flex-shrink-0">{getRankIcon(entry.rank)}</div>

          {/* Student Info */}
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-gray-900 truncate">
              {entry.student_name}
            </div>
            {entry.group_name && (
              <div className="text-sm text-gray-600">{entry.group_name}</div>
            )}
          </div>

          {/* Score */}
          <div className="text-right">
            <div className={`text-2xl font-bold ${getScoreColor(entry.score)}`}>
              {entry.score.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-600">
              {entry.tests_completed} тест(ов)
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Leaderboard;