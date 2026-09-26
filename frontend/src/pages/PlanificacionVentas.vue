<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <PlanIcon class="h-5 w-5" />
        {{ __('Planificación de Ventas') }}
      </div>
    </template>
    <template #right-header>
      <div v-if="isAdminUser" class="flex flex-wrap items-center gap-2">
        <div class="flex rounded-lg border border-outline-gray-2 p-0.5">
          <button
            v-for="opt in METRICS"
            :key="opt.key"
            class="rounded-md px-3 py-1 text-sm font-medium transition"
            :class="metric === opt.key ? 'bg-surface-gray-3 text-ink-gray-9' : 'text-ink-gray-6 hover:text-ink-gray-9'"
            @click="metric = opt.key"
          >{{ opt.label }}</button>
        </div>
        <div class="flex rounded-lg border border-outline-gray-2 p-0.5">
          <button
            v-for="opt in SCENARIOS"
            :key="opt.key"
            class="rounded-md px-3 py-1 text-sm font-medium transition"
            :class="scenario === opt.key ? 'bg-surface-gray-3 text-ink-gray-9' : 'text-ink-gray-6 hover:text-ink-gray-9'"
            :title="opt.hint"
            @click="scenario = opt.key"
          >{{ opt.label }}</button>
        </div>
        <select v-model="fCanal" class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none">
          <option value="">{{ __('Todos los canales') }}</option>
          <option v-for="c in CANALES" :key="c" :value="c">{{ c }}</option>
        </select>
        <select v-model.number="year" class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none">
          <option v-for="y in YEARS" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </template>
  </LayoutHeader>

  <div v-if="!isAdminUser" class="flex h-full items-center justify-center p-10 text-center">
    <div>
      <LockIcon class="mx-auto h-8 w-8 text-ink-gray-4" />
      <div class="mt-3 text-base font-medium text-ink-gray-7">{{ __('Acceso restringido') }}</div>
      <div class="mt-1 text-sm text-ink-gray-5">{{ __('Esta sección es solo para administradores.') }}</div>
    </div>
  </div>

  <div v-else class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- KPIs -->
    <div class="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      <div class="rounded-lg border border-blue-200 bg-blue-50/40 p-3">
        <div class="text-xs font-medium text-blue-700">{{ metricLabel }} {{ year }}</div>
        <div class="mt-0.5 text-xl font-semibold text-blue-700 tabular-nums">{{ money(kpiTotal) }}</div>
        <div class="text-xs text-ink-gray-5">{{ growthVsBase }}</div>
      </div>
      <div class="rounded-lg border border-violet-200 bg-violet-50/40 p-3">
        <div class="text-xs font-medium text-violet-700">{{ __('Pipeline necesario') }} (x3.5)</div>
        <div class="mt-0.5 text-xl font-semibold text-violet-700 tabular-nums">{{ money(pipeline) }}</div>
        <div class="text-xs text-ink-gray-5">{{ __('cobertura sobre objetivo') }}</div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Cantidad de ventas') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9 tabular-nums">{{ kpiQty }}</div>
        <div class="text-xs text-ink-gray-5">{{ __('proyectadas') }} {{ year }}</div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Ticket promedio') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9 tabular-nums">{{ money(kpiTicket) }}</div>
        <div class="text-xs text-ink-gray-5">{{ __('ponderado') }}</div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ metricLabel }} 2026–2030</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9 tabular-nums">{{ moneyK(kpi5y) }}</div>
        <div class="text-xs text-ink-gray-5">{{ __('total del plan') }}</div>
      </div>
      <div class="rounded-lg border p-3" :class="baseline ? 'border-green-200 bg-green-50/40' : ''">
        <div class="text-xs text-ink-gray-5">{{ __('Baseline 2025') }}</div>
        <div class="mt-0.5 text-xl font-semibold tabular-nums" :class="baseline ? 'text-green-700' : 'text-ink-gray-4'">{{ baseline ? money(baselineMetric) : '—' }}</div>
        <div class="text-xs text-ink-gray-5">{{ baseline ? baseline.count + ' ' + __('ganadas') + ' 2025' : __('sin datos 2025') }}</div>
      </div>
    </div>

    <!-- Gráfico + resumen lateral -->
    <div class="flex flex-col gap-4 lg:flex-row">
      <div class="min-w-0 flex-1 rounded-lg border p-4">
        <div class="mb-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-ink-gray-6">
          <span class="font-medium text-ink-gray-7">{{ __('Trayectoria') }} · {{ metricLabel }} · {{ __('por canal') }}</span>
          <span v-for="ser in series" :key="ser.key" class="flex items-center gap-1.5">
            <span class="h-2.5 w-2.5 rounded-sm" :style="{ backgroundColor: ser.color }" />{{ ser.label }}
          </span>
          <span v-if="baseline" class="flex items-center gap-1.5">
            <span class="h-2.5 w-2.5 rounded-sm" style="background:#9AA0AB" />{{ __('Baseline 2025') }}
          </span>
        </div>
        <div v-html="chartSvg" @click="onChartClick" />
      </div>

      <!-- Resumen lateral -->
      <aside class="w-full shrink-0 rounded-lg border bg-surface-gray-1 p-4 lg:w-80">
        <div class="flex items-center justify-between">
          <div class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Resumen') }}</div>
          <div class="flex items-center gap-1">
            <button class="rounded border border-outline-gray-2 px-1.5 py-0.5 text-ink-gray-7 hover:bg-surface-gray-2 disabled:opacity-40" :disabled="year <= YEARS[0]" @click="stepYear(-1)">‹</button>
            <span class="min-w-[3rem] text-center text-sm font-semibold tabular-nums text-ink-gray-9">{{ year }}</span>
            <button class="rounded border border-outline-gray-2 px-1.5 py-0.5 text-ink-gray-7 hover:bg-surface-gray-2 disabled:opacity-40" :disabled="year >= YEARS[YEARS.length-1]" @click="stepYear(1)">›</button>
          </div>
        </div>
        <div class="mt-1 text-2xl font-semibold text-ink-gray-9 tabular-nums">{{ money(kpiTotal) }}</div>
        <div class="text-xs text-ink-gray-5">{{ metricLabel }} · {{ kpiQty }} {{ __('ventas') }}</div>

        <div class="mt-4 text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Por canal') }}</div>
        <div class="mt-2 flex flex-col gap-2">
          <div v-for="c in CANALES" :key="c" class="flex items-center gap-2 text-xs">
            <span class="w-28 shrink-0 text-ink-gray-6">{{ c }}</span>
            <span class="h-2 flex-1 overflow-hidden rounded bg-surface-gray-3">
              <span class="block h-full rounded" :style="{ width: barPct(canalTotal(c)) + '%', background: CANAL_COLOR[c] }" />
            </span>
            <span class="w-16 shrink-0 text-right tabular-nums text-ink-gray-8">{{ moneyK(canalTotal(c)) }}</span>
          </div>
        </div>

        <div class="mt-4 text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Baseline 2025 por canal') }}</div>
        <div class="mt-2 flex flex-col gap-1.5">
          <div v-for="c in CANALES" :key="c" class="flex items-center gap-2 text-xs">
            <span class="flex items-center gap-1.5 w-28 shrink-0 text-ink-gray-6"><span class="h-2.5 w-2.5 rounded-sm" :style="{ background: CANAL_COLOR[c] }" />{{ c }}</span>
            <input
              type="number" min="0" step="1000"
              class="w-28 flex-1 rounded border bg-surface-white px-2 py-1 text-right tabular-nums text-xs text-ink-gray-8"
              :value="baselineCanal[c] || 0"
              @change="(e) => setBaselineCanal(c, e.target.value)"
            />
          </div>
          <div class="text-[11px] text-ink-gray-4">{{ __('Se usa como columna 2025 en el gráfico.') }}</div>
        </div>
      </aside>
    </div>

    <!-- Tabla editable -->
    <div class="mt-4 rounded-lg border">
      <div class="flex items-center justify-between border-b px-4 py-2.5">
        <div class="text-sm font-semibold text-ink-gray-8">{{ __('Iniciativas de venta') }}</div>
        <Button variant="solid" size="sm" :label="__('Nueva iniciativa')" :loading="adding" @click="addRow">
          <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
        </Button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full min-w-[820px] text-[11px]">
          <thead>
            <tr class="border-b text-[10px] uppercase tracking-wide text-ink-gray-5">
              <th class="px-3 py-2 text-left">{{ __('Iniciativa') }}</th>
              <th class="px-2 py-2 text-left">{{ __('Canal') }}</th>
              <th class="px-2 py-2 text-right">{{ __('Ticket') }}</th>
              <th class="px-2 py-2 text-right">%DS</th>
              <th v-for="y in YEARS" :key="y" class="px-2 py-2 text-right">{{ y }}</th>
              <th class="px-3 py-2 text-right">{{ metricLabel }} {{ year }}</th>
              <th class="px-2 py-2"></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="c in CANALES" :key="c">
              <template v-if="grouped[c] && grouped[c].length">
                <tr class="bg-surface-gray-2"><td :colspan="6 + YEARS.length" class="px-3 py-1.5 text-xs font-semibold uppercase text-ink-gray-7">{{ c }}</td></tr>
                <template v-for="r in grouped[c]" :key="r.name">
                <tr class="border-b hover:bg-surface-gray-1">
                  <td class="px-3 py-1.5">
                    <input v-model="r.iniciativa" class="w-40 rounded border-none bg-transparent px-1 py-0.5 text-ink-gray-8 hover:bg-surface-gray-2 focus:bg-surface-white focus:ring-1 focus:ring-outline-gray-3" @change="setField(r,'iniciativa')" />
                  </td>
                  <td class="px-2 py-1.5">
                    <select v-model="r.canal" class="rounded border bg-surface-white px-1 py-1 text-xs" @change="setField(r,'canal')">
                      <option v-for="x in CANALES" :key="x" :value="x">{{ x }}</option>
                    </select>
                  </td>
                  <td class="px-2 py-1.5 text-right">
                    <input type="number" v-model.number="r.ticket_promedio" class="w-20 rounded border bg-surface-white px-1 py-1 text-right tabular-nums" @change="setField(r,'ticket_promedio')" />
                  </td>
                  <td class="px-2 py-1.5 text-right">
                    <input type="number" v-model.number="r.pct_ds" class="w-14 rounded border bg-surface-white px-1 py-1 text-right tabular-nums" @change="setField(r,'pct_ds')" />
                  </td>
                  <td v-for="y in YEARS" :key="y" class="px-2 py-1.5 text-right">
                    <input type="number" min="0" v-model.number="r['qty_'+y]" class="w-12 rounded border bg-surface-white px-1 py-1 text-right tabular-nums" @change="setField(r,'qty_'+y)" />
                  </td>
                  <td class="px-3 py-1.5 text-right font-medium tabular-nums text-ink-gray-8">{{ money(rowMetric(r, year)) }}</td>
                  <td class="px-2 py-1.5 text-right whitespace-nowrap">
                    <button class="mr-2 rounded border border-outline-gray-2 px-2 py-0.5 text-xs text-ink-gray-7 hover:bg-surface-gray-2" :class="expanded === r.name ? 'bg-surface-gray-3 text-ink-gray-9' : ''" @click="toggleCuentas(r)">
                      {{ __('Cuentas') }}<span v-if="cuentasCount[r.name]" class="ml-1 rounded-full bg-blue-100 px-1.5 text-[10px] font-semibold text-blue-700">{{ cuentasCount[r.name] }}</span>
                    </button>
                    <button class="text-ink-gray-4 hover:text-red-600" :title="__('Eliminar')" @click="delRow(r)">✕</button>
                  </td>
                </tr>
                <tr v-if="expanded === r.name" class="border-b bg-surface-gray-1">
                  <td :colspan="6 + YEARS.length" class="px-4 py-3">
                    <div class="text-xs font-semibold uppercase tracking-wide text-ink-gray-5">{{ __('Cuentas objetivo') }} — {{ r.iniciativa }}</div>
                    <div v-if="docCache[r.name]" class="mt-2 flex flex-col gap-1.5">
                      <div v-for="(c, ci) in (docCache[r.name].cuentas || [])" :key="ci" class="flex items-center gap-2 text-xs">
                        <span class="min-w-0 flex-1 truncate text-ink-gray-8">{{ c.organizacion }}</span>
                        <select v-model="c.estado" class="rounded border bg-surface-white px-1 py-1 text-xs" @change="saveDoc(r.name)">
                          <option>Objetivo</option><option>Contactado</option><option>Oportunidad</option><option>Ganado</option><option>Descartado</option>
                        </select>
                        <button class="text-ink-gray-4 hover:text-red-600" :title="__('Quitar')" @click="removeCuenta(r.name, ci)">✕</button>
                      </div>
                      <div v-if="!(docCache[r.name].cuentas || []).length" class="text-xs text-ink-gray-4">{{ __('Sin cuentas objetivo todavía.') }}</div>
                      <div class="mt-1 flex items-center gap-2">
                        <div class="w-72"><Link doctype="CRM Organization" :value="newOrg" @change="(v) => (newOrg = v)" /></div>
                        <Button variant="subtle" size="sm" :label="__('Agregar cuenta')" :disabled="!newOrg" @click="addCuenta(r.name)" />
                      </div>

                      <div class="mt-3 text-xs font-semibold uppercase tracking-wide text-ink-gray-5">{{ __('Industrias objetivo') }}</div>
                      <div class="mt-1.5 flex flex-wrap items-center gap-1.5">
                        <span v-for="(it, ii) in (docCache[r.name].industrias || [])" :key="ii" class="inline-flex items-center gap-1 rounded-full border border-outline-gray-2 bg-surface-white px-2 py-0.5 text-xs text-ink-gray-7">
                          {{ it.industria }}
                          <button class="text-ink-gray-4 hover:text-red-600" :title="__('Quitar')" @click="removeIndustria(r.name, ii)">✕</button>
                        </span>
                        <span v-if="!(docCache[r.name].industrias || []).length" class="text-xs text-ink-gray-4">{{ __('Sin industrias.') }}</span>
                      </div>
                      <div class="mt-1.5 flex items-center gap-2">
                        <div class="w-72"><Link :doctype="INDUSTRY_DT" :value="newIndustria" @change="(v) => (newIndustria = v)" /></div>
                        <Button variant="subtle" size="sm" :label="__('Agregar industria')" :disabled="!newIndustria" @click="addIndustria(r.name)" />
                      </div>
                    </div>
                    <div v-else class="mt-2 text-xs text-ink-gray-4">{{ __('Cargando...') }}</div>
                  </td>
                </tr>
                </template>
                <tr class="border-b border-dashed text-xs font-semibold text-ink-gray-6">
                  <td class="px-3 py-1.5" :colspan="5 + YEARS.length">{{ __('Subtotal') }} {{ c }}</td>
                  <td class="px-3 py-1.5 text-right tabular-nums">{{ money(canalTotal(c)) }}</td><td></td>
                </tr>
              </template>
            </template>
            <tr class="bg-surface-gray-2 font-semibold text-ink-gray-9">
              <td class="px-3 py-2" :colspan="5 + YEARS.length">{{ __('TOTAL PLAN') }} {{ year }} · {{ metricLabel }}</td>
              <td class="px-3 py-2 text-right tabular-nums">{{ money(kpiTotal) }}</td><td></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p class="mt-3 text-xs text-ink-gray-4">
      {{ __('Ingresos = Ticket × Cantidad; DS = Ingresos × %DS; Solaer = el resto. Datos en el DocType «Iniciativa de Venta» (solo administradores).') }}
    </p>
  </div>
</template>

<script setup>
import { Button, FeatherIcon, call, toast } from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'
import { usersStore } from '@/stores/users'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'
import PlanIcon from '~icons/lucide/target'
import LockIcon from '~icons/lucide/lock'

const { isAdmin } = usersStore()
const isAdminUser = computed(() => { try { return !!isAdmin() } catch (e) { return false } })

const YEARS = [2026, 2027, 2028, 2029, 2030]
const CANALES = ['DASSAULT', 'GEOVIA', 'SOLIDWORKS CHILE', 'SOLIDWORKS ARG']
const CANAL_COLOR = { DASSAULT: '#2563EB', GEOVIA: '#B08968', 'SOLIDWORKS CHILE': '#DC2626', 'SOLIDWORKS ARG': '#F59E0B' }
const METRICS = [{ key: 'ing', label: 'Ingresos' }, { key: 'ds', label: 'DS' }, { key: 'sol', label: 'Solaer' }]
const SCENARIOS = [
  { key: 'pes', label: 'Pesimista', hint: '−25% sobre el plan base', f: 0.75 },
  { key: 'base', label: 'Base', hint: 'Plan base', f: 1 },
  { key: 'opt', label: 'Optimista', hint: '+25% sobre el plan base', f: 1.25 },
]
const DT = 'Iniciativa de Venta'
const FIELDS = ['name', 'iniciativa', 'canal', 'ticket_promedio', 'pct_ds',
  'qty_2026', 'qty_2027', 'qty_2028', 'qty_2029', 'qty_2030']

const rows = ref([])
const metric = ref('ing')
const scenario = ref('base')
const year = ref(2030)
const fCanal = ref('')
const scenFactor = computed(() => (SCENARIOS.find(s => s.key === scenario.value) || { f: 1 }).f)
const adding = ref(false)
const baseline = ref(null)
const baselineCanal = ref({})
const expanded = ref(null)
const docCache = ref({})
const cuentasCount = ref({})
const newOrg = ref('')
const newIndustria = ref('')
const INDUSTRY_DT = 'CRM Industry'

const money = n => '$' + Math.round(n || 0).toLocaleString('en-US')
const moneyK = n => { n = Math.round(n || 0); return Math.abs(n) >= 1000 ? '$' + Math.round(n / 1000).toLocaleString('en-US') + 'k' : '$' + n }
const metricLabel = computed(() => ({ ing: 'Ingresos', ds: 'DS Revenue', sol: 'Solaer Revenue' }[metric.value]))

function factor(r) {
  if (metric.value === 'ds') return (r.pct_ds || 0) / 100
  if (metric.value === 'sol') return (100 - (r.pct_ds || 0)) / 100
  return 1
}
const rowMetric = (r, y) => (r.ticket_promedio || 0) * (r['qty_' + y] || 0) * factor(r) * scenFactor.value

// Series del gráfico: por canal
const series = computed(() => CANALES.map(c => ({ key: c, label: c, color: CANAL_COLOR[c] })))
function seriesVal(key, y) {
  return (grouped.value[key] || []).reduce((a, r) => a + rowMetric(r, y), 0)
}

const filtered = computed(() => rows.value.filter(r => !fCanal.value || r.canal === fCanal.value))
const grouped = computed(() => {
  const g = {}; CANALES.forEach(c => g[c] = []); filtered.value.forEach(r => (g[r.canal] || (g[r.canal] = [])).push(r)); return g
})
const canalTotal = c => (grouped.value[c] || []).reduce((a, r) => a + rowMetric(r, year.value), 0)
const kpiTotal = computed(() => filtered.value.reduce((a, r) => a + rowMetric(r, year.value), 0))
const kpiQty = computed(() => filtered.value.reduce((a, r) => a + (r['qty_' + year.value] || 0), 0))
const kpiTicket = computed(() => kpiQty.value ? kpiTotal.value / kpiQty.value : 0)
const kpi5y = computed(() => filtered.value.reduce((a, r) => a + YEARS.reduce((s, y) => s + rowMetric(r, y), 0), 0))
const pipeline = computed(() => kpiTotal.value * 3.5)
const baselineMetric = computed(() => !baseline.value ? 0 : metric.value === 'ds' ? baseline.value.ds : metric.value === 'sol' ? baseline.value.solaer : baseline.value.total)
const growthVsBase = computed(() => {
  const b = baselineMetric.value
  if (!b) return '—'
  const g = kpiTotal.value / b - 1
  return (g >= 0 ? '▲ ' : '▼ ') + Math.abs(g * 100).toFixed(0) + '% vs 2025'
})
const maxCanal = computed(() => Math.max(1, ...CANALES.map(c => canalTotal(c))))
const barPct = v => (v / maxCanal.value) * 100
function stepYear(d) { const i = YEARS.indexOf(year.value) + d; if (i >= 0 && i < YEARS.length) year.value = YEARS[i] }
function onChartClick(e) { const t = e.target.closest && e.target.closest('[data-y]'); if (t) { const y = +t.getAttribute('data-y'); if (YEARS.includes(y)) year.value = y } }

const chartSvg = computed(() => {
  const W = 620, H = 320, padL = 52, padR = 12, padT = 22, padB = 30
  const plotW = W - padL - padR, plotH = H - padT - padB
  const ser = series.value
  const cols = YEARS.map(y => {
    const seg = {}; let tot = 0
    ser.forEach(s => { const v = seriesVal(s.key, y); seg[s.key] = v; tot += v })
    return { y, seg, tot }
  })
  let baseCol = null
  const bseg = {}; let btot = 0
  CANALES.forEach(c => { const v = +(baselineCanal.value[c] || 0); if (v > 0) { bseg[c] = v; btot += v } })
  if (btot > 0) baseCol = { y: 2025, seg: bseg, tot: btot }
  else if (baseline.value) baseCol = { y: baseline.value.year, tot: baselineMetric.value, base: true }
  const all = baseCol ? [baseCol, ...cols] : cols
  const max = Math.max(1, ...all.map(c => c.tot))
  const n = all.length, gap = plotW / n, bw = Math.min(64, gap * 0.6)
  const yv = v => padT + plotH - (v / max) * plotH
  let g = ''
  for (let i = 0; i <= 4; i++) { const v = max * i / 4, y = yv(v); g += `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W - padR}" y2="${y.toFixed(1)}" stroke="#e5e6e2"/><text x="${padL - 8}" y="${(y + 3).toFixed(1)}" text-anchor="end" font-size="8" fill="#8a909c">${moneyK(v)}</text>` }
  let bars = ''
  all.forEach((c, ci) => {
    const cx = padL + gap * ci + gap / 2, x = cx - bw / 2
    const colX = padL + gap * ci
    if (!c.base && c.y === year.value) bars += `<rect x="${colX.toFixed(1)}" y="${padT}" width="${gap.toFixed(1)}" height="${plotH}" fill="#2563EB" opacity="0.07" rx="4"/>`
    if (c.base) {
      const h = (c.tot / max) * plotH; bars += `<rect x="${x.toFixed(1)}" y="${yv(c.tot).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(0, h).toFixed(1)}" rx="4" fill="#9AA0AB" opacity=".7"/>`
    } else {
      let acc = 0
      ser.forEach(s => {
        const v = c.seg[s.key]; if (v <= 0) return
        const h = (v / max) * plotH; acc += v
        const yTop = yv(acc)
        bars += `<rect x="${x.toFixed(1)}" y="${yTop.toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(0, h - 1).toFixed(1)}" rx="3" fill="${s.color}"/>`
        if (h >= 11 && c.tot > 0) bars += `<text x="${cx.toFixed(1)}" y="${(yTop + h / 2 + 2.5).toFixed(1)}" text-anchor="middle" font-size="7" font-weight="600" fill="#ffffff">${Math.round(v / c.tot * 100)}%</text>`
      })
    }
    if (c.tot > 0) bars += `<text x="${cx.toFixed(1)}" y="${(yv(c.tot) - 5).toFixed(1)}" text-anchor="middle" font-size="8" font-weight="600" fill="#181a1f">${moneyK(c.tot)}</text>`
    bars += `<text x="${cx.toFixed(1)}" y="${H - padB + 15}" text-anchor="middle" font-size="9" fill="${c.base ? '#8a909c' : '#5b616e'}">${c.base ? 'Real ' + c.y : c.y}</text>`
    if (!c.base) bars += `<rect data-y="${c.y}" x="${colX.toFixed(1)}" y="${padT}" width="${gap.toFixed(1)}" height="${plotH}" fill="transparent" style="cursor:pointer"><title>${c.y}</title></rect>`
  })
  return `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto" role="img">${g}${bars}</svg>`
})

async function load() {
  if (!isAdminUser.value) return
  try {
    const data = await call('frappe.client.get_list', { doctype: DT, fields: FIELDS, limit_page_length: 0, order_by: 'canal asc, iniciativa asc' })
    rows.value = (data || []).map(d => ({ ...d }))
  } catch (e) { toast.error(__('No se pudieron cargar las iniciativas')) }
}
async function setField(r, f) {
  try { await call('frappe.client.set_value', { doctype: DT, name: r.name, fieldname: f, value: r[f] }) }
  catch (e) { toast.error(__('No se pudo guardar')) }
}
async function addRow() {
  adding.value = true
  try {
    const doc = await call('frappe.client.insert', { doc: { doctype: DT, iniciativa: 'Nueva iniciativa', canal: 'DASSAULT', ticket_promedio: 10000, pct_ds: 65, qty_2026: 0, qty_2027: 0, qty_2028: 0, qty_2029: 0, qty_2030: 0 } })
    rows.value.push({ ...doc })
  } catch (e) { toast.error(__('No se pudo crear')) } finally { adding.value = false }
}
async function delRow(r) {
  if (!confirm(__('¿Eliminar «{0}»?').replace('{0}', r.iniciativa))) return
  try { await call('frappe.client.delete', { doctype: DT, name: r.name }); rows.value = rows.value.filter(x => x.name !== r.name) }
  catch (e) { toast.error(__('No se pudo eliminar')) }
}
async function loadBaseline2025() {
  try { baseline.value = (await call('plan_baseline_real', { year: 2025 })) || null }
  catch (e) { /* baseline opcional */ }
}
async function loadAjustes() {
  try {
    const doc = await call('frappe.client.get', { doctype: 'Plan Ventas Ajustes', name: 'Plan Ventas Ajustes' })
    baselineCanal.value = doc && doc.baseline_contratos ? JSON.parse(doc.baseline_contratos) : {}
  } catch (e) { baselineCanal.value = {} }
}
async function saveBaselineCanal() {
  try { await call('frappe.client.set_value', { doctype: 'Plan Ventas Ajustes', name: 'Plan Ventas Ajustes', fieldname: 'baseline_contratos', value: JSON.stringify(baselineCanal.value) }) }
  catch (e) { toast.error(__('No se pudo guardar el baseline por canal')) }
}
function setBaselineCanal(c, v) {
  baselineCanal.value = { ...baselineCanal.value, [c]: +v || 0 }
  saveBaselineCanal()
}
async function loadCounts() {
  try {
    const kids = await call('frappe.client.get_list', { doctype: 'Iniciativa Cuenta Objetivo', fields: ['parent'], filters: { parenttype: DT }, limit_page_length: 0 })
    const m = {}; (kids || []).forEach(k => { m[k.parent] = (m[k.parent] || 0) + 1 }); cuentasCount.value = m
  } catch (e) { /* opcional */ }
}
async function toggleCuentas(r) {
  if (expanded.value === r.name) { expanded.value = null; return }
  newOrg.value = ''; newIndustria.value = ''
  expanded.value = r.name
  if (!docCache.value[r.name]) {
    try { const doc = await call('frappe.client.get', { doctype: DT, name: r.name }); docCache.value = { ...docCache.value, [r.name]: doc } }
    catch (e) { toast.error(__('No se pudo cargar la iniciativa')) }
  }
}
async function saveDoc(name) {
  try {
    const doc = await call('frappe.client.save', { doc: docCache.value[name] })
    docCache.value = { ...docCache.value, [name]: doc }
    cuentasCount.value = { ...cuentasCount.value, [name]: (doc.cuentas || []).length }
  } catch (e) { toast.error(__('No se pudo guardar')) }
}
function addCuenta(name) {
  const d = docCache.value[name]; if (!d || !newOrg.value) return
  if (!d.cuentas) d.cuentas = []
  if (!d.cuentas.some(c => c.organizacion === newOrg.value)) d.cuentas.push({ organizacion: newOrg.value, estado: 'Objetivo' })
  newOrg.value = ''; saveDoc(name)
}
function removeCuenta(name, idx) { const d = docCache.value[name]; if (d && d.cuentas) { d.cuentas.splice(idx, 1); saveDoc(name) } }
function addIndustria(name) {
  const d = docCache.value[name]; if (!d || !newIndustria.value) return
  if (!d.industrias) d.industrias = []
  if (!d.industrias.some(x => x.industria === newIndustria.value)) d.industrias.push({ industria: newIndustria.value })
  newIndustria.value = ''; saveDoc(name)
}
function removeIndustria(name, idx) { const d = docCache.value[name]; if (d && d.industrias) { d.industrias.splice(idx, 1); saveDoc(name) } }

onMounted(async () => { await load(); loadBaseline2025(); loadCounts(); loadAjustes() })
</script>
