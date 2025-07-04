import React from 'react'
import { getRandomHardColor, getRandomSoftColor } from '../lib/colors';

interface GateProps {
    label: string;
    type: "AND" | "OR" | "XOR" | "NAND" | "XNOR" | "NOR" | "NOT";
    position?: {
        x: number;
        y: number;
    }
}
export const GateSize = {
    x: 50,
    y: 30
}

export default function Gate({ label, type, position }: GateProps) {
    const color = getRandomHardColor()
  return (
    <g transform={`translate(${position?.x}, ${position?.y})`}>
      <rect width={GateSize.x} height={GateSize.y} fill={getRandomSoftColor()} stroke="black" />
      <text x={GateSize.x / 2} y={GateSize  .y / 2} textAnchor="middle" dominantBaseline="middle" fill={color}>
        {label}
      </text>
      <text x={GateSize.x / 2} y={GateSize.y + 5} textAnchor="middle" dominantBaseline="middle" fill={color}>
        {type}
      </text>
    </g>
  )
}
