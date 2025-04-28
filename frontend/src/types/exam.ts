export type ExamQuestion = {
  id: string;
  question: string;
  type: 'multiple-choice' | 'true-false';
  options?: string[];
  points: number;
  chosen_answer?: unknown | null;
  correct_answer?: unknown;
  explanation?: string;
}

export type Exam = {
  questions: ExamQuestion[];
}