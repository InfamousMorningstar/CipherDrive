import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  KeyIcon, 
  UserIcon, 
  ShieldCheckIcon,
  ComputerDesktopIcon 
} from '@heroicons/react/24/outline';
import Button from '../ui/Button';
import Input from '../ui/Input';
import Card from '../ui/Card';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    remember: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      if (formData.email && formData.password) {
        console.log('Login successful');
      } else {
        setError('Invalid credentials');
      }
    }, 2000);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="grid grid-cols-12 h-full text-cipher-purple-400 text-xs font-mono">
          {Array.from({ length: 144 }, (_, i) => (
            <motion.div
              key={i}
              className="flex items-center justify-center border-r border-b border-current"
              initial={{ opacity: 0 }}
              animate={{ opacity: Math.random() > 0.7 ? 1 : 0.3 }}
              transition={{
                duration: 2,
                delay: i * 0.01,
                repeat: Infinity,
                repeatType: 'reverse',
              }}
            >
              {Math.random() > 0.5 ? '1' : '0'}
            </motion.div>
          ))}
        </div>
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo/Brand */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="flex justify-center mb-4">
            <div className="relative">
              <motion.div
                className="absolute inset-0 rounded-2xl bg-cipher-purple-glow blur-xl opacity-30"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [0.3, 0.6, 0.3]
                }}
                transition={{ 
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
              <div className="relative bg-dark-card border border-dark-border rounded-2xl p-4">
                <ComputerDesktopIcon className="h-12 w-12 text-cipher-teal-400 mx-auto" />
              </div>
            </div>
          </div>
          
          <h1 className="text-4xl font-bold font-mono text-dark-text-primary mb-2">
            <span className="text-cipher-purple-400">Cipher</span>
            <span className="text-cipher-teal-400">Drive</span>
          </h1>
          
          <motion.p
            className="text-dark-text-secondary font-mono text-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <span className="text-cipher-teal-400">&gt;</span> Secure file system access
            <motion.span
              className="inline-block w-2 h-4 bg-cipher-teal-400 ml-1"
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
          </motion.p>
        </motion.div>

        {/* Login Form */}
        <Card terminal={true} title="user_login.sh">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Terminal Welcome Message */}
            <motion.div
              className="bg-dark-bg rounded-lg p-3 font-mono text-sm border border-dark-border/30"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <div className="text-cipher-teal-400">
                <span className="text-dark-text-muted">$ </span>
                ./authenticate --user
              </div>
              <div className="text-dark-text-secondary mt-1 pl-2">
                Initializing secure authentication...
              </div>
              <div className="text-status-success mt-1 pl-2">
                ✓ Encryption protocols loaded
              </div>
            </motion.div>

            {/* Error Display */}
            {error && (
              <motion.div
                className="bg-status-error/10 border border-status-error/50 rounded-lg p-3 font-mono text-sm"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <div className="text-status-error flex items-center">
                  <span className="mr-2">!</span>
                  Authentication failed: {error}
                </div>
              </motion.div>
            )}

            {/* Email Field */}
            <Input
              type="email"
              name="email"
              label="Email Address"
              placeholder="user@cipherdrive.com"
              value={formData.email}
              onChange={handleChange}
              terminal={true}
              required
              disabled={loading}
            />

            {/* Password Field */}
            <Input
              type="password"
              name="password"
              label="Password"
              placeholder="••••••••••••"
              value={formData.password}
              onChange={handleChange}
              terminal={true}
              required
              disabled={loading}
            />

            {/* Remember Me */}
            <motion.div
              className="flex items-center justify-between"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  name="remember"
                  checked={formData.remember}
                  onChange={handleChange}
                  className="w-4 h-4 text-cipher-purple-500 bg-dark-card border-dark-border rounded focus:ring-cipher-purple-500 focus:ring-2"
                />
                <span className="text-sm font-mono text-dark-text-secondary">
                  Remember session
                </span>
              </label>
              
              <Link
                to="/reset-password"
                className="text-sm font-mono text-cipher-teal-400 hover:text-cipher-teal-300 transition-colors"
              >
                Reset password?
              </Link>
            </motion.div>

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              terminal={true}
              loading={loading}
              disabled={loading}
            >
              {loading ? 'Authenticating...' : 'Access System'}
            </Button>

            {/* Alternative Actions */}
            <motion.div
              className="space-y-4 pt-4 border-t border-dark-border/30"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
            >
              <div className="text-center">
                <span className="text-sm font-mono text-dark-text-muted">
                  No account registered?{' '}
                </span>
                <Link
                  to="/signup"
                  className="text-sm font-mono text-cipher-purple-400 hover:text-cipher-purple-300 transition-colors"
                >
                  Create new user
                </Link>
              </div>

              {/* Security Info */}
              <div className="bg-dark-bg rounded-lg p-3 font-mono text-xs">
                <div className="flex items-center text-cipher-teal-400 mb-2">
                  <ShieldCheckIcon className="h-4 w-4 mr-2" />
                  Security Status
                </div>
                <div className="space-y-1 text-dark-text-muted pl-6">
                  <div>• End-to-end encryption: <span className="text-status-success">ACTIVE</span></div>
                  <div>• Zero-knowledge auth: <span className="text-status-success">ENABLED</span></div>
                  <div>• Session timeout: <span className="text-status-warning">24h</span></div>
                </div>
              </div>
            </motion.div>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default Login;