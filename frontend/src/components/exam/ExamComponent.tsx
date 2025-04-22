'use client';

import { useState, useEffect } from 'react';
import { useAppStore } from '@/store/store';
import { examService } from '@/lib/api';
import { Exam, UserAnswer, ExamResult } from '@/types';
import QuestionCard from './QuestionCard';
import ResultSummary from './ResultSummary';
import { toast } from 'sonner';

interface ExamComponentProps {
  data: any;
}

export default function ExamComponent({ data }: ExamComponentProps) {
  const [exam, setExam] = useState<Exam | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, string | number>>({});
  const [result, setResult] = useState<ExamResult | null>(null);
  const [loading, setLoading] = useState(false);
  const { addMessage } = useAppStore();
  
  // Cargar examen si hay un ID de examen o un topic
  useEffect(() => {
    if (data.exam_id) {
      // Aquí se podría implementar la carga de un examen existente
      // por ahora suponemos que el examen completo viene en data
      setExam(data as Exam);
    } else if (data.topic) {
      loadExam(data.topic, data.difficulty || 'medium');
    }
  }, [data]);
  
  // Cargar examen desde la API
  const loadExam = async (topic: string, difficulty: string) => {
    setLoading(true);
    try {
      const examData = await examService.generateExam(topic, difficulty);
      setExam(examData);
    } catch (error) {
      console.error('Error al cargar examen:', error);
      toast.error('No se pudo cargar el examen. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };
  
  // Registrar respuesta del usuario
  const handleAnswer = (questionId: string, answer: string | number) => {
    setUserAnswers((prev) => ({
      ...prev,
      [questionId]: answer
    }));
  };
  
  // Navegar a la siguiente pregunta
  const handleNext = () => {
    if (exam && currentQuestion < exam.questions.length - 1) {
      setCurrentQuestion((prev) => prev + 1);
    }
  };
  
  // Navegar a la pregunta anterior
  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion((prev) => prev - 1);
    }
  };
  
  // Enviar examen para evaluación
  const handleSubmit = async () => {
    if (!exam) return;
    
    setLoading(true);
    try {
      const result = await examService.submitExam(exam.id, userAnswers);
      setResult(result);
      
      // Publicar resultado como un mensaje nuevo
      addMessage({
        id: Date.now().toString(),
        content: `Resultado del examen: ${result.score}/${result.total_points} (${result.percentage.toFixed(1)}%)`,
        role: 'assistant',
        timestamp: new Date().toISOString(),
        specialContent: {
          type: 'exam',
          data: { result }
        }
      });
      
    } catch (error) {
      console.error('Error al enviar examen:', error);
      toast.error('Error al evaluar examen. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };
  
  // Iniciar un nuevo examen
  const handleRestart = () => {
    setExam(null);
    setCurrentQuestion(0);
    setUserAnswers({});
    setResult(null);
  };
  
  // Mostrar estado de carga
  if (loading && !exam) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
        <div className="flex flex-col items-center justify-center py-8">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">Generando examen...</p>
        </div>
      </div>
    );
  }
  
  // Mostrar resultados si están disponibles
  if (result) {
    return <ResultSummary result={result} onRestart={handleRestart} />;
  }
  
  // Mostrar mensaje si no hay examen
  if (!exam) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
        <p className="text-center text-gray-600 dark:text-gray-300">
          No se pudo cargar el examen. Intenta solicitar uno nuevo.
        </p>
      </div>
    );
  }
  
  // Mostrar la pregunta actual
  const question = exam.questions[currentQuestion];
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-sm">
      <div className="p-4 bg-primary-50 dark:bg-primary-900/20 border-b border-primary-100 dark:border-primary-900/30">
        <h3 className="font-medium text-primary-800 dark:text-primary-200">{exam.title}</h3>
        {exam.description && (
          <p className="text-sm text-primary-600 dark:text-primary-300 mt-1">{exam.description}</p>
        )}
      </div>
      
      <div className="p-4">
        {/* Barra de progreso */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
            <span>Pregunta {currentQuestion + 1} de {exam.questions.length}</span>
            <span>
              {Object.keys(userAnswers).length} de {exam.questions.length} respondidas
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div 
              className="bg-primary-500 h-2 rounded-full"
              style={{ width: `${((currentQuestion + 1) / exam.questions.length) * 100}%` }}
            ></div>
          </div>
        </div>
        
        {/* Tarjeta de pregunta */}
        <QuestionCard 
          question={question}
          userAnswer={userAnswers[question.id]}
          onAnswer={(answer) => handleAnswer(question.id, answer)}
        />
        
        {/* Navegación */}
        <div className="flex justify-between mt-4">
          <button
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
            className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Anterior
          </button>
          
          {currentQuestion < exam.questions.length - 1 ? (
            <button
              onClick={handleNext}
              disabled={!userAnswers[question.id]}
              className="px-4 py-2 bg-primary-500 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Siguiente
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={Object.keys(userAnswers).length < exam.questions.length || loading}
              className="px-4 py-2 bg-green-500 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Evaluando...' : 'Finalizar examen'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}