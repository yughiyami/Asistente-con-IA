'use client';

import { useState, useEffect } from 'react';
import { useAppStore } from '@/store/store';
import { gameService } from '@/lib/api';
import { Game, GameAction } from '@/types';
import { toast } from 'sonner';

// Importar componentes específicos para cada juego
//import CacheSimulator from './CacheSimulator';
///import BinaryConverter from './BinaryConverter';
//import LogicCircuits from './LogicCircuits';
//import Assembler from './Assembler';
import Hangman from './Hangman';
//import WordScramble from './WordScramble';
import GameSelector from './GameSelector';

interface GameComponentProps {
  data: any;
}

export default function GameComponent({ data }: GameComponentProps) {
  const [game, setGame] = useState<Game | null>(null);
  const [loading, setLoading] = useState(false);
  const { addMessage } = useAppStore();
  
  // Inicializar juego si hay datos
  useEffect(() => {
    if (data.game_id) {
      setGame(data as Game);
    } else if (data.game_type) {
      initializeGame(data.game_type, data.config);
    }
  }, [data]);
  
  // Inicializar un nuevo juego
  const initializeGame = async (gameType: string, config?: any) => {
    setLoading(true);
    try {
      const gameData = await gameService.initializeGame(gameType, config);
      setGame(gameData);
    } catch (error) {
      console.error('Error al inicializar juego:', error);
      toast.error('No se pudo inicializar el juego. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };
  
  // Procesar acción en el juego
  const handleGameAction = async (action: GameAction) => {
    if (!game) return;
    
    setLoading(true);
    try {
      const updatedGame = await gameService.gameAction(game.game_id, action);
      setGame(updatedGame);
      
      // Si el juego se ha completado, enviar resultado como mensaje
      if (updatedGame.completed && !game.completed) {
        addMessage({
          id: Date.now().toString(),
          content: `Juego completado: ${updatedGame.message || ''}`,
          role: 'assistant',
          timestamp: new Date().toISOString(),
          specialContent: {
            type: 'game',
            data: {
              result: {
                game_type: updatedGame.game_type,
                completed: true,
                score: updatedGame.score,
                message: updatedGame.message
              }
            }
          }
        });
      }
      
    } catch (error) {
      console.error('Error en acción de juego:', error);
      toast.error('Error al procesar acción. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };
  
  // Mostrar estado de carga
  if (loading && !game) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-xs">
        <div className="flex flex-col items-center justify-center py-8">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">Inicializando juego...</p>
        </div>
      </div>
    );
  }
  
  // Mostrar selector de juegos si no hay juego
  if (!game) {
    return <GameSelector onSelectGame={initializeGame} />;
  }
  
  // Renderizar el juego específico
  const renderGame = () => {
    const gameState = game.state;
    const gameType = game.game_type;
    
    switch (gameType) {
      //case 'cache_simulator':
      ///  return <CacheSimulator game={gameState} onAction={handleGameAction} />;
      //case 'binary_converter':
      //  return <BinaryConverter game={gameState} onAction={handleGameAction} />;
      //case 'logic_circuits':
      //  return <LogicCircuits game={gameState} onAction={handleGameAction} />;
      //case 'assembler':
      //  return <Assembler game={gameState} onAction={handleGameAction} />;
      case 'hangman':
        return <Hangman game={gameState} onAction={handleGameAction} />;
      //case 'word_scramble':
      //  return <WordScramble game={gameState} onAction={handleGameAction} />;
      default:
        return (
          <div className="p-4 text-center text-gray-600 dark:text-gray-300">
            Juego no soportado: {gameType}
          </div>
        );
    }
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-xs">
      <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 border-b border-indigo-100 dark:border-indigo-900/30">
        <h3 className="font-medium text-indigo-800 dark:text-indigo-200">
          {game.state.type === 'cache_simulator' ? 'Simulador de Memoria Caché' :
           game.state.type === 'binary_converter' ? 'Conversor Binario' :
           game.state.type === 'logic_circuits' ? 'Constructor de Circuitos Lógicos' :
           game.state.type === 'assembler' ? 'Ensamblador Interactivo' :
           game.state.type === 'hangman' ? 'Juego del Ahorcado' :
           game.state.type === 'word_scramble' ? 'Palabras Desordenadas' :
           'Juego Educativo'}
        </h3>
        {game.state.instructions && (
          <p className="text-sm text-indigo-600 dark:text-indigo-300 mt-1">
            {game.state.instructions}
          </p>
        )}
      </div>
      
      <div className="p-4">
        {/* Mensaje si está cargando una acción */}
        {loading && (
          <div className="absolute inset-0 bg-white/70 dark:bg-gray-800/70 flex items-center justify-center z-10">
            <div className="w-10 h-10 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        )}
        
        {/* Renderizar juego específico */}
        {renderGame()}
      </div>
    </div>
  );
}