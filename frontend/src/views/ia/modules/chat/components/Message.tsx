'use client';

import { useState } from 'react';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';
import { Message as MessageType } from '@/types';
import { FiUser, FiCpu, FiImage } from 'react-icons/fi';

// Componentes especializados
// import ExamComponent from '@/views/ia/modules/exam/components/content/exam/ExamComponent';
// import GameComponent from '@/views/ia/modules/games/components/GameComponent';

interface MessageProps {
  message: MessageType;
}

export default function Message({ message }: MessageProps) {
  const [imageExpanded, setImageExpanded] = useState<string | null>(null);
  
  const isUser = message.role === 'user';
  
  // Renderizar contenido especializado
  const renderSpecialContent = () => {
    if (!message.specialContent) return null;
    
    switch (message.specialContent.type) {
      // case 'exam':
      //   return <ExamComponent data={message.specialContent.data} />;
      // case 'game':
      //   return <GameComponent data={message.specialContent.data} />;
      case 'diagram':
        // Un simple contenedor para diagramas
        return (
          <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-md overflow-hidden">
            <div className="font-medium mb-1">Diagrama</div>
            <div className="text-sm">{message.specialContent.data.description}</div>
            {message.specialContent.data.url && (
              <div className="mt-2">
                <Image 
                  src={message.specialContent.data.url} 
                  alt={message.specialContent.data.description || 'Diagrama'} 
                  width={500} 
                  height={300} 
                  className="rounded-md object-contain" 
                />
              </div>
            )}
          </div>
        );
      default:
        return null;
    }
  };
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div 
          className={`shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-primary-500 ml-2' : 'bg-gray-500 dark:bg-gray-700 mr-2'
          }`}
        >
          {isUser ? (
            <FiUser className="text-white w-4 h-4" />
          ) : (
            <FiCpu className="text-white w-4 h-4" />
          )}
        </div>
        
        {/* Contenido del mensaje */}
        <div 
          className={`px-4 py-3 rounded-lg ${
            isUser
              ? 'bg-primary-500 text-white rounded-tr-none'
              : 'bg-gray-200 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-none'
          }`}
        >
          {/* Texto del mensaje con Markdown */}
          <div className="prose dark:prose-invert prose-sm max-w-none">
            <ReactMarkdown>
              {message.content}
            </ReactMarkdown>
          </div>
          
          {/* Imágenes (si hay) */}
          {message.images && message.images.length > 0 && (
            <div className="mt-3 grid grid-cols-2 gap-2">
              {message.images.map((image, index) => (
                <div key={index} className="relative">
                  <button 
                    onClick={() => setImageExpanded(image.url)} 
                    className="block w-full relative rounded-md overflow-hidden bg-gray-100 dark:bg-gray-700"
                  >
                    <Image 
                      src={image.url} 
                      alt={image.alt_text} 
                      width={200} 
                      height={150} 
                      className="w-full h-32 object-cover" 
                    />
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 bg-black/40 transition-opacity">
                      <FiImage className="w-8 h-8 text-white" />
                    </div>
                  </button>
                  <div className="text-xs mt-1 truncate text-gray-600 dark:text-gray-400">
                    {image.alt_text}
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Contenido especializado según el modo */}
          {renderSpecialContent()}
        </div>
      </div>
      
      {/* Modal de imagen expandida */}
      {imageExpanded && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75"
          onClick={() => setImageExpanded(null)}
        >
          <div className="relative max-w-3xl max-h-screen overflow-auto p-4">
            <Image 
              src={imageExpanded} 
              alt="Imagen ampliada" 
              width={800} 
              height={600} 
              className="max-w-full max-h-[80vh] object-contain rounded-lg" 
            />
            <button 
              onClick={() => setImageExpanded(null)}
              className="absolute top-2 right-2 bg-black/50 text-white rounded-full p-2"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className="h-6 w-6" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}