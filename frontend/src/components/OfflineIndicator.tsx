/**
 * Компонент индикатора офлайн статуса
 */
import { useOnlineStatus } from '../hooks/useOnlineStatus';

export function OfflineIndicator() {
  const isOnline = useOnlineStatus();

  if (isOnline) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-auto bg-yellow-600 text-black px-4 py-2 rounded-lg shadow-lg z-50">
      <div className="flex items-center gap-2">
        <span>⚠️</span>
        <span className="font-medium">Офлайн режим. Данные из кэша.</span>
      </div>
    </div>
  );
}

