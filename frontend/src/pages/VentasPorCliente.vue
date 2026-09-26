<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <LucideBuilding2 class="h-5 w-5" />
        {{ __('Ventas por Cliente') }}
      </div>
    </template>
  </LayoutHeader>

  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Filtros -->
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
      <select
        v-model="clientFilter"
        class="h-8 max-w-64 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
      >
        <option value="">{{ __('Todos los clientes') }}</option>
        <option v-for="c in clientNames" :key="c" :value="c">{{ c }}</option>
      </select>
      <FormControl class="w-56" type="text" :placeholder="__('Buscar cliente...')" v-model="search" />
    </div>

    <!-- KPIs -->
    <div class="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
      <div class="rounded-lg border p-4">
        <div class="text-xs text-ink-gray-5">{{ __('Total') }} {{ metricLabel }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">{{ money(grandTotal) }}</div>
      </div>
      <div class="rounded-lg border p-4">
        <div class="text-xs text-ink-gray-5">{{ __('Clientes') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">{{ clientRows.length }}</div>
      </div>
      <div class="rounded-lg border p-4">
        <div class="text-xs text-ink-gray-5">{{ __('Oportunidades ganadas') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">{{ filteredDeals.length }}</div>
      </div>
    </div>

    <!-- Gráfico de barras por año -->
    <div class="mb-5 rounded-lg border p-4">
      <div class="mb-3 text-base font-semibold text-ink-gray-8">
        {{ __('Ventas por año') }}
        <span v-if="clientFilter" class="text-sm font-normal text-ink-gray-5">· {{ clientFilter }}</span>
      </div>
      <div v-if="byYear.length" class="flex items-end gap-3" style="height: 240px">
        <div v-for="b in byYear" :key="b.year" class="flex flex-1 flex-col items-center justify-end gap-1">
          <div class="text-xs font-medium text-ink-gray-7">{{ b.amount ? moneyShort(b.amount) : '' }}</div>
          <div
            class="w-full rounded-t bg-blue-500 transition-all"
            :style="{ height: barHeight(b.amount) }"
            :title="b.year + ': ' + money(b.amount)"
          ></div>
          <div class="text-xs text-ink-gray-6">{{ b.year }}</div>
        </div>
      </div>
      <div v-else class="py-8 text-center text-sm text-ink-gray-4">{{ __('Sin datos') }}</div>
    </div>

    <!-- Tabla de clientes -->
    <div class="overflow-x-auto rounded-lg border">
      <table class="w-full text-sm">
        <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
          <tr>
            <th class="px-4 py-2 text-left font-medium">{{ __('Cliente') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('Oportunidades') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ metricLabel }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="c in clientRows"
            :key="c.name"
            class="cursor-pointer border-b last:border-0 hover:bg-surface-gray-1"
            :class="clientFilter === c.name ? 'bg-surface-blue-1' : ''"
            @click="clientFilter = clientFilter === c.name ? '' : c.name"
          >
            <td class="px-4 py-2 font-medium text-ink-gray-8">{{ c.name }}</td>
            <td class="px-3 py-2 text-right text-ink-gray-7">{{ c.count }}</td>
            <td class="px-3 py-2 text-right font-medium text-ink-gray-9">{{ money(c.total) }}</td>
          </tr>
          <tr v-if="!clientRows.length">
            <td colspan="3" class="px-4 py-6 text-center text-sm text-ink-gray-4">{{ __('Sin datos') }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideBuilding2 from '~icons/lucide/building-2'
import { FormControl, call, usePageMeta } from 'frappe-ui'
import { ref, computed } from 'vue'

const amountOptions = [
  { key: 'custom_solaer_revenue', label: 'Solaer Revenue' },
  { key: 'custom_ds_revenue', label: 'DS Revenue' },
  { key: 'deal_value', label: 'Valor de Oportunidad' },
]
const amount = ref('custom_solaer_revenue')
const metricLabel = computed(
  () => amountOptions.find((o) => o.key === amount.value)?.label || '',
)

const clientFilter = ref('')
const search = ref('')
const deals = ref([])

async function load() {
  try {
    const st = await call('frappe.client.get_list', {
      doctype: 'CRM Deal Status',
      filters: { type: 'Won' },
      fields: ['name'],
      limit_page_length: 0,
    })
    const wons = st.map((s) => s.name)
    deals.value = await call('frappe.client.get_list', {
      doctype: 'CRM Deal',
      filters: { status: ['in', wons] },
      fields: [
        'name',
        'organization',
        'closed_date',
        'custom_solaer_revenue',
        'custom_ds_revenue',
        'deal_value',
      ],
      limit_page_length: 0,
    })
  } catch (e) {
    deals.value = []
  }
}
load()

function val(d) {
  return Number(d[amount.value]) || 0
}

// deals filtrados por cliente seleccionado (para el gráfico)
const filteredDeals = computed(() => {
  let arr = deals.value
  if (clientFilter.value) arr = arr.filter((d) => (d.organization || '') === clientFilter.value)
  return arr
})

// agrupado por cliente (para la tabla) — respeta la búsqueda
const clientRows = computed(() => {
  const m = {}
  for (const d of deals.value) {
    const org = d.organization || '(sin organización)'
    const e = (m[org] = m[org] || { name: org, count: 0, total: 0 })
    e.count += 1
    e.total += val(d)
  }
  let arr = Object.values(m)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    arr = arr.filter((c) => c.name.toLowerCase().includes(q))
  }
  return arr.sort((a, b) => b.total - a.total)
})
const clientNames = computed(() =>
  [...new Set(deals.value.map((d) => d.organization).filter(Boolean))].sort((a, b) =>
    a.localeCompare(b),
  ),
)

const grandTotal = computed(() => filteredDeals.value.reduce((a, d) => a + val(d), 0))

// ventas por año (del cliente seleccionado o todos)
const byYear = computed(() => {
  const m = {}
  for (const d of filteredDeals.value) {
    if (!d.closed_date) continue
    const y = Number(String(d.closed_date).slice(0, 4))
    if (!y) continue
    m[y] = (m[y] || 0) + val(d)
  }
  const years = Object.keys(m).map(Number)
  if (!years.length) return []
  const min = Math.min(...years)
  const max = Math.max(...years)
  const out = []
  for (let y = min; y <= max; y++) out.push({ year: y, amount: m[y] || 0 })
  return out
})
const maxYear = computed(() => Math.max(1, ...byYear.value.map((b) => b.amount)))
function barHeight(v) {
  const pct = (v / maxYear.value) * 100
  return (v > 0 ? Math.max(3, pct) : 0) + '%'
}

function money(v) {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(v || 0)
}
function moneyShort(v) {
  const n = Number(v) || 0
  if (Math.abs(n) >= 1e6) return '$' + (n / 1e6).toFixed(1) + 'M'
  if (Math.abs(n) >= 1e3) return '$' + Math.round(n / 1e3) + 'k'
  return '$' + Math.round(n)
}

usePageMeta(() => ({ title: __('Ventas por Cliente') }))
</script>
