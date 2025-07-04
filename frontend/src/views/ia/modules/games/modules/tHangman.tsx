'use client';

import { useState } from 'react';
import { FiRefreshCw } from 'react-icons/fi';

interface HangmanProps {
  game: {
    wrong_guesses?: number;
    max_wrong_guesses?: number;
    completed?: boolean;
    won?: boolean;
    display?: string;
    hint?: string;
    word?: string;
    guessed_letters?: string[];
  };
  onAction: (action: unknown) => void;
}

export default function Hangman({ game, onAction }: HangmanProps) {
  const [guessInput, setGuessInput] = useState('');
  const wrongGuesses = game.wrong_guesses || 0;
  const maxGuesses = game.max_wrong_guesses || 6;
  const completed = game.completed || false;
  const won = game.won || false;
  
  // Manejar intento de adivinar letra
  const handleGuessLetter = (letter: string) => {
    if (!letter || letter.length !== 1 || completed) return;
    
    // Verificar si ya se ha intentado
    if ((game.guessed_letters || []).includes(letter.toUpperCase())) {
      return;
    }
    
    onAction({
      action: 'guess_letter',
      data: { letter }
    });
    
    setGuessInput('');
  };
  
  // Manejar intento de adivinar palabra completa
  const handleGuessWord = () => {
    if (!guessInput.trim() || completed) return;
    
    onAction({
      action: 'guess_word',
      data: { word: guessInput.trim() }
    });
    
    setGuessInput('');
  };
  
  // Reiniciar juego
  const handleRestart = () => {
    onAction({
      action: 'restart'
    });
  };
  
  // Renderizar dibujo del ahorcado
  const renderHangman = () => {
    return (
      <div className="hangman-drawing">
        {/* Base */}
        <div className="absolute bottom-0 left-0 w-32 h-1 bg-gray-800 dark:bg-gray-200"></div>
        
        {/* Poste vertical */}
        <div className="absolute bottom-0 left-8 w-1 h-40 bg-gray-800 dark:bg-gray-200"></div>
        
        {/* Travesaño superior */}
        <div className="absolute top-8 left-8 w-24 h-1 bg-gray-800 dark:bg-gray-200"></div>
        
        {/* Cuerda */}
        <div className="absolute top-8 right-8 w-1 h-6 bg-gray-800 dark:bg-gray-200"></div>
        
        {/* Cabeza */}
        {wrongGuesses >= 1 && (
          <div className="absolute top-14 right-6 w-6 h-6 rounded-full border-2 border-gray-800 dark:border-gray-200"></div>
        )}
        
        {/* Cuerpo */}
        {wrongGuesses >= 2 && (
          <div className="absolute top-20 right-8 w-1 h-12 bg-gray-800 dark:bg-gray-200"></div>
        )}
        
        {/* Brazo izquierdo */}
        {wrongGuesses >= 3 && (
          <div className="absolute top-22 right-8 w-6 h-1 bg-gray-800 dark:bg-gray-200 transform rotate-45 origin-left"></div>
        )}
        
        {/* Brazo derecho */}
        {wrongGuesses >= 4 && (
          <div className="absolute top-22 right-8 w-6 h-1 bg-gray-800 dark:bg-gray-200 transform -rotate-45 origin-right"></div>
        )}
        
        {/* Pierna izquierda */}
        {wrongGuesses >= 5 && (
          <div className="absolute top-32 right-8 w-6 h-1 bg-gray-800 dark:bg-gray-200 transform rotate-45 origin-left"></div>
        )}
        
        {/* Pierna derecha */}
        {wrongGuesses >= 6 && (
          <div className="absolute top-32 right-8 w-6 h-1 bg-gray-800 dark:bg-gray-200 transform -rotate-45 origin-right"></div>
        )}
      </div>
    );
  };
  
  // Renderizar teclado
  const renderKeyboard = () => {
    const rows = [
      ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
      ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
      ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
    ];
    
    return (
      <div className="mt-4">
        {rows.map((row, rowIndex) => (
          <div key={rowIndex} className="flex justify-center mb-2">
            {row.map((letter) => {
              const isGuessed = (game.guessed_letters || []).includes(letter);
              const isInWord = game.word && game.word.includes(letter);
              
              return (
                <button
                  key={letter}
                  onClick={() => handleGuessLetter(letter)}
                  disabled={isGuessed || completed}
                  className={`m-1 w-8 h-8 rounded-md flex items-center justify-center ${
                    isGuessed
                      ? isInWord
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200'
                      : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600'
                  }`}
                >
                  {letter}
                </button>
              );
            })}
          </div>
        ))}
      </div>
    );
  };
  
  return (
    <div className="flex flex-col items-center">
      {/* Estado del juego */}
      <div className="mb-4 flex items-center">
        <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mr-3">
          Intentos: {wrongGuesses}/{maxGuesses}
        </div>
        
        <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${
              (wrongGuesses / maxGuesses) > 0.7 
                ? 'bg-red-500' 
                : (wrongGuesses / maxGuesses) > 0.3 
                  ? 'bg-yellow-500' 
                  : 'bg-green-500'
            }`}
            style={{ width: `${(wrongGuesses / maxGuesses) * 100}%` }}
          ></div>
        </div>
      </div>
      
      {/* Dibujo del ahorcado */}
      {renderHangman()}
      
      {/* Palabra a adivinar */}
      <div className="my-6 flex justify-center items-center space-x-2">
        {game.display && game.display.split('').map((char: string, index: number) => (
          <div 
            key={index}
            className="w-8 h-10 flex items-center justify-center border-b-2 border-gray-800 dark:border-gray-200"
          >
            <span className="text-xl font-bold text-gray-800 dark:text-gray-200">
              {char !== '_' ? char : ' '}
            </span>
          </div>
        ))}
      </div>
      
      {/* Pista */}
      {game.hint && (
        <div className="mb-4 p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-md">
          <p className="text-sm text-indigo-800 dark:text-indigo-200">
            <span className="font-medium">Pista:</span> {game.hint}
          </p>
        </div>
      )}
      
      {/* Mensaje de finalización */}
      {completed && (
        <div className={`my-4 p-3 rounded-md ${
          won 
            ? 'bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-200' 
            : 'bg-red-50 text-red-800 dark:bg-red-900/20 dark:text-red-200'
        }`}>
          <p className="font-medium">
            {won 
              ? '¡Felicidades! Has adivinado la palabra.' 
              : `¡Oh no! La palabra era "${game.word}".`}
          </p>
        </div>
      )}
      
      {/* Entrada para adivinar palabra */}
      {!completed && (
        <div className="mt-4 flex w-full max-w-xs">
          <input
            type="text"
            value={guessInput}
            onChange={(e) => setGuessInput(e.target.value.toUpperCase())}
            placeholder="Adivina la palabra..."
            className="flex-1 p-2 border border-gray-300 dark:border-gray-700 rounded-l-md focus:outline-hidden focus:ring-2 focus:ring-primary-500 dark:bg-gray-800 dark:text-white"
          />
          <button
            onClick={handleGuessWord}
            disabled={!guessInput.trim()}
            className="px-4 py-2 bg-primary-500 text-white rounded-r-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Adivinar
          </button>
        </div>
      )}
      
      {/* Teclado */}
      {!completed && renderKeyboard()}
      
      {/* Botón de reinicio */}
      {completed && (
        <button
          onClick={handleRestart}
          className="mt-4 flex items-center px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
        >
          <FiRefreshCw className="mr-2" />
          Jugar de nuevo
        </button>
      )}
    </div>
  );
}