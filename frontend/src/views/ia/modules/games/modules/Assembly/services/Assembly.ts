import api from "@/views/ia/service/api";

interface AssemblyConfig {
  difficulty: string;
  topic?: string;
}

interface AssemblyGame {
  game_id: string;
  code: string;
  architecture: string;
  hint: string;
  expected_behavior: string;
}

export async function CreateAssemblyGame({... props} : AssemblyConfig) : Promise<AssemblyGame>{
  try {
    const {data} = await api.post("/games/assembly", { ...props,
      game_type: "assembly",
    })
    return data
  } catch (error) {
    console.error("Error al crear el juego de ahorcado:", error);
    throw error;
  }
}

interface GuessAssemblyResponse {
  correct: boolean
  correct_explanation: string
  feedback: string
  score: number
}

interface GuessAssemblyWordRequest {
  game_id:string;
  explanation:string;
}

export async function GuessAssemblyWord({game_id, explanation}: GuessAssemblyWordRequest): Promise<GuessAssemblyResponse> {
  try {
    const {data} = await api.post("/games/assembly/answer", {
      game_id,
      explanation
    })
    return data
  } catch (error) {
    console.error("Error al adivinar la letra:", error);
    throw error;
  }
}