import api from "@/views/ia/service/api";

interface LogicConfig {
  difficulty: string;
  // topic: string;
}

interface Circuit {
  inputs: string[];
  output: string;
  gates: {
    id: string;
    type: "AND" | "OR" | "XOR" | "NOT";
    inputs: string[];
  }[];
  description: string;
}
interface LogicGame {
  game_id: string;
  circuit: Circuit;
  question: string;
  num_inputs: number;
  
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
  score: number,
  expected_truth_table: {
    inputs: {
      [key:string]: (0|1)
    },
    output: (0|1)
  }
  explanation: string
}

interface GuessLogicWordRequest {
  game_id:string;
  truth_table: {
    inputs: {
      [key:string]: (0|1)
    },
    output: (0|1)
  }[];
}

export async function GuessLogicWord({game_id, truth_table}: GuessLogicWordRequest): Promise<GuessLogicWordResponse> {
  try {
    const {data} = await api.post("/games/logic/answer", {
      game_id,
      truth_table
    })
    return data
  } catch (error) {
    console.error("Error al adivinar la letra:", error);
    throw error;
  }
}