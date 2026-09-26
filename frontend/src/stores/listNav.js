import { reactive } from 'vue'

// Guarda el orden de nombres de cada lista para navegar prev/next desde el detalle.
const state = reactive({ lists: {} })

export function setListNav(doctype, names) {
  if (Array.isArray(names)) state.lists[doctype] = names.filter(Boolean)
}

export function listNavStore() {
  return {
    prevOf(doctype, name) {
      const l = state.lists[doctype] || []
      const i = l.indexOf(name)
      return i > 0 ? l[i - 1] : null
    },
    nextOf(doctype, name) {
      const l = state.lists[doctype] || []
      const i = l.indexOf(name)
      return i >= 0 && i < l.length - 1 ? l[i + 1] : null
    },
  }
}
