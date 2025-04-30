'use client';

import { Button } from '@/components/ui/button';
import { DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useExamStore } from '@/store/exam';
import { useEffect, useRef, useState } from 'react';
import { FiCheckCircle, FiRefreshCw } from 'react-icons/fi'
import { validateExam } from '../../../services/exam.service';

export default function ResultSummary() {
  // Determinar clase de color según porcentaje
  
  const {
    exam,
    updateExam,
    resetIndex,
    // clearExam,
    deleteExam,
  } = useExamStore()

  const [done, setDone] = useState(false)
  const pending = useRef(false)
  useEffect(() => {
    if(pending.current || done) return
    pending.current = true
    
    if(exam && !exam.feedback) validateExam(exam).then((exam) => {
      updateExam(exam)
      setDone(true)
      pending.current = false
    })
  },[done, exam, updateExam])

  const getScoreClass = () => {
    if ((exam?.score ?? 0) >= 80) return 'text-green-500';
    if ((exam?.score ?? 0) >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <DialogContent>
      <DialogHeader>
        <DialogTitle>
          {exam?.title}
        </DialogTitle>
        <DialogDescription>
          {exam?.feedback ?? "Aquí se mostrarán los resultados del examen."}
        </DialogDescription>
        <div className={`flex flex-col items-center justify-center p-4 text-4xl ${getScoreClass()}`}>
          {exam?.score ?? 0} %
        </div>
      </DialogHeader>
      <DialogFooter>
        <Button
          type="button"
          onClick={resetIndex}
        >
          <FiRefreshCw className="mr-2" />
          Revisar resultados
        </Button>
        <Button
          type="button"
          onClick={deleteExam}
        >
          <FiCheckCircle className="mr-2" />
          Salir
        </Button>
      </DialogFooter>
    </DialogContent>
    // <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xs overflow-hidden">
    //   <div className="p-4 bg-primary-50 dark:bg-primary-900/20 border-b border-primary-100 dark:border-primary-900/30">
    //     <h3 className="font-medium text-primary-800 dark:text-primary-200">
    //       Resultados del Examen
    //     </h3>
    //   </div>
      
    //   <div className="p-6">
    //     {/* Puntuación */}
    //     <div className="flex flex-col items-center justify-center mb-6">
    //       <div className={`text-4xl font-bold ${getScoreClass()}`}>
    //         {result.score}/{result.total_points}
    //       </div>
    //       <div className={`text-lg ${getScoreClass()}`}>
    //         {result.percentage.toFixed(1)}%
    //       </div>
          
    //       {/* Barra de progreso */}
    //       <div className="w-full max-w-md mt-3">
    //         <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
    //           <div 
    //             className={`h-3 rounded-full ${
    //               result.percentage >= 80 ? 'bg-green-500' :
    //               result.percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'
    //             }`}
    //             style={{ width: `${result.percentage}%` }}
    //           ></div>
    //         </div>
    //       </div>
    //     </div>
        
    //     {/* Retroalimentación */}
    //     <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg mb-6">
    //       <h4 className="font-medium mb-2 text-gray-800 dark:text-gray-200">
    //         Retroalimentación
    //       </h4>
    //       <p className="text-gray-600 dark:text-gray-300">
    //         {result.feedback}
    //       </p>
    //     </div>
        
    //     {/* Resumen de preguntas */}
    //     <div className="mb-6">
    //       <h4 className="font-medium mb-3 text-gray-800 dark:text-gray-200">
    //         Resumen de Respuestas
    //       </h4>
          
    //       <div className="space-y-3">
    //         {result.question_results.map((qResult, index) => (
    //           <div 
    //             key={qResult.question_id}
    //             className={`p-3 rounded-md border ${
    //               qResult.correct 
    //                 ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20' 
    //                 : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
    //             }`}
    //           >
    //             <div className="flex items-start">
    //               <div className="shrink-0 mr-3">
    //                 {qResult.correct ? (
    //                   <FiCheckCircle className="w-5 h-5 text-green-500" />
    //                 ) : (
    //                   <FiXCircle className="w-5 h-5 text-red-500" />
    //                 )}
    //               </div>
    //               <div>
    //                 <div className="font-medium text-gray-800 dark:text-gray-200">
    //                   Pregunta {index + 1}
    //                 </div>
    //                 <div className="text-sm text-gray-600 dark:text-gray-300 mt-1">
    //                   {qResult.correct 
    //                     ? `Correcta (+${qResult.points_earned} puntos)` 
    //                     : `Incorrecta (0/${qResult.points_possible} puntos)`}
    //                 </div>
    //                 {!qResult.correct && qResult.explanation && (
    //                   <div className="mt-2 text-sm text-gray-600 dark:text-gray-300 p-2 bg-gray-100 dark:bg-gray-800 rounded-sm">
    //                     <span className="font-medium">Explicación:</span> {qResult.explanation}
    //                   </div>
    //                 )}
    //               </div>
    //             </div>
    //           </div>
    //         ))}
    //       </div>
    //     </div>
        
    //     {/* Botón para reiniciar */}
    //     <div className="flex justify-center">
    //       <button
    //         onClick={onRestart}
    //         className="flex items-center px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
    //       >
    //         <FiRefreshCw className="mr-2" />
    //         Realizar otro examen
    //       </button>
    //     </div>
    //   </div>
    // </div>
  );
}