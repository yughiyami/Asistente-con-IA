'use client';
import { useAppStore } from '@/store/store';
import PromptForm from '@/views/ia/components/forms';
import { toast } from 'sonner';
import { useExamStore } from '@/store/exam';
import { generateExam, makeExam } from '../../services/exam.service';
import { examTest } from '../../test/exam';
export default function MessageInput() {
  
  const { 
    mode, 
    sessionId, 
    setSessionId, 
    setLoading, 
    addMessage, 
    predefinedPrompts
  } = useAppStore();


  const {
    setExam,
  } = useExamStore()
  
  // Enviar mensaje
  const handleSubmit = async (input: string) => {
    
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
      const exam = await generateExam({
        topic: input,
        difficulty: "medium",
        num_questions: 7
      });
      
      // // Guardar ID de sesión si no existe
      // if (!sessionId && response.special_content?.session_id) {
      //   setSessionId(response.special_content.session_id);
      // }
      
      // Crear mensaje del asistente
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        content: "Abriendo Examen...",
        role: 'assistant' as const,
        timestamp: new Date().toISOString(),
        // images: response.images,
        // specialContent: response.special_content ? {
        //     type: (mode === 'chat' ? 'diagram' : mode) as 'exam' | 'game' | 'diagram',
        //     data: response.special_content
        // } : undefined,
      };
      
      // Añadir respuesta a la UI
      addMessage(assistantMessage);
      setExam(exam)
      // toast.success('Examen insertado con éxito!')
      
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
      toast.error('Error al enviar mensaje. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };
  
  // Filtrar prompts según el modo actual
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
        onSubmit={handleSubmit}
      />
    );
  }