/**
 * Компонент поисковой строки
 */
import { Input } from './ui/Input';
import { useAppStore } from '../lib/store';
import { useDebouncedCallback } from '../hooks/useDebounce';

export function SearchBar() {
  const { searchQuery, setSearchQuery } = useAppStore();
  
  const debouncedSetSearch = useDebouncedCallback((value: string) => {
    setSearchQuery(value);
  }, 300);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    debouncedSetSearch(value);
  };
  
  return (
    <Input
      type="text"
      placeholder="Поиск промптов..."
      defaultValue={searchQuery}
      onChange={handleChange}
      className="w-full"
    />
  );
}

