import api from "@/views/ia/service/api";

interface HangmanConfig {
  difficulty: string;
  topic: string;
}

interface HangmanGame {
  game_id: string;
  word_length: number;
  clue: string;
  argument: string;
  max_attempts: number;
  hidden_word: string;
}

export async function CreateHangmanGame({... props} : HangmanConfig) : Promise<HangmanGame>{
  try {
    const {data} = await api.post("/games/hangman", { ...props,
      game_type: "hangman",
    })
    return data
  } catch (error) {
    console.error("Error al crear el juego de ahorcado:", error);
    throw error;
  }
}

interface GuessHangmanWordResponse {
  correct: boolean;
  current_word: string;
  remaining_attempts: number;
  game_over: boolean;
  win: boolean;
  correct_word: string;
}

interface GuessHangmanWordRequest {
  game_id:string;
  guess:string;
}

export async function GuessHangmanWord({game_id, guess}: GuessHangmanWordRequest): Promise<GuessHangmanWordResponse> {
  try {
    const {data} = await api.post("/games/hangman/guess", {
      game_id,
      guess
    })
    return data
  } catch (error) {
    console.error("Error al adivinar la letra:", error);
    throw error;
  }
}