import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ComputerDesktopIcon, HomeIcon } from '@heroicons/react/24/outline';

const NotFound = () => {
  const asciiArt = `
   _____ _____  _____    _____ _____  _____   _____ _____  _____  
  |  |  |  |  ||  |  |  |   | |     ||_   _| |   __|     ||  |  | 
  |     |     ||     |  | | | |  |  |  | |   |   __|  |  ||  |  | 
  |__|__|_____|__|___|  |_|___|_____|  |_|   |__|  |_____||_____| 
  `;

  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4">
      {/* Matrix Background Effect */}
      <div className="absolute inset-0 opacity-5">
        <div className="grid grid-cols-8 h-full text-cipher-purple-400 text-xs font-mono">
          {Array.from({ length: 64 }, (_, i) => (
            <motion.div
              key={i}
              className="flex items-center justify-center border-r border-b border-current"
              initial={{ opacity: 0 }}
              animate={{ opacity: Math.random() > 0.8 ? 1 : 0.2 }}
              transition={{
                duration: 3,
                delay: i * 0.05,
                repeat: Infinity,
                repeatType: 'reverse',
              }}
            >
              {Math.random() > 0.5 ? 'ERROR' : '404'}
            </motion.div>
          ))}
        </div>
      </div>

      <div className="relative z-10 text-center max-w-2xl mx-auto">
        {/* Terminal Window */}
        <motion.div
          className="bg-dark-card border border-dark-border rounded-2xl p-8 backdrop-blur-sm"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {/* Terminal Header */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-dark-border">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 rounded-full bg-status-error"></div>
              <div className="w-3 h-3 rounded-full bg-status-warning"></div>
              <div className="w-3 h-3 rounded-full bg-status-success"></div>
            </div>
            <span className="text-sm font-mono text-dark-text-muted">error_404.sh</span>
          </div>

          {/* Error Content */}
          <div className="space-y-6">
            {/* ASCII Art */}
            <motion.div
              className="font-mono text-xs text-cipher-purple-400 whitespace-pre-line overflow-hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 1 }}
            >
              {asciiArt.split('').map((char, index) => (
                <motion.span
                  key={index}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 + index * 0.01 }}
                >
                  {char}
                </motion.span>
              ))}
            </motion.div>

            {/* Terminal Commands */}
            <motion.div
              className="bg-dark-bg rounded-xl p-4 font-mono text-sm text-left"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 0.8 }}
            >
              <div className="space-y-2">
                <div className="text-cipher-teal-400">
                  <span className="text-dark-text-muted">$ </span>
                  cd /cipherdrive/pages/
                </div>
                <div className="text-status-error pl-2">
                  ERROR: File not found in quantum filesystem
                </div>
                <div className="text-cipher-teal-400">
                  <span className="text-dark-text-muted">$ </span>
                  ls -la | grep "requested-page"
                </div>
                <div className="text-status-error pl-2">
                  404: No such file or directory exists in this dimension
                </div>
                <div className="text-cipher-teal-400">
                  <span className="text-dark-text-muted">$ </span>
                  ./recovery --return-home
                  <motion.span
                    className="inline-block w-2 h-4 bg-cipher-teal-400 ml-1"
                    animate={{ opacity: [1, 0, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  />
                </div>
              </div>
            </motion.div>

            {/* Error Message */}
            <motion.div
              className="space-y-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.5, duration: 0.8 }}
            >
              <h1 className="text-4xl font-bold font-mono text-dark-text-primary">
                <span className="text-cipher-purple-400">404</span> File Not Found
              </h1>
              <p className="text-dark-text-secondary font-mono">
                The requested quantum file path does not exist in our secure filesystem.
                <br />
                Initializing recovery protocols...
              </p>
            </motion.div>

            {/* Action Buttons */}
            <motion.div
              className="flex flex-col sm:flex-row gap-4 justify-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 2, duration: 0.8 }}
            >
              <Link to="/">
                <motion.button
                  className="group relative px-6 py-3 bg-cipher-purple-600 hover:bg-cipher-purple-700 text-white border border-cipher-purple-500 rounded-xl font-mono transition-all duration-300"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="relative z-10 flex items-center">
                    <HomeIcon className="h-5 w-5 mr-2" />
                    <span className="text-cipher-purple-200 mr-2">&gt;</span>
                    Return to Base
                  </span>
                  <motion.div
                    className="absolute inset-0 rounded-xl"
                    initial={false}
                    whileHover={{ 
                      boxShadow: "0 0 30px rgba(168, 85, 247, 0.3)" 
                    }}
                  />
                </motion.button>
              </Link>

              <motion.button
                className="group relative px-6 py-3 bg-dark-card hover:bg-dark-hover text-dark-text-primary border border-dark-border hover:border-cipher-teal-500 rounded-xl font-mono transition-all duration-300"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => window.history.back()}
              >
                <span className="relative z-10 flex items-center">
                  <span className="text-cipher-teal-400 mr-2">&gt;</span>
                  Go Back
                </span>
              </motion.button>
            </motion.div>

            {/* System Status */}
            <motion.div
              className="mt-8 pt-6 border-t border-dark-border/30 text-xs font-mono"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 2.5, duration: 0.8 }}
            >
              <div className="flex items-center justify-between text-dark-text-muted">
                <span>System Status: Operational</span>
                <div className="flex items-center space-x-2">
                  <ComputerDesktopIcon className="h-4 w-4 text-cipher-teal-400" />
                  <span>CipherDrive v1.0.0</span>
                </div>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default NotFound;