import React from 'react'
import Cable from './Cable'
import Input, { InputSize } from './Input'
import Output, { OutputSize } from './Output'
import Gate, { GateSize } from './Gate'
import { getRandomSoftColor } from '../lib/colors'

interface CircuitProps {
    inputs: string[];
    output: string;
    gates: {
        id: string;
        type: "AND" | "OR" | "XOR" | "NAND" | "XNOR" | "NOR" | "NOT";
        inputs: string[];
    }[];
}

export default function Circuit({inputs, output, gates}: CircuitProps) {

 // ===== LAYOUT CONFIGURATION =====
  const LAYOUT = {
    canvas: {
      width: 800,
      minHeight: 250,
      heightPerGate: 60
    },
    spacing: {
      inputFromEdge: 50,
      gateFromInputs: 120,
      gateHorizontal: 120,
      gateVertical: 70,
      outputFromLastGate: 100,
      cableOffset: 8
    },
    margins: {
      top: 40,
      bottom: 40,
      inputDistribution: 0.7 // Use 70% of canvas height for input distribution
    },
    randomization: {
      gateOffsetX: 25,  // Max random offset in X
      gateOffsetY: 20,  // Max random offset in Y
      inputOutputY: 10  // Max random offset for input/output connections
    }
  };
  
  // Random offset function
  const getRandomOffset = (max: number) => (Math.random() - 0.5) * 2 * max;
  
  // Calculate dynamic dimensions
  const SVG_WIDTH = LAYOUT.canvas.width;
  const SVG_HEIGHT = Math.max(
    LAYOUT.canvas.minHeight, 
    LAYOUT.margins.top + LAYOUT.margins.bottom + gates.length * LAYOUT.canvas.heightPerGate
  );
  
  // Calculate input spacing dynamically based on canvas height
  const availableHeightForInputs = SVG_HEIGHT * LAYOUT.margins.inputDistribution;
  const inputSpacing = inputs.length > 1 
    ? availableHeightForInputs / (inputs.length - 1) 
    : 0;
  const inputStartY = (SVG_HEIGHT - availableHeightForInputs) / 2;
  
  // Calculate positions for inputs (dynamically distributed with variation)
  const inputPositions = inputs.map((input, index) => ({
    label: input,
    position: {
      x: LAYOUT.spacing.inputFromEdge,
      y: inputs.length === 1 
        ? SVG_HEIGHT / 2 - InputSize / 2  // Center single input
        : inputStartY + index * inputSpacing
    },
    // Add slight variation to output connection points
    outputOffset: getRandomOffset(LAYOUT.randomization.inputOutputY)
  }));
  
  // Organize gates by levels (depth in the circuit)
  const organizeGatesByLevels = (gates: typeof gates) => {
    const levels: string[][] = [];
    
    // Helper function to calculate gate level
    const getGateLevel = (gateId: string, visited = new Set<string>()): number => {
      if (visited.has(gateId)) return 0; // Avoid circular dependencies
      visited.add(gateId);
      
      const gate = gates.find(g => g.id === gateId);
      if (!gate) return 0;
      
      let maxInputLevel = -1;
      gate.inputs.forEach(input => {
        // If input is from another gate, get its level
        if (gates.some(g => g.id === input)) {
          maxInputLevel = Math.max(maxInputLevel, getGateLevel(input, new Set(visited)));
        }
      });
      
      return maxInputLevel + 1;
    };
    
    // Calculate levels for all gates
    gates.forEach(gate => {
      const level = getGateLevel(gate.id);
      if (!levels[level]) levels[level] = [];
      levels[level].push(gate.id);
    });
    
    return levels;
  };
  
  const gateLevels = organizeGatesByLevels(gates);
  
  // Calculate positions for gates organized by levels
  const gateStartX = LAYOUT.spacing.inputFromEdge + LAYOUT.spacing.gateFromInputs;
  const gatePositions = gates.map((gate) => {
    // Find which level this gate belongs to
    let level = 0;
    let positionInLevel = 0;
    
    for (let i = 0; i < gateLevels.length; i++) {
      const levelIndex = gateLevels[i].indexOf(gate.id);
      if (levelIndex !== -1) {
        level = i;
        positionInLevel = levelIndex;
        break;
      }
    }
    
    // Calculate positions within level
    const levelGatesCount = gateLevels[level]?.length || 1;
    const levelHeight = SVG_HEIGHT - LAYOUT.margins.top - LAYOUT.margins.bottom;
    const gateSpacingInLevel = levelGatesCount > 1 ? levelHeight / (levelGatesCount + 1) : levelHeight / 2;
    
    return {
      ...gate,
      position: {
        x: gateStartX + (level * LAYOUT.spacing.gateHorizontal) + getRandomOffset(LAYOUT.randomization.gateOffsetX),
        y: LAYOUT.margins.top + (positionInLevel + 1) * gateSpacingInLevel + getRandomOffset(LAYOUT.randomization.gateOffsetY)
      }
    };
  });
  
  // Find the output gate (gate that produces the final output)
  const outputGateIndex = gates.findIndex(gate => gate.id === output);
  const finalGateIndex = outputGateIndex !== -1 
    ? outputGateIndex 
    : gates.findIndex(gate => !gates.some(otherGate => otherGate.inputs.includes(gate.id)));
  
  // Calculate output position dynamically based on the correct final gate
  const outputSourceGate = finalGateIndex !== -1 ? gatePositions[finalGateIndex] : null;
  const lastGateX = outputSourceGate 
    ? outputSourceGate.position.x 
    : (gatePositions.length > 0 ? Math.max(...gatePositions.map(g => g.position.x)) : gateStartX);
  const outputY = outputSourceGate 
    ? outputSourceGate.position.y + GateSize.y / 2 - OutputSize / 2
    : (gatePositions.length > 0 
        ? gatePositions.reduce((sum, g) => sum + g.position.y, 0) / gatePositions.length + GateSize.y / 2 - OutputSize / 2
        : SVG_HEIGHT / 2 - OutputSize / 2);
    
  const outputPosition = {
    label: output,
    position: {
      x: lastGateX + GateSize.x + LAYOUT.spacing.outputFromLastGate,
      y: outputY
    }
  };
  
  // Generate cables with improved vertical separation to avoid convergence
  const cables = [];
  const gateConnectionCounters = new Map();
  
  // Helper function to get connection offset for better cable separation
  const getConnectionOffset = (gateId: string, totalInputs: number) => {
    if (!gateConnectionCounters.has(gateId)) {
      gateConnectionCounters.set(gateId, 0);
    }
    const currentCount = gateConnectionCounters.get(gateId);
    gateConnectionCounters.set(gateId, currentCount + 1);
    
    // Center the cables around the gate's center
    const spacing = LAYOUT.spacing.cableOffset;
    const totalOffset = (totalInputs - 1) * spacing;
    const startOffset = -totalOffset / 2;
    return startOffset + currentCount * spacing;
  };
  
  // Create smart cable routing with vertical separation
  const createSmartCable = (origin: {x: number, y: number}, destination: {x: number, y: number}, routingIndex: number = 0) => {
    const deltaX = destination.x - origin.x;
    const deltaY = destination.y - origin.y;
    
    // Calculate vertical separation to avoid convergence
    const verticalSeparation = routingIndex * 12; // 12px separation per cable
    const horizontalMidpoint = origin.x + deltaX * 0.7;
    
    // For connections crossing multiple levels, add intermediate routing
    if (Math.abs(deltaX) > LAYOUT.spacing.gateHorizontal) {
      // Route through an intermediate point to avoid convergence
      const intermediateY = origin.y + deltaY * 0.3 + verticalSeparation;
      
      return {
        origin,
        destination: {
          x: horizontalMidpoint,
          y: intermediateY
        },
        color: getRandomSoftColor(),
        continuation: {
          origin: {
            x: horizontalMidpoint,
            y: intermediateY
          },
          destination,
          color: getRandomSoftColor()
        }
      };
    }
    
    // For short connections, simple direct route with slight offset
    return {
      origin: {
        x: origin.x,
        y: origin.y + (routingIndex % 3 - 1) * 5 // Slight vertical offset
      },
      destination,
      color: getRandomSoftColor()
    };
  };
  
  // Track routing indices to prevent convergence
  const routingIndices = new Map();
  const getRoutingIndex = (originX: number, destX: number) => {
    const key = `${Math.floor(originX / 50)}-${Math.floor(destX / 50)}`;
    if (!routingIndices.has(key)) {
      routingIndices.set(key, 0);
    }
    const index = routingIndices.get(key);
    routingIndices.set(key, index + 1);
    return index;
  };
  
  // Connect inputs to gates with smart routing
  inputs.forEach((input, inputIndex) => {
    const inputPos = inputPositions[inputIndex];
    const gatesUsingThisInput = gates.filter(gate => gate.inputs.includes(input));
    
    gatesUsingThisInput.forEach((gate, connectionIndex) => {
      const gateIndex = gates.findIndex(g => g.id === gate.id);
      const gatePos = gatePositions[gateIndex];
      
      // Add variation to input output point
      const inputOutputY = inputPos.position.y + InputSize / 2 + 
        (connectionIndex - (gatesUsingThisInput.length - 1) / 2) * LAYOUT.spacing.cableOffset;
      
      const connectionOffset = getConnectionOffset(gate.id, gate.inputs.length);
      const routingIndex = getRoutingIndex(inputPos.position.x, gatePos.position.x);
      
      const cableData = createSmartCable(
        {
          x: inputPos.position.x + InputSize,
          y: inputOutputY
        },
        {
          x: gatePos.position.x,
          y: gatePos.position.y + GateSize.y / 2 + connectionOffset
        },
        routingIndex
      );
      
      cables.push(cableData);
      
      // Add continuation cable if exists
      if (cableData.continuation) {
        cables.push(cableData.continuation);
      }
    });
  });
  
  // Reset counters for gate-to-gate connections
  gateConnectionCounters.clear();
  
  // Connect gates to other gates with smart routing
  gates.forEach((gate) => {
    gate.inputs.forEach(inputName => {
      const sourceGateIndex = gates.findIndex(g => g.id === inputName);
      if (sourceGateIndex !== -1) {
        const sourceGate = gatePositions[sourceGateIndex];
        const targetGateIndex = gates.findIndex(g => g.id === gate.id);
        const targetGate = gatePositions[targetGateIndex];
        
        const connectionOffset = getConnectionOffset(gate.id, gate.inputs.length);
        const routingIndex = getRoutingIndex(sourceGate.position.x, targetGate.position.x);
        
        const cableData = createSmartCable(
          {
            x: sourceGate.position.x + GateSize.x,
            y: sourceGate.position.y + GateSize.y / 2
          },
          {
            x: targetGate.position.x,
            y: targetGate.position.y + GateSize.y / 2 + connectionOffset
          },
          routingIndex
        );
        
        cables.push(cableData);
        
        // Add continuation cable if exists
        if (cableData.continuation) {
          cables.push(cableData.continuation);
        }
      }
    });
  });
  
  // Connect the correct final gate to output
  if (finalGateIndex !== -1) {
    const finalGate = gatePositions[finalGateIndex];
    const routingIndex = getRoutingIndex(finalGate.position.x, outputPosition.position.x);
    
    const cableData = createSmartCable(
      {
        x: finalGate.position.x + GateSize.x,
        y: finalGate.position.y + GateSize.y / 2
      },
      {
        x: outputPosition.position.x,
        y: outputPosition.position.y + OutputSize / 2
      },
      routingIndex
    );
    
    cables.push(cableData);
    
    // Add continuation cable if exists
    if (cableData.continuation) {
      cables.push(cableData.continuation);
    }
  }

  return (
    <svg width="100%" height="100%" className='overflow-y-scroll' viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}>
        <rect width="100%" height="100%" fill={getRandomSoftColor()}/>   
       {/* Grid pattern (optional, like in the image) */}
      <defs>
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e9ecef" strokeWidth="0.5"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />
      
      {/* Render cables first (behind other elements) */}
      {cables.map((cable, index) => (
        <Cable 
          key={`cable-${index}`}
          origin={cable.origin}
          destination={cable.destination}
        />
      ))}
      
      {/* Render inputs */}
      {inputPositions.map((input, index) => (
        <Input 
          key={`input-${index}`}
          label={input.label}
          position={input.position}
        />
      ))}
      
      {/* Render gates */}
      {gatePositions.map((gate) => (
        <Gate 
          key={gate.id}
          label={gate.id}
          type={gate.type}
          position={gate.position}
        />
      ))}
      
      {/* Render output */}
      <Output 
        label={outputPosition.label}
        position={outputPosition.position}
      />
    </svg>
  )
}
