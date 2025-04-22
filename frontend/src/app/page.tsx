'use client';

import { useEffect } from 'react';
import { useAppStore } from '@/store/store';
import ThemeToggle from '@/components/ThemeToggle';
import ModeSelector from '@/components/ModeSelector';
import MessageList from '@/components/chat/MessageList';
import MessageInput from '@/components/chat/MessageInput';
import { FiCpu, FiInfo } from 'react-icons/fi';

export default function Home() {
  const { theme, setTheme, mode } = useAppStore();
  
  // Detectar tema del sistema
  useEffect(() => {
    if (theme === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', isDark);
      
      // Escuchar cambios en preferencia de tema
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e: MediaQueryListEvent) => {
        document.documentElement.classList.toggle('dark', e.matches);
      };
      
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } else {
      document.documentElement.classList.toggle('dark', theme === 'dark');
    }
  }, [theme]);
  
  return (
    <main className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {/* Barra de navegación */}
      <header className="px-4 py-3 bg-white dark:bg-gray-800 shadow-sm z-10">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div className="flex items-center">
            <FiCpu className="w-6 h-6 text-primary-500 mr-2" />
            <h1 className="text-lg font-bold">Asistente de Arquitectura</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <ModeSelector />
            <ThemeToggle />
          </div>
        </div>
      </header>
      
      {/* Contenido principal */}
      <div className="flex-1 flex flex-col overflow-hidden max-w-6xl w-full mx-auto">
        <MessageList />
        <MessageInput />
      </div>
      
      {/* Pie de página */}
      <footer className="px-4 py-2 text-xs text-center text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-center">
          <FiInfo className="w-3 h-3 mr-1" />
          <span>Asistente educativo para Arquitectura de Computadoras • {new Date().getFullYear()}</span>
        </div>
      </footer>
    </main>
  );
}