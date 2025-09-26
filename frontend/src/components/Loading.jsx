import { motion } from 'framer-motion';
import { ComputerDesktopIcon } from '@heroicons/react/24/outline';

const Loading = ({ message = "Initializing CipherDrive...", fullScreen = true }) => {
  const bootSequence = [
    "Initializing quantum encryption protocols...",
    "Loading neural network interface...",
    "Establishing secure connections...",
    "Activating matrix authentication...",
    "CipherDrive ready for operation.",
  ];

  const LoadingContent = () => (
    <div className="flex flex-col items-center justify-center space-y-8">
      {/* Logo with Pulsing Effect */}
      <motion.div
        className="relative"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        <motion.div
          className="absolute inset-0 rounded-2xl bg-cipher-purple-glow blur-xl"
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.6, 0.3]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <div className="relative bg-dark-card border border-dark-border rounded-2xl p-6">
          <ComputerDesktopIcon className="h-16 w-16 text-cipher-teal-400 mx-auto" />
        </div>
      </motion.div>

      {/* Brand Name */}
      <motion.h1
        className="text-4xl font-bold font-mono text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.8 }}
      >
        <span className="text-cipher-purple-400">Cipher</span>
        <span className="text-cipher-teal-400">Drive</span>
      </motion.h1>

      {/* Terminal Loading Interface */}
      <motion.div
        className="w-full max-w-2xl bg-dark-card border border-dark-border rounded-2xl p-6 backdrop-blur-sm"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1, duration: 0.8 }}
      >
        {/* Terminal Header */}
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-dark-border/50">
          <div className="flex items-center space-x-3">
            <div className="w-2.5 h-2.5 rounded-full bg-status-error"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-status-warning"></div>
            <div className="w-2.5 h-2.5 rounded-full bg-status-success"></div>
          </div>
          <span className="text-xs font-mono text-dark-text-muted">boot_sequence.sh</span>
        </div>

        {/* Boot Sequence */}
        <div className="space-y-3 font-mono text-sm">
          {bootSequence.map((step, index) => (
            <motion.div
              key={index}
              className="flex items-center space-x-3"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 1.5 + index * 0.8, duration: 0.5 }}
            >
              <motion.div
                className={`w-2 h-2 rounded-full ${
                  index < 3 ? 'bg-status-success' : 
                  index === 3 ? 'bg-status-warning' : 'bg-cipher-teal-400'
                }`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 1.5 + index * 0.8 + 0.3, duration: 0.3 }}
              />
              <span className="text-dark-text-secondary">
                {step}
              </span>
              {index === bootSequence.length - 1 && (
                <motion.span
                  className="inline-block w-2 h-4 bg-cipher-teal-400 ml-2"
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
              )}
            </motion.div>
          ))}
        </div>

        {/* Progress Bar */}
        <div className="mt-6 pt-4 border-t border-dark-border/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono text-dark-text-muted">
              Loading quantum systems...
            </span>
            <span className="text-xs font-mono text-cipher-purple-400">
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 2, duration: 0.5 }}
              >
                100%
              </motion.span>
            </span>
          </div>
          <div className="w-full bg-dark-bg rounded-full h-2 overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-cipher-purple-500 to-cipher-teal-500"
              initial={{ width: "0%" }}
              animate={{ width: "100%" }}
              transition={{ delay: 2, duration: 3, ease: "easeInOut" }}
            />
          </div>
        </div>
      </motion.div>

      {/* Spinning Loader */}
      <motion.div
        className="flex items-center space-x-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2.5, duration: 0.5 }}
      >
        <motion.div
          className="w-8 h-8 border-2 border-cipher-purple-500 border-t-transparent rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
        <span className="font-mono text-dark-text-secondary">
          {message}
        </span>
      </motion.div>

      {/* Matrix Grid Animation */}
      <div className="absolute inset-0 opacity-5 pointer-events-none">
        <div className="grid grid-cols-12 h-full text-cipher-purple-400 text-xs font-mono">
          {Array.from({ length: 144 }, (_, i) => (
            <motion.div
              key={i}
              className="flex items-center justify-center border-r border-b border-current"
              initial={{ opacity: 0 }}
              animate={{ opacity: Math.random() > 0.8 ? 1 : 0.3 }}
              transition={{
                duration: 2,
                delay: i * 0.02,
                repeat: Infinity,
                repeatType: 'reverse',
              }}
            >
              {Math.random() > 0.5 ? '1' : '0'}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-dark-bg flex items-center justify-center z-50">
        <div className="relative w-full h-full flex items-center justify-center p-4">
          <LoadingContent />
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center p-8">
      <LoadingContent />
    </div>
  );
};

export default Loading;