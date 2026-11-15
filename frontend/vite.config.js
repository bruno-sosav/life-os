import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// En Vercel, sin VITE_API_URL el build apuntaría a localhost y la app no podría entrar
if (process.env.VERCEL && !process.env.VITE_API_URL) {
  throw new Error('Falta VITE_API_URL en las variables de entorno de Vercel')
}

export default defineConfig({
  base: '/',
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: false,  // usamos public/manifest.json manual para control total
      includeAssets: ['icon.svg', 'icons/*.png'],
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,woff2}'],
        // El SW sirve index.html para navegaciones SPA, pero NO para assets estáticos
        navigateFallback: 'index.html',
        navigateFallbackDenylist: [
          /^\/manifest\.json$/,
          /^\/icons\//,
          /^\/assets\//,
          /^\/sw\.js$/,
          /^\/workbox-/,
          /^\/registerSW\.js$/
        ],
        runtimeCaching: [
          {
            // GETs a la API: red primero, cache solo si no hay conexión. Sin timeout: con red
            // lenta mostraría la copia vieja justo después de guardar algo
            urlPattern: ({ url }) => url.pathname.startsWith('/api/'),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 }
            }
          },
          {
            urlPattern: ({ url }) => url.origin.includes('fonts.googleapis.com') || url.origin.includes('fonts.gstatic.com'),
            handler: 'CacheFirst',
            options: {
              cacheName: 'fonts-cache',
              expiration: { maxEntries: 30, maxAgeSeconds: 60 * 60 * 24 * 365 }
            }
          }
        ]
      }
    })
  ]
})
