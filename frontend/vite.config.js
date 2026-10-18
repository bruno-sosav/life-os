import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

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
            // GETs a la API: red primero, cache como respaldo sin conexión
            urlPattern: ({ url }) => url.pathname.startsWith('/api/'),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 5,
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
