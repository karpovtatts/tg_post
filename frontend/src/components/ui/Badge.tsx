/**
 * Компонент бейджа (тега)
 */
import { ReactNode } from 'react';
import { cn } from '../../lib/utils';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'primary' | 'success';
  className?: string;
  onClick?: () => void;
}

export function Badge({
  children,
  variant = 'default',
  className,
  onClick,
}: BadgeProps) {
  const variants = {
    default: 'bg-gray-700 text-gray-300',
    primary: 'bg-blue-600 text-white',
    success: 'bg-green-600 text-white',
  };
  
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variants[variant],
        onClick && 'cursor-pointer hover:opacity-80 transition-opacity',
        className
      )}
      onClick={onClick}
    >
      {children}
    </span>
  );
}

