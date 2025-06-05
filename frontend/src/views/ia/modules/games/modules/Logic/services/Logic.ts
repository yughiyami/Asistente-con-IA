import api from "@/views/ia/service/api";

interface LogicConfig {
  difficulty: string;
  topic: string;
}

interface LogicGame {
  game_id: string;
  difficulty: string;
  pattern: ("AND" | "OR" | "XOR")[];
  question: string;
  input_values: (1 | 0)[]
  expected_output: {
    case1: (1|0)
    case2: (1|0)
    pattern: (1|0)[]
  },
  complexity_type: "multiple_cases"
}

export async function CreateLogicGame({... props} : LogicConfig) : Promise<LogicGame>{
  try {
    const {data} = await api.post("/games/logic", { ...props,
      game_type: "logic",
    })
    return data
  } catch (error) {
    console.error("Error al crear el juego de ahorcado:", error);
    throw error;
  }
}

interface GuessLogicWordResponse {
  correct: boolean,
  correct_answer: (0|1)
  partial_score: number
  explanation: string
  complexity_feedback: string
}

interface GuessLogicWordRequest {
  game_id:string;
  answer: {
    case1: (0|1)
    case2: (0|1)
    pattern: (0|1)[]
  };
}

export async function GuessLogicWord({game_id, answer}: GuessLogicWordRequest): Promise<GuessLogicWordResponse> {
  try {
    const {data} = await api.post("/games/logic/answer", {
      game_id,
      answer
    })
    return data
  } catch (error) {
    console.error("Error al adivinar la letra:", error);
    throw error;
  }
}