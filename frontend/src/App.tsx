import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SearchBar } from './components/SearchBar';
import { TagFilter } from './components/TagFilter';
import { TagCloud } from './components/TagCloud';
import { PromptList } from './components/PromptList';
import { OfflineIndicator } from './components/OfflineIndicator';
import { Button } from './components/ui/Button';
import { useAppStore } from './lib/store';
import { useState } from 'react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const { showPinnedOnly, setShowPinnedOnly, clearFilters, compactMode, setCompactMode } = useAppStore();
  const [showTagCloud, setShowTagCloud] = useState(true);
  
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-black text-white">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          {/* Заголовок */}
          <header className="mb-8">
            <h1 className="text-4xl font-bold mb-2">PromptVault</h1>
            <p className="text-gray-400">
              Персональное хранилище промптов для AI
            </p>
          </header>
          
          {/* Фильтры */}
          <div className="mb-6 space-y-4">
            <SearchBar />
            
            <div className="flex items-center gap-4 flex-wrap">
              <Button
                variant={showPinnedOnly === true ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setShowPinnedOnly(showPinnedOnly === true ? null : true)}
              >
                📌 Только закрепленные
              </Button>
              
              <Button
                variant={compactMode ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setCompactMode(!compactMode)}
                title={compactMode ? 'Переключить на обычный режим' : 'Переключить на компактный режим'}
              >
                {compactMode ? '📋' : '📄'} {compactMode ? 'Компактный' : 'Обычный'}
              </Button>
              
              <Button
                variant={showTagCloud ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setShowTagCloud(!showTagCloud)}
              >
                {showTagCloud ? '☁️' : '🏷️'} {showTagCloud ? 'Облако' : 'Список'}
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
              >
                Очистить фильтры
              </Button>
            </div>
            
            {showTagCloud ? <TagCloud /> : <TagFilter />}
          </div>
          
          {/* Список промптов */}
          <PromptList />
        </div>
        
        {/* Индикатор офлайн статуса */}
        <OfflineIndicator />
      </div>
    </QueryClientProvider>
  );
}

export default App

