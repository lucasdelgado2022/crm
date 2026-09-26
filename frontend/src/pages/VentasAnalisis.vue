<template>
  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Controles -->
    <div class="mb-4 flex flex-wrap items-center gap-3">
      <select
        v-model="amountKey"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm font-medium text-ink-gray-8"
        :title="__('Monto')"
      >
        <option v-for="a in AMOUNTS" :key="a.key" :value="a.key">{{ a.label }}</option>
      </select>
      <div class="flex rounded-lg border border-outline-gray-2 p-0.5">
        <button
          v-for="m in MODES"
          :key="m.key"
          type="button"
          class="rounded-md px-3 py-1 text-sm font-medium transition"
          :class="metricMode === m.key ? 'bg-surface-gray-3 text-ink-gray-9' : 'text-ink-gray-6 hover:text-ink-gray-9'"
          @click="metricMode = m.key"
        >{{ m.label }}</button>
      </div>
      <select
        v-model="year"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8"
        :title="__('Filtrar por año')"
      >
        <option value="">{{ __('Todos los años') }}</option>
        <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
      </select>
      <select
        v-model="tipoFilter"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8"
        :title="__('Nuevo / Renovación')"
      >
        <option value="">{{ __('Nuevo + Renovación') }}</option>
        <option v-for="t in TIPOS" :key="t" :value="t">{{ t }}</option>
      </select>
      <div class="flex items-center gap-3">
        <label
          v-for="e in ESTADOS"
          :key="e.key"
          class="flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7"
        >
          <input type="checkbox" v-model="selected[e.key]" class="h-3.5 w-3.5 rounded border-outline-gray-3" />
          <span class="h-2.5 w-2.5 rounded-sm" :style="{ background: e.color }" />
          {{ e.label }}
        </label>
      </div>
      <Button variant="ghost" icon="refresh-cw" :loading="loading" :tooltip="__('Actualizar')" @click="load" />
      <span class="ml-auto text-sm text-ink-gray-5">
        {{ shownCount }} {{ __('oportunidades') }} · {{ money(totalValue) }}
      </span>
    </div>

    <div
      v-if="!rows.length && !loading"
      class="flex flex-1 items-center justify-center text-sm text-ink-gray-4"
    >
      {{ __('Sin datos.') }}
    </div>

    <template v-else>
      <!-- Grilla de gráficos -->
      <div class="grid gap-4 lg:grid-cols-2">
        <div
          v-for="sec in sections"
          :key="sec.title"
          class="rounded-lg border p-4"
        >
          <div class="mb-3 flex items-center justify-between">
            <div class="text-sm font-semibold text-ink-gray-8">{{ __(sec.title) }}</div>
            <div class="text-xs text-ink-gray-5">{{ sec.groups.length }}</div>
          </div>
          <div class="flex flex-col gap-2">
            <div
              v-for="g in sec.groups"
              :key="g.key"
              class="flex items-center gap-2 text-xs"
            >
              <span class="w-32 shrink-0 truncate text-ink-gray-6" :title="g.label">{{ g.label }}</span>
              <span class="flex h-3 flex-1 overflow-hidden rounded bg-surface-gray-2">
                <template v-if="sec.colorByKey">
                  <span class="block h-full" :style="{ width: totalPct(sec, g) + '%', background: keyColor(g.key) }" />
                </template>
                <template v-else-if="metricMode === 'ticket'">
                  <span class="block h-full" :style="{ width: totalPct(sec, g) + '%', background: '#2563eb' }" />
                </template>
                <template v-else>
                  <span
                    v-for="e in activeEstados"
                    :key="e.key"
                    class="block h-full"
                    :style="{ width: segPct(sec, g, e.key) + '%', background: e.color }"
                    :title="e.label + ': ' + fmt(segVal(g, e.key))"
                  />
                </template>
              </span>
              <span class="w-24 shrink-0 text-right tabular-nums text-ink-gray-8">{{ fmt(barVal(g)) }}</span>
            </div>
            <div v-if="!sec.groups.length" class="text-xs text-ink-gray-4">{{ __('Sin datos') }}</div>
          </div>
        </div>
      </div>

      <!-- Pareto de productos -->
      <div class="mt-4 rounded-lg border p-4">
        <div class="mb-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-ink-gray-6">
          <span class="text-sm font-semibold text-ink-gray-8">{{ __('Pareto de productos') }}</span>
          <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-sm" style="background:#2563eb" />{{ metricLabel }}</span>
          <span class="flex items-center gap-1.5"><span class="h-2.5 w-4 rounded-sm" style="background:#dc2626" />{{ __('% acumulado') }}</span>
          <span class="flex items-center gap-1.5"><span class="h-0.5 w-4" style="background:#f59e0b" />{{ __('80%') }}</span>
        </div>
        <div v-html="paretoSvg" />
      </div>

      <!-- Producto por año -->
      <div class="mt-4 rounded-lg border p-4">
        <div class="mb-3 flex items-center justify-between">
          <div class="text-sm font-semibold text-ink-gray-8">{{ __('Producto por año') }}</div>
          <div class="text-xs text-ink-gray-5">{{ metricLabel }} · {{ __('todos los años') }}</div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[560px] text-xs">
            <thead>
              <tr class="border-b text-[10px] uppercase tracking-wide text-ink-gray-5">
                <th class="px-2 py-1.5 text-left">{{ __('Producto') }}</th>
                <th v-for="y in pxaAnios" :key="y" class="px-2 py-1.5 text-right">{{ y }}</th>
                <th class="px-2 py-1.5 text-right">{{ __('Total') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in pxaRows" :key="row.producto" class="border-b hover:bg-surface-gray-1">
                <td class="px-2 py-1.5 text-ink-gray-8">{{ row.producto }}</td>
                <td v-for="y in pxaAnios" :key="y" class="px-2 py-1.5 text-right tabular-nums text-ink-gray-7">{{ cellFmt(row.byY[y]) }}</td>
                <td class="px-2 py-1.5 text-right font-medium tabular-nums text-ink-gray-9">{{ cellFmt(row.total) }}</td>
              </tr>
              <tr v-if="!pxaRows.length"><td :colspan="pxaAnios.length + 2" class="px-2 py-3 text-center text-ink-gray-4">{{ __('Sin datos') }}</td></tr>
              <tr v-else class="bg-surface-gray-2 font-semibold text-ink-gray-9">
                <td class="px-2 py-1.5">{{ __('Total') }}</td>
                <td v-for="y in pxaAnios" :key="y" class="px-2 py-1.5 text-right tabular-nums">{{ cellFmt(pxaTotals.byY[y]) }}</td>
                <td class="px-2 py-1.5 text-right tabular-nums">{{ cellFmt(pxaTotals.total) }}</td>
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
import { usersStore } from '@/stores/users'

const { getUser } = usersStore()

const rows = ref([])
const loading = ref(false)

// Monto: qué campo de importe se usa
const AMOUNTS = [
  { key: 'value', label: 'Valor oportunidad', f: 'value' },
  { key: 'ds', label: 'DS Revenue', f: 'value_ds' },
  { key: 'sol', label: 'Solaer Revenue', f: 'value_sol' },
]
const amountKey = ref('value')
const amountField = computed(() => (AMOUNTS.find((a) => a.key === amountKey.value) || AMOUNTS[0]).f)
const amt = (r) => r[amountField.value] || 0

// Métrica: totales / ticket promedio / cantidad
const MODES = [
  { key: 'total', label: 'Totales' },
  { key: 'ticket', label: 'Ticket promedio' },
  { key: 'count', label: 'Cantidad' },
]
const metricMode = ref('total')
const isCount = computed(() => metricMode.value === 'count')
const metricLabel = computed(() => {
  const a = AMOUNTS.find((x) => x.key === amountKey.value)?.label || ''
  const m = MODES.find((x) => x.key === metricMode.value)?.label || ''
  return metricMode.value === 'count' ? m : m + ' · ' + a
})

const ESTADOS = [
  { key: 'Won', label: 'Ganadas', color: '#16a34a' },
  { key: 'Abierta', label: 'Abiertas', color: '#2563eb' },
  { key: 'Lost', label: 'Perdidas', color: '#dc2626' },
]
const selected = reactive({ Won: true, Abierta: false, Lost: false })
const activeEstados = computed(() => ESTADOS.filter((e) => selected[e.key]))

const year = ref(String(new Date().getFullYear()))
const yearOptions = computed(() => {
  const s = new Set()
  for (const r of rows.value) if (selected[r.estado] && r.anio) s.add(r.anio)
  return [...s].sort((a, b) => b.localeCompare(a))
})
const inYear = (r) => !year.value || r.anio === year.value
const tipoFilter = ref('Nuevo')
const TIPOS = ['Nuevo', 'Renovación', 'Servicio']
const inTipo = (r) => !tipoFilter.value || r.tipo === tipoFilter.value

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sept', 'oct', 'nov', 'dic']
const money = (n) => '$' + Math.round(n || 0).toLocaleString('en-US')
const moneyK = (n) => { n = Math.round(n || 0); return Math.abs(n) >= 1000 ? '$' + Math.round(n / 1000).toLocaleString('en-US') + 'k' : '$' + n }
const fmt = (n) => (isCount.value ? String(Math.round(n || 0)) : money(n))
const esc = (s) => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
const axLabel = (v) => (isCount.value ? String(Math.round(v)) : moneyK(v))
// Color determinístico por clave (para las barras de país)
const KEY_COLORS = ['#2563eb', '#16a34a', '#9333ea', '#d97706', '#db2777', '#0d9488', '#ea580c', '#4f46e5', '#0891b2', '#65a30d']
function keyColor(name) {
  if (!name) return '#94a3b8'
  let h = 0
  for (let i = 0; i < String(name).length; i++) h = (h * 31 + String(name).charCodeAt(i)) >>> 0
  return KEY_COLORS[h % KEY_COLORS.length]
}

async function load() {
  loading.value = true
  try {
    const r = await call('ventas_analisis')
    rows.value = Array.isArray(r) ? r : r?.message || []
  } catch (e) {
    rows.value = []
    toast.error(__('No se pudieron cargar las oportunidades'))
  } finally {
    loading.value = false
  }
}

const shownRows = computed(() => rows.value.filter((r) => selected[r.estado] && inYear(r) && inTipo(r)))
const shownCount = computed(() => shownRows.value.length)
const totalValue = computed(() => shownRows.value.reduce((a, r) => a + amt(r), 0))

function mesLabel(ym) {
  if (!ym || ym.length < 7) return ym || '—'
  const y = ym.slice(0, 4)
  const m = parseInt(ym.slice(5, 7), 10) - 1
  return (MESES[m] || '') + ' ' + y.slice(2)
}

// Valor de un grupo según la métrica
function groupVal(g) {
  if (metricMode.value === 'count') return g.count
  if (metricMode.value === 'ticket') return g.count ? g.sum / g.count : 0
  return g.sum
}

function agg(dimKey, ordered, isUser, isMonth) {
  const m = {}
  for (const r of rows.value) {
    if (!selected[r.estado] || !inYear(r) || !inTipo(r)) continue
    const k = r[dimKey] || '—'
    if (!m[k]) m[k] = { key: k, seg: { Won: 0, Abierta: 0, Lost: 0 }, segC: { Won: 0, Abierta: 0, Lost: 0 }, sum: 0, count: 0 }
    m[k].seg[r.estado] += amt(r)
    m[k].segC[r.estado] += 1
    m[k].sum += amt(r)
    m[k].count += 1
  }
  let arr = Object.values(m)
  if (ordered) arr.sort((a, b) => String(a.key).localeCompare(String(b.key)))
  else arr.sort((a, b) => groupVal(b) - groupVal(a))
  return arr.map((g) => ({
    ...g,
    label: isUser ? getUser(g.key)?.full_name || g.key : isMonth ? mesLabel(g.key) : g.key,
  }))
}

const sections = computed(() => [
  { title: 'Por producto', groups: agg('producto') },
  { title: 'Por país', groups: agg('pais'), colorByKey: true },
  { title: 'Por mes', groups: agg('mes', true, false, true) },
  { title: 'Por responsable comercial', groups: agg('responsable', false, true) },
])

// Pareto de productos
const paretoProd = computed(() => {
  const groups = sections.value[0].groups
  const arr = groups.map((g) => ({ label: g.label, val: groupVal(g), sum: g.sum, count: g.count })).filter((x) => x.val > 0)
  const total = arr.reduce((a, x) => a + x.val, 0) || 1
  let cum = 0
  return arr.map((x) => { cum += x.val; return { ...x, cumPct: (cum / total) * 100 } })
})
const paretoSvg = computed(() => {
  const data = paretoProd.value
  if (!data.length) return ''
  const W = 700, H = 300, padL = 50, padR = 40, padT = 14, padB = 70
  const plotW = W - padL - padR, plotH = H - padT - padB
  const maxVal = Math.max(1, ...data.map((d) => d.val))
  const n = data.length, gap = plotW / n, bw = Math.min(46, gap * 0.62)
  const yv = (v) => padT + plotH - (v / maxVal) * plotH
  const yp = (p) => padT + plotH - (p / 100) * plotH
  let g = ''
  for (let i = 0; i <= 4; i++) {
    const v = (maxVal * i) / 4, y = yv(v)
    g += `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W - padR}" y2="${y.toFixed(1)}" stroke="#e5e6e2"/><text x="${padL - 6}" y="${(y + 3).toFixed(1)}" text-anchor="end" font-size="8" fill="#8a909c">${axLabel(v)}</text>`
  }
  for (let i = 0; i <= 4; i++) {
    const p = i * 25, y = yp(p)
    g += `<text x="${W - padR + 5}" y="${(y + 3).toFixed(1)}" text-anchor="start" font-size="8" fill="#8a909c">${p}%</text>`
  }
  const y80 = yp(80)
  g += `<line x1="${padL}" y1="${y80.toFixed(1)}" x2="${W - padR}" y2="${y80.toFixed(1)}" stroke="#f59e0b" stroke-dasharray="4 3"/>`
  let bars = '', pts = []
  data.forEach((d, i) => {
    const cx = padL + gap * i + gap / 2, x = cx - bw / 2
    const h = (d.val / maxVal) * plotH
    bars += `<rect x="${x.toFixed(1)}" y="${yv(d.val).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(0, h).toFixed(1)}" rx="2" fill="#2563eb"/>`
    bars += `<text x="${cx.toFixed(1)}" y="${(yv(d.val) - 4).toFixed(1)}" text-anchor="middle" font-size="7.5" font-weight="600" fill="#181a1f">${esc(moneyK(d.sum) + ' (' + d.count + ')')}</text>`
    const lbl = esc((d.label || '').slice(0, 16))
    bars += `<text x="${cx.toFixed(1)}" y="${(H - padB + 12).toFixed(1)}" text-anchor="end" font-size="7.5" fill="#5b616e" transform="rotate(-40 ${cx.toFixed(1)} ${(H - padB + 12).toFixed(1)})">${lbl}</text>`
    pts.push([cx, yp(d.cumPct)])
  })
  const path = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ')
  let line = `<path d="${path}" fill="none" stroke="#dc2626" stroke-width="1.6"/>`
  pts.forEach((p) => { line += `<circle cx="${p[0].toFixed(1)}" cy="${p[1].toFixed(1)}" r="2.2" fill="#dc2626"/>` })
  return `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto" role="img">${g}${bars}${line}</svg>`
})

const barVal = (g) => groupVal(g)
function segVal(g, k) {
  if (metricMode.value === 'count') return g.segC[k]
  if (metricMode.value === 'ticket') return g.segC[k] ? g.seg[k] / g.segC[k] : 0
  return g.seg[k]
}
function segPct(sec, g, k) {
  const max = Math.max(1, ...sec.groups.map((x) => barVal(x)))
  return (segVal(g, k) / max) * 100
}
function totalPct(sec, g) {
  const max = Math.max(1, ...sec.groups.map((x) => barVal(x)))
  return (barVal(g) / max) * 100
}

// Producto × Año (respeta estado + tipo; ignora el filtro de año)
const pxaAnios = computed(() => {
  const s = new Set()
  for (const r of rows.value) if (selected[r.estado] && r.anio && inTipo(r)) s.add(r.anio)
  return [...s].sort((a, b) => a.localeCompare(b))
})
const pxaRows = computed(() => {
  const m = {}
  for (const r of rows.value) {
    if (!selected[r.estado] || !r.anio || !inTipo(r)) continue
    const p = r.producto || '(Sin producto)'
    if (!m[p]) m[p] = { producto: p, byY: {}, total: { sum: 0, count: 0 } }
    if (!m[p].byY[r.anio]) m[p].byY[r.anio] = { sum: 0, count: 0 }
    m[p].byY[r.anio].sum += amt(r)
    m[p].byY[r.anio].count += 1
    m[p].total.sum += amt(r)
    m[p].total.count += 1
  }
  return Object.values(m).sort((a, b) => cellNum(b.total) - cellNum(a.total))
})
const pxaTotals = computed(() => {
  const t = { byY: {}, total: { sum: 0, count: 0 } }
  for (const row of pxaRows.value) {
    t.total.sum += row.total.sum
    t.total.count += row.total.count
    for (const y of pxaAnios.value) {
      const c = row.byY[y]
      if (!c) continue
      if (!t.byY[y]) t.byY[y] = { sum: 0, count: 0 }
      t.byY[y].sum += c.sum
      t.byY[y].count += c.count
    }
  }
  return t
})
function cellNum(c) {
  if (!c) return 0
  if (metricMode.value === 'count') return c.count
  if (metricMode.value === 'ticket') return c.count ? c.sum / c.count : 0
  return c.sum
}
function cellFmt(c) {
  if (!c || !c.count) return '—'
  return fmt(cellNum(c))
}

onMounted(load)
</script>
