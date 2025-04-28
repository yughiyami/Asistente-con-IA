'use client';

// import { useEffect } from 'react';
// import { useAppStore } from '@/store/store';
// import ThemeToggle from '@/components/ThemeToggle';
// import ModeSelector from '@/components/ModeSelector';
// import MessageList from '@/views/ia/components/chat/components/MessageList';
// import MessageInput from '@/views/ia/components/chat/components/MessageInput';
// import { FiCpu, FiInfo } from 'react-icons/fi';
import AsistenteIA from '@/views/ia';

export default function Home() {
  // const { theme, setTheme, mode } = useAppStore();
  
  // // Detectar tema del sistema
  // useEffect(() => {
  //   if (theme === 'system') {
  //     const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  //     document.documentElement.classList.toggle('dark', isDark);
      
  //     // Escuchar cambios en preferencia de tema
  //     const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  //     const handleChange = (e: MediaQueryListEvent) => {
  //       document.documentElement.classList.toggle('dark', e.matches);
  //     };
      
  //     mediaQuery.addEventListener('change', handleChange);
  //     return () => mediaQuery.removeEventListener('change', handleChange);
  //   } else {
  //     document.documentElement.classList.toggle('dark', theme === 'dark');
  //   }
  // }, [theme]);
  
  return (
    <AsistenteIA />
  );
}