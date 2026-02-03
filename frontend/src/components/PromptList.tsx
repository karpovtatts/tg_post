/**
 * Компонент списка промптов
 */
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { promptsApi } from '../lib/api';
import { useAppStore } from '../lib/store';
import { PromptCard } from './PromptCard';
import { Button } from './ui/Button';
import { savePrompts, saveTags } from '../lib/indexeddb';
import { useOnlineStatus } from '../hooks/useOnlineStatus';

export function PromptList() {
  const { searchQuery, selectedTags, showPinnedOnly } = useAppStore();
  const [page, setPage] = useState(1);
  const limit = 50;
  const isOnline = useOnlineStatus();
  
  const { data, isLoading, isError } = useQuery({
    queryKey: ['prompts', page, searchQuery, selectedTags, showPinnedOnly],
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
  
  return (
    <div className="space-y-4">
      <div className="grid gap-4">
        {data.items.map((prompt) => (
          <PromptCard key={prompt.id} prompt={prompt} />
        ))}
      </div>
      
      {/* Пагинация */}
      {data.total > limit && (
        <div className="flex items-center justify-center gap-4">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Назад
          </Button>
          <span className="text-gray-400">
            Страница {page} из {Math.ceil(data.total / limit)}
          </span>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= Math.ceil(data.total / limit)}
          >
            Вперед
          </Button>
        </div>
      )}
    </div>
  );
}

