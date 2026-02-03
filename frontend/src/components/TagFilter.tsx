/**
 * Компонент фильтра по тегам
 */
import { useEffect } from 'react';
import { Badge } from './ui/Badge';
import { useAppStore } from '../lib/store';
import { useQuery } from '@tanstack/react-query';
import { tagsApi } from '../lib/api';
import { saveTags } from '../lib/indexeddb';
import { useOnlineStatus } from '../hooks/useOnlineStatus';

export function TagFilter() {
  const { selectedTags, setSelectedTags, setTags } = useAppStore();
  
  const isOnline = useOnlineStatus();
  
  const { data: tags = [] } = useQuery({
    queryKey: ['tags'],
    queryFn: tagsApi.getTags,
    onSuccess: (data) => {
      setTags(data);
    },
  });
  
  // Сохранение тегов в IndexedDB
  useEffect(() => {
    if (tags.length > 0 && isOnline) {
      saveTags(tags).catch(console.error);
    }
  }, [tags, isOnline]);
  
  const toggleTag = (tagId: number) => {
    if (selectedTags.includes(tagId)) {
      setSelectedTags(selectedTags.filter((id) => id !== tagId));
    } else {
      if (selectedTags.length < 10) {
        setSelectedTags([...selectedTags, tagId]);
      }
    }
  };
  
  if (tags.length === 0) {
    return null;
  }
  
  return (
    <div className="space-y-2">
      <div className="text-sm text-gray-400">Фильтр по тегам:</div>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <Badge
            key={tag.id}
            variant={selectedTags.includes(tag.id) ? 'primary' : 'default'}
            onClick={() => toggleTag(tag.id)}
          >
            {tag.name}
          </Badge>
        ))}
      </div>
    </div>
  );
}

