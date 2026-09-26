<template>
  <LayoutHeader v-if="plan">
    <template #left-header>
      <div class="flex items-center gap-2">
        <Button variant="ghost" iconLeft="arrow-left" :label="__('Viajes')" @click="volver" />
        <span class="text-lg font-semibold text-ink-gray-8">{{ plan.titulo }}</span>
        <Badge variant="subtle" :theme="estadoTheme(plan.estado)" size="sm">{{ plan.estado }}</Badge>
        <span v-if="plan.responsable" class="text-sm text-ink-gray-5">· {{ plan.responsable }}</span>
      </div>
    </template>
    <template #right-header>
      <Button iconLeft="edit" :label="__('Editar')" @click="openEdit" />
    </template>
  </LayoutHeader>

  <div v-if="plan" class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <div class="mb-4 flex gap-1 border-b">
      <button
        v-for="t in ['Agenda', 'Costos']"
        :key="t"
        class="border-b-2 px-4 py-2 text-sm font-medium"
        :class="tab === t ? 'border-ink-gray-9 text-ink-gray-9' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
        @click="tab = t"
      >
        {{ __(t) }}
      </button>
    </div>

    <!-- AGENDA -->
    <div v-show="tab === 'Agenda'" class="flex flex-col gap-4">
      <!-- Controles: ubicación + agregar visita -->
      <div class="flex flex-wrap items-end gap-2 rounded-lg border p-3">
        <div>
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Ubicación (país)') }}</div>
          <select v-model="paisFiltro" class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm focus:outline-none">
            <option value="">{{ __('Todos') }}</option>
            <option v-for="p in PAISES" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
        <div class="w-56">
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Empresa') }}</div>
          <Link doctype="CRM Organization" :value="nv.organization" @change="(v) => (nv.organization = v)" />
        </div>
        <div>
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Día') }}</div>
          <select v-model="nv.dia" class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm focus:outline-none">
            <option v-for="d in DIAS" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
        <div>
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Hora') }}</div>
          <input type="time" v-model="nv.hora" class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm focus:outline-none" />
        </div>
        <Button variant="solid" iconLeft="plus" :label="__('Agregar')" @click="addVisita" />
      </div>

      <!-- Favoritos -->
      <div class="rounded-lg border p-3">
        <div class="mb-2 flex items-center justify-between gap-2">
          <div class="flex items-center gap-2 text-sm font-semibold text-ink-gray-8">
            <FeatherIcon name="star" class="h-4 w-4 text-amber-500" />
            {{ __('Ubicaciones favoritas') }}
            <span v-if="paisFiltro" class="text-xs font-normal text-ink-gray-5">· {{ paisFiltro }}</span>
          </div>
          <Button variant="subtle" iconLeft="plus" :label="__('Nuevo favorito')" @click="nuevoFavorito" />
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="f in favoritosFiltrados"
            :key="f.name"
            class="flex items-center gap-1.5 rounded-full border border-amber-300 bg-amber-50 px-2.5 py-1 text-sm text-ink-gray-8 hover:bg-amber-100"
            @click="addVisitaOrg(f.name)"
          >
            <FeatherIcon name="star" class="h-3 w-3 text-amber-500" />
            {{ f.organization_name || f.name }}
          </button>
          <span v-if="!favoritosFiltrados.length" class="py-1 text-sm text-ink-gray-4">{{ __('Sin favoritos') }}</span>
        </div>
      </div>

      <!-- Empresas sugeridas por ubicación -->
      <div v-if="paisFiltro" class="rounded-lg border p-3">
        <div class="mb-2 flex items-center justify-between gap-2">
          <div class="text-sm font-semibold text-ink-gray-8">{{ __('Empresas sugeridas en {0}', [paisFiltro]) }}</div>
          <FormControl class="w-56" type="text" :placeholder="__('Buscar empresa...')" v-model="sugeridaSearch" />
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="o in sugeridas"
            :key="o.name"
            class="rounded-full border border-outline-gray-2 px-2.5 py-1 text-sm text-ink-gray-8 hover:bg-surface-gray-1"
            @click="addVisitaOrg(o.name)"
          >
            {{ o.organization_name || o.name }}
          </button>
          <span v-if="!sugeridas.length" class="py-1 text-sm text-ink-gray-4">{{ __('Sin resultados') }}</span>
        </div>
      </div>

      <!-- Calendario semanal -->
      <div class="grid grid-cols-1 gap-px overflow-hidden rounded-lg border bg-surface-gray-2 sm:grid-cols-7">
        <div v-for="d in DIAS" :key="d" class="flex min-h-40 flex-col bg-surface-white">
          <div class="border-b bg-surface-gray-1 px-2 py-1.5 text-center text-xs font-semibold text-ink-gray-7">{{ d }}</div>
          <div class="flex flex-1 flex-col gap-1 p-1.5">
            <div v-for="(v, i) in visitasByDay(d)" :key="i" class="rounded bg-surface-blue-1 px-2 py-1 text-xs">
              <div class="flex items-start justify-between gap-1">
                <span class="font-medium text-ink-gray-8">{{ orgLabel(v.organization) }}</span>
                <button @click="removeVisita(v)"><FeatherIcon name="x" class="h-3 w-3 text-ink-gray-5 hover:text-ink-red-6" /></button>
              </div>
              <div v-if="v.hora" class="text-ink-gray-6">{{ v.hora }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Mapa por día -->
      <div class="rounded-lg border">
        <div class="flex flex-wrap items-center justify-between gap-2 border-b px-4 py-2">
          <div class="flex items-center gap-2 text-sm font-semibold text-ink-gray-8">
            <FeatherIcon name="map-pin" class="h-4 w-4" />
            {{ __('Itinerario en mapa') }}
          </div>
          <div class="flex items-center gap-2">
            <select v-model="mapDia" class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm focus:outline-none">
              <option value="">{{ __('Todos los días') }}</option>
              <option v-for="d in DIAS" :key="d" :value="d">{{ d }}</option>
            </select>
            <a v-if="mapLocs.length > 1" :href="rutaUrl" target="_blank" class="text-xs text-ink-blue-link">{{ __('Abrir ruta') }}</a>
          </div>
        </div>
        <iframe v-if="mapUrl" :src="mapUrl" class="h-96 w-full rounded-b-lg border-0" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        <div v-else class="py-10 text-center text-sm text-ink-gray-4">{{ __('Agregá empresas para ver el mapa') }}</div>
      </div>
    </div>

    <!-- COSTOS -->
    <div v-show="tab === 'Costos'" class="rounded-lg border">
      <div class="flex items-center justify-between gap-2 border-b px-4 py-2">
        <div class="text-sm font-semibold text-ink-gray-8">{{ __('Costos del viaje') }}</div>
        <Button variant="subtle" iconLeft="plus" :label="__('Agregar costo')" @click="addCosto" />
      </div>
      <table class="w-full text-sm">
        <thead class="text-xs text-ink-gray-5">
          <tr>
            <th class="px-3 py-1.5 text-left font-medium">{{ __('Concepto') }}</th>
            <th class="w-40 px-3 py-1.5 text-left font-medium">{{ __('Categoría') }}</th>
            <th class="w-40 px-3 py-1.5 text-right font-medium">{{ __('Monto USD') }}</th>
            <th class="w-8"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(c, i) in plan.costos" :key="i" class="border-t">
            <td class="px-3 py-1"><input class="w-full rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 focus:outline-none" :value="c.concepto" @change="(e) => setCosto(i, 'concepto', e.target.value)" /></td>
            <td class="px-3 py-1">
              <select class="w-full rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 focus:outline-none" :value="c.categoria" @change="(e) => setCosto(i, 'categoria', e.target.value)">
                <option v-for="cat in CATEGORIAS" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </td>
            <td class="px-3 py-1"><input type="number" class="w-full rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 text-right focus:outline-none" :value="c.monto" @change="(e) => setCosto(i, 'monto', Number(e.target.value) || 0)" /></td>
            <td class="px-3 py-1 text-right"><button @click="removeCosto(i)"><FeatherIcon name="x" class="h-4 w-4 text-ink-gray-5 hover:text-ink-red-6" /></button></td>
          </tr>
          <tr v-if="!(plan.costos && plan.costos.length)"><td colspan="4" class="px-3 py-4 text-center text-sm text-ink-gray-4">{{ __('Sin costos') }}</td></tr>
        </tbody>
        <tfoot v-if="plan.costos && plan.costos.length">
          <tr class="border-t bg-surface-gray-1">
            <td class="px-3 py-2 font-semibold" colspan="2">{{ __('Total') }}</td>
            <td class="px-3 py-2 text-right font-semibold text-ink-gray-9">{{ money(costoTotal) }}</td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>

  <Dialog v-model="showEdit" :options="{ title: __('Editar plan'), size: 'lg' }">
    <template #body-content>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <FormControl type="text" :label="__('Título')" v-model="form.titulo" class="sm:col-span-2" />
        <FormControl type="select" :label="__('Estado')" v-model="form.estado" :options="ESTADOS" />
        <FormControl type="date" :label="__('Semana desde')" v-model="form.fecha_desde" />
        <div><div class="mb-1 text-xs text-ink-gray-5">{{ __('Responsable') }}</div><Link doctype="User" :value="form.responsable" @change="(v) => (form.responsable = v)" /></div>
        <FormControl type="textarea" :label="__('Descripción')" v-model="form.descripcion" class="sm:col-span-2" />
      </div>
    </template>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button @click="showEdit = false">{{ __('Cancelar') }}</Button>
        <Button variant="solid" :loading="saving" @click="saveEdit">{{ __('Guardar') }}</Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'
import { FeatherIcon, FormControl, Button, Badge, Dialog, call, toast, usePageMeta } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ planId: { type: String, required: true } })
const router = useRouter()

const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
const CATEGORIAS = ['Transporte', 'Alojamiento', 'Comidas', 'Viáticos', 'Otros']
const ESTADOS = ['Planificado', 'En curso', 'Realizado', 'Cancelado']
const PAISES = ['Argentina', 'Chile', 'Colombia', 'Perú', 'Ecuador', 'Uruguay', 'Paraguay', 'Bolivia', 'Venezuela', 'España', 'Brasil', 'República Dominicana']

const plan = ref(null)
const saving = ref(false)
const tab = ref('Agenda')
const orgInfo = ref({})
const nv = ref({ organization: '', dia: 'Lunes', hora: '' })
const paisFiltro = ref('')
const mapDia = ref('')
const favoritos = ref([])
const sugeridas = ref([])
const sugeridaSearch = ref('')

async function load() {
  plan.value = await call('frappe.client.get', { doctype: 'CRM Plan Viaje', name: props.planId })
  await loadOrgInfo()
  loadFavoritos()
}
async function loadOrgInfo() {
  const names = [...new Set((plan.value.visitas || []).map((v) => v.organization).filter(Boolean))]
  if (!names.length) {
    orgInfo.value = {}
    return
  }
  try {
    const rows = await call('frappe.client.get_list', {
      doctype: 'CRM Organization',
      filters: { name: ['in', names] },
      fields: ['name', 'organization_name', 'territory'],
      limit_page_length: 0,
    })
    const m = {}
    for (const r of rows) m[r.name] = r
    orgInfo.value = m
  } catch (e) {
    orgInfo.value = {}
  }
}
async function loadFavoritos() {
  try {
    favoritos.value = await call('frappe.client.get_list', {
      doctype: 'CRM Organization',
      filters: { custom_es_favorito: 1 },
      fields: ['name', 'organization_name', 'territory'],
      limit_page_length: 0,
      order_by: 'organization_name asc',
    })
  } catch (e) {
    favoritos.value = []
  }
}
async function loadSugeridas() {
  if (!paisFiltro.value) {
    sugeridas.value = []
    return
  }
  const filters = { territory: paisFiltro.value }
  if (sugeridaSearch.value.trim())
    filters.organization_name = ['like', '%' + sugeridaSearch.value.trim() + '%']
  try {
    sugeridas.value = await call('frappe.client.get_list', {
      doctype: 'CRM Organization',
      filters,
      fields: ['name', 'organization_name', 'territory'],
      limit_page_length: 20,
      order_by: 'organization_name asc',
    })
  } catch (e) {
    sugeridas.value = []
  }
}
load()
watch([paisFiltro, sugeridaSearch], loadSugeridas)

const favoritosFiltrados = computed(() => {
  if (!paisFiltro.value) return favoritos.value
  return favoritos.value.filter((f) => (f.territory || '') === paisFiltro.value)
})

async function saveDoc() {
  saving.value = true
  try {
    plan.value = await call('frappe.client.save', { doc: plan.value })
    await loadOrgInfo()
  } catch (e) {
    toast.error((e && e.messages && e.messages[0]) || __('No se pudo guardar'))
  } finally {
    saving.value = false
  }
}

function orgLabel(name) {
  return orgInfo.value[name]?.organization_name || name
}
function orgLoc(name) {
  const o = orgInfo.value[name]
  if (!o) return name
  return [o.organization_name || o.name, o.territory].filter(Boolean).join(', ')
}
function visitasByDay(d) {
  return (plan.value?.visitas || []).filter((v) => v.dia === d)
}

async function addVisita() {
  if (!nv.value.organization) {
    toast.error(__('Elegí una empresa'))
    return
  }
  await addVisitaOrg(nv.value.organization)
  nv.value = { organization: '', dia: nv.value.dia, hora: '' }
}
async function addVisitaOrg(orgName) {
  plan.value.visitas = plan.value.visitas || []
  if (plan.value.visitas.some((v) => v.organization === orgName && v.dia === nv.value.dia)) {
    toast.info(__('Ya está en ese día'))
    return
  }
  plan.value.visitas.push({ organization: orgName, dia: nv.value.dia, hora: nv.value.hora })
  await saveDoc()
}
async function removeVisita(v) {
  const idx = plan.value.visitas.indexOf(v)
  if (idx >= 0) plan.value.visitas.splice(idx, 1)
  await saveDoc()
}

async function nuevoFavorito() {
  const nombre = window.prompt(__('Nombre de la ubicación favorita (ej. Hotel X)'))
  if (!nombre || !nombre.trim()) return
  const pais = paisFiltro.value || window.prompt(__('País'), 'Chile') || ''
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'CRM Organization',
        organization_name: nombre.trim(),
        territory: pais,
        custom_es_favorito: 1,
      },
    })
    toast.success(__('Favorito agregado'))
    loadFavoritos()
  } catch (e) {
    toast.error((e && e.messages && e.messages[0]) || __('No se pudo crear'))
  }
}

// --- Mapa por día ---
const mapVisitas = computed(() => {
  const vs = plan.value?.visitas || []
  return mapDia.value ? vs.filter((v) => v.dia === mapDia.value) : vs
})
const mapLocs = computed(() =>
  [...new Set(mapVisitas.value.map((v) => v.organization).filter(Boolean))].map(orgLoc).filter(Boolean),
)
const mapUrl = computed(() => {
  const locs = mapLocs.value
  if (!locs.length) return ''
  if (locs.length === 1)
    return 'https://maps.google.com/maps?q=' + encodeURIComponent(locs[0]) + '&output=embed&z=6'
  const saddr = encodeURIComponent(locs[0])
  const rest = locs.slice(1).map(encodeURIComponent).join('+to:')
  return 'https://maps.google.com/maps?saddr=' + saddr + '&daddr=' + rest + '&output=embed'
})
const rutaUrl = computed(
  () => 'https://www.google.com/maps/dir/' + mapLocs.value.map(encodeURIComponent).join('/'),
)

// --- Costos ---
const costoTotal = computed(() =>
  (plan.value?.costos || []).reduce((a, c) => a + (Number(c.monto) || 0), 0),
)
async function addCosto() {
  plan.value.costos = plan.value.costos || []
  plan.value.costos.push({ concepto: '', categoria: 'Transporte', monto: 0 })
  await saveDoc()
}
async function setCosto(i, field, val) {
  plan.value.costos[i][field] = val
  await saveDoc()
}
async function removeCosto(i) {
  plan.value.costos.splice(i, 1)
  await saveDoc()
}

// --- Editar ---
const showEdit = ref(false)
const form = ref({})
function openEdit() {
  const p = plan.value
  form.value = { titulo: p.titulo, estado: p.estado, fecha_desde: p.fecha_desde, responsable: p.responsable, descripcion: p.descripcion }
  showEdit.value = true
}
async function saveEdit() {
  Object.assign(plan.value, form.value)
  showEdit.value = false
  await saveDoc()
}

function estadoTheme(e) {
  return { Planificado: 'gray', 'En curso': 'blue', Realizado: 'green', Cancelado: 'red' }[e] || 'gray'
}
function money(v) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v || 0)
}
function volver() {
  router.push({ name: 'PlanificacionViajes' })
}

usePageMeta(() => ({ title: plan.value?.titulo || __('Plan de Viaje') }))
</script>
