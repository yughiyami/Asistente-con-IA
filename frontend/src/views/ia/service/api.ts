import axios from 'axios';
import { Exam, ExamResult, Game, GameAction } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

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