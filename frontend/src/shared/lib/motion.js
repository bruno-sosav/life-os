// Animaciones compartidas: todas las pantallas se mueven igual

const EASE = [0.2, 0.8, 0.2, 1]

// Una lista que aparece en cascada: el contenedor lleva `list`, cada hijo `item`
export const list = {
  hidden: {},
  show: { transition: { staggerChildren: 0.04 } }
}

export const item = {
  hidden: { opacity: 0, y: 6 },
  show: { opacity: 1, y: 0, transition: { duration: 0.25, ease: EASE } }
}

// Cambio de contenido en el mismo lugar (otro proyecto, otra pestaña)
export const swap = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.22, ease: EASE } },
  exit: { opacity: 0, y: -4, transition: { duration: 0.12 } }
}
