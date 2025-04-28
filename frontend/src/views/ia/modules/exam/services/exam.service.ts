import { Exam } from "@/types/exam";

export interface ExamQuestion {
  id: string;
  question: string;
  type: 'multiple-choice' | 'true-false';
  options?: string[];
  points: number;
  correct_answer?: unknown;
  explanation?: string;
}

export interface ExamAdapter {
  questions: ExamQuestion[]
}

export async function makeExam({questions}: ExamAdapter) : Promise<Exam> {

  return {
    questions: questions.map((question) => ({ ...question,
      chosen_answer: null,
      correct_answer: question.correct_answer,
    }))
    // Aquí puedes agregar métodos y propiedades para interactuar con el examen
    // Por
  }
}