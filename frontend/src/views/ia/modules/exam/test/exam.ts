import { ExamAdapter } from "../services/exam.service";

export const examTest : ExamAdapter = {
  questions: [
    {
      id: '1',
      question: '¿Cuál es la capital de Francia?',
      type: 'multiple-choice',
      options: ['Berlín', 'Madrid', 'París', 'Roma'],
      points: 10,
      correct_answer: 'París',
      explanation: 'La capital de Francia es París.'
    },
    {
      id: '2',
      question: '¿Es el sol una estrella?',
      type: 'true-false',
      points: 5,
      correct_answer: true,
      explanation: 'Sí, el sol es una estrella.'
    },
    {
      id: '3',
      question: '¿Cuántos continentes hay en el mundo?',
      type: 'multiple-choice',
      options: ['5', '6', '7', '8'],
      points: 10,
      correct_answer: '7',
      explanation: 'Hay 7 continentes en el mundo.'
    }
  ]
}