'use client';

import { useEffect, useRef } from 'react';
import { useAppStore } from '@/store/store';
import Message from './Message';
import LoadingMessage from './LoadingMessage';

export default function MessageList() {
  const { messages, loading } = useAppStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll al último mensaje
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);
  
  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.length === 0 ? (
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
      ) : (
        <div className="space-y-4">
          {messages.map((message) => (
            <Message key={message.id} message={message} />
          ))}
          {loading && <LoadingMessage />}
          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  );
}