import { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import api from '../../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const TestStatsChart = ({ testId, days = 30 }) => {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    loadTrendData();
  }, [testId, days]);

  const loadTrendData = async () => {
    setLoading(true);
    try {
      const response = await api.get(
        `/api/statistics/trend?test_id=${testId}&days=${days}`
      );

      const data = response.data.data;

      setChartData({
        labels: data.map((point) => point.date),
        datasets: [
          {
            label: 'Средний балл',
            data: data.map((point) => point.value),
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
          },
        ],
      });
    } catch (error) {
      console.error('Failed to load trend data:', error);
    } finally {
      setLoading(false);
    }
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `Средний балл: ${context.parsed.y.toFixed(1)}%`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: (value) => `${value}%`,
        },
      },
    },
  };

  if (loading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!chartData || chartData.labels.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-500">
        Недостаточно данных для построения графика
      </div>
    );
  }

  return (
    <div className="h-64">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default TestStatsChart;