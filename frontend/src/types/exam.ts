export type MultipleChoiceOption = {
  key: string,
  value: string | number | boolean
}

export type ExamQuestion = {
  id: string;
  question: string;
  type: 'multiple-choice' // | 'true-false';
  options?: MultipleChoiceOption[];
  is_correct?: boolean;
  chosen_answer?: unknown | null;
  correct_answer?: unknown;
  explanation?: string;
}

export type Exam = {
  exam_id: string
  title: string
  questions: ExamQuestion[];
  score?: number,
  feedback?: string,
}