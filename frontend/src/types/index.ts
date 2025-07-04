// import { MultipleChoiceOption } from "./exam";

// Tipos generales
export interface User {
    id: string;
    username: string;
  }
  
  export interface Message {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: string;
    images?: ImageInfo[];
    specialContent?: SpecialContent;
  }
  
  export type ImageInfo = 
  {
    url: string;
    title: string;
    source?: string;
  }
  
  export interface SpecialContent {
    type: 'exam' | 'game' | 'diagram' | 'chat';  // Add 'chat' as a valid type
    data: unknown;
  }
  
  // Tipos para Chat
  export interface ChatRequest {
    message: string;
    session_id?: string;
    mode: 'chat' | 'exam' | 'game';
  }
  
  export interface ChatResponse {
    message: string;
    images?: ImageInfo[];
    special_content?: unknown;
  }
  
  // Tipos para Exámenes
  export interface Question {
    id: string;
    text: string;
    // question_type: 'multiple_choice' //| 'open_ended';
    alternatives: {
      [key: string]: string
    }
    //points: number;
  }
  
  export interface Exam {
    exam_id: string;
    title: string;
    // description?: string;
    // topic: string;
    // difficulty: string;
    time_limit_minutes: number;
    questions: Question[];
  }
  
  export interface UserAnswer {
    question_id: string;
    answer: string | number;
  }
  
  export interface ExamResult {
    // exam_id: string;
    score: number;
    // total_points: number;
    // percentage: number;
    question_results: Record<string, QuestionResult> //QuestionResult[];
    feedback: string;
    time_taken_seconds: number;
  }
  
  export interface QuestionResult {
    // question_id: string;
    is_correct: boolean;
    // points_earned: number;
    // points_possible: number;
    // user_answer: string | number;
    correct_answer?: string //| number;
    explanation?: string;
  }
  
  // Tipos para Juegos
  export interface Game {
    game_id: string;
    game_type: string;
    state: unknown;
    message?: string;
    completed: boolean;
    score?: number;
  }
  
  export interface GameAction {
    action: string;
    data?: unknown;
  }
  
  // Tipos para temas predefinidos
  export interface PredefinedPrompt {
    id: string;
    text: string;
    icon: string;
    mode: 'chat' | 'exam' | 'game';
  }
  
  // Tipos para modos
  export type ChatMode = 'chat' | 'exam' | 'game';
  export type ThemeMode = 'light' | 'dark' | 'system';