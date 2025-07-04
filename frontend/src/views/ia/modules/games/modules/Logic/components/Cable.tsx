import React from 'react'
import { getRandomHardColor } from '../lib/colors';

interface CableProps {
    origin: {
        x: number;
        y: number;
    }
    destination: {
        x: number;
        y: number;
    }
}

export const CableSize = 2

export default function Cable({ origin, destination }: CableProps) {
  return (
    <polyline
      points={`${origin.x},${origin.y} ${(origin.x * 3 + destination.x) / 4},${origin.y} ${(origin.x + destination.x * 3) / 4},${destination.y} ${destination.x},${destination.y}`}
      stroke={getRandomHardColor()}
      strokeWidth={CableSize}
      fill="none"
    />
  )
}
