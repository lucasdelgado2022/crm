<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <LucideChartPie class="h-5 w-5" />
        {{ __('ABC de Clientes') }}
      </div>
    </template>
    <template #right-header>
      <div class="flex items-center gap-1">
        <button
          v-for="y in yearOptions"
          :key="y"
          class="rounded-md px-2.5 py-1 text-sm transition-colors"
          :class="
            selectedYear === y
              ? 'bg-blue-600 text-white'
              : 'text-ink-gray-7 hover:bg-surface-gray-2'
          "
          @click="selectedYear = y"
        >
          {{ y === 'all' ? __('Todos') : y }}
        </button>
      </div>
    </template>
  </LayoutHeader>

  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Resumen por clase -->
    <div class="mb-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div
        v-for="t in tiers"
        :key="t.key"
        class="rounded-lg border p-4"
        :class="t.border"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span
              class="flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold text-white"
              :class="t.badge"
            >
              {{ t.key }}
            </span>
            <span class="text-sm text-ink-gray-6">{{ t.desc }}</span>
          </div>
          <span class="text-sm text-ink-gray-5">
            {{ summary[t.key].count }} {{ __('clientes') }}
          </span>
        </div>
        <div class="mt-2 text-xl font-semibold text-ink-gray-9">
          {{ money(summary[t.key].amount) }}
        </div>
        <div class="text-xs text-ink-gray-5">
          {{ pct(summary[t.key].amount, totalRevenue) }}% {{ __('del total') }}
        </div>
      </div>
    </div>

    <!-- Tabla de clientes -->
    <div v-if="rows.length" class="overflow-x-auto rounded-lg border">
      <table class="w-full text-sm">
        <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
          <tr>
            <th class="px-3 py-2 text-left font-medium">{{ __('Clase') }}</th>
            <th class="px-4 py-2 text-left font-medium">{{ __('Cliente') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('Solaer Revenue') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('% del total') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('% acumulado') }}</th>
            <th class="px-3 py-2 text-right font-medium">{{ __('Negocios') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="r in rows"
            :key="r.name"
            class="cursor-pointer border-b last:border-0 hover:bg-surface-gray-1"
            @click="openOrg(r.name)"
          >
            <td class="px-3 py-2">
              <span
                class="flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold text-white"
                :class="tierBadge(r.tier)"
              >
                {{ r.tier }}
              </span>
            </td>
            <td class="px-4 py-2 font-medium text-ink-gray-8">{{ r.name }}</td>
            <td class="px-3 py-2 text-right text-ink-gray-8">{{ money(r.amount) }}</td>
            <td class="px-3 py-2 text-right text-ink-gray-6">{{ pct(r.amount, totalRevenue) }}%</td>
            <td class="px-3 py-2 text-right text-ink-gray-6">{{ r.cumPct.toFixed(1) }}%</td>
            <td class="px-3 py-2 text-right text-ink-gray-6">{{ r.count }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="border-t bg-surface-gray-1 font-semibold">
            <td class="px-3 py-2"></td>
            <td class="px-4 py-2 text-ink-gray-8">{{ __('Total') }} ({{ rows.length }})</td>
            <td class="px-3 py-2 text-right text-ink-gray-9">{{ money(totalRevenue) }}</td>
            <td class="px-3 py-2"></td>
            <td class="px-3 py-2"></td>
            <td class="px-3 py-2"></td>
          </tr>
        </tfoot>
      </table>
    </div>
    <div
      v-else
      class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
    >
      <LucideChartPie class="h-10 w-10" />
      <div>{{ __('Sin ventas ganadas en el período') }}</div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideChartPie from '~icons/lucide/chart-pie'
import { createResource, usePageMeta } from 'frappe-ui'
import { ref, computed } from 'vue'

const CURRENT_YEAR = 2026
const selectedYear = ref(CURRENT_YEAR)

const tiers = [
  { key: 'A', desc: '80% del revenue', border: 'border-green-200', badge: 'bg-green-600' },
  { key: 'B', desc: 'Siguiente 15%', border: 'border-amber-200', badge: 'bg-amber-500' },
  { key: 'C', desc: 'Último 5%', border: 'border-gray-200', badge: 'bg-gray-500' },
]

const dealsRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Deal',
    filters: { status: 'Won' },
    fields: ['name', 'organization', 'closed_date', 'custom_solaer_revenue'],
    limit_page_length: 0,
  },
  auto: true,
})
const deals = computed(() => dealsRes.data || [])

const yearOptions = computed(() => {
  const ys = new Set()
  for (const d of deals.value) {
    if (d.closed_date) ys.add(Number(String(d.closed_date).slice(0, 4)))
  }
  ys.add(CURRENT_YEAR)
  return [...[...ys].sort((a, b) => b - a), 'all']
})

// Agregado por organización (revenue ganado en el año seleccionado)
const rows = computed(() => {
  const m = {}
  for (const d of deals.value) {
    if (!d.organization) continue
    if (selectedYear.value !== 'all') {
      const y = d.closed_date ? Number(String(d.closed_date).slice(0, 4)) : null
      if (y !== selectedYear.value) continue
    }
    const val = Number(d.custom_solaer_revenue) || 0
    if (!m[d.organization]) m[d.organization] = { name: d.organization, amount: 0, count: 0 }
    m[d.organization].amount += val
    m[d.organization].count += 1
  }
  let arr = Object.values(m).filter((r) => r.amount > 0)
  arr.sort((a, b) => b.amount - a.amount)
  const total = arr.reduce((s, r) => s + r.amount, 0) || 1
  let cum = 0
  for (const r of arr) {
    cum += r.amount
    r.cumPct = (cum / total) * 100
    r.tier = r.cumPct <= 80 ? 'A' : r.cumPct <= 95 ? 'B' : 'C'
  }
  return arr
})

const totalRevenue = computed(() => rows.value.reduce((s, r) => s + r.amount, 0))

const summary = computed(() => {
  const s = { A: { count: 0, amount: 0 }, B: { count: 0, amount: 0 }, C: { count: 0, amount: 0 } }
  for (const r of rows.value) {
    s[r.tier].count += 1
    s[r.tier].amount += r.amount
  }
  return s
})

function tierBadge(t) {
  return t === 'A' ? 'bg-green-600' : t === 'B' ? 'bg-amber-500' : 'bg-gray-500'
}
function pct(part, total) {
  if (!total) return '0.0'
  return ((part / total) * 100).toFixed(1)
}
function money(v) {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(v || 0)
}
function openOrg(name) {
  window.location.href = '/crm/organizations/' + encodeURIComponent(name)
}

usePageMeta(() => ({ title: __('ABC de Clientes') }))
</script>
