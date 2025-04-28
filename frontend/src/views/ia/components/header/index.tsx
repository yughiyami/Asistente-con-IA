import React from 'react'
import ModeSelector from './ModeSelector'
import ThemeToggle from './ThemeToggle'
import { FiCpu } from 'react-icons/fi'

export default function Header() {
  return (
    <header className="px-4 py-3 bg-white dark:bg-gray-800 shadow-xs z-10">
    <div className="flex items-center justify-between max-w-6xl mx-auto">
      <div className="flex items-center">
        <FiCpu className="w-6 h-6 text-primary-500 mr-2" />
        <h1 className="text-lg font-bold">Asistente de Arquitectura</h1>
      </div>
      
      <div className="flex items-center space-x-4">
        <ModeSelector />
        <ThemeToggle />
      </div>
    </div>
  </header>
  )
}
