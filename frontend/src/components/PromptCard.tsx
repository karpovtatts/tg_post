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
}

export function PromptCard({ prompt, onPinToggle }: PromptCardProps) {
  const [copied, setCopied] = useState(false);
  
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
      
      {/* Текст промпта */}
      <div className="text-gray-200 whitespace-pre-wrap break-words">
        {prompt.text}
      </div>
      
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

