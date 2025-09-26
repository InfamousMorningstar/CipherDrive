import { motion } from 'framer-motion';
import { forwardRef } from 'react';

const Button = forwardRef(({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  terminal = false,
  className = '', 
  disabled = false,
  loading = false,
  onClick,
  ...props 
}, ref) => {
  const baseClasses = 'relative inline-flex items-center justify-center font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-bg disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: `
      bg-cipher-purple-600 hover:bg-cipher-purple-700 text-white 
      border border-cipher-purple-500 hover:border-cipher-purple-400
      focus:ring-cipher-purple-500 shadow-glow-purple hover:shadow-glow-purple
      ${terminal ? 'font-mono' : ''}
    `,
    secondary: `
      bg-cipher-teal-600 hover:bg-cipher-teal-700 text-white 
      border border-cipher-teal-500 hover:border-cipher-teal-400
      focus:ring-cipher-teal-500 shadow-glow-teal hover:shadow-glow-teal
      ${terminal ? 'font-mono' : ''}
    `,
    outline: `
      bg-transparent hover:bg-cipher-purple-600/10 text-cipher-purple-400 hover:text-cipher-purple-300
      border border-cipher-purple-500 hover:border-cipher-purple-400
      focus:ring-cipher-purple-500
      ${terminal ? 'font-mono' : ''}
    `,
    ghost: `
      bg-transparent hover:bg-dark-hover text-dark-text-secondary hover:text-dark-text-primary
      border border-transparent hover:border-dark-border
      ${terminal ? 'font-mono' : ''}
    `,
    terminal: `
      bg-dark-card hover:bg-dark-hover text-dark-text-primary
      border border-dark-border hover:border-cipher-purple-500
      font-mono shadow-inner-glow
      focus:ring-cipher-purple-500
    `,
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm rounded-lg',
    md: 'px-6 py-3 text-sm rounded-xl',
    lg: 'px-8 py-4 text-base rounded-xl',
    xl: 'px-10 py-5 text-lg rounded-2xl',
  };

  const terminalPrompt = terminal || variant === 'terminal' ? '> ' : '';

  return (
    <motion.button
      ref={ref}
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      onClick={onClick}
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      {...props}
    >
      {loading ? (
        <div className="flex items-center">
          <motion.div
            className="w-4 h-4 border-2 border-current border-t-transparent rounded-full mr-2"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
          Loading...
        </div>
      ) : (
        <span className="relative z-10">
          {terminalPrompt}{children}
        </span>
      )}
      
      {/* Neon glow effect */}
      <motion.div
        className="absolute inset-0 rounded-inherit opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{
          background: variant === 'primary' ? 
            'linear-gradient(90deg, rgba(168, 85, 247, 0.1), rgba(168, 85, 247, 0.2))' : 
            'linear-gradient(90deg, rgba(45, 212, 191, 0.1), rgba(45, 212, 191, 0.2))'
        }}
        initial={false}
      />
    </motion.button>
  );
});

Button.displayName = 'Button';

export default Button;