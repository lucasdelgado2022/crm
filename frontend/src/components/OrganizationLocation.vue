<template>
  <div class="flex flex-col gap-2 rounded-lg border border-outline-gray-2 p-3">
    <div class="flex items-center justify-between">
      <div
        class="flex items-center gap-1.5 text-base font-medium text-ink-gray-8"
      >
        <span class="lucide-map-pin size-4" aria-hidden="true" />
        {{ __('Ubicación') }}
      </div>
      <a
        v-if="mapsLink"
        :href="mapsLink"
        target="_blank"
        rel="noopener"
        class="text-sm text-ink-blue-link underline hover:text-ink-blue-3"
      >
        {{ __('Abrir en Google Maps') }}
      </a>
    </div>

    <div class="flex gap-2">
      <FormControl
        class="flex-1"
        type="text"
        :placeholder="__('Pegá el link de Google Maps…')"
        :modelValue="linkInput"
        @update:modelValue="(v) => (linkInput = v)"
        @keydown.enter.prevent="resolveLink"
      />
      <Button
        variant="solid"
        :label="__('Ubicar')"
        :loading="resolving"
        @click="resolveLink"
      />
    </div>

    <div v-if="coords" class="text-sm text-ink-gray-6">
      {{ __('Coordenadas') }}: {{ coords }}
    </div>

    <div
      v-show="coords"
      ref="mapEl"
      class="h-56 w-full overflow-hidden rounded border border-outline-gray-2"
    />
    <div
      v-if="!coords"
      class="flex h-20 items-center justify-center rounded bg-surface-gray-1 text-sm text-ink-gray-4"
    >
      {{ __('Sin ubicación cargada — pegá un link de Google Maps') }}
    </div>
  </div>
</template>

<script setup>
import leafletIconUrl from 'leaflet/dist/images/marker-icon.png?url'
import leafletIconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png?url'
import leafletShadowUrl from 'leaflet/dist/images/marker-shadow.png?url'
import { FormControl, Button, call, toast } from 'frappe-ui'
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  doctype: { type: String, default: 'CRM Organization' },
  docname: { type: String, required: true },
  googleMaps: { type: String, default: '' },
  coordenadas: { type: String, default: '' },
})

const linkInput = ref(props.googleMaps || '')
const coords = ref(props.coordenadas || '')
const resolving = ref(false)

const mapEl = ref(null)
let L = null
let map = null
let marker = null

const latLng = computed(() => {
  const parts = (coords.value || '').split(',').map((s) => parseFloat(s.trim()))
  if (parts.length === 2 && !isNaN(parts[0]) && !isNaN(parts[1])) return parts
  return null
})

const mapsLink = computed(() => {
  if (linkInput.value) return linkInput.value
  if (coords.value) return `https://www.google.com/maps?q=${coords.value}`
  return ''
})

async function resolveLink() {
  const url = (linkInput.value || '').trim()
  if (!url) return
  resolving.value = true
  try {
    const res = await call('crm.api.doc.resolve_maps_coords', { url })
    if (res && res.coordenadas) {
      coords.value = res.coordenadas
      await save()
      await ensureMap()
      updateMarker()
      toast.success(__('Ubicación cargada'))
    } else {
      // guardo el link igual aunque no se hayan podido extraer coords
      await save()
      toast.warning(__('No se pudieron extraer coordenadas de ese link'))
    }
  } catch (e) {
    toast.error(__('No se pudo resolver el link'))
  } finally {
    resolving.value = false
  }
}

async function save() {
  try {
    await call('frappe.client.set_value', {
      doctype: props.doctype,
      name: props.docname,
      fieldname: {
        custom_google_maps: linkInput.value || '',
        custom_coordenadas: coords.value || '',
      },
    })
  } catch (e) {
    toast.error(__('No se pudo guardar la ubicación'))
  }
}

async function ensureMap() {
  if (map) return
  await import('leaflet/dist/leaflet.css')
  const mod = await import('leaflet')
  L = mod.default ?? mod
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconUrl: leafletIconUrl,
    iconRetinaUrl: leafletIconRetinaUrl,
    shadowUrl: leafletShadowUrl,
  })
  await nextTick()
  const center = latLng.value || [-34.6037, -58.3816]
  map = L.map(mapEl.value).setView(center, latLng.value ? 15 : 4)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
    maxZoom: 19,
  }).addTo(map)
  // click para reubicar
  map.on('click', (e) => {
    coords.value = `${e.latlng.lat.toFixed(6)},${e.latlng.lng.toFixed(6)}`
    updateMarker()
    save()
  })
  setTimeout(() => map && map.invalidateSize(), 200)
}

function updateMarker() {
  if (!map || !latLng.value) return
  if (!marker) {
    marker = L.marker(latLng.value, { draggable: true }).addTo(map)
    marker.on('dragend', () => {
      const p = marker.getLatLng()
      coords.value = `${p.lat.toFixed(6)},${p.lng.toFixed(6)}`
      save()
    })
  } else {
    marker.setLatLng(latLng.value)
  }
  map.setView(latLng.value, 15)
}

onMounted(async () => {
  if (latLng.value) {
    await ensureMap()
    updateMarker()
  }
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>
