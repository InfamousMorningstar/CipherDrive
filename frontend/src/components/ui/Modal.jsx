import { motion, AnimatePresence } from 'framer-motion';
import { useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'md', 
  terminal = false,
  showCloseButton = true,
  className = '' 
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4',
  };

  const backdropVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
  };

  const modalVariants = {
    hidden: { 
      opacity: 0, 
      scale: 0.95,
      y: 20,
    },
    visible: { 
      opacity: 1, 
      scale: 1,
      y: 0,
    },
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            variants={backdropVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
            onClick={onClose}
          />
          
          {/* Modal */}
          <motion.div
            className={`
              relative w-full ${sizes[size]} bg-dark-card border border-dark-border rounded-2xl 
              shadow-2xl backdrop-blur-md ${className}
            `}
            variants={modalVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
            transition={{ type: 'spring', duration: 0.5, bounce: 0.3 }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Terminal Header */}
            {terminal && (
              <div className="flex items-center justify-between p-4 pb-2 border-b border-dark-border/50">
                <div className="flex items-center space-x-3">
                  <div className="flex space-x-2">
                    <div className="w-3 h-3 rounded-full bg-status-error"></div>
                    <div className="w-3 h-3 rounded-full bg-status-warning"></div>
                    <div className="w-3 h-3 rounded-full bg-status-success"></div>
                  </div>
                  {title && (
                    <span className="text-sm font-mono text-dark-text-muted">
                      {title}
                    </span>
                  )}
                </div>
                {showCloseButton && (
                  <button
                    onClick={onClose}
                    className="p-1 text-dark-text-muted hover:text-dark-text-primary transition-colors rounded-lg hover:bg-dark-hover"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                )}
              </div>
            )}
            
            {/* Regular Header */}
            {!terminal && title && (
              <div className="flex items-center justify-between p-6 pb-4">
                <h2 className="text-xl font-semibold text-dark-text-primary">
                  {title}
                </h2>
                {showCloseButton && (
                  <motion.button
                    onClick={onClose}
                    className="p-2 text-dark-text-muted hover:text-dark-text-primary transition-colors rounded-xl hover:bg-dark-hover"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </motion.button>
                )}
              </div>
            )}
            
            {/* Content */}
            <div className={terminal ? 'p-4 pt-2' : title ? 'px-6 pb-6' : 'p-6'}>
              {children}
            </div>
            
            {/* Glow Effect */}
            <motion.div
              className="absolute inset-0 rounded-2xl pointer-events-none"
              style={{
                background: 'linear-gradient(45deg, rgba(168, 85, 247, 0.1), rgba(45, 212, 191, 0.1))',
                opacity: 0.5,
              }}
              animate={{ opacity: [0.3, 0.6, 0.3] }}
              transition={{ duration: 3, repeat: Infinity }}
            />
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default Modal;