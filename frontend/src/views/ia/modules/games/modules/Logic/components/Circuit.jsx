import React, { useState, useCallback, useMemo } from 'react';

// ========================= LÓGICA PURA (SIN EFECTOS) =========================

// Funciones puras para cálculos lógicos
export const calculateGateOutput = (gateType, inputs, inputCount = 2) => {
  const { A, B, C } = inputs;
  const inputValues = Object.values(inputs);
  
  switch(gateType.toLowerCase()) {
    case 'and':
      return inputCount === 2 ? (A && B) : (A && B && C);
    case 'or':
      return inputCount === 2 ? (A || B) : (A || B || C);
    case 'xor':
      if (inputCount === 2) {
        return A !== B;
      } else {
        const activeCount = inputValues.filter(x => x).length;
        return activeCount % 2 === 1;
      }
    case 'nand':
      return inputCount === 2 ? !(A && B) : !(A && B && C);
    case 'nor':
      return inputCount === 2 ? !(A || B) : !(A || B || C);
    case 'nxor':
    case 'xnor':
      if (inputCount === 2) {
        return A === B;
      } else {
        const activeCount = inputValues.filter(x => x).length;
        return activeCount % 2 === 0;
      }
    default:
      return false;
  }
};

// ========================= COMPONENTE SVG PURO =========================

const LogicGateSVG = React.memo(({ 
  gateType, 
  inputs, 
  output, 
  inputCount = 2, 
  width = 100, 
  height = inputCount === 2 ? 60 : 70,
  scale = 1 
}) => {
  const actualWidth = width * scale;
  const actualHeight = height * scale;
  const inputNames = inputCount === 2 ? ['A', 'B'] : ['A', 'B', 'C'];
  const inputPositions = inputCount === 2 
    ? [{ y: 18, label: 'A' }, { y: 42, label: 'B' }]
    : [{ y: 15, label: 'A' }, { y: 35, label: 'B' }, { y: 55, label: 'C' }];
  
  const outputY = inputCount === 2 ? 30 : 35;

  const renderGateShape = () => {
    switch(gateType.toLowerCase()) {
      case 'and':
      case 'nand':
        return (
          <path 
            d={`M 20 ${inputCount === 2 ? '10' : '15'} L 50 ${inputCount === 2 ? '10' : '15'} A 20 20 0 0 1 50 ${inputCount === 2 ? '50' : '55'} L 20 ${inputCount === 2 ? '50' : '55'} Z`}
            fill="white" 
            stroke="black" 
            strokeWidth="2"
          />
        );
      case 'or':
      case 'nor':
        return (
          <path 
            d={`M 20 ${inputCount === 2 ? '10' : '15'} Q 35 ${inputCount === 2 ? '10' : '15'} 50 ${outputY} Q 35 ${inputCount === 2 ? '50' : '55'} 20 ${inputCount === 2 ? '50' : '55'} Q 30 ${outputY} 20 ${inputCount === 2 ? '10' : '15'}`}
            fill="white" 
            stroke="black" 
            strokeWidth="2"
          />
        );
      case 'xor':
      case 'nxor':
      case 'xnor':
        return (
          <g>
            <path 
              d={`M 15 ${inputCount === 2 ? '10' : '15'} Q 25 ${outputY} 15 ${inputCount === 2 ? '50' : '55'}`}
              fill="none" 
              stroke="black" 
              strokeWidth="2"
            />
            <path 
              d={`M 20 ${inputCount === 2 ? '10' : '15'} Q 35 ${inputCount === 2 ? '10' : '15'} 50 ${outputY} Q 35 ${inputCount === 2 ? '50' : '55'} 20 ${inputCount === 2 ? '50' : '55'} Q 30 ${outputY} 20 ${inputCount === 2 ? '10' : '15'}`}
              fill="white" 
              stroke="black" 
              strokeWidth="2"
            />
          </g>
        );
      default:
        return null;
    }
  };

  const renderNegationCircle = () => {
    if (['nand', 'nor', 'nxor', 'xnor'].includes(gateType.toLowerCase())) {
      const circleX = gateType.toLowerCase() === 'nand' ? 75 : 55;
      return (
        <circle 
          cx={circleX} 
          cy={outputY} 
          r="5" 
          fill="white" 
          stroke="black" 
          strokeWidth="2"
        />
      );
    }
    return null;
  };

  const getOutputStartX = () => {
    if (gateType.toLowerCase() === 'nand') return 70;
    if (['nor', 'nxor', 'xnor'].includes(gateType.toLowerCase())) return 50;
    if (['xor', 'or'].includes(gateType.toLowerCase())) return 50;
    return 70;
  };

  return (
    <svg width={actualWidth} height={actualHeight}>
      <defs>
        <style>{`
          .input-active { fill: #00ff00; stroke: #008000; }
          .input-inactive { fill: #cccccc; stroke: #666666; }
          .output-active { fill: #0080ff; stroke: #004080; }
          .output-inactive { fill: #cccccc; stroke: #666666; }
          .line-active { stroke: #00ff00; stroke-width: 3; }
          .line-inactive { stroke: #666666; stroke-width: 2; }
        `}</style>
      </defs>
      
      <g transform={`scale(${scale})`}>
        {inputPositions.map((pos, index) => {
          const inputName = inputNames[index];
          const isActive = inputs[inputName];
          const lineEndX = ['xor', 'nxor', 'xnor'].includes(gateType.toLowerCase()) ? 15 : 20;
          
          return (
            <g key={inputName}>
              <line 
                x1="0" 
                y1={pos.y} 
                x2={lineEndX} 
                y2={pos.y} 
                className={isActive ? 'line-active' : 'line-inactive'}
              />
              <circle 
                cx="0" 
                cy={pos.y} 
                r="3" 
                className={isActive ? 'input-active' : 'input-inactive'}
              />
              <text 
                x="8" 
                y={pos.y - 3} 
                fontFamily="Arial" 
                fontSize="10" 
                fill="black"
              >
                {pos.label}
              </text>
            </g>
          );
        })}

        {renderGateShape()}
        {renderNegationCircle()}

        <line 
          x1={getOutputStartX()} 
          y1={outputY} 
          x2={width} 
          y2={outputY} 
          className={output ? 'line-active' : 'line-inactive'}
        />
        
        <circle 
          cx={width} 
          cy={outputY} 
          r="3" 
          className={output ? 'output-active' : 'output-inactive'}
        />

        <text 
          x={gateType.toLowerCase() === 'nand' ? 35 : 30} 
          y={outputY + 3} 
          fontFamily="Arial" 
          fontSize={gateType.length > 3 ? "9" : "11"} 
          textAnchor="middle" 
          fill="black"
        >
          {gateType.toUpperCase()}
        </text>
        
        <text 
          x={width - 8} 
          y={outputY - 3} 
          fontFamily="Arial" 
          fontSize="10" 
          fill="black"
        >
          Y
        </text>
      </g>
    </svg>
  );
});

// ========================= COMPUERTA INDIVIDUAL SIMPLE =========================

export const SimpleLogicGate = ({ type, inputCount = 2, className = "" }) => {
  // Estado local simple sin efectos
  const [inputs, setInputs] = useState(() => {
    const initInputs = {};
    const inputNames = inputCount === 2 ? ['A', 'B'] : ['A', 'B', 'C'];
    inputNames.forEach(name => initInputs[name] = false);
    return initInputs;
  });

  // Cálculo inmediato de salida (sin useEffect)
  const output = useMemo(() => 
    calculateGateOutput(type, inputs, inputCount), 
    [type, inputs, inputCount]
  );

  const handleInputChange = useCallback((inputName, value) => {
    setInputs(prev => ({ ...prev, [inputName]: value }));
  }, []);

  return (
    <div className={`simple-logic-gate ${className}`}>
      <LogicGateSVG 
        gateType={type}
        inputs={inputs}
        output={output}
        inputCount={inputCount}
      />
      
      <div className="gate-controls">
        {Object.keys(inputs).map(inputName => (
          <label key={inputName} className="input-control">
            <input 
              type="checkbox"
              checked={inputs[inputName]}
              onChange={(e) => handleInputChange(inputName, e.target.checked)}
            />
            {inputName}: {inputs[inputName] ? 1 : 0}
          </label>
        ))}
        <div className="output-display">
          Output: <span className={output ? 'active' : 'inactive'}>
            {output ? 1 : 0}
          </span>
        </div>
      </div>
    </div>
  );
};
