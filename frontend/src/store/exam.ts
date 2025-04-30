import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Exam } from '@/types/exam';

// Definir el estado de la aplicación
interface ExamState {
  index: number;
  exam: Exam | null;
  sessionId: string | null;
  
  // Acciones
  answerQuestion: (answer: unknown) => void;
  nextQuestion: () => void;
  setExam: (exam: Exam) => void;
  updateExam: (exam: Exam) => void;
  deleteExam: () => void;
  clearExam: () => void;
  resetIndex: () => void
}

// Crear store
export const useExamStore = create<ExamState>()(
  persist(
    (set) => ({
      totalPoints: 0,
      points: 0,
      index: 0,
      // Atributos
      exam: null,
      sessionId: null,
      loading: false,

      // Acciones
      answerQuestion: (answer) => set((state) => {
        if (state.exam) {
          const updatedExam = { ...state.exam };
          const questionIndex = state.index;
          if (questionIndex !== -1) {
            updatedExam.questions[questionIndex].chosen_answer = answer;
          }
          return {
            exam: updatedExam 
          };
        }
        return state;
      }),
      setExam: (exam) => set({ 
        index: 0,
        exam,
      }),
      updateExam: (exam) => set({ exam }),
      clearExam: () => set({ exam: null }),
      deleteExam: () => set({ exam: null }),
      resetIndex: () => set({ index: 0 }),
      nextQuestion: () => set((state) => {
        if (state.exam) {
          const nextIndex = state.index + 1;
          if (nextIndex < state.exam.questions.length) {
            return {
              index: nextIndex 
            };
          } else {
            return { 
              index: -1 
            }; // Indica que no hay más preguntas
          }
        }
        return state;
      }),
    }),
    {
      name: 'computer-arch-exam-storage', // Nombre del almacenamiento
      partialize: (state) => ({ 
        sessionId: state.sessionId,
      }),
    }
  )
);