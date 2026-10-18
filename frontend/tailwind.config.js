/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', "'SF Pro Text'", "'Helvetica Neue'", 'system-ui', 'sans-serif'],
        display: ['-apple-system', 'BlinkMacSystemFont', "'SF Pro Display'", "'Helvetica Neue'", 'system-ui', 'sans-serif']
      },
      colors: {
        ios: {
          blue:   '#0A84FF',
          green:  '#30D158',
          purple: '#BF5AF2',
          orange: '#FF9F0A',
          red:    '#FF453A',
          yellow: '#FFD60A',
          teal:   '#5AC8FA',
          indigo: '#5E5CE6'
        },
        surface: {
          0:  '#0a0a0f',
          1:  '#111116',
          2:  '#18181f',
          3:  '#1e1e27',
          4:  '#26263200',
          glass: 'rgba(255,255,255,0.06)',
          'glass-hover': 'rgba(255,255,255,0.09)',
          'glass-active': 'rgba(255,255,255,0.04)'
        },
        label: {
          primary:   'rgba(255,255,255,0.95)',
          secondary: 'rgba(255,255,255,0.60)',
          tertiary:  'rgba(255,255,255,0.35)',
          quarternary: 'rgba(255,255,255,0.18)'
        }
      },
      borderRadius: {
        ios: '16px',
        'ios-lg': '20px',
        'ios-xl': '24px'
      },
      boxShadow: {
        glass: '0 2px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.08)',
        'glass-sm': '0 1px 8px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.06)',
        ios: '0 4px 30px rgba(0,0,0,0.5)'
      },
      backdropBlur: {
        ios: '20px'
      },
      transitionTimingFunction: {
        ios: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'ios-ease': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
      },
      animation: {
        'check-in': 'checkIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
        'fade-up': 'fadeUp 0.25s ease-out forwards'
      },
      keyframes: {
        checkIn: {
          '0%':   { transform: 'scale(0) rotate(-45deg)', opacity: 0 },
          '100%': { transform: 'scale(1) rotate(0deg)', opacity: 1 }
        },
        fadeUp: {
          '0%':   { transform: 'translateY(6px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 }
        }
      }
    }
  },
  plugins: []
}
