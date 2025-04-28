'use client';

import { useEffect, useState } from 'react';
import { FiCheck, FiChevronRight } from 'react-icons/fi';
import { DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ExamQuestion } from '@/types/exam';
import MultipleChoice from './options/MultipleChoice';
import TrueFalse from './options/TrueFalse';
import { Button } from '@/components/ui/button';
import { useExamStore } from '@/store/exam';

interface QuestionCardProps {
  question: ExamQuestion;
}

export default function QuestionCard({ question }: QuestionCardProps) {
  // const isMultipleChoice = question.question_type === 'multiple_choice';
  // const [textAnswer, setTextAnswer] = useState(
  //   typeof userAnswer === 'string' ? userAnswer : ''
  // );
  
  // // Manejar selección de opción múltiple
  // const handleOptionSelect = (index: number) => {
  //   if (userAnswer === undefined) {
  //     onAnswer(index);
  //   }
  // };
  
  // // Manejar envío de respuesta abierta
  // const handleSubmitText = () => {
  //   if (textAnswer.trim()) {
  //     onAnswer(textAnswer.trim());
  //   }
  // };

  const [answer, setAnswer] = useState<unknown>(null);

  const {
    answerQuestion,
    nextQuestion,
  } = useExamStore()

  useEffect(() => {
    setAnswer(null);
  }, [question]);

  function handleAnswer() {
    if (question.type === 'multiple-choice') {
      answerQuestion(answer);
    } else if (question.type === 'true-false') {
      answerQuestion(answer);
    }
  }
  
  return (
    <DialogContent>
      <DialogHeader>
        <DialogTitle>
          {question.question}
        </DialogTitle>
        <DialogDescription>
          {question.points} puntos
        </DialogDescription>
          {
            question.type === 'multiple-choice' ? 
              <MultipleChoice options={question.options ?? []} handler={setAnswer} /> :
            question.type === 'true-false' ?
              <TrueFalse handler={setAnswer}/> :
            ""
          }
      </DialogHeader>
      <DialogFooter>
        <Button type="button" 
          disabled={!answer || !!question.chosen_answer}
          onClick={handleAnswer}
        >
          <FiCheck />
          OK
        </Button>
        <Button type="button" 
          disabled={!question.chosen_answer}
          onClick={nextQuestion}
        >
          <FiChevronRight />
          Siguiente
        </Button>
      </DialogFooter>
    </DialogContent>
    // <div className="question-card">
    //   <h4 className="text-lg font-medium mb-3 text-gray-800 dark:text-gray-200">
    //     {question.question_text}
    //   </h4>
      
    //   {isMultipleChoice && question.options ? (
    //     <div className="space-y-2">
    //       {question.options.map((option, index) => (
    //         <button
    //           key={index}
    //           onClick={() => handleOptionSelect(index)}
    //           className={`option-button ${
    //             userAnswer === index ? 'selected' : ''
    //           }`}
    //           disabled={userAnswer !== undefined}
    //         >
    //           <span className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-200 dark:bg-gray-700 mr-3 shrink-0">
    //             {String.fromCharCode(65 + index)}
    //           </span>
    //           <span>{option}</span>
    //         </button>
    //       ))}
    //     </div>
    //   ) : (
    //     <div className="space-y-3">
    //       <textarea
    //         value={textAnswer}
    //         onChange={(e) => setTextAnswer(e.target.value)}
    //         placeholder="Escribe tu respuesta aquí..."
    //         rows={4}
    //         disabled={userAnswer !== undefined}
    //         className="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-md focus:outline-hidden focus:ring-2 focus:ring-primary-500 dark:bg-gray-800 dark:text-white"
    //       />
          
    //       {userAnswer === undefined && (
    //         <div className="flex justify-end">
    //           <button
    //             onClick={handleSubmitText}
    //             disabled={!textAnswer.trim()}
    //             className="px-4 py-2 bg-primary-500 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
    //           >
    //             Responder
    //           </button>
    //         </div>
    //       )}
    //     </div>
    //   )}
      
    //   {/* Puntos de la pregunta */}
    //   <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
    //     Puntos: {question.points}
    //   </div>
    // </div>
  );
}