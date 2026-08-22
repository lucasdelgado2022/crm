<template>
  <LayoutHeader v-if="!embedded">
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <ChartIcon class="h-5 w-5" />
        {{ __('Ventas por Mes') }}
      </div>
    </template>
    <template #right-header>
      <div class="flex items-center gap-3">
        <!-- Solo ganadas -->
        <label
          class="flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7"
        >
          <input v-model="onlyWon" type="checkbox" class="rounded" />
          {{ __('Solo ganadas') }}
        </label>
        <!-- Incluir sin fecha de cierre -->
        <label
          class="flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7"
        >
          <input v-model="includeNoDate" type="checkbox" class="rounded" />
          {{ __('Sin fecha') }}
        </label>
        <!-- Tipo: venta / renovación -->
        <select
          v-model="tipoFilter"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="">{{ __('Venta y Renovación') }}</option>
          <option value="venta">{{ __('Solo Venta') }}</option>
          <option value="renovacion">{{ __('Solo Renovación') }}</option>
        </select>
        <!-- Año -->
        <select
          v-model.number="year"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </template>
  </LayoutHeader>

  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Selector de monto -->
    <div class="mb-4 flex flex-wrap items-center gap-2">
      <span class="text-sm text-ink-gray-5">{{ __('Monto') }}:</span>
      <div class="flex rounded-lg border border-outline-gray-2 p-0.5">
        <button
          v-for="opt in amountOptions"
          :key="opt.key"
          class="rounded-md px-3 py-1 text-sm font-medium transition"
          :class="
            amount === opt.key
              ? 'bg-surface-gray-3 text-ink-gray-9'
              : 'text-ink-gray-6 hover:text-ink-gray-9'
          "
          @click="amount = opt.key"
        >
          {{ opt.label }}
        </button>
      </div>
      <!-- Controles año/solo-ganadas cuando está embebido en Dashboard -->
      <template v-if="embedded">
        <label
          class="ml-auto flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7"
        >
          <input v-model="onlyWon" type="checkbox" class="rounded" />
          {{ __('Solo ganadas') }}
        </label>
        <label
          class="flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7"
        >
          <input v-model="includeNoDate" type="checkbox" class="rounded" />
          {{ __('Sin fecha') }}
        </label>
        <select
          v-model="tipoFilter"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="">{{ __('Venta y Renovación') }}</option>
          <option value="venta">{{ __('Solo Venta') }}</option>
          <option value="renovacion">{{ __('Solo Renovación') }}</option>
        </select>
        <select
          v-model.number="year"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </template>
    </div>

    <!-- Totales -->
    <div class="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Total') }} {{ year }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">
          {{ money(yearTotal) }}
        </div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Oportunidades') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">
          {{ yearCount }}
        </div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Promedio mensual') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">
          {{ money(monthlyTotal / 12) }}
        </div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Mejor mes') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">
          {{ bestMonth.total ? MONTHS[bestMonth.idx] : '—' }}
        </div>
      </div>
    </div>

    <!-- Gráfico de barras -->
    <div class="rounded-lg border p-4">
      <div class="mb-3 flex items-center gap-4 text-xs text-ink-gray-6">
        <span class="flex items-center gap-1.5">
          <span class="h-2.5 w-2.5 rounded-sm bg-green-500" />
          {{ __('Ganadas') }}
        </span>
        <span class="flex items-center gap-1.5">
          <span class="h-2.5 w-2.5 rounded-sm bg-violet-500" />
          {{ __('Proyectadas') }}
        </span>
      </div>
      <div
        v-if="loading"
        class="flex h-64 items-center justify-center text-ink-gray-4"
      >
        {{ __('Cargando...') }}
      </div>
      <div
        v-else-if="!yearTotal"
        class="flex h-64 flex-col items-center justify-center gap-2 text-ink-gray-4"
      >
        <ChartIcon class="h-8 w-8" />
        <span>{{ __('Sin datos para') }} {{ year }}</span>
      </div>
      <div v-else class="flex h-72 items-end gap-2 sm:gap-3">
        <div
          v-for="(m, i) in monthly"
          :key="i"
          class="group flex h-full flex-1 cursor-pointer flex-col items-center justify-end"
          @click="selectBucket(i)"
        >
          <div
            class="mb-1 whitespace-nowrap text-[10px] font-semibold text-ink-gray-7 sm:text-xs"
          >
            {{ m.total ? moneyShort(m.total) : '' }}
          </div>
          <div
            class="w-full overflow-hidden rounded-t transition-all"
            :class="selected === i ? 'ring-2 ring-ink-gray-4' : ''"
            :style="{ height: barHeight(m.total) }"
            :title="
              MONTHS[i] +
              ': ' +
              money(m.total) +
              ' — Ganadas ' +
              money(m.wonAmt) +
              ' / Proyectadas ' +
              money(m.projAmt)
            "
          >
            <div
              class="w-full bg-violet-500 transition-all hover:bg-violet-600"
              :style="{ height: segPct(m.projAmt, m.total) + '%' }"
            />
            <div
              class="w-full bg-green-500 transition-all hover:bg-green-600"
              :style="{ height: segPct(m.wonAmt, m.total) + '%' }"
            />
          </div>
          <div
            class="mt-1.5 text-xs"
            :class="selected === i ? 'font-semibold text-ink-gray-8' : 'text-ink-gray-5'"
          >
            {{ MONTHS[i] }}
          </div>
        </div>
        <!-- Barra: oportunidades sin fecha de cierre -->
        <div
          v-if="showNoDate"
          class="group flex h-full flex-1 cursor-pointer flex-col items-center justify-end"
          @click="selectBucket('nodate')"
        >
          <div
            class="mb-1 whitespace-nowrap text-[10px] font-semibold text-ink-gray-7 sm:text-xs"
          >
            {{ noDate.total ? moneyShort(noDate.total) : '' }}
          </div>
          <div
            class="w-full overflow-hidden rounded-t transition-all"
            :class="selected === 'nodate' ? 'ring-2 ring-ink-gray-4' : ''"
            :style="{ height: barHeight(noDate.total) }"
            :title="
              'Sin fecha: ' +
              money(noDate.total) +
              ' — Ganadas ' +
              money(noDate.wonAmt) +
              ' / Proyectadas ' +
              money(noDate.projAmt)
            "
          >
            <div
              class="w-full bg-violet-500 transition-all hover:bg-violet-600"
              :style="{ height: segPct(noDate.projAmt, noDate.total) + '%' }"
            />
            <div
              class="w-full bg-green-500 transition-all hover:bg-green-600"
              :style="{ height: segPct(noDate.wonAmt, noDate.total) + '%' }"
            />
          </div>
          <div
            class="mt-1.5 text-xs"
            :class="
              selected === 'nodate'
                ? 'font-semibold text-ink-gray-8'
                : 'text-ink-gray-5'
            "
          >
            {{ __('Sin fecha') }}
          </div>
        </div>
      </div>
    </div>

    <!-- Lista de oportunidades del bucket seleccionado -->
    <div v-if="selected !== null" class="mt-5 rounded-lg border">
      <div class="flex items-center justify-between border-b px-4 py-3">
        <div class="text-sm font-semibold text-ink-gray-8">
          {{ __('Oportunidades') }}: {{ selectedLabel }}
          <span class="font-normal text-ink-gray-5"
            >({{ selectedDeals.length }})</span
          >
        </div>
        <button
          class="text-sm text-ink-gray-5 hover:text-ink-gray-8"
          @click="selected = null"
        >
          {{ __('Cerrar') }}
        </button>
      </div>
      <div v-if="selectedDeals.length" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
            <tr>
              <th class="px-4 py-2 text-left font-medium">
                {{ __('Organización') }}
              </th>
              <th class="px-4 py-2 text-left font-medium">{{ __('Tipo') }}</th>
              <th class="px-4 py-2 text-left font-medium">{{ __('Estado') }}</th>
              <th class="px-4 py-2 text-right font-medium">{{ __('Monto') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="d in selectedDeals"
              :key="d.name"
              class="cursor-pointer border-b last:border-0 hover:bg-surface-gray-1"
              @click="openDeal(d.name)"
            >
              <td class="px-4 py-2 text-ink-gray-8">
                {{ d.organization || d.name }}
              </td>
              <td class="px-4 py-2 text-ink-gray-6">
                {{ d.custom_tipo_oportunidad || '—' }}
              </td>
              <td class="px-4 py-2">
                <span
                  :class="
                    d.status === 'Won' ? 'text-green-700' : 'text-ink-gray-6'
                  "
                  >{{ d.status || '—' }}</span
                >
              </td>
              <td class="px-4 py-2 text-right font-medium text-ink-gray-9">
                {{ money(Number(d[amount]) || 0) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="px-4 py-6 text-center text-sm text-ink-gray-4">
        {{ __('Sin oportunidades') }}
      </div>
    </div>

    <!-- Tabla -->
    <div class="mt-5 overflow-x-auto rounded-lg border">
      <table class="w-full text-sm">
        <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
          <tr>
            <th class="px-4 py-2 text-left font-medium">{{ __('Mes') }}</th>
            <th class="px-4 py-2 text-right font-medium">{{ __('Oportunidades') }}</th>
            <th class="px-4 py-2 text-right font-medium">{{ __('Ganadas') }}</th>
            <th class="px-4 py-2 text-right font-medium">{{ __('Monto') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(m, i) in monthly"
            :key="i"
            class="border-b last:border-0 hover:bg-surface-gray-1"
          >
            <td class="px-4 py-2 text-ink-gray-8">{{ MONTHS_FULL[i] }}</td>
            <td class="px-4 py-2 text-right text-ink-gray-7">{{ m.count }}</td>
            <td class="px-4 py-2 text-right text-green-700">{{ m.won }}</td>
            <td class="px-4 py-2 text-right font-medium text-ink-gray-9">
              {{ m.total ? money(m.total) : '—' }}
            </td>
          </tr>
          <tr
            v-if="showNoDate"
            class="border-b last:border-0 hover:bg-surface-gray-1"
          >
            <td class="px-4 py-2 text-ink-gray-8">
              {{ __('Sin fecha de cierre') }}
            </td>
            <td class="px-4 py-2 text-right text-ink-gray-7">
              {{ noDate.count }}
            </td>
            <td class="px-4 py-2 text-right text-green-700">{{ noDate.won }}</td>
            <td class="px-4 py-2 text-right font-medium text-ink-gray-9">
              {{ noDate.total ? money(noDate.total) : '—' }}
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="border-t bg-surface-gray-1 font-semibold">
            <td class="px-4 py-2 text-ink-gray-9">{{ __('Total') }}</td>
            <td class="px-4 py-2 text-right text-ink-gray-9">{{ yearCount }}</td>
            <td class="px-4 py-2 text-right text-green-700">{{ yearWon }}</td>
            <td class="px-4 py-2 text-right text-ink-gray-9">{{ money(yearTotal) }}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ChartIcon from '~icons/lucide/bar-chart-3'
import { createResource } from 'frappe-ui'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

defineProps({
  embedded: { type: Boolean, default: false },
})

const MONTHS = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
const MONTHS_FULL = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

const amountOptions = [
  { key: 'custom_solaer_revenue', label: 'Solaer Revenue' },
  { key: 'custom_ds_revenue', label: 'DS Revenue' },
  { key: 'deal_value', label: 'Valor de Oportunidad' },
]
const amount = ref('custom_solaer_revenue')
const onlyWon = ref(false)
const year = ref(new Date().getFullYear())
// '' = todos, 'venta' = Nuevo:*, 'renovacion' = Renovación:*
const tipoFilter = ref('')
// incluir oportunidades sin fecha de cierre en un bucket "Sin fecha"
const includeNoDate = ref(true)

// pasa los filtros de "solo ganadas" y tipo (venta/renovación)
function passesFilters(d) {
  if (onlyWon.value && d.status !== 'Won') return false
  const t = d.custom_tipo_oportunidad || ''
  if (tipoFilter.value === 'venta' && !t.startsWith('Nuevo')) return false
  if (tipoFilter.value === 'renovacion' && !t.startsWith('Renov')) return false
  return true
}

const dealsRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Deal',
    fields: [
      'expected_closure_date',
      'status',
      'deal_value',
      'custom_ds_revenue',
      'custom_solaer_revenue',
      'custom_tipo_oportunidad',
      'name',
      'organization',
    ],
    limit_page_length: 0,
  },
  auto: true,
})
const deals = computed(() => dealsRes.data || [])
const loading = computed(() => dealsRes.loading)

const years = computed(() => {
  const s = new Set()
  for (const d of deals.value) {
    if (d.expected_closure_date) s.add(Number(d.expected_closure_date.slice(0, 4)))
  }
  s.add(new Date().getFullYear())
  return [...s].sort((a, b) => b - a)
})

// wonAmt = monto de ganadas (verde) | projAmt = monto del resto/proyectadas (violeta)
const monthly = computed(() => {
  const arr = Array.from({ length: 12 }, () => ({
    total: 0,
    count: 0,
    won: 0,
    wonAmt: 0,
    projAmt: 0,
  }))
  for (const d of deals.value) {
    if (!d.expected_closure_date) continue
    if (Number(d.expected_closure_date.slice(0, 4)) !== year.value) continue
    if (!passesFilters(d)) continue
    const mi = Number(d.expected_closure_date.slice(5, 7)) - 1
    if (mi < 0 || mi > 11) continue
    const val = Number(d[amount.value]) || 0
    arr[mi].total += val
    arr[mi].count += 1
    if (d.status === 'Won') {
      arr[mi].won += 1
      arr[mi].wonAmt += val
    } else {
      arr[mi].projAmt += val
    }
  }
  return arr
})

// Oportunidades SIN fecha de cierre (no caen en ningún mes/año)
const noDate = computed(() => {
  const b = { total: 0, count: 0, won: 0, wonAmt: 0, projAmt: 0 }
  if (!includeNoDate.value) return b
  for (const d of deals.value) {
    if (d.expected_closure_date) continue
    if (!passesFilters(d)) continue
    const val = Number(d[amount.value]) || 0
    b.total += val
    b.count += 1
    if (d.status === 'Won') {
      b.won += 1
      b.wonAmt += val
    } else {
      b.projAmt += val
    }
  }
  return b
})

// % de cada segmento dentro de la barra
function segPct(part, total) {
  if (!total) return 0
  return (part / total) * 100
}
const showNoDate = computed(() => includeNoDate.value && noDate.value.count > 0)

// Selección de barra -> lista de oportunidades que la componen
// null | 0..11 (índice de mes) | 'nodate'
const selected = ref(null)
function selectBucket(key) {
  selected.value = selected.value === key ? null : key
}
const selectedLabel = computed(() => {
  if (selected.value === null) return ''
  if (selected.value === 'nodate') return 'Sin fecha de cierre'
  return (MONTHS_FULL[selected.value] || '') + ' ' + year.value
})
const selectedDeals = computed(() => {
  if (selected.value === null) return []
  const out = []
  for (const d of deals.value) {
    if (!passesFilters(d)) continue
    if (selected.value === 'nodate') {
      if (d.expected_closure_date) continue
    } else {
      if (!d.expected_closure_date) continue
      if (Number(d.expected_closure_date.slice(0, 4)) !== year.value) continue
      if (Number(d.expected_closure_date.slice(5, 7)) - 1 !== selected.value)
        continue
    }
    out.push(d)
  }
  return out.sort(
    (a, b) => (Number(b[amount.value]) || 0) - (Number(a[amount.value]) || 0),
  )
})
function openDeal(name) {
  router.push({ name: 'Deal', params: { dealId: name } })
}

const monthlyTotal = computed(() =>
  monthly.value.reduce((a, m) => a + m.total, 0),
)
const yearTotal = computed(() => monthlyTotal.value + noDate.value.total)
const yearCount = computed(
  () => monthly.value.reduce((a, m) => a + m.count, 0) + noDate.value.count,
)
const yearWon = computed(
  () => monthly.value.reduce((a, m) => a + m.won, 0) + noDate.value.won,
)
const maxMonth = computed(() =>
  Math.max(1, ...monthly.value.map((m) => m.total), noDate.value.total),
)
const bestMonth = computed(() => {
  let idx = -1
  let total = 0
  monthly.value.forEach((m, i) => {
    if (m.total > total) {
      total = m.total
      idx = i
    }
  })
  return { idx, total }
})

function barHeight(v) {
  const pct = (v / maxMonth.value) * 100
  return (v > 0 ? Math.max(2, pct) : 0) + '%'
}
function money(n) {
  const v = Number(n) || 0
  return '$' + Math.round(v).toLocaleString('es-AR')
}
function moneyShort(n) {
  const v = Number(n) || 0
  if (v >= 1000000) return '$' + (v / 1000000).toFixed(1) + 'M'
  if (v >= 1000) return '$' + Math.round(v / 1000) + 'k'
  return '$' + Math.round(v)
}
</script>
