import { Exam, ExamResult } from "@/types";
import api from "@/views/ia/service/api";


interface generateExamProps {
  topic: string,
  difficulty?: "easy" | "medium" | "hard"
  num_questions?: number
  subtopics?: string[]
}

interface validateExamProps {
  exam_id: string,
  answers: Record<string, string>
}
// Servicios para exámenes
export const examService = {
  generateExam: async ({...props}: generateExamProps): Promise<Exam> => {
    const response = await api.post(`/exam/generate`, props);
    return response.data;
  },
  
  submitExam: async ({...props} : validateExamProps): Promise<ExamResult> => {
    const response = await api.post('/exam/validate', props);
    return response.data;
  },
};