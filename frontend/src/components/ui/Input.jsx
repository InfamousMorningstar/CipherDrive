import { motion } from 'framer-motion';
import { forwardRef, useState } from 'react';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

const Input = forwardRef(({ 
  type = 'text',
  label,
  placeholder,
  error,
  terminal = false,
  className = '',
  containerClassName = '',
  disabled = false,
  required = false,
  ...props 
}, ref) => {
  const [showPassword, setShowPassword] = useState(false);
  const [focused, setFocused] = useState(false);

  const inputType = type === 'password' && showPassword ? 'text' : type;
  const isPassword = type === 'password';

  const baseClasses = `
    w-full px-4 py-3 rounded-xl border transition-all duration-300
    bg-dark-card text-dark-text-primary placeholder-dark-text-muted
    focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-bg
    disabled:opacity-50 disabled:cursor-not-allowed
    ${terminal ? 'font-mono' : ''}
    ${error ? 
      'border-status-error focus:border-status-error focus:ring-status-error/50' : 
      focused ? 
        'border-cipher-purple-500 focus:border-cipher-purple-400 focus:ring-cipher-purple-500/50' :
        'border-dark-border hover:border-dark-border/70'
    }
  `;

  return (
    <div className={`space-y-2 ${containerClassName}`}>
      {label && (
        <motion.label 
          className={`block text-sm font-medium ${terminal ? 'font-mono' : ''} ${
            error ? 'text-status-error' : 'text-dark-text-secondary'
          }`}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          {terminal && '> '}{label}
          {required && <span className="text-status-error ml-1">*</span>}
        </motion.label>
      )}
      
      <div className="relative">
        <motion.input
          ref={ref}
          type={inputType}
          placeholder={placeholder}
          className={`${baseClasses} ${isPassword ? 'pr-12' : ''} ${className}`}
          disabled={disabled}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          {...props}
          whileFocus={{
            boxShadow: error ? 
              '0 0 0 3px rgba(239, 68, 68, 0.1)' : 
              '0 0 0 3px rgba(168, 85, 247, 0.1)'
          }}
        />
        
        {/* Terminal cursor animation when focused */}
        {terminal && focused && !props.value && (
          <motion.div
            className="absolute right-4 top-1/2 transform -translate-y-1/2 w-2 h-5 bg-cipher-teal-400"
            animate={{ opacity: [1, 0, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}
        
        {/* Password toggle */}
        {isPassword && (
          <button
            type="button"
            className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 text-dark-text-muted hover:text-dark-text-secondary transition-colors"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? (
              <EyeSlashIcon className="h-5 w-5" />
            ) : (
              <EyeIcon className="h-5 w-5" />
            )}
          </button>
        )}
        
        {/* Glow effect when focused */}
        {focused && (
          <motion.div
            className={`absolute inset-0 rounded-xl ${
              error ? 'shadow-[0_0_20px_rgba(239,68,68,0.2)]' : 'shadow-[0_0_20px_rgba(168,85,247,0.2)]'
            } pointer-events-none`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
        )}
      </div>
      
      {/* Error message */}
      {error && (
        <motion.p 
          className={`text-sm text-status-error ${terminal ? 'font-mono' : ''}`}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {terminal && '! '}Error: {error}
        </motion.p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;