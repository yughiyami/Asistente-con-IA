'use client';

// import MessageInput from '@/views/ia/modules/chat/components/MessageInput';
import Footer from './components/footer';
import Header from './components/header';
import { useAppRouter } from './hooks/router/useAppRouter';
import Chat from './modules/chat';
import Exam from './modules/exam';

export default function AsistenteIA() {
  // const {} = useAppRouter()
  // Detectar tema del sistema
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
  const {App} = useAppRouter({
    router: {
      chat: Chat,
      exam: Exam,
      game: Footer,
    }
  })

  return (
    <main className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <Header />
      
      {/* Contenido principal */}
      <div className="flex-1 flex flex-col overflow-hidden max-w-6xl w-full mx-auto">
        {/* <MessageList />
        <MessageInput /> */}
        <App />
        {/* <Chat /> */}
      </div>
      
      {/* Pie de página */}
      <Footer />
    </main>
  );
}