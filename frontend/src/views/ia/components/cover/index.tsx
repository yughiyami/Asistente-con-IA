import React from 'react'

export default function Cover() {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center text-gray-500">
    <div className="mb-3">
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        className="h-12 w-12 mx-auto mb-4 text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={1.5} 
          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" 
        />
      </svg>
    </div>
    <h3 className="text-xl font-medium mb-1">Asistente de Arquitectura de Computadoras</h3>
    <p className="max-w-md text-sm">
      Haz una pregunta sobre arquitectura de computadoras, genera un examen o juega a uno de los juegos educativos disponibles.
    </p>
  </div>
  )
}
