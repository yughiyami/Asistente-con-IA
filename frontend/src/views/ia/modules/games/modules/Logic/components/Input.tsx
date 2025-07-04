import React from 'react'
import { getRandomHardColor } from '../lib/colors';

interface InputProps {
    label: string;
    position?: {
        x: number;
        y: number;
    }
}

export const InputSize = 20
export default function Input({label, position}: InputProps) {
  return (
    <g transform={`translate(${position?.x}, ${position?.y})`}>
        <circle cx={InputSize} cy={InputSize} r={InputSize} fill='#f0f0f0' stroke='#000' strokeWidth={2}>
        </circle>
        <text x={InputSize} y={InputSize} textAnchor="middle" dominantBaseline="middle" fill={getRandomHardColor()}>
            {label}
        </text>
    </g>
  )
}
