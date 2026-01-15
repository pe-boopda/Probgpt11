import { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon, Loader2 } from 'lucide-react';
import api from '../../services/api';

const ImageUploader = ({ onUpload, currentImageUrl, onRemove }) => {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(currentImageUrl || null);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Валидация
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Неподдерживаемый формат. Используйте JPG, PNG, GIF или WebP');
      return;
    }

    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      setError('Файл слишком большой. Максимум 10MB');
      return;
    }

    setError('');
    setUploading(true);

    try {
      // Превью
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);

      // Загрузка на сервер
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/api/images/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onUpload && onUpload(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Ошибка при загрузке');
      setPreview(null);
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = () => {
    setPreview(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onRemove && onRemove();
  };

  return (
    <div className="space-y-3">
      {!preview ? (
        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp"
            onChange={handleFileSelect}
            className="hidden"
          />

          {uploading ? (
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
              <p className="text-sm text-gray-600">Загрузка изображения...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                <Upload className="w-8 h-8 text-gray-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Нажмите для загрузки изображения
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  JPG, PNG, GIF или WebP до 10MB
                </p>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="relative">
          <img
            src={preview}
            alt="Preview"
            className="w-full h-64 object-contain bg-gray-100 rounded-lg"
          />
          <button
            onClick={handleRemove}
            className="absolute top-2 right-2 p-2 bg-red-600 text-white rounded-full hover:bg-red-700 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
          {error}
        </div>
      )}
    </div>
  );
};

export default ImageUploader;