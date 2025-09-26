import { motion } from 'framer-motion';
import { forwardRef } from 'react';

const Card = forwardRef(({ 
  children, 
  title,
  terminal = false,
  hover = true,
  glow = false,
  className = '', 
  onClick,
  ...props 
}, ref) => {
  const baseClasses = `
    bg-dark-card border border-dark-border rounded-2xl backdrop-blur-sm
    ${hover ? 'transition-all duration-300 hover:border-cipher-purple-500/50 hover:shadow-glow-purple/20' : ''}
    ${onClick ? 'cursor-pointer' : ''}
    ${glow ? 'shadow-glow-purple' : ''}
  `;

  const cardContent = (
    <>
      {/* Terminal Header */}
      {terminal && (
        <div className="flex items-center justify-between p-4 pb-3 border-b border-dark-border/50">
          <div className="flex items-center space-x-3">
            <div className="flex space-x-2">
              <div className="w-2.5 h-2.5 rounded-full bg-status-error"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-status-warning"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-status-success"></div>
            </div>
            {title && (
              <span className="text-xs font-mono text-dark-text-muted">
                {title}
              </span>
            )}
          </div>
          <div className="flex space-x-1">
            <motion.div
              className="w-1 h-1 bg-cipher-teal-400 rounded-full"
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0 }}
            />
            <motion.div
              className="w-1 h-1 bg-cipher-teal-400 rounded-full"
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
            />
            <motion.div
              className="w-1 h-1 bg-cipher-teal-400 rounded-full"
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.6 }}
            />
          </div>
        </div>
      )}
      
      {/* Regular Header */}
      {!terminal && title && (
        <div className="p-6 pb-4">
          <h3 className="text-lg font-semibold text-dark-text-primary">
            {title}
          </h3>
        </div>
      )}
      
      {/* Content */}
      <div className={terminal ? 'p-4 pt-3' : title && !terminal ? 'px-6 pb-6' : 'p-6'}>
        {children}
      </div>
    </>
  );

  if (onClick) {
    return (
      <motion.div
        ref={ref}
        className={`${baseClasses} ${className}`}
        onClick={onClick}
        whileHover={hover ? { y: -2, scale: 1.01 } : {}}
        whileTap={{ scale: 0.99 }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        {...props}
      >
        {cardContent}
        
        {/* Hover glow effect */}
        {hover && (
          <motion.div
            className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cipher-purple-500/5 to-cipher-teal-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
            initial={false}
          />
        )}
      </motion.div>
    );
  }

  return (
    <motion.div
      ref={ref}
      className={`${baseClasses} ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      {...props}
    >
      {cardContent}
    </motion.div>
  );
});

Card.displayName = 'Card';

export default Card;