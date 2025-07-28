import { ChatRequest, ChatResponse } from "@/types";
import api from "@/views/ia/service/api";

// Servicios para el chat
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await api.post('/chat/', { ...request,
    query: request.message,
  });
  return response.data;
}