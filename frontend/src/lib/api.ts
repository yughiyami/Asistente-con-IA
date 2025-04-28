import axios from 'axios';
import { ChatRequest, ChatResponse, Exam, ExamResult, Game, GameAction } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Servicios para el chat
export const chatService = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/chat', request);
    return response.data;
  },
};

// Servicios para exámenes
export const examService = {
  generateExam: async (topic: string, difficulty: string = "medium"): Promise<Exam> => {
    const response = await api.post(`/exam/generate?topic=${encodeURIComponent(topic)}&difficulty=${difficulty}`);
    return response.data;
  },
  
  submitExam: async (examId: string, answers: Record<string, string | number>): Promise<ExamResult> => {
    const response = await api.post('/exam/submit', {
      exam_id: examId,
      answers: answers
    });
    return response.data;
  },
};

// Servicios para juegos
export const gameService = {
  initializeGame: async (gameType: string, config?: any): Promise<Game> => {
    const response = await api.post('/game/initialize', {
      game_type: gameType,
      config: config || {}
    });
    return response.data;
  },
  
  gameAction: async (gameId: string, action: GameAction): Promise<Game> => {
    const response = await api.post(`/game/${gameId}/action`, action);
    return response.data;
  },
};

export default api;