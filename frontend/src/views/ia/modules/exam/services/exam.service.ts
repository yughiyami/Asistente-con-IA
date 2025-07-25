import { Exam } from "@/types/exam";
import { examService } from "./api";

export interface ExamQuestion {
  id: string;
  text: string;
  // alternatives: {
  //   [key: string]: string | number | boolean;
  // }
  options: { id: string, text: string }[];
  // question: string;
  // type: 'multiple-choice' | 'true-false';
  // options?: string[];
  // points: number;
  // correct_answer?: unknown;
  // explanation?: string;
}

export interface ExamAdapter {
  exam_id: string;
  title: string;
  questions: ExamQuestion[]
  time_limit_minutes: number
}

export async function makeExam({questions, ...props}: ExamAdapter) : Promise<Exam> {
  return { ...props,
    questions: questions.map((question) => ({ ...question,
      chosen_answer: null,
      question: question.text,
      type: 'multiple-choice',
      options: question.options.map((option) => ({ key: option.id, value: option.text })),
    }))
    // Aquí puedes agregar métodos y propiedades para interactuar con el examen
    // Por
  }
}

interface generateExamProps {
  topic: string,
  difficulty?: "easy" | "medium" | "hard"
  num_questions: number
  subtopics?: string[]
}

export async function generateExam({...props}: generateExamProps) {
  console.log("Prepare fetch")
  const exam = await examService.generateExam({ ...props,
    subtopics: props.subtopics ?? []
  })
  return makeExam(exam)
}

export async function validateExam({exam_id, questions, ...props}: Exam): Promise<Exam>{

  const answers : Record<string,string> = {}

  questions.forEach((question) => {
    answers[question.id] = question.chosen_answer as string ?? ""
  })

  const {score, question_results, feedback} = await examService.submitExam({
    exam_id,
    answers
  })

  return { ...props,
    score,
    feedback,
    exam_id,
    questions: questions.map((question) => { 
        return { ...question,
        is_correct: question_results[question.id].is_correct,
        correct_answer: question_results[question.id].correct_answer,
        explanation: question_results[question.id].explanation,
      }
    })
  }

  
}