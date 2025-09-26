import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  InformationCircleIcon, 
  ExclamationTriangleIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline';

const Toast = ({ 
  toast, 
  onDismiss, 
  terminal = true 
}) => {
  const { id, type = 'info', title, message, duration = 5000 } = toast;

  const icons = {
    success: CheckCircleIcon,
    error: XCircleIcon,
    warning: ExclamationTriangleIcon,
    info: InformationCircleIcon,
  };

  const colors = {
    success: {
      bg: 'bg-status-success/10',
      border: 'border-status-success/50',
      text: 'text-status-success',
      glow: 'shadow-[0_0_20px_rgba(16,185,129,0.3)]',
    },
    error: {
      bg: 'bg-status-error/10',
      border: 'border-status-error/50',
      text: 'text-status-error',
      glow: 'shadow-[0_0_20px_rgba(239,68,68,0.3)]',
    },
    warning: {
      bg: 'bg-status-warning/10',
      border: 'border-status-warning/50',
      text: 'text-status-warning',
      glow: 'shadow-[0_0_20px_rgba(245,158,11,0.3)]',
    },
    info: {
      bg: 'bg-cipher-purple-500/10',
      border: 'border-cipher-purple-500/50',
      text: 'text-cipher-purple-400',
      glow: 'shadow-[0_0_20px_rgba(168,85,247,0.3)]',
    },
  };

  const Icon = icons[type];
  const colorScheme = colors[type];

  const toastVariants = {
    initial: { 
      opacity: 0, 
      x: 300, 
      scale: 0.9,
    },
    animate: { 
      opacity: 1, 
      x: 0, 
      scale: 1,
    },
    exit: { 
      opacity: 0, 
      x: 300, 
      scale: 0.9,
    },
  };

  return (
    <motion.div
      variants={toastVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ type: 'spring', duration: 0.5, bounce: 0.3 }}
      className={`
        relative max-w-sm w-full bg-dark-card border rounded-2xl p-4 backdrop-blur-md
        ${colorScheme.bg} ${colorScheme.border} ${colorScheme.glow}
      `}
    >
      {/* Terminal Header */}
      {terminal && (
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-dark-border/30">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-status-error"></div>
            <div className="w-2 h-2 rounded-full bg-status-warning"></div>
            <div className="w-2 h-2 rounded-full bg-status-success"></div>
            <span className="text-xs font-mono text-dark-text-muted ml-2">
              system.log
            </span>
          </div>
          <button
            onClick={() => onDismiss(id)}
            className="p-1 text-dark-text-muted hover:text-dark-text-primary transition-colors rounded"
          >
            <XMarkIcon className="h-4 w-4" />
          </button>
        </div>
      )}
      
      {/* Content */}
      <div className="flex items-start space-x-3">
        <div className={`flex-shrink-0 ${colorScheme.text}`}>
          <Icon className="h-6 w-6" />
        </div>
        
        <div className="flex-1 min-w-0">
          {title && (
            <p className={`text-sm font-semibold ${terminal ? 'font-mono' : ''} ${colorScheme.text}`}>
              {terminal && '> '}{title}
            </p>
          )}
          <p className={`text-sm text-dark-text-secondary mt-1 ${terminal ? 'font-mono' : ''}`}>
            {terminal && '  '}{message}
          </p>
        </div>
        
        {!terminal && (
          <button
            onClick={() => onDismiss(id)}
            className="flex-shrink-0 p-1 text-dark-text-muted hover:text-dark-text-primary transition-colors rounded"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        )}
      </div>
      
      {/* Progress Bar */}
      {duration && (
        <motion.div
          className={`absolute bottom-0 left-0 h-1 rounded-b-2xl ${colorScheme.text.replace('text-', 'bg-')}`}
          initial={{ width: '100%' }}
          animate={{ width: '0%' }}
          transition={{ duration: duration / 1000, ease: 'linear' }}
          onAnimationComplete={() => onDismiss(id)}
        />
      )}
      
      {/* Glitch effect on error */}
      {type === 'error' && (
        <motion.div
          className="absolute inset-0 bg-status-error/5 rounded-2xl pointer-events-none"
          animate={{ opacity: [0, 0.3, 0] }}
          transition={{ duration: 0.1, repeat: 3, repeatDelay: 0.5 }}
        />
      )}
    </motion.div>
  );
};

// Toast Container Component
export const ToastContainer = ({ toasts, onDismiss, position = 'top-right' }) => {
  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2',
  };

  return (
    <div className={`fixed z-50 ${positionClasses[position]} space-y-4`}>
      <AnimatePresence>
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            toast={toast}
            onDismiss={onDismiss}
          />
        ))}
      </AnimatePresence>
    </div>
  );
};

export default Toast;