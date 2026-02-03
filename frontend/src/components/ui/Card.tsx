/**
 * Компонент карточки
 */
import { ReactNode } from 'react';
import { cn } from '../../lib/utils';

interface CardProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div
      className={cn(
        'bg-gray-800 border border-gray-700 rounded-lg p-4',
        'transition-shadow hover:shadow-lg',
        className
      )}
    >
      {children}
    </div>
  );
}

