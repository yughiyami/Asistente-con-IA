import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Message, ChatMode, ThemeMode, PredefinedPrompt } from '@/types';

// Definir el estado de la aplicación
interface AppState {
  messages: Message[];
  sessionId: string | null;
  loading: boolean;
  mode: ChatMode;
  Modelmode: boolean;
  theme: ThemeMode;
  predefinedPrompts: PredefinedPrompt[];
  
  // Acciones
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setSessionId: (sessionId: string) => void;
  setLoading: (loading: boolean) => void;
  setMode: (mode: ChatMode) => void;
  setTheme: (theme: ThemeMode) => void;
  setModelMode: (mode: boolean) => void;
}

// Crear store
export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      messages: [],
      Modelmode: true,
      sessionId: null,
      loading: false,
      mode: 'chat',
      theme: 'system',
      
      // Lista de prompts predefinidos
      predefinedPrompts: [
        // Modo Chat
        { id: 'cpu', text: 'Explícame la arquitectura de CPU', icon: '🔍', mode: 'chat' },
        { id: 'memory', text: 'Cómo funciona la memoria caché', icon: '💾', mode: 'chat' },
        { id: 'pipeline', text: 'Qué es el pipeline en procesadores', icon: '⚙️', mode: 'chat' },
        
        // Modo Examen
        { id: 'exam-cpu', text: 'Generar examen sobre CPU', icon: '📝', mode: 'exam' },
        { id: 'exam-memory', text: 'Generar examen sobre memoria', icon: '📝', mode: 'exam' },
        { id: 'exam-architecture', text: 'Generar examen sobre arquitectura', icon: '📝', mode: 'exam' },
        
        // Modo Juego
        { id: 'game-cache', text: 'Jugar Simulador de Memoria Cache', icon: '🎮', mode: 'game' },
        { id: 'game-binary', text: 'Jugar Conversor Binario', icon: '🎮', mode: 'game' },
        { id: 'game-circuits', text: 'Jugar Constructor de Circuitos', icon: '🎮', mode: 'game' },
        { id: 'game-assembler', text: 'Jugar Ensamblador Interactivo', icon: '🎮', mode: 'game' },
        { id: 'game-hangman', text: 'Jugar Ahorcado', icon: '🎮', mode: 'game' },
        { id: 'game-word', text: 'Jugar Palabras Desordenadas', icon: '🎮', mode: 'game' },
      ],
      
      // Acciones
      setMessages: (messages) => set({ messages }),
      addMessage: (message) => set((state) => ({ 
        messages: [...state.messages, message] 
      })),
      clearMessages: () => set({ messages: [] }),
      setSessionId: (sessionId) => set({ sessionId }),
      setLoading: (loading) => set({ loading }),
      setMode: (mode) => set({ mode }),
      setTheme: (theme) => set({ theme }),
      setModelMode: (mode) => set({ Modelmode: mode }),
    }),
    {
      name: 'computer-arch-assistant',
      partialize: (state) => ({ 
        sessionId: state.sessionId,
        theme: state.theme,
      }),
    }
  )
);