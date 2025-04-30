'use client';

import { useAppStore } from '@/store/store';
import { chatService } from '../../services/api';
import PromptForm from '@/views/ia/components/forms';

export default function MessageInput() {
  
  const { 
    mode, 
    sessionId, 
    setSessionId, 
    setLoading, 
    addMessage, 
    predefinedPrompts
  } = useAppStore();
  
  async function sendMessage(input: string) {
     // Crear mensaje del usuario
     const userMessage = {
      id: Date.now().toString(),
      content: input,
      role: 'user' as const,
      timestamp: new Date().toISOString(),
    };
    
    // Añadir mensaje a la UI
    addMessage(userMessage);
    setLoading(true);
    
    try {
      // Enviar mensaje al backend
      const response = await chatService.sendMessage({
        message: input,
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
    } finally {
      setLoading(false);
    }
  }

  const filteredPrompts = predefinedPrompts.filter(prompt => prompt.mode === mode);

  return (
    <PromptForm 
      filteredPrompts={filteredPrompts}
      placeholder={
        mode === 'exam' ? 'Solicita un examen sobre un tema específico...' : 
        mode === 'chat' ? 'Escribe una pregunta sobre arquitectura de computadoras...' :
        mode === 'game' ? 'Elige un juego educativo para aprender...' :
        undefined
      }
      onSubmit={sendMessage}
    />
  );
}