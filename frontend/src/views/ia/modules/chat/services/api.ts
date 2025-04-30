import { ChatRequest, ChatResponse } from "@/types";
import api from "@/views/ia/service/api";

// Servicios para el chat
export const chatService = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/chat', request);
    return response.data;
  },
};