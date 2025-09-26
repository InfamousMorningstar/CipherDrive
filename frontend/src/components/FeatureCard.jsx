import { motion } from 'framer-motion';

const FeatureCard = ({ icon, title, description, delay = 0 }) => {
  return (
    <motion.div
      className="group relative bg-dark-card border border-dark-border rounded-2xl p-6 backdrop-blur-sm hover:border-cipher-purple-400/50 transition-all duration-300"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.6 }}
      whileHover={{ y: -5 }}
    >
      {/* Terminal window header */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-dark-border/50">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-status-error"></div>
          <div className="w-2 h-2 rounded-full bg-status-warning"></div>
          <div className="w-2 h-2 rounded-full bg-status-success"></div>
        </div>
        <span className="text-xs font-mono text-dark-text-muted">feature.exe</span>
      </div>

      {/* Feature content */}
      <div className="space-y-4">
        {/* Icon with glow effect */}
        <div className="flex justify-center">
          <motion.div
            className="relative"
            whileHover={{ scale: 1.1 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <motion.div
              className="absolute inset-0 rounded-full bg-cipher-teal-glow blur-lg opacity-0 group-hover:opacity-30"
              initial={false}
              whileHover={{ opacity: 0.4 }}
              transition={{ duration: 0.3 }}
            />
            <div className="relative p-3 bg-dark-bg rounded-full border border-dark-border">
              {icon}
            </div>
          </motion.div>
        </div>

        {/* Title with terminal prompt */}
        <div className="text-center">
          <h3 className="font-mono font-semibold text-lg text-dark-text-primary mb-2">
            <span className="text-cipher-teal-400">&gt;</span> {title}
          </h3>
          <p className="text-dark-text-secondary text-sm font-mono leading-relaxed">
            {description}
          </p>
        </div>

        {/* Bottom status bar */}
        <div className="pt-3 border-t border-dark-border/30">
          <div className="flex items-center justify-between text-xs font-mono text-dark-text-muted">
            <span>Status: Active</span>
            <motion.div
              className="flex space-x-1"
              initial={false}
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <div className="w-1 h-1 bg-cipher-teal-400 rounded-full"></div>
              <div className="w-1 h-1 bg-cipher-teal-400 rounded-full"></div>
              <div className="w-1 h-1 bg-cipher-teal-400 rounded-full"></div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Hover glow effect */}
      <motion.div
        className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cipher-purple-400/5 to-cipher-teal-400/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        initial={false}
      />
    </motion.div>
  );
};

export default FeatureCard;