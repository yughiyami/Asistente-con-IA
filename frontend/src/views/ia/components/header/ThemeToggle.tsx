'use client';

import { useState, useEffect } from 'react';
import { useAppStore } from '@/store/store';

import { FiSun, FiMoon, FiMonitor } from 'react-icons/fi';

export default function ThemeToggle() {
  const { theme, setTheme } = useAppStore();
  const [mounted, setMounted] = useState(false);

  // Necesario para evitar errores de hidratación
  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }
  }, [theme]);

  if (!mounted) {
    return null;
  }

  return (
    <div className="flex items-center justify-center">
      <div className="flex space-x-1 bg-gray-200 dark:bg-gray-700 p-1 rounded-md">
        <button
          onClick={() => setTheme('light')}
          className={`p-1.5 rounded-md ${
            theme === 'light' ? 'bg-white dark:bg-gray-600 shadow-xs' : ''
          }`}
          aria-label="Tema claro"
        >
          <FiSun className="w-4 h-4" />
        </button>
        
        <button
          onClick={() => setTheme('dark')}
          className={`p-1.5 rounded-md ${
            theme === 'dark' ? 'bg-white dark:bg-gray-600 shadow-xs' : ''
          }`}
          aria-label="Tema oscuro"
        >
          <FiMoon className="w-4 h-4" />
        </button>
        
        <button
          onClick={() => setTheme('system')}
          className={`p-1.5 rounded-md ${
            theme === 'system' ? 'bg-white dark:bg-gray-600 shadow-xs' : ''
          }`}
          aria-label="Tema del sistema"
        >
          <FiMonitor className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}