/**
 * Компонент карточки промпта
 */
import { Prompt } from '../lib/api';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { copyToClipboard, formatDate } from '../lib/utils';
import { useState } from 'react';

interface PromptCardProps {
  prompt: Prompt;
  onPinToggle?: (id: number, pinned: boolean) => void;
  compact?: boolean;
}

export function PromptCard({ prompt, onPinToggle, compact = false }: PromptCardProps) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);
  
  const MAX_PREVIEW_LENGTH = 200;
  const shouldTruncate = prompt.text.length > MAX_PREVIEW_LENGTH;
  const displayText = shouldTruncate && !expanded 
    ? prompt.text.substring(0, MAX_PREVIEW_LENGTH) + '...' 
    : prompt.text;
  
  const handleCopy = async () => {
    const success = await copyToClipboard(prompt.text);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };
  
  const handlePinToggle = () => {
    if (onPinToggle) {
      onPinToggle(prompt.id, !prompt.is_pinned);
    }
  };
  
  if (compact) {
    return (
      <Card className="p-3 hover:bg-gray-900 transition-colors">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              {prompt.is_pinned && (
                <span className="text-yellow-400 text-xs" title="Закреплено">
                  📌
                </span>
              )}
              <span className="text-xs text-gray-500 whitespace-nowrap">
                {formatDate(prompt.created_at)}
              </span>
              {prompt.tags && prompt.tags.length > 0 && (
                <div className="flex gap-1 flex-wrap">
                  {prompt.tags.slice(0, 2).map((tag) => (
                    <Badge key={tag.id} variant="default" className="text-xs px-1.5 py-0">
                      {tag.name}
                    </Badge>
                  ))}
                  {prompt.tags.length > 2 && (
                    <span className="text-xs text-gray-500">+{prompt.tags.length - 2}</span>
                  )}
                </div>
              )}
            </div>
            {/* Миниатюра изображения в компактном режиме */}
            {prompt.image_url && (
              <div className="mb-2 rounded overflow-hidden border border-gray-700">
                <img
                  src={prompt.image_url}
                  alt="Превью"
                  className="w-full h-24 object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              </div>
            )}
            <div className="text-gray-200 text-sm whitespace-pre-wrap break-words" style={{
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }}>
              {displayText}
            </div>
          </div>
          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={handleCopy}
              className="text-gray-400 hover:text-blue-400 transition-colors p-1"
              title="Копировать"
            >
              {copied ? '✓' : '📋'}
            </button>
            <button
              onClick={handlePinToggle}
              className="text-gray-400 hover:text-yellow-400 transition-colors p-1"
              title={prompt.is_pinned ? 'Открепить' : 'Закрепить'}
            >
              {prompt.is_pinned ? '📌' : '📍'}
            </button>
          </div>
        </div>
        {shouldTruncate && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-blue-400 hover:text-blue-300 mt-2"
          >
            {expanded ? 'Свернуть' : 'Развернуть'}
          </button>
        )}
      </Card>
    );
  }
  
  return (
    <Card className="space-y-4">
      {/* Заголовок с закреплением */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          {prompt.is_pinned && (
            <span className="text-yellow-400" title="Закреплено">
              📌
            </span>
          )}
          <span className="text-xs text-gray-500">
            {formatDate(prompt.created_at)}
          </span>
        </div>
        <button
          onClick={handlePinToggle}
          className="text-gray-400 hover:text-yellow-400 transition-colors"
          title={prompt.is_pinned ? 'Открепить' : 'Закрепить'}
        >
          {prompt.is_pinned ? '📌' : '📍'}
        </button>
      </div>
      
      {/* Изображение */}
      {prompt.image_url && (
        <div className="rounded-lg overflow-hidden border border-gray-700">
          <img
            src={prompt.image_url}
            alt="Превью промпта"
            className="w-full h-auto max-h-96 object-cover cursor-pointer hover:opacity-90 transition-opacity"
            onClick={() => window.open(prompt.image_url!, '_blank')}
            onError={(e) => {
              // Если изображение не загрузилось, скрываем его
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
        </div>
      )}
      
      {/* Текст промпта */}
      <div className="text-gray-200 whitespace-pre-wrap break-words">
        {displayText}
      </div>
      {shouldTruncate && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-sm text-blue-400 hover:text-blue-300"
        >
          {expanded ? 'Свернуть' : 'Развернуть полностью'}
        </button>
      )}
      
      {/* Теги */}
      {prompt.tags && prompt.tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {prompt.tags.map((tag) => (
            <Badge key={tag.id} variant="default">
              {tag.name}
            </Badge>
          ))}
        </div>
      )}
      
      {/* Кнопка копирования */}
      <Button
        variant="primary"
        size="lg"
        onClick={handleCopy}
        className="w-full"
      >
        {copied ? '✓ Скопировано!' : '📋 Копировать промпт'}
      </Button>
    </Card>
  );
}

