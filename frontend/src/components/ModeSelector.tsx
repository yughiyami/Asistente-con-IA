'use client';

import { useAppStore } from '@/store/store';
import { FiMessageSquare, FiFileText } from 'react-icons/fi';
import { FaGamepad } from 'react-icons/fa';

export default function ModeSelector() {
  const { mode, setMode, clearMessages } = useAppStore();

  const handleModeChange = (newMode: 'chat' | 'exam' | 'game') => {
    if (mode !== newMode) {
      setMode(newMode);
      clearMessages();
    }
  };

  return (
    <div className="flex items-center space-x-1 bg-gray-200 dark:bg-gray-700 p-1 rounded-md">
      <button
        onClick={() => handleModeChange('chat')}
        className={`flex items-center px-3 py-1.5 rounded-md ${
          mode === 'chat' ? 'bg-white dark:bg-gray-600 shadow-sm' : ''
        }`}
        aria-label="Modo Chat"
      >
        <FiMessageSquare className="w-4 h-4 mr-2" />
        <span className="text-sm">Chat</span>
      </button>
      
      <button
        onClick={() => handleModeChange('exam')}
        className={`flex items-center px-3 py-1.5 rounded-md ${
          mode === 'exam' ? 'bg-white dark:bg-gray-600 shadow-sm' : ''
        }`}
        aria-label="Modo Examen"
      >
        <FiFileText className="w-4 h-4 mr-2" />
        <span className="text-sm">Examen</span>
      </button>
      
      <button
        onClick={() => handleModeChange('game')}
        className={`flex items-center px-3 py-1.5 rounded-md ${
          mode === 'game' ? 'bg-white dark:bg-gray-600 shadow-sm' : ''
        }`}
          aria-label="Modo Juegos"
        >
          <FaGamepad className="w-4 h-4 mr-2" />
        <span className="text-sm">Juegos</span>
      </button>
    </div>
  );
}