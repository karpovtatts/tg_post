/**
 * Компонент поля ввода
 */
import { InputHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export function Input({ label, className, ...props }: InputProps) {
  const input = (
    <input
      className={cn(
        'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg',
        'text-white placeholder-gray-500',
        'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
        'transition-colors',
        className
      )}
      {...props}
    />
  );
  
  if (label) {
    return (
      <label className="block">
        <span className="block text-sm text-gray-400 mb-1">{label}</span>
        {input}
      </label>
    );
  }
  
  return input;
}

