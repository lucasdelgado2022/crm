<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <LucideCalendarHeart class="h-5 w-5" />
        {{ __('Eventos de Marketing') }}
      </div>
    </template>
    <template #right-header>
      <Button variant="solid" iconLeft="plus" :label="__('Nuevo evento')" @click="openNew" />
    </template>
  </LayoutHeader>

  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Métricas agregadas -->
    <div class="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      <div class="rounded-lg border p-4">
        <div class="text-2xl font-semibold text-ink-gray-9">{{ eventos.length }}</div>
        <div class="text-sm text-ink-gray-5">{{ __('Eventos') }}</div>
      </div>
      <div class="rounded-lg border p-4">
        <div class="text-2xl font-semibold text-ink-gray-9">{{ totals.inscriptos }}</div>
        <div class="text-sm text-ink-gray-5">{{ __('Inscriptos') }}</div>
      </div>
      <div class="rounded-lg border p-4">
        <div class="text-2xl font-semibold text-ink-gray-9">{{ totals.asistieron }}</div>
        <div class="text-sm text-ink-gray-5">{{ __('Asistieron') }}</div>
      </div>
      <div class="rounded-lg border border-blue-200 bg-blue-50/40 p-4">
        <div class="text-2xl font-semibold text-blue-700">{{ totals.pctAsist }}%</div>
        <div class="text-sm text-ink-gray-5">{{ __('Asistentes / Inscriptos') }}</div>
      </div>
      <div class="rounded-lg border p-4">
        <div class="text-2xl font-semibold text-ink-gray-9">{{ totals.leads }}</div>
        <div class="text-sm text-ink-gray-5">{{ __('Leads asociados') }}</div>
      </div>
      <div class="rounded-lg border border-green-200 bg-green-50/40 p-4">
        <div class="text-2xl font-semibold text-green-700">{{ totals.pctLeads }}%</div>
        <div class="text-sm text-ink-gray-5">{{ __('Leads / Asistentes') }}</div>
      </div>
    </div>

    <div class="mb-3 flex items-center justify-between gap-2">
      <div class="text-base text-ink-gray-6">{{ __('{0} eventos', [filtered.length]) }}</div>
      <FormControl class="w-64" type="text" :placeholder="__('Buscar evento...')" v-model="search">
        <template #prefix><FeatherIcon name="search" class="h-4 w-4 text-ink-gray-5" /></template>
      </FormControl>
    </div>

    <div v-if="filtered.length" class="overflow-x-auto rounded-lg border">
      <table class="w-full text-sm">
        <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
          <tr>
            <th class="px-4 py-2 text-left font-medium">{{ __('Título') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Tipo') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Estado') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Fecha') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('Inscriptos') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('Asistieron') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('% Asist.') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('Leads') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('% L/A') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('Oport.') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="e in filtered"
            :key="e.name"
            class="cursor-pointer border-b last:border-0 hover:bg-surface-gray-1"
            @click="open(e)"
          >
            <td class="px-4 py-2 font-medium text-ink-gray-8">{{ e.titulo }}</td>
            <td class="px-3 py-2">
              <Badge variant="subtle" :theme="tipoTheme(e.tipo)" size="sm">{{ e.tipo }}</Badge>
            </td>
            <td class="px-3 py-2">
              <Badge variant="subtle" :theme="estadoTheme(e.estado)" size="sm">{{ e.estado }}</Badge>
            </td>
            <td class="px-3 py-2 text-ink-gray-7">{{ e.fecha_inicio || '—' }}</td>
            <td class="px-3 py-2 text-right text-ink-gray-8">{{ metrics[e.name]?.inscriptos || 0 }}</td>
            <td class="px-3 py-2 text-right text-ink-gray-8">{{ metrics[e.name]?.asistieron || 0 }}</td>
            <td class="px-3 py-2 text-right font-medium text-blue-700">{{ pct(metrics[e.name]?.asistieron || 0, metrics[e.name]?.inscriptos || 0) }}%</td>
            <td class="px-3 py-2 text-right text-ink-gray-8">{{ metrics[e.name]?.leads || 0 }}</td>
            <td class="px-3 py-2 text-right font-medium text-green-700">{{ pct(metrics[e.name]?.leads || 0, metrics[e.name]?.asistieron || 0) }}%</td>
            <td class="px-3 py-2 text-right text-ink-gray-8">{{ metrics[e.name]?.opps || 0 }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4">
      <LucideCalendarHeart class="h-10 w-10" />
      <div>{{ __('Sin eventos') }}</div>
    </div>
  </div>

  <!-- Modal nuevo evento -->
  <Dialog v-model="showNew" :options="{ title: __('Nuevo evento'), size: 'lg' }">
    <template #body-content>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <FormControl type="text" :label="__('Título')" v-model="form.titulo" class="sm:col-span-2" />
        <FormControl type="select" :label="__('Tipo')" v-model="form.tipo" :options="TIPOS" />
        <FormControl type="select" :label="__('Modalidad')" v-model="form.modalidad" :options="MODALIDADES" />
        <FormControl type="date" :label="__('Fecha inicio')" v-model="form.fecha_inicio" />
        <FormControl type="date" :label="__('Fecha fin')" v-model="form.fecha_fin" />
        <FormControl type="select" :label="__('Estado')" v-model="form.estado" :options="ESTADOS" />
        <FormControl type="select" :label="__('País')" v-model="form.pais" :options="PAISES" />
        <FormControl type="select" :label="__('Canal')" v-model="form.canal" :options="CANALES" />
        <FormControl type="text" :label="__('Ubicación / Link')" v-model="form.ubicacion" />
        <div>
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Responsable') }}</div>
          <Link doctype="User" :value="form.responsable" @change="(v) => (form.responsable = v)" />
        </div>
        <div class="sm:col-span-2">
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Industrias') }}</div>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="ind in industriaOptions"
              :key="ind"
              type="button"
              class="rounded-full border px-2.5 py-1 text-xs transition"
              :class="form.industrias.includes(ind)
                ? 'border-transparent bg-surface-gray-7 text-ink-white'
                : 'border-outline-gray-2 text-ink-gray-7 hover:border-outline-gray-3'"
              @click="toggleIndustria(ind)"
            >{{ ind }}</button>
          </div>
        </div>
        <FormControl type="textarea" :label="__('Descripción')" v-model="form.descripcion" class="sm:col-span-2" />
      </div>
    </template>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button @click="showNew = false">{{ __('Cancelar') }}</Button>
        <Button variant="solid" :loading="saving" @click="createEvento">{{ __('Crear') }}</Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'
import LucideCalendarHeart from '~icons/lucide/calendar-heart'
import { FeatherIcon, FormControl, Button, Badge, Dialog, call, toast, usePageMeta } from 'frappe-ui'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const TIPOS = ['Curso', 'Webinar', 'Feria', 'Conferencia', 'Otro']
const MODALIDADES = ['Presencial', 'Virtual', 'Híbrido']
const ESTADOS = ['Planificado', 'En curso', 'Finalizado', 'Cancelado']
const PAISES = ['', 'Argentina', 'Chile', 'Perú', 'Colombia', 'México', 'Brasil', 'Uruguay', 'Paraguay', 'Bolivia', 'Ecuador', 'Otro']
const CANALES = ['', 'Email', 'LinkedIn', 'Web / Landing', 'Google Ads', 'Redes sociales', 'Referido', 'Partner', 'WhatsApp', 'Evento presencial', 'Otro']
const INDUSTRIAS_FALLBACK = [
  'Manufactura', 'Automotriz', 'Aeroespacial', 'Energía', 'Oil & Gas', 'Minería',
  'Naval', 'Defensa', 'Construcción', 'Electrónica', 'Consumo masivo', 'Salud / Médico',
  'Educación', 'Agroindustria', 'Otro',
]
const industriaOptions = ref([...INDUSTRIAS_FALLBACK])
async function loadIndustrias() {
  try {
    const r = await call('frappe.client.get_list', {
      doctype: 'CRM Industry',
      fields: ['name'],
      limit_page_length: 0,
    })
    const arr = (Array.isArray(r) ? r : r?.message || []).map((x) => x.name).filter(Boolean)
    if (arr.length) industriaOptions.value = arr
  } catch (e) {
    // se mantiene el fallback
  }
}

const eventos = ref([])
const metrics = ref({})
const search = ref('')

async function load() {
  eventos.value = await call('frappe.client.get_list', {
    doctype: 'CRM Marketing Evento',
    fields: ['name', 'titulo', 'tipo', 'estado', 'modalidad', 'fecha_inicio', 'fecha_fin', 'responsable', 'pais', 'canal', 'industrias'],
    order_by: 'fecha_inicio desc',
    limit_page_length: 0,
  })
  await loadMetrics()
}
async function loadMetrics() {
  // Server Script (frappe.get_all): evita el bloqueo de child doctypes (istable)
  // de frappe.client.get_list en v16 para usuarios que no son System Manager.
  try {
    const r = await call('evento_metrics')
    metrics.value = (r && r.message) || r || {}
  } catch (e) {
    metrics.value = {}
  }
}
// % con protección de división por cero
function pct(a, b) {
  return b ? Math.round((a / b) * 100) : 0
}
load()
loadIndustrias()

const totals = computed(() => {
  const t = { inscriptos: 0, asistieron: 0, leads: 0 }
  for (const k in metrics.value) {
    t.inscriptos += metrics.value[k].inscriptos
    t.asistieron += metrics.value[k].asistieron
    t.leads += metrics.value[k].leads
  }
  t.pctAsist = pct(t.asistieron, t.inscriptos)
  t.pctLeads = pct(t.leads, t.asistieron)
  return t
})

const filtered = computed(() => {
  let arr = eventos.value
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    arr = arr.filter((e) => (e.titulo || '').toLowerCase().includes(q))
  }
  return arr
})

function tipoTheme(t) {
  return { Curso: 'green', Webinar: 'blue', Feria: 'orange', Conferencia: 'purple' }[t] || 'gray'
}
function estadoTheme(e) {
  return { Planificado: 'gray', 'En curso': 'blue', Finalizado: 'green', Cancelado: 'red' }[e] || 'gray'
}

function open(e) {
  router.push({ name: 'EventoDetalle', params: { eventoId: e.name } })
}

// --- Nuevo evento ---
const showNew = ref(false)
const saving = ref(false)
const form = ref({})
function openNew() {
  form.value = {
    titulo: '', tipo: 'Webinar', modalidad: 'Virtual', estado: 'Planificado',
    fecha_inicio: '', fecha_fin: '', ubicacion: '', responsable: '', descripcion: '',
    pais: '', canal: '', industrias: [],
  }
  showNew.value = true
}
function toggleIndustria(ind) {
  const arr = form.value.industrias || (form.value.industrias = [])
  const i = arr.indexOf(ind)
  if (i === -1) arr.push(ind)
  else arr.splice(i, 1)
}
async function createEvento() {
  if (!form.value.titulo?.trim()) {
    toast.error(__('El título es obligatorio'))
    return
  }
  saving.value = true
  try {
    const payload = { ...form.value, industrias: (form.value.industrias || []).join(', ') }
    const doc = await call('frappe.client.insert', {
      doc: { doctype: 'CRM Marketing Evento', ...payload },
    })
    showNew.value = false
    toast.success(__('Evento creado'))
    router.push({ name: 'EventoDetalle', params: { eventoId: doc.name } })
  } catch (e) {
    toast.error((e && e.messages && e.messages[0]) || __('No se pudo crear'))
  } finally {
    saving.value = false
  }
}

usePageMeta(() => ({ title: __('Eventos de Marketing') }))
</script>
