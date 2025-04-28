import { Textarea } from '@/components/ui/textarea'
import React from 'react'
import { FiSend, FiX } from 'react-icons/fi'
import { Toaster } from 'sonner'

interface PromptType {
  id: string
  text: string
  icon: React.ReactNode
}

interface PromptFormProps {
  filteredPrompts: PromptType[]
  onSubmit?: (input: string) => void
  placeholder?: string
}

function usePromptObject() {
  
  const [input, setInput] = React.useState('')
  const inputRef = React.useRef<HTMLTextAreaElement>(null)

  return {
    values: {
      input,
    },
    handlers: {
      setInput,
    },
    refs: {
      inputRef,
    }
  }
}

function usePromptForm(action : (a: string) => Promise<void>) {
  const object = usePromptObject()

  const {
    values: { input },
    handlers: { setInput },
    refs: { inputRef },
  } = object
  const [loading, setLoading] = React.useState(false)

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const trimmedInput = input.trim();
    setInput('');
    action(trimmedInput).then(() => {
      setLoading(false)
    })
    // Aquí iría la lógica para enviar el mensaje al backend
  }

  const handlePredefinedPrompt = (prompt: string) => {
    setInput(prompt);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  return { 
    object,
    form: {
      handleAction: sendMessage,
      loading,
    },
    actions: {
      handlePredefinedPrompt
    }
  }
}

export default function PromptForm({filteredPrompts, onSubmit, placeholder}: PromptFormProps) {

  const {
    object: {
      values: { input },
      handlers: { setInput },
      refs: { inputRef },
    },
    form: { handleAction, loading },
    actions: { handlePredefinedPrompt },
  } = usePromptForm(async (a) => onSubmit?.(a))

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const trimmedInput = input.trim();
    setInput('');

    onSubmit?.(trimmedInput)
  }

  return (
    <form className="border-t dark:border-gray-800 p-4">
      <Toaster position="bottom-center" />
      
      {/* Prompts predefinidos */}
      {filteredPrompts.length > 0 && (
        <div className="mb-4 overflow-x-auto whitespace-nowrap pb-2 scrollbar-thin">
          <div className="flex space-x-2">
            {filteredPrompts.map((prompt) => (
              <button
                type='button'
                key={prompt.id}
                onClick={() => handlePredefinedPrompt(prompt.text)}
                className="flex items-center px-3 py-1.5 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-full hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <span className="mr-2">{prompt.icon}</span>
                <span className="truncate max-w-[150px]">{prompt.text}</span>
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* Área de entrada de mensaje */}
      <div className="flex items-center gap-x-4">
        <div className="flex-1 relative">
          <Textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            // rows={rows}
            placeholder={ placeholder ?? "Escribe un mensaje..."
              // mode === 'chat' ? "Escribe una pregunta sobre arquitectura de computadoras..." :
              // mode === 'exam' ? "Solicita un examen sobre un tema específico..." :
              // "Elige un juego educativo para aprender..."
            }
            disabled={loading}
            className="w-full max-h-32 resize-none py-3 px-4 rounded-lg border border-gray-300 dark:border-gray-700 focus:outline-hidden focus:ring-2 focus:ring-primary-500 dark:bg-gray-800 dark:text-white"
          />
            
            {input && (
              <button
                type="button"
                onClick={() => setInput('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <FiX className="w-4 h-4" />
              </button>
            )}
          </div>
          
          <button
            onClick={handleAction}
            disabled={!input.trim() || loading}
            className="shrink-0 p-3 rounded-lg bg-primary-500 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary-600 transition-colors"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <FiSend className="w-5 h-5" />
            )}
          </button>
        </div>
      </form>
  )
}
