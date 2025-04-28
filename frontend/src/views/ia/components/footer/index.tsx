import React from 'react'
import { FiInfo } from 'react-icons/fi'

export default function Footer() {
  return (
    <footer className="px-4 py-2 text-xs text-center text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-center">
          <FiInfo className="w-3 h-3 mr-1" />
          <span>Asistente educativo para Arquitectura de Computadoras • {new Date().getFullYear()}</span>
        </div>
      </footer>
  )
}
