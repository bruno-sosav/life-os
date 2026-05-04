/**
 * Genera íconos PNG reales para la PWA usando solo módulos built-in de Node.js.
 * Gradiente diagonal #7F77DD → #D85A30 con esquinas redondeadas.
 * Uso: node scripts/gen-icons.mjs
 */
import { deflateSync } from 'zlib'
import { writeFileSync, mkdirSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const iconsDir = resolve(__dirname, '..', 'public', 'icons')
mkdirSync(iconsDir, { recursive: true })

// ── CRC32 ────────────────────────────────────────────────────
const CRC_TABLE = new Uint32Array(256)
for (let i = 0; i < 256; i++) {
  let c = i
  for (let j = 0; j < 8; j++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1
  CRC_TABLE[i] = c
}
function crc32(buf) {
  let crc = 0xffffffff
  for (const b of buf) crc = CRC_TABLE[(crc ^ b) & 0xff] ^ (crc >>> 8)
  return (crc ^ 0xffffffff) >>> 0
}

// ── PNG chunk ────────────────────────────────────────────────
function pngChunk(type, data) {
  const typeBuf = Buffer.from(type, 'ascii')
  const lenBuf = Buffer.alloc(4)
  lenBuf.writeUInt32BE(data.length)
  const crcBuf = Buffer.alloc(4)
  crcBuf.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])))
  return Buffer.concat([lenBuf, typeBuf, data, crcBuf])
}

// ── Generar PNG ──────────────────────────────────────────────
function makePNG(size) {
  const r1 = 0x7F, g1 = 0x77, b1 = 0xDD  // #7F77DD (violeta)
  const r2 = 0xD8, g2 = 0x5A, b2 = 0x30  // #D85A30 (naranja)
  const radius = Math.round(size * 0.22)  // esquinas redondeadas ~22%

  // IHDR: RGBA (color type 6)
  const ihdr = Buffer.alloc(13)
  ihdr.writeUInt32BE(size, 0)
  ihdr.writeUInt32BE(size, 4)
  ihdr[8] = 8   // bit depth
  ihdr[9] = 6   // color type: RGBA
  // compression=0, filter=0, interlace=0 (defaults)

  // Pixel data con filtro None (0x00) al inicio de cada fila
  const rows = []
  for (let y = 0; y < size; y++) {
    const row = Buffer.alloc(1 + size * 4)
    row[0] = 0 // filter: None
    for (let x = 0; x < size; x++) {
      // Máscara rounded rect con anti-aliasing en las esquinas
      let alpha = 255
      const dx = Math.min(x, size - 1 - x)
      const dy = Math.min(y, size - 1 - y)
      if (dx < radius && dy < radius) {
        const cx = radius - dx - 1
        const cy = radius - dy - 1
        const dist = Math.sqrt(cx * cx + cy * cy)
        if (dist > radius - 0.5) alpha = 0
        else if (dist > radius - 1.5) alpha = Math.round(255 * (radius - 0.5 - dist))
      }

      // Gradiente diagonal
      const t = (x + y) / (size * 2 - 2)
      const idx = 1 + x * 4
      row[idx + 0] = Math.round(r1 + t * (r2 - r1))
      row[idx + 1] = Math.round(g1 + t * (g2 - g1))
      row[idx + 2] = Math.round(b1 + t * (b2 - b1))
      row[idx + 3] = alpha
    }
    rows.push(row)
  }

  const idat = deflateSync(Buffer.concat(rows), { level: 6 })

  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), // PNG signature
    pngChunk('IHDR', ihdr),
    pngChunk('IDAT', idat),
    pngChunk('IEND', Buffer.alloc(0))
  ])
}

// ── Escribir archivos ────────────────────────────────────────
const sizes = [192, 512]
for (const size of sizes) {
  const png = makePNG(size)
  const path = resolve(iconsDir, `icon-${size}x${size}.png`)
  writeFileSync(path, png)
  console.log(`✓ icon-${size}x${size}.png (${png.length} bytes)`)
}
console.log('Icons written to public/icons/')
