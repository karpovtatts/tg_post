/**
 * Компонент списка промптов
 */
import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { promptsApi } from '../lib/api';
import { useAppStore } from '../lib/store';
import { PromptCard } from './PromptCard';
import { Button } from './ui/Button';
import { savePrompts, saveTags } from '../lib/indexeddb';
import { useOnlineStatus } from '../hooks/useOnlineStatus';
import { formatDate } from '../lib/utils';

export function PromptList() {
  const { searchQuery, selectedTags, showPinnedOnly, compactMode } = useAppStore();
  const [page, setPage] = useState(1);
  const limit = compactMode ? 100 : 50;
  const isOnline = useOnlineStatus();
  
  const { data, isLoading, isError } = useQuery({
    queryKey: ['prompts', page, searchQuery, selectedTags, showPinnedOnly, compactMode],
    queryFn: () => {
      if (searchQuery) {
        return promptsApi.searchPrompts({
          q: searchQuery,
          page,
          limit,
          tags: selectedTags.length > 0 ? selectedTags : undefined,
          pinned: showPinnedOnly ?? undefined,
        });
      }
      return promptsApi.getPrompts({
        page,
        limit,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
        pinned: showPinnedOnly ?? undefined,
      });
    },
  });
  
  // Сохранение данных в IndexedDB при успешной загрузке
  useEffect(() => {
    if (data && isOnline) {
      savePrompts(data.items).catch(console.error);
      // Сохраняем теги из промптов
      const allTags = data.items.flatMap((p) => p.tags);
      if (allTags.length > 0) {
        saveTags(allTags).catch(console.error);
      }
    }
  }, [data, isOnline]);
  
  // Группировка по датам (должен быть ПЕРЕД условными return)
  const groupedPrompts = useMemo(() => {
    if (compactMode && data?.items) {
      const groups: { [key: string]: typeof data.items } = {};
      data.items.forEach((prompt) => {
        const dateKey = formatDate(prompt.created_at, 'YYYY-MM-DD');
        if (!groups[dateKey]) {
          groups[dateKey] = [];
        }
        groups[dateKey].push(prompt);
      });
      return groups;
    }
    return null;
  }, [data?.items, compactMode]);
  
  if (isLoading) {
    return (
      <div className="text-center text-gray-400 py-8">
        Загрузка промптов...
      </div>
    );
  }
  
  if (isError) {
    return (
      <div className="text-center text-red-400 py-8">
        Ошибка при загрузке промптов
      </div>
    );
  }
  
  if (!data || data.items.length === 0) {
    return (
      <div className="text-center text-gray-400 py-8">
        Промпты не найдены
      </div>
    );
  }
  
  const formatGroupDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === today.toDateString()) {
      return 'Сегодня';
    }
    if (date.toDateString() === yesterday.toDateString()) {
      return 'Вчера';
    }
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
  };
  
  return (
    <div className="space-y-4">
      {/* Информация о количестве */}
      <div className="text-sm text-gray-400">
        Найдено: <span className="text-white font-semibold">{data.total}</span> промптов
        {data.total > limit && (
          <span className="ml-2">
            (показано {((page - 1) * limit) + 1}-{Math.min(page * limit, data.total)})
          </span>
        )}
      </div>
      
      {/* Компактный режим с группировкой */}
      {compactMode && groupedPrompts ? (
        <div className="space-y-6">
          {Object.entries(groupedPrompts)
            .sort((a, b) => b[0].localeCompare(a[0]))
            .map(([dateKey, prompts]) => (
              <div key={dateKey}>
                <h3 className="text-sm font-semibold text-gray-400 mb-3 sticky top-0 bg-black py-2 z-10">
                  {formatGroupDate(dateKey)}
                </h3>
                <div className="space-y-1">
                  {prompts.map((prompt) => (
                    <PromptCard key={prompt.id} prompt={prompt} compact={true} />
                  ))}
                </div>
              </div>
            ))}
        </div>
      ) : (
        /* Обычный режим */
        <div className="grid gap-4">
          {data.items.map((prompt) => (
            <PromptCard key={prompt.id} prompt={prompt} compact={false} />
          ))}
        </div>
      )}
      
      {/* Пагинация */}
      {data.total > limit && (
        <div className="flex items-center justify-center gap-4 pt-4">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            ← Назад
          </Button>
          <span className="text-gray-400 text-sm">
            Страница {page} из {Math.ceil(data.total / limit)}
          </span>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= Math.ceil(data.total / limit)}
          >
            Вперед →
          </Button>
        </div>
      )}
    </div>
  );
}

