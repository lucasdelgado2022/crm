<template>
  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Controles -->
    <div class="mb-4 flex flex-wrap items-center gap-3">
      <select
        v-model="year"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8"
        :title="__('Filtrar por año')"
      >
        <option value="">{{ __('Todos los años') }}</option>
        <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
      </select>
      <div class="flex flex-wrap items-center gap-3">
        <label
          v-for="m in METRICS"
          :key="m.key"
          class="flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7"
        >
          <input type="checkbox" v-model="selected[m.key]" class="h-3.5 w-3.5 rounded border-outline-gray-3" />
          <span class="h-2.5 w-2.5 rounded-sm" :style="{ background: m.color }" />
          {{ __(m.label) }}
        </label>
      </div>
      <Button variant="ghost" icon="refresh-cw" :loading="loading" :tooltip="__('Actualizar')" @click="load" />
      <span class="ml-auto text-sm text-ink-gray-5">
        {{ shownEventos.length }} {{ __('eventos') }}
      </span>
    </div>

    <!-- KPIs -->
    <div class="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div
        v-for="m in METRICS"
        :key="m.key"
        class="rounded-lg border p-4"
        :style="{ borderColor: m.color + '55', background: m.color + '10' }"
      >
        <div class="text-2xl font-semibold" :style="{ color: m.color }">{{ totals[m.key] }}</div>
        <div class="text-sm text-ink-gray-5">{{ __(m.label) }}</div>
      </div>
    </div>

    <div
      v-if="!shownEventos.length && !loading"
      class="flex flex-1 items-center justify-center text-sm text-ink-gray-4"
    >
      {{ __('Sin eventos.') }}
    </div>

    <template v-else>
      <!-- Barras horizontales por mes -->
      <div class="rounded-lg border p-4">
        <div class="mb-3 flex items-center justify-between">
          <div class="text-sm font-semibold text-ink-gray-8">{{ __('Eventos por mes') }}</div>
          <div class="text-xs text-ink-gray-5">{{ porMes.length }} {{ __('meses') }}</div>
        </div>
        <div v-html="chartSvg" />
      </div>

      <!-- Detalle por evento -->
      <div class="mt-4 rounded-lg border p-4">
        <div class="mb-3 text-sm font-semibold text-ink-gray-8">{{ __('Detalle por evento') }}</div>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[560px] text-xs">
            <thead>
              <tr class="border-b text-[10px] uppercase tracking-wide text-ink-gray-5">
                <th class="px-2 py-1.5 text-left">{{ __('Evento') }}</th>
                <th class="px-2 py-1.5 text-left">{{ __('Fecha') }}</th>
                <th class="px-2 py-1.5 text-right">{{ __('Inscriptos') }}</th>
                <th class="px-2 py-1.5 text-right">{{ __('Asistentes') }}</th>
                <th class="px-2 py-1.5 text-right">{{ __('Leads') }}</th>
                <th class="px-2 py-1.5 text-right">{{ __('Oport.') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in shownEventos" :key="e.name" class="border-b hover:bg-surface-gray-1">
                <td class="px-2 py-1.5 font-medium text-ink-gray-8">{{ e.titulo }}</td>
                <td class="px-2 py-1.5 text-ink-gray-6">{{ e.fecha_inicio || '—' }}</td>
                <td class="px-2 py-1.5 text-right tabular-nums text-ink-gray-7">{{ mx(e).inscriptos }}</td>
                <td class="px-2 py-1.5 text-right tabular-nums text-ink-gray-7">{{ mx(e).asistieron }}</td>
                <td class="px-2 py-1.5 text-right tabular-nums text-ink-gray-7">{{ mx(e).leads }}</td>
                <td class="px-2 py-1.5 text-right tabular-nums text-ink-gray-7">{{ mx(e).opps }}</td>
              </tr>
              <tr class="bg-surface-gray-2 font-semibold text-ink-gray-9">
                <td class="px-2 py-1.5" colspan="2">{{ __('Total') }}</td>
                <td class="px-2 py-1.5 text-right tabular-nums">{{ totals.inscriptos }}</td>
                <td class="px-2 py-1.5 text-right tabular-nums">{{ totals.asistieron }}</td>
                <td class="px-2 py-1.5 text-right tabular-nums">{{ totals.leads }}</td>
                <td class="px-2 py-1.5 text-right tabular-nums">{{ totals.opps }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Button, call, toast } from 'frappe-ui'

defineProps({ embedded: { type: Boolean, default: false } })

const eventos = ref([])
const metrics = ref({})
const loading = ref(false)

const METRICS = [
  { key: 'inscriptos', label: 'Inscriptos', color: '#2563eb' },
  { key: 'asistieron', label: 'Asistentes', color: '#16a34a' },
  { key: 'leads', label: 'Leads', color: '#f59e0b' },
  { key: 'opps', label: 'Oportunidades', color: '#9333ea' },
]
const selected = reactive({ inscriptos: true, asistieron: true, leads: true, opps: true })
const activeMetrics = computed(() => METRICS.filter((m) => selected[m.key]))

const year = ref(String(new Date().getFullYear()))
const yearOptions = computed(() => {
  const s = new Set()
  s.add(String(new Date().getFullYear()))
  for (const e of eventos.value) if (e.fecha_inicio) s.add(String(e.fecha_inicio).slice(0, 4))
  return [...s].sort((a, b) => b.localeCompare(a))
})
const inYear = (e) => !year.value || String(e.fecha_inicio || '').slice(0, 4) === year.value

const EMPTY = { inscriptos: 0, asistieron: 0, leads: 0, opps: 0 }
const mx = (e) => metrics.value[e.name] || EMPTY

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sept', 'oct', 'nov', 'dic']
function mesLabel(ym) {
  if (!ym || ym.length < 7) return ym || '—'
  const m = parseInt(ym.slice(5, 7), 10) - 1
  return (MESES[m] || '') + ' ' + ym.slice(2, 4)
}
const esc = (s) => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
// Suma 1 mes a un YYYY-MM
function nextMonth(ym) {
  let y = parseInt(ym.slice(0, 4), 10)
  let m = parseInt(ym.slice(5, 7), 10) + 1
  if (m > 12) { m = 1; y += 1 }
  return y + '-' + String(m).padStart(2, '0')
}

async function load() {
  loading.value = true
  try {
    const ev = await call('frappe.client.get_list', {
      doctype: 'CRM Marketing Evento',
      fields: ['name', 'titulo', 'fecha_inicio'],
      order_by: 'fecha_inicio asc',
      limit_page_length: 0,
    })
    eventos.value = Array.isArray(ev) ? ev : ev?.message || []
    const r = await call('evento_metrics')
    metrics.value = (r && r.message) || r || {}
  } catch (e) {
    toast.error(__('No se pudieron cargar los eventos'))
  } finally {
    loading.value = false
  }
}

const shownEventos = computed(() =>
  eventos.value.filter((e) => inYear(e)).sort((a, b) => String(a.fecha_inicio || '').localeCompare(String(b.fecha_inicio || ''))),
)

const totals = computed(() => {
  const t = { inscriptos: 0, asistieron: 0, leads: 0, opps: 0 }
  for (const e of shownEventos.value) {
    const m = mx(e)
    t.inscriptos += m.inscriptos || 0
    t.asistieron += m.asistieron || 0
    t.leads += m.leads || 0
    t.opps += m.opps || 0
  }
  return t
})

// Agrupado por mes (YYYY-MM), mostrando TODOS los meses del período aunque no haya eventos
const porMes = computed(() => {
  const m = {}
  for (const e of shownEventos.value) {
    const ym = String(e.fecha_inicio || '').slice(0, 7)
    if (!ym) continue
    if (!m[ym]) m[ym] = { mes: ym, eventos: 0, inscriptos: 0, asistieron: 0, leads: 0, opps: 0 }
    const mt = mx(e)
    m[ym].eventos += 1
    m[ym].inscriptos += mt.inscriptos || 0
    m[ym].asistieron += mt.asistieron || 0
    m[ym].leads += mt.leads || 0
    m[ym].opps += mt.opps || 0
  }
  // Secuencia completa de meses
  let seq = []
  if (year.value) {
    for (let i = 1; i <= 12; i++) seq.push(year.value + '-' + String(i).padStart(2, '0'))
  } else {
    const keys = Object.keys(m).sort()
    if (keys.length) {
      let cur = keys[0]
      const last = keys[keys.length - 1]
      seq.push(cur)
      while (cur < last) { cur = nextMonth(cur); seq.push(cur) }
    }
  }
  return seq.map((ym) => m[ym] || { mes: ym, eventos: 0, inscriptos: 0, asistieron: 0, leads: 0, opps: 0 })
})

// Escala común: máximo entre las métricas activas de todos los meses
const barMax = computed(() => {
  let mx = 1
  for (const row of porMes.value) {
    for (const m of activeMetrics.value) mx = Math.max(mx, row[m.key])
  }
  return mx
})

// Gráfico de barras verticales agrupadas por mes
const chartSvg = computed(() => {
  const months = porMes.value
  const mets = activeMetrics.value
  if (!months.length || !mets.length) return ''
  const W = 720, H = 320, padL = 34, padR = 12, padT = 16, padB = 46
  const plotW = W - padL - padR, plotH = H - padT - padB
  const max = barMax.value
  const n = months.length
  const groupW = plotW / n
  const innerPad = groupW * 0.18
  const usable = groupW - innerPad
  const bw = Math.max(3, Math.min(22, usable / mets.length))
  const yv = (v) => padT + plotH - (Math.max(0, v) / max) * plotH
  let g = ''
  // gridlines + eje Y
  for (let i = 0; i <= 4; i++) {
    const v = (max * i) / 4, y = yv(v)
    g += `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W - padR}" y2="${y.toFixed(1)}" stroke="#e5e6e2"/>`
    g += `<text x="${padL - 5}" y="${(y + 3).toFixed(1)}" text-anchor="end" font-size="8" fill="#8a909c">${Math.round(v)}</text>`
  }
  let bars = ''
  months.forEach((row, i) => {
    const gx = padL + groupW * i + innerPad / 2
    const bandW = bw * mets.length
    const startX = gx + (usable - bandW) / 2
    mets.forEach((mt, j) => {
      const val = row[mt.key] || 0
      const x = startX + j * bw
      const y = yv(val)
      const h = padT + plotH - y
      if (val > 0) {
        bars += `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${(bw - 1.2).toFixed(1)}" height="${Math.max(0, h).toFixed(1)}" rx="1.5" fill="${mt.color}"><title>${esc(mesLabel(row.mes) + ' · ' + mt.label + ': ' + val)}</title></rect>`
        if (n <= 14) bars += `<text x="${(x + (bw - 1.2) / 2).toFixed(1)}" y="${(y - 2).toFixed(1)}" text-anchor="middle" font-size="7" font-weight="600" fill="#181a1f">${val}</text>`
      }
    })
    // etiqueta del mes
    const cx = gx + usable / 2
    bars += `<text x="${cx.toFixed(1)}" y="${(H - padB + 14).toFixed(1)}" text-anchor="middle" font-size="8" fill="#5b616e">${esc(mesLabel(row.mes))}</text>`
    if (row.eventos) bars += `<text x="${cx.toFixed(1)}" y="${(H - padB + 24).toFixed(1)}" text-anchor="middle" font-size="7" fill="#a1a7b3">${row.eventos} ev.</text>`
  })
  return `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto" role="img">${g}${bars}</svg>`
})

onMounted(load)
</script>
