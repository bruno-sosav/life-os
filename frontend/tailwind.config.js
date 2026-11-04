/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ["'JetBrains Mono'", 'ui-monospace', 'monospace']
      },
      colors: {
        // Fondo y superficies, de la más oscura a la más clara
        ink: {
          950: '#07090A', // fondo
          900: '#0A0D0C', // hundido: inputs, barra de navegación
          800: '#0F1312', // tarjetas
          700: '#1A201E', // bordes
          600: '#1F2623', // bordes fuertes, hover
          500: '#5E6662', // texto apagado (solo grande o decorativo)
          400: '#8C948F', // texto secundario
          300: '#C9CFCB',
          100: '#E8ECE9' // texto principal
        },
        up: '#2EBD85', // positivo: hecho, ingreso, acción principal
        down: '#F6465D', // negativo: faltó, gasto, borrar
        warn: '#E0B84A', // parcial, pendiente
        accent: '#7C5CFF' // lo actual o seleccionado: hoy, pestaña activa
      }
    }
  },
  plugins: []
}
