<template>
  <div class="flex h-full min-h-0 flex-col gap-3 -m-4 p-4 sm:-m-5 sm:p-5">
    <!-- Cabecera: ventana de años + acciones -->
    <div class="flex shrink-0 flex-wrap items-center gap-2">
      <div class="flex items-center gap-1">
        <Button variant="ghost" icon="chevron-left" :tooltip="__('Año anterior')" @click="startYear--" />
        <div class="min-w-[9rem] text-center text-lg font-semibold text-ink-gray-9">
          {{ startYear }} – {{ startYear + SPAN - 1 }}
        </div>
        <Button variant="ghost" icon="chevron-right" :tooltip="__('Año siguiente')" @click="startYear++" />
        <Button variant="ghost" size="sm" :label="__('Hoy')" @click="startYear = thisYear" />
      </div>
      <div class="flex rounded-lg border border-outline-gray-2 p-0.5">
        <button
          v-for="v in VIEWS"
          :key="v.key"
          type="button"
          class="rounded-md px-2.5 py-1 text-xs font-medium transition"
          :class="viewMode === v.key ? 'bg-surface-gray-3 text-ink-gray-9' : 'text-ink-gray-6 hover:text-ink-gray-9'"
          :title="__('Vista del eje de tiempo')"
          @click="viewMode = v.key"
        >{{ v.label }}</button>
      </div>
      <div class="flex rounded-lg border border-outline-gray-2 p-0.5">
        <button
          v-for="m in AMT_METRICS"
          :key="m.key"
          type="button"
          class="rounded-md px-2.5 py-1 text-xs font-medium transition"
          :class="amountMetric === m.key ? 'bg-surface-gray-3 text-ink-gray-9' : 'text-ink-gray-6 hover:text-ink-gray-9'"
          :title="__('Tipo de valor de oportunidad')"
          @click="amountMetric = m.key"
        >{{ m.label }}</button>
      </div>
      <Button variant="subtle" :label="hideMoney ? __('Mostrar $') : __('Ocultar $')" @click="hideMoney = !hideMoney" />
      <Button variant="subtle" :label="__('+ Stream')" @click="startAddStream" />
      <Button variant="subtle" :label="__('+ Ítem')" :disabled="!streams.length" @click="startAddItemGlobal" />
      <Button variant="solid" :label="__('Guardar')" :loading="saving" @click="persist(true)" />
      <span v-if="dirty" class="text-xs text-ink-gray-4">{{ __('Cambios sin guardar') }}</span>
    </div>

    <!-- Nuevo stream (inline) -->
    <div v-if="addingStream" class="flex shrink-0 items-center gap-2 rounded-lg border bg-surface-gray-1 p-2">
      <input
        ref="newStreamRef"
        v-model="newStreamName"
        type="text"
        class="flex-1 rounded border-none bg-surface-white px-2 py-1 text-sm text-ink-gray-8 focus:ring-1 focus:ring-outline-gray-3"
        :placeholder="__('Nombre del stream (ej. Implementación 3DEXPERIENCE)')"
        @keydown.enter="confirmAddStream"
        @keydown.esc="addingStream = false"
      />
      <Button variant="solid" :label="__('Agregar')" @click="confirmAddStream" />
      <Button variant="ghost" :label="__('Cancelar')" @click="addingStream = false" />
    </div>

    <!-- Form de ítem (agregar / editar) -->
    <div v-if="showItemForm" class="flex shrink-0 flex-wrap items-end gap-2 rounded-lg border bg-surface-gray-1 p-2">
      <label class="flex flex-col gap-1 text-xs text-ink-gray-5">{{ __('Stream') }}
        <select v-model="formStreamId" :disabled="formMode === 'edit'" class="rounded border bg-surface-white px-2 py-1 text-sm text-ink-gray-8 disabled:opacity-60">
          <option v-for="s in streams" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </label>
      <label class="flex flex-col gap-1 text-xs text-ink-gray-5">{{ __('Etiqueta') }}
        <input v-model="itemDraft.label" type="text" class="rounded border bg-surface-white px-2 py-1 text-sm text-ink-gray-8" :placeholder="__('Etiqueta')" />
      </label>
      <label class="flex flex-col gap-1 text-xs text-ink-gray-5">{{ __('Tipo') }}
        <select v-model="itemDraft.type" class="rounded border bg-surface-white px-2 py-1 text-sm text-ink-gray-8">
          <option value="milestone">{{ __('Hito (fecha)') }}</option>
          <option value="bar">{{ __('Barra (rango)') }}</option>
        </select>
      </label>
      <label v-if="itemDraft.type === 'milestone'" class="flex flex-col gap-1 text-xs text-ink-gray-5">{{ __('Fecha') }}
        <input v-model="itemDraft.date" type="date" class="rounded border bg-surface-white px-2 py-1 text-sm text-ink-gray-8" />
      </label>
      <template v-else>
        <label class="flex flex-col gap-1 text-xs text-ink-gray-5">{{ __('Desde') }}
          <div class="flex items-center gap-1">
            <select v-model.number="itemDraft.startY" class="w-16 rounded border bg-surface-white px-1 py-1 text-sm"><option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option></select>
            <select v-model.number="itemDraft.startM" class="rounded border bg-surface-white px-1 py-1 text-sm"><option v-for="(m, i) in MONTHS" :key="i" :value="i">{{ m }}</option></select>
          </div>
        </label>
        <label class="flex flex-col gap-1 text-xs text-ink-gray-5">{{ __('Hasta') }}
          <div class="flex items-center gap-1">
            <select v-model.number="itemDraft.endY" class="w-16 rounded border bg-surface-white px-1 py-1 text-sm"><option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option></select>
            <select v-model.number="itemDraft.endM" class="rounded border bg-surface-white px-1 py-1 text-sm"><option v-for="(m, i) in MONTHS" :key="i" :value="i">{{ m }}</option></select>
          </div>
        </label>
      </template>
      <label class="flex flex-col gap-1 text-xs text-ink-gray-5">{{ __('Color') }}
        <input type="color" v-model="itemDraft.color" class="h-8 w-12 cursor-pointer rounded border bg-surface-white p-0.5" />
      </label>
      <label class="flex flex-col gap-1 text-xs text-ink-gray-5">{{ __('Oportunidad') }}
        <div class="w-56"><Link doctype="CRM Deal" :value="itemDraft.deal" :filters="{ organization: props.organizationId }" @change="(v) => (itemDraft.deal = v)" /></div>
      </label>
      <Button variant="solid" :label="formMode === 'edit' ? __('Guardar ítem') : __('Agregar')" @click="confirmItem" />
      <Button variant="ghost" :label="__('Cancelar')" @click="showItemForm = false" />
    </div>

    <!-- Timeline (scroll horizontal para 3 años) -->
    <div class="min-h-0 flex-1 overflow-auto rounded-lg border">
      <div class="w-full min-w-[1100px]">
        <!-- Banda de años -->
        <div class="flex sticky top-0 z-20 border-b bg-surface-gray-3">
          <div class="w-44 shrink-0 border-r px-3 py-1.5 text-xs font-semibold uppercase text-ink-gray-6">
            {{ __('Streams') }}
          </div>
          <div class="flex flex-1">
            <div
              v-for="(y, yi) in windowYears"
              :key="y"
              class="flex-1 py-1.5 text-center text-sm font-semibold text-ink-gray-8"
              :class="yi < windowYears.length - 1 ? 'border-r-2 border-outline-gray-3' : ''"
            >
              {{ y }}
            </div>
          </div>
        </div>
        <!-- Sub-banda (meses / trimestres) -->
        <div v-if="viewMode !== 'anio'" class="flex sticky top-[33px] z-10 border-b bg-surface-gray-2">
          <div class="w-44 shrink-0 border-r bg-surface-gray-2" />
          <div class="flex flex-1">
            <div
              v-for="(c, i) in cells"
              :key="i"
              class="flex-1 py-1 text-center text-[10px] font-medium text-ink-gray-5"
              :class="c.yearStart ? 'border-l-2 border-outline-gray-3' : 'border-l border-outline-gray-1'"
            >
              {{ c.label }}
            </div>
          </div>
        </div>

        <!-- Sin streams -->
        <div v-if="!streams.length" class="px-4 py-12 text-center text-sm text-ink-gray-4">
          {{ __('Sin streams todavía. Agregá el primero con "+ Stream".') }}
        </div>

        <!-- Lanes -->
        <div
          v-for="stream in streams"
          :key="stream.id"
          class="flex border-b last:border-b-0 hover:bg-surface-gray-1"
        >
          <!-- Etiqueta / acciones -->
          <div class="w-44 shrink-0 border-r p-2">
            <div class="flex items-center gap-1.5">
              <input type="color" v-model="stream.color" class="h-4 w-4 shrink-0 cursor-pointer rounded border-0 bg-transparent p-0" :title="__('Color del stream')" @change="() => { markDirty(); persist() }" />
              <input
                v-model="stream.name"
                type="text"
                class="min-w-0 flex-1 rounded border-none bg-transparent px-1 py-0.5 text-sm font-medium text-ink-gray-8 hover:bg-surface-gray-2 focus:bg-surface-white focus:ring-1 focus:ring-outline-gray-3"
                @change="markDirty"
              />
            </div>
            <div class="mt-1 flex items-center justify-between gap-1 pl-5">
              <span v-if="streamTotal(stream) && !hideMoney" class="text-xs font-semibold tabular-nums text-ink-gray-7" :title="__('Total del stream')">{{ money(streamTotal(stream)) }}</span>
              <Button variant="ghost" size="sm" icon="trash-2" :tooltip="__('Eliminar stream')" @click="removeStream(stream)" />
            </div>
          </div>

          <!-- Track -->
          <div class="relative min-h-[3.5rem] flex-1">
            <!-- grilla de meses -->
            <div class="absolute inset-0 flex">
              <div
                v-for="(c, i) in cells"
                :key="i"
                class="flex-1"
                :class="c.yearStart ? 'border-l-2 border-outline-gray-2' : 'border-l border-outline-gray-1'"
              />
            </div>
            <!-- línea de hoy -->
            <div
              v-if="todayLeft !== null"
              class="absolute top-0 bottom-0 z-10 w-0.5 bg-red-400"
              :style="{ left: todayLeft + '%' }"
            />
            <!-- items: uno por línea -->
            <div class="relative z-20 py-1">
              <div v-for="it in stream.items" :key="it.id" class="relative flex h-7 items-center">
                <div
                  v-if="it.type === 'bar' && barGeom(it)"
                  class="group absolute flex items-center gap-1 overflow-hidden rounded-md px-2 text-xs font-medium text-white shadow-sm ring-1 ring-black/5"
                  :style="{ left: barGeom(it).left + '%', width: barGeom(it).width + '%', height: '20px', backgroundColor: it.color || stream.color }"
                  :title="it.label + (itemAmount(it) != null ? '  ' + money(itemAmount(it)) : '')"
                >
                  <span class="truncate">{{ it.label }}<template v-if="itemAmount(it) != null && !hideMoney"> · {{ money(itemAmount(it)) }}</template></span>
                  <span v-if="itemStatus(it)" class="shrink-0 rounded px-1 text-[9px] font-semibold" :style="statusStyle(itemStatus(it))">{{ itemStatus(it) }}</span>
                  <span class="ml-auto hidden shrink-0 cursor-pointer leading-none group-hover:inline" :title="__('Editar')" @click.stop="startEditItem(stream, it)">✎</span>
                  <span class="hidden shrink-0 cursor-pointer leading-none group-hover:inline" :title="__('Eliminar')" @click.stop="removeItem(stream, it)">✕</span>
                </div>
                <div
                  v-else-if="it.type === 'milestone' && msLeft(it) !== null"
                  class="group absolute flex items-center gap-1"
                  :style="{ left: msLeft(it) + '%', transform: 'translateX(-7px)' }"
                  :title="(it.label || '') + '  ' + (it.date || '')"
                >
                  <span class="h-3.5 w-3.5 shrink-0 rotate-45 rounded-[3px] border border-white shadow" :style="{ backgroundColor: it.color || stream.color }" />
                  <span class="max-w-[200px] truncate text-[10px] leading-tight text-ink-gray-7">{{ it.label }}<template v-if="itemAmount(it) != null && !hideMoney"> · {{ money(itemAmount(it)) }}</template></span>
                  <span v-if="itemStatus(it)" class="shrink-0 rounded px-1 text-[9px] font-semibold" :style="statusStyle(itemStatus(it))">{{ itemStatus(it) }}</span>
                  <span class="hidden shrink-0 cursor-pointer text-[11px] leading-none text-ink-gray-5 group-hover:inline" :title="__('Editar')" @click.stop="startEditItem(stream, it)">✎</span>
                  <span class="hidden shrink-0 cursor-pointer text-[11px] leading-none text-ink-gray-5 group-hover:inline" :title="__('Eliminar')" @click.stop="removeItem(stream, it)">✕</span>
                </div>
              </div>
              <div v-if="!stream.items.length" class="h-7" />
            </div>
          </div>
        </div>
        <button
          type="button"
          class="flex w-full items-center gap-2 border-t px-4 py-2.5 text-sm text-ink-gray-6 hover:bg-surface-gray-1"
          @click="startAddStream"
        >
          <span class="text-base leading-none">＋</span>{{ __('Agregar stream') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, call, toast } from 'frappe-ui'
import { ref, computed, watch, nextTick } from 'vue'
import Link from '@/components/Controls/Link.vue'
import { statusesStore } from '@/stores/statuses'

const props = defineProps({
  organizationId: { type: String, required: true },
})

const MONTHS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
const MI = ['E', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
const PALETTE = ['#2563eb', '#16a34a', '#9333ea', '#d97706', '#db2777', '#0d9488', '#ea580c', '#4f46e5', '#0891b2', '#65a30d']
const VIEWS = [{ key: 'mes', label: 'Mes' }, { key: 'trimestre', label: 'Trimestre' }, { key: 'anio', label: 'Año' }]
const viewMode = ref('mes')
// Años visibles y meses totales según la vista
const SPAN = computed(() => (viewMode.value === 'anio' ? 8 : viewMode.value === 'trimestre' ? 5 : 3))
const TOTAL = computed(() => SPAN.value * 12)

const thisYear = new Date().getFullYear()
const startYear = ref(thisYear)
const streams = ref([])
const saving = ref(false)
const dirty = ref(false)

const addingStream = ref(false)
const newStreamName = ref('')
const newStreamRef = ref(null)

const showItemForm = ref(false)
const formMode = ref('add')
const formStreamId = ref(null)
const editId = ref(null)
const itemDraft = ref({ label: '', type: 'milestone', date: '', startY: thisYear, startM: 0, endY: thisYear, endM: 2 })

const windowYears = computed(() => { const a = []; for (let i = 0; i < SPAN.value; i++) a.push(startYear.value + i); return a })
const yearOptions = (() => { const a = []; for (let y = thisYear - 8; y <= thisYear + 15; y++) a.push(y); return a })()
const money = n => '$' + Math.round(n || 0).toLocaleString('en-US')
const AMT_METRICS = [{ key: 'value', label: 'Valor', f: 'deal_value' }, { key: 'ds', label: 'DS', f: 'custom_ds_revenue' }, { key: 'sol', label: 'Solaer', f: 'custom_solaer_revenue' }]
const amountMetric = ref('value')
const hideMoney = ref(false)
const dealMap = ref({})
const { getDealStatus } = statusesStore()
function itemAmount(it) {
  if (!it || !it.deal) return null
  const d = dealMap.value[it.deal]; if (!d) return null
  const f = (AMT_METRICS.find(m => m.key === amountMetric.value) || AMT_METRICS[0]).f
  const v = d[f]; return v == null ? null : v
}
function itemStatus(it) {
  if (!it || !it.deal) return null
  const d = dealMap.value[it.deal]; if (!d) return null
  let t
  try { t = getDealStatus(d.status)?.type } catch (e) { t = null }
  return t === 'Won' ? 'Won' : t === 'Lost' ? 'Lost' : 'In work'
}
function statusStyle(st) {
  if (st === 'Won') return { backgroundColor: '#16a34a', color: '#fff' }
  if (st === 'Lost') return { backgroundColor: '#dc2626', color: '#fff' }
  return { backgroundColor: '#2563eb', color: '#fff' }
}
function streamTotal(stream) {
  return (stream.items || []).reduce((a, it) => a + (itemAmount(it) || 0), 0)
}
async function loadDeals() {
  const names = []
  for (const s of streams.value) for (const it of (s.items || [])) if (it.deal) names.push(it.deal)
  const uniq = [...new Set(names)]
  if (!uniq.length) { dealMap.value = {}; return }
  try {
    const rows = await call('frappe.client.get_list', { doctype: 'CRM Deal', fields: ['name', 'custom_numero_solaer', 'deal_value', 'custom_ds_revenue', 'custom_solaer_revenue', 'status'], filters: { name: ['in', uniq] }, limit_page_length: 0 })
    const m = {}; (rows || []).forEach(r => { m[r.name] = r }); dealMap.value = m
  } catch (e) { /* ignore */ }
}
const cells = computed(() => {
  const out = []
  const years = windowYears.value
  if (viewMode.value === 'anio') {
    years.forEach((y) => out.push({ y, label: String(y), yearStart: true }))
  } else if (viewMode.value === 'trimestre') {
    years.forEach((y) => { for (let q = 0; q < 4; q++) out.push({ y, label: 'T' + (q + 1), yearStart: q === 0 }) })
  } else {
    years.forEach((y) => { for (let m = 0; m < 12; m++) out.push({ y, label: MI[m], yearStart: m === 0 }) })
  }
  return out
})

function uid() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7)
}
function markDirty() {
  dirty.value = true
}

async function load() {
  try {
    const r = await call('frappe.client.get_value', {
      doctype: 'CRM Organization',
      filters: { name: props.organizationId },
      fieldname: 'custom_roadmap_data',
    })
    const raw = r?.custom_roadmap_data
    const data = raw ? JSON.parse(raw) : {}
    streams.value = Array.isArray(data.streams) ? data.streams : []
  } catch (e) {
    streams.value = []
  }
  dirty.value = false
  loadDeals()
}
load()
watch(() => props.organizationId, load)

async function persist(explicit = false) {
  saving.value = true
  try {
    await call('frappe.client.set_value', {
      doctype: 'CRM Organization',
      name: props.organizationId,
      fieldname: 'custom_roadmap_data',
      value: JSON.stringify({ streams: streams.value }),
    })
    dirty.value = false
    if (explicit) toast.success(__('Roadmap guardado'))
  } catch (e) {
    toast.error(__('No se pudo guardar el roadmap'))
  } finally {
    saving.value = false
  }
}

// ── streams ───────────────────────────────────────────────
function startAddStream() {
  addingStream.value = true
  newStreamName.value = ''
  nextTick(() => newStreamRef.value?.focus())
}
function confirmAddStream() {
  const name = (newStreamName.value || '').trim()
  if (!name) return
  streams.value.push({
    id: uid(),
    name,
    color: PALETTE[streams.value.length % PALETTE.length],
    items: [],
  })
  addingStream.value = false
  markDirty()
  persist()
}
function removeStream(stream) {
  streams.value = streams.value.filter((s) => s.id !== stream.id)
  markDirty()
  persist()
}

// ── items ─────────────────────────────────────────────────
function applyDraftTo(item) {
  const d = itemDraft.value
  item.label = (d.label || '').trim()
  item.type = d.type
  if (d.type === 'milestone') {
    item.date = d.date || `${startYear.value}-01-01`
    delete item.start; delete item.end
  } else {
    const s = d.startY * 12 + d.startM, e = d.endY * 12 + d.endM
    const a = Math.min(s, e), b = Math.max(s, e)
    item.start = `${Math.floor(a / 12)}-${String((a % 12) + 1).padStart(2, '0')}`
    item.end = `${Math.floor(b / 12)}-${String((b % 12) + 1).padStart(2, '0')}`
    delete item.date
  }
  if (d.color) item.color = d.color; else delete item.color
  if (d.deal) item.deal = d.deal; else delete item.deal
}
function startAddItemGlobal() {
  if (!streams.value.length) return
  formMode.value = 'add'; editId.value = null
  formStreamId.value = streams.value[0].id
  const d = new Date()
  const yy = windowYears.value.includes(d.getFullYear()) ? d.getFullYear() : startYear.value
  const iso = `${yy}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  const st = streams.value.find(s => s.id === formStreamId.value)
  itemDraft.value = { label: '', type: 'milestone', date: iso, startY: startYear.value, startM: 0, endY: startYear.value, endM: 2, color: (st && st.color) || '#2563eb', deal: '' }
  showItemForm.value = true
}
function startEditItem(stream, it) {
  formMode.value = 'edit'; formStreamId.value = stream.id; editId.value = it.id
  const col = it.color || (stream && stream.color) || '#2563eb'
  if (it.type === 'bar') {
    const [sy, sm] = String(it.start).split('-').map(Number)
    const [ey, em] = String(it.end).split('-').map(Number)
    itemDraft.value = { label: it.label, type: 'bar', date: '', startY: sy, startM: sm - 1, endY: ey, endM: em - 1, color: col, deal: it.deal || '' }
  } else {
    itemDraft.value = { label: it.label, type: 'milestone', date: it.date || '', startY: startYear.value, startM: 0, endY: startYear.value, endM: 2, color: col, deal: it.deal || '' }
  }
  showItemForm.value = true
}
function confirmItem() {
  const stream = streams.value.find((s) => s.id === formStreamId.value)
  if (!stream || !(itemDraft.value.label || '').trim()) return
  if (formMode.value === 'edit') {
    const it = (stream.items || []).find((x) => x.id === editId.value)
    if (!it) return
    applyDraftTo(it)
  } else {
    const it = { id: uid() }
    applyDraftTo(it)
    stream.items.push(it)
  }
  showItemForm.value = false
  markDirty()
  persist()
  loadDeals()
}
function removeItem(stream, it) {
  stream.items = stream.items.filter((x) => x.id !== it.id)
  markDirty()
  persist()
}

// ── geometría (36 meses) ──────────────────────────────────
function daysInMonth(y, m) {
  return new Date(y, m + 1, 0).getDate()
}
function absIndex(y, m) {
  return (y - startYear.value) * 12 + m
}
function msLeft(it) {
  if (!it.date) return null
  const parts = String(it.date).split('-')
  const y = +parts[0], m = +parts[1] - 1, d = +parts[2] || 1
  const idx = absIndex(y, m)
  if (idx < 0 || idx >= TOTAL.value) return null
  const frac = (idx + (d - 1) / daysInMonth(y, m)) / TOTAL.value
  return frac * 100
}
function barGeom(it) {
  if (!it.start || !it.end) return null
  const [sy, sm] = String(it.start).split('-').map(Number)
  const [ey, em] = String(it.end).split('-').map(Number)
  let startAbs = absIndex(sy, sm - 1)
  let endAbs = absIndex(ey, em - 1)
  if (endAbs < 0 || startAbs > TOTAL.value - 1) return null
  startAbs = Math.max(0, startAbs)
  endAbs = Math.min(TOTAL.value - 1, endAbs)
  const left = (startAbs / TOTAL.value) * 100
  const width = ((endAbs - startAbs + 1) / TOTAL.value) * 100
  return { left, width }
}
const todayLeft = computed(() => {
  const d = new Date()
  const idx = absIndex(d.getFullYear(), d.getMonth())
  if (idx < 0 || idx >= TOTAL.value) return null
  const frac = (idx + (d.getDate() - 1) / daysInMonth(d.getFullYear(), d.getMonth())) / TOTAL.value
  return frac * 100
})
</script>
