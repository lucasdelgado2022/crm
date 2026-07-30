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
          {{ money(yearTotal / 12) }}
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
          class="group flex h-full flex-1 flex-col items-center justify-end"
        >
          <div
            class="mb-1 text-xs font-medium text-ink-gray-7 opacity-0 transition group-hover:opacity-100"
          >
            {{ m.total ? moneyShort(m.total) : '' }}
          </div>
          <div
            class="w-full rounded-t bg-blue-500 transition-all hover:bg-blue-600"
            :style="{ height: barHeight(m.total) }"
            :title="MONTHS[i] + ': ' + money(m.total) + ' (' + m.count + ')'"
          />
          <div class="mt-1.5 text-xs text-ink-gray-5">{{ MONTHS[i] }}</div>
        </div>
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

defineProps({
  embedded: { type: Boolean, default: false },
})

const MONTHS = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
const MONTHS_FULL = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

const amountOptions = [
  { key: 'custom_solaer_revenue', label: 'Solaer Revenue' },
  { key: 'custom_ds_revenue', label: 'DS Revenue' },
  { key: 'annual_revenue', label: 'Valor de Oportunidad' },
]
const amount = ref('custom_solaer_revenue')
const onlyWon = ref(false)
const year = ref(new Date().getFullYear())

const dealsRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Deal',
    fields: [
      'expected_closure_date',
      'status',
      'annual_revenue',
      'custom_ds_revenue',
      'custom_solaer_revenue',
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

const monthly = computed(() => {
  const arr = Array.from({ length: 12 }, () => ({ total: 0, count: 0, won: 0 }))
  for (const d of deals.value) {
    if (!d.expected_closure_date) continue
    if (Number(d.expected_closure_date.slice(0, 4)) !== year.value) continue
    const isWon = d.status === 'Won'
    if (onlyWon.value && !isWon) continue
    const mi = Number(d.expected_closure_date.slice(5, 7)) - 1
    if (mi < 0 || mi > 11) continue
    const val = Number(d[amount.value]) || 0
    arr[mi].total += val
    arr[mi].count += 1
    if (isWon) arr[mi].won += 1
  }
  return arr
})

const yearTotal = computed(() => monthly.value.reduce((a, m) => a + m.total, 0))
const yearCount = computed(() => monthly.value.reduce((a, m) => a + m.count, 0))
const yearWon = computed(() => monthly.value.reduce((a, m) => a + m.won, 0))
const maxMonth = computed(() =>
  Math.max(1, ...monthly.value.map((m) => m.total)),
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
