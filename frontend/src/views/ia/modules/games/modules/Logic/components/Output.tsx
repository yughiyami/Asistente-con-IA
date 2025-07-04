import React from 'react'
import { getRandomHardColor, getRandomSoftColor } from '../lib/colors';

interface OutputProps {
    label: string;
    position?: {
        x: number;
        y: number;
    }
}

export const OutputSize = 20;
export default function Output({ label, position }: OutputProps) {
  return (
    <g transform={`translate(${position?.x}, ${position?.y})`}>
        <circle cx={OutputSize} cy={OutputSize} r={OutputSize} fill={getRandomSoftColor()} stroke={getRandomHardColor()} strokeWidth={2} />
        <text x={OutputSize} y={OutputSize} textAnchor="middle" dominantBaseline="middle">
            {label}
        </text>
    </g>
  )
}
