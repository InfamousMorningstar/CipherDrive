import React from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { 
  CloudArrowUpIcon, 
  ShieldCheckIcon, 
  DevicePhoneMobileIcon,
  CpuChipIcon,
  LockClosedIcon,
  RocketLaunchIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';
import MatrixBackground from './MatrixBackground';
import FeatureCard from './FeatureCard';

const LandingPage = () => {
  const navigate = useNavigate();

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

  const handleInitializeSystem = () => {
    navigate('/login');
  };

  const handleViewDocumentation = () => {
    // For now, open GitHub repo. Could be changed to docs page later
    window.open('https://github.com/InfamousMorningstar/CipherDrive', '_blank');
  };

  return (
    <div className="min-h-screen bg-dark-bg text-dark-text-primary relative overflow-hidden">
      {/* Animated Matrix Background */}
      <MatrixBackground />
      
      {/* Navigation */}
      <motion.nav 
        className="absolute top-0 left-0 right-0 z-20 flex justify-between items-center p-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex items-center space-x-2">
          <ComputerDesktopIcon className="h-8 w-8 text-cipher-teal-400" />
          <span className="font-mono text-xl font-bold">CipherDrive</span>
        </div>
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Link
            to="/login"
            className="px-4 py-2 border border-cipher-purple-400 rounded-lg font-mono text-cipher-purple-400 hover:bg-cipher-purple-400 hover:text-white transition-all duration-300"
          >
            Access Terminal
          </Link>
        </motion.div>
      </motion.nav>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 sm:px-6 lg:px-8">
        
        {/* Hero Section */}
        <motion.div 
          className="text-center max-w-4xl mx-auto mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {/* Glowing Icon */}
          <motion.div 
            className="flex justify-center mb-8"
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
              <div className="relative bg-dark-card border border-cipher-border rounded-2xl p-6 backdrop-blur-sm">
                <ComputerDesktopIcon className="h-20 w-20 text-cipher-teal-400 mx-auto" />
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
              <span className="bg-gradient-to-r from-cipher-teal-400 to-cipher-purple-400 bg-clip-text text-transparent">
                CIPHER
              </span>
              <span className="text-white">DRIVE</span>
            </h1>
            <p className="text-xl sm:text-2xl text-gray-300 font-mono mb-8">
              Next-Generation Secure File System
            </p>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            className="flex flex-col sm:flex-row gap-6 justify-center items-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
          >
            <motion.button
              onClick={handleInitializeSystem}
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
            </motion.button>

            <motion.button
              onClick={handleViewDocumentation}
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
            </motion.button>
          </motion.div>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          className="w-full max-w-6xl mx-auto"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9, duration: 0.8 }}
        >
          <motion.h2 
            className="text-3xl font-bold font-mono text-center mb-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.8 }}
          >
            <span className="text-cipher-teal-400">&gt;</span> System Features
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2 + index * 0.1, duration: 0.6 }}
              >
                <FeatureCard
                  icon={feature.icon}
                  title={feature.title}
                  description={feature.description}
                />
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          className="mt-20 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8, duration: 0.8 }}
        >
          <p className="text-gray-400 font-mono text-sm">
            CipherDrive v1.0.0 | Secure • Private • Fast
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default LandingPage;