import React, { ReactNode, CSSProperties } from 'react';

// TypeScript interface for Marquee component props
interface MarqueeProps {
  /** Content to be displayed in the marquee */
  children: ReactNode;
  /** Direction of the scroll animation */
  direction?: 'left' | 'right';
  /** Speed of the animation in seconds (lower = faster) */
  speed?: number;
  /** Whether to pause animation on hover */
  pauseOnHover?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Inline styles */
  style?: CSSProperties;
  /** Element ID */
  id?: string;
}

export const Marquee: React.FC<MarqueeProps> = ({ 
  children, 
  direction = 'left', 
  speed = 50, 
  pauseOnHover = true,
  className = '',
  style,
  id
}) => {
  const animationDirection = direction === 'right' ? 'reverse' : 'normal';
  
  const marqueeStyle = {
    overflow: 'hidden',
    whiteSpace: 'nowrap',
    width: '100%'
  };

  const contentStyle = {
    display: 'inline-block',
    animation: `scroll ${speed}s linear infinite`,
    animationDirection: animationDirection,
    ...(pauseOnHover && {
      animationPlayState: 'running'
    })
  };

  // const hoverStyle = pauseOnHover ? {
  //   ':hover': {
  //     animationPlayState: 'paused'
  //   }
  // } : {};

  return (
    <div className={className} style={style} id={id}>
      <style jsx>{`
        @keyframes scroll {
          0% {
            transform: translateX(100%);
          }
          100% {
            transform: translateX(-100%);
          }
        }
        
        .marquee-content:hover {
          animation-play-state: ${pauseOnHover ? 'paused' : 'running'};
        }
      `}</style>
      
      <div style={marqueeStyle}>
        <div 
          className="marquee-content"
          style={contentStyle}
        >
          {children}
        </div>
      </div>
    </div>
  );
};
