import { motion } from 'framer-motion';
import { FolderIcon, ServerIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';

const Hero = () => {
  return (
    <motion.div 
      className="relative z-10 text-center px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
    >
      {/* Main Hero Content */}
      <motion.div
        className="space-y-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.8 }}
      >
        {/* Neon Glow Icon */}
        <motion.div 
          className="flex justify-center"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <div className="relative">
            <motion.div
              className="absolute inset-0 rounded-2xl bg-cyber-purple-glow blur-xl opacity-50"
              animate={{ 
                scale: [1, 1.1, 1],
                opacity: [0.5, 0.8, 0.5]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
            <div className="relative bg-cyber-dark-card border border-cyber-border rounded-2xl p-6 backdrop-blur-sm">
              <FolderIcon className="h-20 w-20 text-cyber-teal-400 mx-auto animate-glow-pulse" />
            </div>
          </div>
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.8 }}
        >
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold font-mono mb-4">
            <span className="bg-gradient-to-r from-cyber-purple-400 to-cyber-teal-400 bg-clip-text text-transparent">
              Dropbox
            </span>
            <span className="text-white ml-4">Lite</span>
          </h1>
          
          <motion.div
            className="text-lg sm:text-xl lg:text-2xl text-gray-300 font-mono"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.8 }}
          >
            <span className="text-cyber-teal-400">&gt;</span> Modern file sharing platform
            <motion.span
              className="inline-block w-3 h-6 bg-cyber-teal-400 ml-1"
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
          </motion.div>
        </motion.div>

        {/* Terminal-style Buttons */}
        <motion.div
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.8 }}
        >
          <motion.button
            className="group relative px-8 py-4 bg-cyber-dark-card border border-cyber-purple-400 rounded-lg font-mono text-white hover:bg-cyber-purple-400/10 transition-all duration-300 min-w-[200px]"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onHoverStart={() => {}}
          >
            <span className="relative z-10 flex items-center justify-center">
              <span className="text-cyber-purple-400 mr-2">&gt;</span>
              Get Started
            </span>
            <motion.div
              className="absolute inset-0 rounded-lg bg-cyber-purple-400 opacity-0 group-hover:opacity-10"
              initial={false}
              whileHover={{ opacity: 0.2 }}
            />
            <motion.div
              className="absolute inset-0 rounded-lg"
              initial={false}
              whileHover={{ 
                boxShadow: "0 0 30px rgba(168, 85, 247, 0.3)" 
              }}
            />
          </motion.button>

          <motion.button
            className="group relative px-8 py-4 bg-cyber-dark-card border border-cyber-teal-400 rounded-lg font-mono text-white hover:bg-cyber-teal-400/10 transition-all duration-300 min-w-[200px]"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="relative z-10 flex items-center justify-center">
              <span className="text-cyber-teal-400 mr-2">&gt;</span>
              Learn More
            </span>
            <motion.div
              className="absolute inset-0 rounded-lg bg-cyber-teal-400 opacity-0 group-hover:opacity-10"
              initial={false}
              whileHover={{ opacity: 0.2 }}
            />
            <motion.div
              className="absolute inset-0 rounded-lg"
              initial={false}
              whileHover={{ 
                boxShadow: "0 0 30px rgba(45, 212, 191, 0.3)" 
              }}
            />
          </motion.button>
        </motion.div>

        {/* Status Terminal */}
        <motion.div
          className="mx-auto max-w-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.8 }}
        >
          <div className="bg-cyber-dark-card border border-cyber-border rounded-lg p-4 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
              </div>
              <span className="text-xs font-mono text-gray-400">system.log</span>
            </div>
            <div className="font-mono text-sm space-y-1">
              <div className="text-green-400">
                <span className="text-gray-500">$ </span>
                status --check
              </div>
              <div className="text-gray-300 pl-2">
                <ShieldCheckIcon className="inline w-4 h-4 mr-2 text-cyber-teal-400" />
                Server: <span className="text-green-400">ONLINE</span>
              </div>
              <div className="text-gray-300 pl-2">
                <ServerIcon className="inline w-4 h-4 mr-2 text-cyber-purple-400" />
                Frontend: <span className="text-green-400">ACTIVE</span>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default Hero;