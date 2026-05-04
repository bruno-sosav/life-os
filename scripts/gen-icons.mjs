// Genera PNGs placeholder para PWA usando un canvas SVG renderizado vía
// minúscula utilidad: simplemente escribimos un PNG base64 fijo.
// Para íconos reales después, reemplazá pwa-192x192.png y pwa-512x512.png.
import { writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const pub = resolve(__dirname, '..', 'public')

// PNG mínimo 1x1 lila (placeholder). Se reemplaza fácilmente con un PNG real.
// (browsers respetan el manifest aún con íconos chicos; lo importante es que existan.)
const png1x1 = Buffer.from(
  '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c63607060f8cf000000050001a55a4f5d0000000049454e44ae426082',
  'hex'
)

writeFileSync(resolve(pub, 'pwa-192x192.png'), png1x1)
writeFileSync(resolve(pub, 'pwa-512x512.png'), png1x1)
console.log('Wrote PWA placeholder PNGs to', pub)
