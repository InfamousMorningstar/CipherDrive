import { motion } from 'framer-motion';
import { 
  CloudArrowUpIcon, 
  ShieldCheckIcon, 
  DevicePhoneMobileIcon,
  CpuChipIcon,
  LockClosedIcon,
  RocketLaunchIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';
import MatrixBackground from './components/MatrixBackground';
import FeatureCard from './components/FeatureCard';

function App() {
  const features = [
    {
      icon: <CloudArrowUpIcon className="h-8 w-8 text-cipher-teal-400" />,
      title: "Quantum Upload",
      description: "Lightning-fast file transfers with quantum-encrypted protocols and real-time progress tracking."
    },
    {
      icon: <ShieldCheckIcon className="h-8 w-8 text-cipher-purple-400" />,
      title: "Zero-Trust Security",
      description: "Military-grade encryption with zero-knowledge architecture and blockchain verification."
    },
    {
      icon: <DevicePhoneMobileIcon className="h-8 w-8 text-cipher-teal-400" />,
      title: "Neural Interface",
      description: "AI-powered responsive design that adapts to any device with predictive user interface."
    },
    {
      icon: <CpuChipIcon className="h-8 w-8 text-cipher-purple-400" />,
      title: "AI Core",
      description: "Advanced machine learning for intelligent file organization and content analysis."
    },
    {
      icon: <LockClosedIcon className="h-8 w-8 text-cipher-teal-400" />,
      title: "Privacy Matrix",
      description: "Your data remains invisible with quantum encryption and distributed storage architecture."
    },
    {
      icon: <RocketLaunchIcon className="h-8 w-8 text-cipher-purple-400" />,
      title: "Hyperspeed",
      description: "Optimized performance with edge computing, neural networks, and quantum acceleration."
    }
  ];

  return (
    <div className="min-h-screen bg-dark-bg text-dark-text-primary relative overflow-hidden">
      {/* Animated Matrix Background */}
      <MatrixBackground />
      
      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Hero Section */}
        <section className="flex-1 flex items-center justify-center py-20">
          <div className="relative z-10 text-center px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
            <motion.div
              className="space-y-8"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
            >
              {/* Neon Glow Icon */}
              <motion.div 
                className="flex justify-center"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="relative">
                  <motion.div
                    className="absolute inset-0 rounded-2xl bg-cipher-purple-glow blur-xl opacity-50"
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
                  <div className="relative bg-dark-card border border-dark-border rounded-2xl p-6 backdrop-blur-sm">
                    <ComputerDesktopIcon className="h-20 w-20 text-cipher-teal-400 mx-auto animate-glow-pulse" />
                  </div>
                </div>
              </motion.div>

              {/* Title */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.8 }}
              >
                <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold font-mono mb-4">
                  <span className="bg-gradient-to-r from-cipher-purple-400 to-cipher-teal-400 bg-clip-text text-transparent">
                    Cipher
                  </span>
                  <span className="text-white ml-4">Drive</span>
                </h1>
                
                <motion.div
                  className="text-lg sm:text-xl lg:text-2xl text-gray-300 font-mono"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6, duration: 0.8 }}
                >
                  <span className="text-cipher-teal-400">&gt;</span> Futuristic file sharing platform
                  <motion.span
                    className="inline-block w-3 h-6 bg-cipher-teal-400 ml-1"
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
                transition={{ delay: 0.8, duration: 0.8 }}
              >
                <motion.button
                  className="group relative px-8 py-4 bg-dark-card border border-cipher-purple-400 rounded-xl font-mono text-white hover:bg-cipher-purple-400/10 transition-all duration-300 min-w-[200px]"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="relative z-10 flex items-center justify-center">
                    <span className="text-cipher-purple-400 mr-2">&gt;</span>
                    Initialize System
                  </span>
                  <motion.div
                    className="absolute inset-0 rounded-xl bg-cipher-purple-400 opacity-0 group-hover:opacity-10"
                    initial={false}
                    whileHover={{ opacity: 0.2 }}
                  />
                  <motion.div
                    className="absolute inset-0 rounded-xl"
                    initial={false}
                    whileHover={{ 
                      boxShadow: "0 0 30px rgba(168, 85, 247, 0.3)" 
                    }}
                  />
                </motion.button>

                <motion.button
                  className="group relative px-8 py-4 bg-dark-card border border-cipher-teal-400 rounded-xl font-mono text-white hover:bg-cipher-teal-400/10 transition-all duration-300 min-w-[200px]"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="relative z-10 flex items-center justify-center">
                    <span className="text-cipher-teal-400 mr-2">&gt;</span>
                    View Documentation
                  </span>
                  <motion.div
                    className="absolute inset-0 rounded-xl bg-cipher-teal-400 opacity-0 group-hover:opacity-10"
                    initial={false}
                    whileHover={{ opacity: 0.2 }}
                  />
                  <motion.div
                    className="absolute inset-0 rounded-xl"
                    initial={false}
                    whileHover={{ 
                      boxShadow: "0 0 30px rgba(45, 212, 191, 0.3)" 
                    }}
                  />
                </motion.button>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            {/* Section Header */}
            <motion.div
              className="text-center mb-16"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
            >
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold font-mono mb-4">
                <span className="text-cipher-teal-400">&gt;</span> Core_Systems
                <motion.span
                  className="inline-block w-3 h-8 bg-cipher-teal-400 ml-2"
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
              </h2>
              <p className="text-dark-text-secondary font-mono text-lg max-w-2xl mx-auto">
                Advanced quantum-encrypted infrastructure with AI-powered capabilities
              </p>
            </motion.div>

            {/* Features Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <FeatureCard
                  key={index}
                  icon={feature.icon}
                  title={feature.title}
                  description={feature.description}
                  delay={0.2 * index}
                />
              ))}
            </div>
          </div>
        </section>

        {/* System Status Section */}
        <section className="relative z-10 py-16 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto">
            <motion.div
              className="bg-dark-card border border-dark-border rounded-2xl p-8 backdrop-blur-sm"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.8 }}
            >
              {/* Terminal Header */}
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-dark-border">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 rounded-full bg-status-error"></div>
                  <div className="w-3 h-3 rounded-full bg-status-warning"></div>
                  <div className="w-3 h-3 rounded-full bg-status-success"></div>
                </div>
                <span className="text-sm font-mono text-dark-text-muted">system_status.sh</span>
              </div>

              {/* Terminal Content */}
              <div className="font-mono space-y-3">
                <div className="flex items-center">
                  <span className="text-cipher-teal-400 mr-2">$</span>
                  <span className="text-white">./check-cipherdrive-status.sh --verbose</span>
                </div>
                
                <motion.div
                  className="pl-4 space-y-2 text-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.8, duration: 0.5 }}
                >
                  <div className="text-status-success">
                    ✓ Quantum Encryption Core: OPERATIONAL
                  </div>
                  <div className="text-status-success">
                    ✓ Neural Interface: ACTIVE (localhost:3000)
                  </div>
                  <div className="text-status-success">
                    ✓ AI Processing Matrix: INITIALIZED
                  </div>
                  <div className="text-status-success">
                    ✓ Security Protocols: MAXIMUM
                  </div>
                  <div className="text-cipher-purple-400">
                    → CipherDrive v1.0.0 ready for deployment
                  </div>
                </motion.div>

                <motion.div
                  className="mt-6 p-4 bg-dark-bg rounded-xl border border-dark-border/50"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1, duration: 0.5 }}
                >
                  <div className="text-cipher-teal-400 text-sm mb-2">
                    <span className="text-dark-text-muted">Next deployment phase:</span>
                  </div>
                  <div className="text-dark-text-secondary text-sm space-y-1 pl-2">
                    <div>• Deploy quantum backend infrastructure</div>
                    <div>• Initialize zero-trust authentication system</div>
                    <div>• Activate neural file processing capabilities</div>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Footer */}
        <footer className="relative z-10 py-8 px-4 sm:px-6 lg:px-8 border-t border-dark-border/30">
          <div className="max-w-7xl mx-auto">
            <div className="text-center">
              <p className="text-dark-text-muted font-mono text-sm">
                Powered by <span className="text-cipher-purple-400">React</span> • 
                <span className="text-cipher-teal-400"> Quantum TailwindCSS</span> • 
                <span className="text-cipher-purple-400"> Neural Motion</span>
              </p>
              <motion.div
                className="mt-2 text-xs font-mono text-dark-text-muted"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.5, duration: 0.5 }}
              >
                &copy; 2024 CipherDrive - Quantum Secure File System
              </motion.div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;