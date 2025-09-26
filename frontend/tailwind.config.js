/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', 'monospace'],
        'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        // Primary brand colors
        cipher: {
          purple: {
            50: '#f3f1ff',
            100: '#ebe5ff',
            200: '#d9ceff',
            300: '#bea6ff',
            400: '#9f75ff',
            500: '#843dff',
            600: '#7916ff',
            700: '#6b04fd',
            800: '#5a03d4',
            900: '#4a02ad',
            950: '#2c0175',
            glow: '#a855f7',
          },
          teal: {
            50: '#f0fdfa',
            100: '#ccfbf1',
            200: '#99f6e4',
            300: '#5eead4',
            400: '#2dd4bf',
            500: '#14b8a6',
            600: '#0d9488',
            700: '#0f766e',
            800: '#115e59',
            900: '#134e4a',
            950: '#042f2e',
            glow: '#2dd4bf',
          },
        },
        // Dark theme colors
        dark: {
          bg: '#0a0a0f',
          surface: '#12121a',
          card: '#1a1a26',
          border: '#2a2a3a',
          hover: '#252530',
          text: {
            primary: '#ffffff',
            secondary: '#a1a1aa',
            muted: '#71717a',
          }
        },
        // Status colors
        status: {
          success: '#10b981',
          error: '#ef4444',
          warning: '#f59e0b',
          info: '#3b82f6',
        }
      },
      animation: {
        // Existing animations
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-gentle': 'bounceGentle 2s infinite',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite alternate',
        'matrix-rain': 'matrixRain 20s linear infinite',
        'glitch': 'glitch 0.3s ease-in-out',
        // New animations
        'terminal-typing': 'terminalTyping 2s steps(20) infinite',
        'neon-glow': 'neonGlow 2s ease-in-out infinite alternate',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        // Existing keyframes
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(-5%)' },
          '50%': { transform: 'translateY(0)' },
        },
        glowPulse: {
          '0%': { 
            boxShadow: '0 0 20px rgba(168, 85, 247, 0.3), 0 0 40px rgba(168, 85, 247, 0.1)',
          },
          '100%': { 
            boxShadow: '0 0 30px rgba(168, 85, 247, 0.6), 0 0 60px rgba(168, 85, 247, 0.2)',
          },
        },
        matrixRain: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        glitch: {
          '0%, 100%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' },
          '80%': { transform: 'translate(2px, -2px)' },
        },
        // New keyframes
        terminalTyping: {
          '0%, 50%': { opacity: '1' },
          '51%, 100%': { opacity: '0' },
        },
        neonGlow: {
          '0%': {
            textShadow: '0 0 10px rgba(168, 85, 247, 0.5), 0 0 20px rgba(168, 85, 247, 0.3), 0 0 30px rgba(168, 85, 247, 0.1)',
          },
          '100%': {
            textShadow: '0 0 20px rgba(168, 85, 247, 0.8), 0 0 30px rgba(168, 85, 247, 0.5), 0 0 40px rgba(168, 85, 247, 0.3)',
          },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
      },
      backdropBlur: {
        'xs': '2px',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
      },
      boxShadow: {
        'glow-purple': '0 0 20px rgba(168, 85, 247, 0.3)',
        'glow-teal': '0 0 20px rgba(45, 212, 191, 0.3)',
        'inner-glow': 'inset 0 0 20px rgba(255, 255, 255, 0.1)',
      },
    },
  },
  plugins: [],
}