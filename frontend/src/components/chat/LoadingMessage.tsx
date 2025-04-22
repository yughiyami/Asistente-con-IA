import { FiCpu } from 'react-icons/fi';

export default function LoadingMessage() {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex flex-row">
        {/* Avatar */}
        <div className="flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center bg-gray-500 dark:bg-gray-700 mr-2">
          <FiCpu className="text-white w-4 h-4" />
        </div>
        
        {/* Indicador de carga */}
        <div className="px-4 py-3 rounded-lg bg-gray-200 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-none">
          <div className="flex space-x-2">
            <div className="w-2 h-2 rounded-full bg-gray-500 dark:bg-gray-400 animate-pulse" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 rounded-full bg-gray-500 dark:bg-gray-400 animate-pulse" style={{ animationDelay: '300ms' }}></div>
            <div className="w-2 h-2 rounded-full bg-gray-500 dark:bg-gray-400 animate-pulse" style={{ animationDelay: '600ms' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}