import api from "@/views/ia/service/api";

interface WordleConfig {
  difficulty: string;
  topic: string;
}

interface WordleGame {
  game_id: string;
  word_length: number;
  max_attempts: number;
  topic_hint: string;
}

export async function CreateWordleGame({... props} : WordleConfig) : Promise<WordleGame>{
  try {
    const {data} = await api.post("/games/wordle", { ...props,
      game_type: "wordle",
    })
    return data
  } catch (error) {
    console.error("Error al crear el juego de ahorcado:", error);
    throw error;
  }
}

interface GuessWordleWordResponse {
  results: ("correct" | "absent" | "present") []
  attempt_number: number;
  remaining_attempts: number;
  game_over: boolean;
  correct_word: string;
  explanation: string;
  win: true;
}

interface GuessWordleWordRequest {
  game_id:string;
  word:string;
}

export async function GuessWordleWord({game_id, word}: GuessWordleWordRequest): Promise<GuessWordleWordResponse> {
  try {
    const {data} = await api.post("/games/wordle/guess", {
      game_id,
      word
    })
    return data
  } catch (error) {
    console.error("Error al adivinar la letra:", error);
    throw error;
  }
}