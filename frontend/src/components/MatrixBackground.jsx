import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const MatrixBackground = () => {
  const [matrixColumns, setMatrixColumns] = useState([]);

  useEffect(() => {
    // Create matrix columns
    const columns = [];
    const columnCount = Math.floor(window.innerWidth / 20);
    
    for (let i = 0; i < columnCount; i++) {
      columns.push({
        id: i,
        chars: generateRandomChars(20),
        delay: Math.random() * 2,
        duration: 15 + Math.random() * 10,
        x: i * 20,
      });
    }
    
    setMatrixColumns(columns);
  }, []);

  const generateRandomChars = (count) => {
    const chars = '01ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz~!@#$%^&*()_+-=[]{}|;:,.<>?';
    const result = [];
    
    for (let i = 0; i < count; i++) {
      result.push({
        char: chars.charAt(Math.floor(Math.random() * chars.length)),
        opacity: Math.random() * 0.8 + 0.2,
      });
    }
    
    return result;
  };

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {/* Main matrix effect */}
      <div className="relative w-full h-full">
        {matrixColumns.map((column) => (
          <motion.div
            key={column.id}
            className="absolute top-0 text-cipher-teal-400"
            style={{ left: column.x }}
            initial={{ y: '-100%' }}
            animate={{ y: '100vh' }}
            transition={{
              duration: column.duration,
              delay: column.delay,
              repeat: Infinity,
              ease: 'linear',
            }}
          >
            {column.chars.map((item, index) => (
              <div
                key={index}
                className="text-xs font-mono leading-tight"
                style={{ 
                  opacity: item.opacity * 0.3,
                  color: index === 0 ? '#2dd4bf' : '#a855f7',
                }}
              >
                {item.char}
              </div>
            ))}
          </motion.div>
        ))}
      </div>

      {/* Binary grid overlay */}
      <div className="absolute inset-0 opacity-5">
        <div className="grid grid-cols-20 gap-4 h-full text-cipher-purple-400 text-xs font-mono">
          {Array.from({ length: 400 }, (_, i) => (
            <div key={i} className="flex items-center justify-center">
              {Math.random() > 0.5 ? '1' : '0'}
            </div>
          ))}
        </div>
      </div>

      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-dark-bg/50 to-dark-bg/80" />
    </div>
  );
};

export default MatrixBackground;