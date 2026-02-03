/**
 * Компонент облака тегов
 */
import { useQuery } from '@tanstack/react-query';
import { tagsApi, Tag } from '../lib/api';
import { useAppStore } from '../lib/store';
import { Badge } from './ui/Badge';

export function TagCloud() {
  const { selectedTags, setSelectedTags } = useAppStore();
  
  const { data: tags = [], isLoading } = useQuery({
    queryKey: ['tags-cloud'],
    queryFn: () => tagsApi.getTagsCloud(50),
  });
  
  const toggleTag = (tagId: number) => {
    if (selectedTags.includes(tagId)) {
      setSelectedTags(selectedTags.filter((id) => id !== tagId));
    } else {
      if (selectedTags.length < 10) {
        setSelectedTags([...selectedTags, tagId]);
      }
    }
  };
  
  if (isLoading) {
    return (
      <div className="text-center text-gray-400 py-4">
        Загрузка тегов...
      </div>
    );
  }
  
  if (tags.length === 0) {
    return null;
  }
  
  // Вычисляем размеры тегов на основе количества промптов
  const maxCount = Math.max(...tags.map(t => t.prompt_count || 0));
  const minCount = Math.min(...tags.map(t => t.prompt_count || 0));
  const range = maxCount - minCount || 1;
  
  const getTagSize = (count: number): string => {
    if (range === 0) return 'text-sm';
    
    const ratio = (count - minCount) / range;
    if (ratio > 0.7) return 'text-2xl font-bold';
    if (ratio > 0.4) return 'text-xl font-semibold';
    if (ratio > 0.2) return 'text-lg font-medium';
    return 'text-sm';
  };
  
  const getTagOpacity = (count: number): string => {
    if (range === 0) return 'opacity-70';
    
    const ratio = (count - minCount) / range;
    if (ratio > 0.7) return 'opacity-100';
    if (ratio > 0.4) return 'opacity-90';
    if (ratio > 0.2) return 'opacity-80';
    return 'opacity-60';
  };
  
  // Цвета для разных уровней популярности
  const getTagColor = (count: number, isSelected: boolean): string => {
    if (isSelected) {
      return 'bg-blue-600 text-white border-blue-500 shadow-lg shadow-blue-500/50';
    }
    
    const ratio = range > 0 ? (count - minCount) / range : 0.5;
    
    if (ratio > 0.7) {
      return 'bg-gradient-to-r from-purple-600 to-pink-600 text-white border-purple-500 shadow-md';
    }
    if (ratio > 0.4) {
      return 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white border-blue-500';
    }
    if (ratio > 0.2) {
      return 'bg-gradient-to-r from-green-600 to-teal-600 text-white border-green-500';
    }
    return 'bg-gray-700 text-gray-300 border-gray-600';
  };
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <span className="text-2xl">☁️</span>
          Облако тегов
        </h3>
        {selectedTags.length > 0 && (
          <button
            onClick={() => setSelectedTags([])}
            className="text-sm text-blue-400 hover:text-blue-300 font-medium px-3 py-1 rounded-md bg-blue-900/30 hover:bg-blue-900/50 transition-colors"
          >
            ✕ Очистить ({selectedTags.length})
          </button>
        )}
      </div>
      
      <div className="flex flex-wrap gap-3 items-center justify-center py-6 px-4 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-xl border-2 border-gray-700 shadow-2xl min-h-[120px]">
        {tags.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            Теги не найдены. Добавьте теги к промптам для отображения облака.
          </div>
        ) : (
          tags.map((tag) => {
            const isSelected = selectedTags.includes(tag.id);
            const count = tag.prompt_count || 0;
            
            return (
              <button
                key={tag.id}
                onClick={() => toggleTag(tag.id)}
                className={`
                  ${getTagSize(count)} ${getTagOpacity(count)}
                  ${getTagColor(count, isSelected)}
                  transition-all duration-300 
                  hover:scale-125 hover:rotate-2 hover:z-10
                  ${isSelected ? 'ring-4 ring-blue-400 ring-offset-2 ring-offset-gray-900 scale-110' : ''}
                  px-4 py-2 rounded-full
                  border-2 font-medium
                  cursor-pointer
                  shadow-lg
                  relative
                  transform
                `}
                title={`${tag.name} — ${count} ${count === 1 ? 'промпт' : count < 5 ? 'промпта' : 'промптов'}`}
                style={{
                  transform: isSelected ? 'scale(1.1)' : 'scale(1)',
                }}
              >
                <span className="relative z-10">
                  {tag.name}
                </span>
                <span className="ml-2 text-xs opacity-90 font-bold">
                  {count}
                </span>
                {isSelected && (
                  <span className="absolute -top-1 -right-1 bg-blue-400 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                    ✓
                  </span>
                )}
              </button>
            );
          })
        )}
      </div>
      
      {selectedTags.length > 0 && (
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-400">Активные фильтры:</span>
          <div className="flex flex-wrap gap-2">
            {tags
              .filter(tag => selectedTags.includes(tag.id))
              .map(tag => (
                <span
                  key={tag.id}
                  className="px-2 py-1 bg-blue-900/50 text-blue-300 rounded-md text-xs font-medium"
                >
                  {tag.name}
                </span>
              ))}
          </div>
        </div>
      )}
      
      {tags.length > 0 && (
        <div className="text-xs text-gray-500 text-center">
          💡 Кликните на тег для фильтрации промптов. Размер тега показывает его популярность.
        </div>
      )}
    </div>
  );
}

