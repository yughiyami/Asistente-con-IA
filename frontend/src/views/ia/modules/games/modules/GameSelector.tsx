'use client';

import { FiCpu, FiCode, FiGrid, FiTerminal, FiHardDrive, FiHash } from 'react-icons/fi';

interface GameSelectorProps {
  onSelectGame: (gameType: string, config?: unknown) => void;
}

export default function GameSelector({ onSelectGame }: GameSelectorProps) {
  const games = [
    {
      id: 'cache_simulator',
      name: 'Simulador de Memoria Caché',
      description: 'Aprende cómo funciona la memoria caché simulando accesos a memoria.',
      icon: <FiHardDrive className="w-8 h-8" />,
      color: 'bg-blue-50 dark:bg-blue-900/20 text-blue-500'
    },
    {
      id: 'binary_converter',
      name: 'Conversor Binario',
      description: 'Practica la conversión entre sistemas numéricos binarios, decimales y hexadecimales.',
      icon: <FiHash className="w-8 h-8" />,
      color: 'bg-green-50 dark:bg-green-900/20 text-green-500'
    },
    {
      id: 'logic_circuits',
      name: 'Constructor de Circuitos',
      description: 'Diseña y prueba circuitos lógicos para aprender sobre operaciones booleanas.',
      icon: <FiGrid className="w-8 h-8" />,
      color: 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-500'
    },
    {
      id: 'assembler',
      name: 'Ensamblador Interactivo',
      description: 'Aprende lenguaje ensamblador escribiendo y ejecutando programas simples.',
      icon: <FiTerminal className="w-8 h-8" />,
      color: 'bg-purple-50 dark:bg-purple-900/20 text-purple-500'
    },
    {
      id: 'hangman',
      name: 'Ahorcado',
      description: 'Adivina términos de arquitectura de computadoras en este clásico juego.',
      icon: <FiCode className="w-8 h-8" />,
      color: 'bg-red-50 dark:bg-red-900/20 text-red-500'
    },
    {
      id: 'word_scramble',
      name: 'Palabras Desordenadas',
      description: 'Reordena las letras para formar términos relacionados con la arquitectura de computadoras.',
      icon: <FiCpu className="w-8 h-8" />,
      color: 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-500'
    }
  ];
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {games.map((game) => (
        <button
          key={game.id}
          onClick={() => onSelectGame(game.id)}
          className="flex flex-col items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-primary-300 dark:hover:border-primary-700 transition-colors"
        >
          <div className={`p-4 rounded-full ${game.color} mb-3`}>
            {game.icon}
          </div>
          <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-1">
            {game.name}
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
            {game.description}
          </p>
        </button>
      ))}
    </div>
  );
}