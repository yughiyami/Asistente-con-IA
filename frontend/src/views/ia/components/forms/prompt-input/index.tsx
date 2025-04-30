'use client';

import { useState, useRef, useEffect } from 'react';
import { useAppStore } from '@/store/store';
import { chatService } from '@/views/ia/service/api';
import { FiSend, FiX } from 'react-icons/fi';
import { Toaster, toast } from 'sonner';

export default function PromptInput() {
  const [input, setInput] = useState('');
  const [rows, setRows] = useState(1);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  
  const { 
    mode, 
    sessionId, 
    setSessionId, 
    loading, 
    setLoading, 
    addMessage, 
    predefinedPrompts
  } = useAppStore();
  
  // Ajuste automático de altura del textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 200)}px`;
      
      // Determinar el número de filas
      const newRows = Math.min(Math.floor(inputRef.current.scrollHeight / 24), 5);
      setRows(newRows || 1);
    }
  }, [input]);
  
  // Manejar entrada al presionar Enter (sin Shift)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
  
  // Enviar mensaje
  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    
    const trimmedInput = input.trim();
    setInput('');
    
    // Crear mensaje del usuario
    const userMessage = {
      id: Date.now().toString(),
      content: trimmedInput,
      role: 'user' as const,
      timestamp: new Date().toISOString(),
    };
    
    // Añadir mensaje a la UI
    addMessage(userMessage);
    setLoading(true);
    
    try {
      // Enviar mensaje al backend
      const response = await chatService.sendMessage({
        message: trimmedInput,
        session_id: sessionId || undefined,
        mode: mode,
      });
      
      // Guardar ID de sesión si no existe
      if (!sessionId && response.special_content?.session_id) {
        setSessionId(response.special_content.session_id);
      }
      
      // Crear mensaje del asistente
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        content: response.text,
        role: 'assistant' as const,
        timestamp: new Date().toISOString(),
        images: response.images,
        specialContent: response.special_content ? {
            type: (mode === 'chat' ? 'diagram' : mode) as 'exam' | 'game' | 'diagram',
            data: response.special_content
        } : undefined,
      };
      
      // Añadir respuesta a la UI
      addMessage(assistantMessage);
      
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
      toast.error('Error al enviar mensaje. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };
  
  // Usar un prompt predefinido
  const handlePredefinedPrompt = (prompt: string) => {
    setInput(prompt);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };
  
  // Filtrar prompts según el modo actual
  const filteredPrompts = predefinedPrompts.filter(prompt => prompt.mode === mode);
  
  return (
    <div className="border-t dark:border-gray-800 p-4">
      <Toaster position="bottom-center" />
      
      {/* Prompts predefinidos */}
      {filteredPrompts.length > 0 && (
        <div className="mb-4 overflow-x-auto whitespace-nowrap pb-2 scrollbar-thin">
          <div className="flex space-x-2">
            {filteredPrompts.map((prompt) => (
              <button
                key={prompt.id}
                onClick={() => handlePredefinedPrompt(prompt.text)}
                className="flex items-center px-3 py-1.5 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-full hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <span className="mr-2">{prompt.icon}</span>
                <span className="truncate max-w-[150px]">{prompt.text}</span>
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Área de entrada de mensaje */}
      <div className="flex items-center gap-x-2">
        <div className="flex-1 relative">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={rows}
            placeholder={
              mode === 'chat' ? "Escribe una pregunta sobre arquitectura de computadoras..." :
              mode === 'exam' ? "Solicita un examen sobre un tema específico..." :
              "Elige un juego educativo para aprender..."
            }
            disabled={loading}
            className="w-full resize-none overflow-hidden py-3 px-4 rounded-lg border border-gray-300 dark:border-gray-700 focus:outline-hidden focus:ring-2 focus:ring-primary-500 dark:bg-gray-800 dark:text-white"
          />
            
            {input && (
              <button
                type="button"
                onClick={() => setInput('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <FiX className="w-4 h-4" />
              </button>
            )}
          </div>
          
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="shrink-0 p-3 rounded-lg bg-primary-500 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary-600 transition-colors"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <FiSend className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    );
  }