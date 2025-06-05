import { Button } from '@/components/ui/button';
import React from 'react'

interface WordBlockProps {
  text: string;
  onClick?: () => void;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  disabled?: boolean;
  className?: string
}

export default function WordBlock({text, onClick, variant, disabled, className}: WordBlockProps) {
  className = `aspect-square p-2 bg-primary-500 rounded-md w-8 h-8 text-center align-middle ${className}`
  return (
    <Button variant={variant} className={className}
      onClick={onClick}
      disabled={disabled}
    >
      {text}
    </Button>
  )
}
