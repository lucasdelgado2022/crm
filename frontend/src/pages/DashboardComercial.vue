<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <LucideTrophy class="h-5 w-5" />
        {{ __('Dashboard Comercial') }}
      </div>
    </template>
    <template #right-header>
      <select
        v-model="respFilter"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
      >
        <option value="">{{ __('Todos los responsables') }}</option>
        <option v-for="o in ownerList" :key="o" :value="o">{{ userMap[o] || o }}</option>
      </select>
      <select
        v-model.number="year"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
      >
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>
    </template>
  </LayoutHeader>

  <div class="flex h-full flex-col gap-5 overflow-y-auto p-4 sm:p-6">
    <!-- Selector de monto -->
    <div class="flex flex-wrap items-center gap-2">
      <span class="text-xs text-ink-gray-5">{{ __('Monto') }}:</span>
      <div class="flex overflow-hidden rounded-lg border border-outline-gray-2">
        <button
          v-for="opt in amountOptions"
          :key="opt.key"
          class="border-r px-3 py-1 text-xs last:border-r-0"
          :class="amount === opt.key ? 'bg-surface-gray-3 font-medium text-ink-gray-9' : 'bg-surface-white text-ink-gray-6 hover:text-ink-gray-9'"
          @click="amount = opt.key"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- KPIs anuales de cierre -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-5">
      <div class="rounded-lg border border-green-200 bg-green-50/40 p-3">
        <div class="text-xs font-medium text-green-700">{{ __('Cerrado') }} {{ year }}</div>
        <div class="mt-0.5 text-xl font-semibold text-green-700">{{ money(kpi.wonAmt) }}</div>
        <div class="text-xs text-ink-gray-5">{{ kpi.wonCnt }} {{ __('ventas') }}</div>
      </div>
      <div class="rounded-lg border border-violet-200 bg-violet-50/40 p-3">
        <div class="text-xs font-medium text-violet-700">{{ __('Pipeline') }} {{ year }}</div>
        <div class="mt-0.5 text-xl font-semibold text-violet-700">{{ money(kpi.openAmt) }}</div>
        <div class="text-xs text-ink-gray-5">{{ kpi.openCnt }} {{ __('oportunidades') }}</div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Ticket promedio') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">{{ money(kpi.ticket) }}</div>
        <div class="text-xs text-ink-gray-5">{{ __('por venta') }}</div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Win rate') }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">{{ kpi.winRate }}%</div>
        <div class="text-xs text-ink-gray-5">{{ kpi.wonCnt }} / {{ kpi.wonCnt + kpi.lostCnt }} {{ __('cerradas') }}</div>
      </div>
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Perdido') }} {{ year }}</div>
        <div class="mt-0.5 text-xl font-semibold text-red-700">{{ money(kpi.lostAmt) }}</div>
        <div class="text-xs text-ink-gray-5">{{ kpi.lostCnt }} {{ __('oportunidades') }}</div>
      </div>
    </div>

    <!-- Ventas y Pipeline por mes -->
    <div class="rounded-lg border p-4">
      <div class="mb-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-ink-gray-6">
        <span class="flex items-center gap-1.5">
          <span class="h-2.5 w-2.5 rounded-sm bg-green-500" /> {{ __('Ventas (cerradas)') }}
        </span>
        <span class="flex items-center gap-1.5">
          <span class="h-2.5 w-2.5 rounded-sm bg-violet-500" /> {{ __('Pipeline') }}
        </span>
      </div>
      <div v-if="loading" class="flex h-64 items-center justify-center text-ink-gray-4">
        {{ __('Cargando...') }}
      </div>
      <div v-else class="flex h-72 items-end gap-2 sm:gap-3">
        <div
          v-for="(m, i) in monthly"
          :key="i"
          class="flex h-full flex-1 flex-col items-center justify-end"
        >
          <div class="mb-1 whitespace-nowrap text-[9px] font-semibold leading-tight text-ink-gray-7">
            <span v-if="m.wonCnt" class="text-green-700">{{ m.wonCnt }}v</span>
          </div>
          <div class="flex h-full w-full items-end justify-center gap-0.5">
            <div
              class="w-full rounded-t bg-green-500 transition-all hover:opacity-80"
              :class="m.wonAmt > 0 ? '' : 'opacity-0'"
              :style="{ height: barH(m.wonAmt) }"
              :title="MONTHS[i] + ' — ' + __('Ventas') + ': ' + money(m.wonAmt) + ' (' + m.wonCnt + ')'"
            />
            <div
              class="w-full rounded-t bg-violet-500 transition-all hover:opacity-80"
              :class="m.openAmt > 0 ? '' : 'opacity-0'"
              :style="{ height: barH(m.openAmt) }"
              :title="MONTHS[i] + ' — ' + __('Pipeline') + ': ' + money(m.openAmt) + ' (' + m.openCnt + ')'"
            />
          </div>
          <div class="mt-1.5 text-xs text-ink-gray-5">{{ MONTHS[i] }}</div>
        </div>
      </div>
    </div>

    <!-- Ranking por responsable -->
    <div class="rounded-lg border">
      <div class="border-b px-4 py-3 text-sm font-semibold text-ink-gray-8">
        {{ __('Por responsable comercial') }} · {{ year }}
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
            <tr>
              <th class="px-4 py-2 text-left">{{ __('Responsable') }}</th>
              <th class="px-4 py-2 text-right">{{ __('Ventas') }}</th>
              <th class="px-4 py-2 text-right">{{ __('Cerrado') }}</th>
              <th class="px-4 py-2 text-right">{{ __('Pipeline') }}</th>
              <th class="px-4 py-2 text-right">{{ __('Win rate') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="r in ranking" :key="r.owner" class="hover:bg-surface-gray-1">
              <td class="px-4 py-2 text-ink-gray-9">{{ userMap[r.owner] || r.owner }}</td>
              <td class="px-4 py-2 text-right text-green-700">{{ r.wonCnt }}</td>
              <td class="px-4 py-2 text-right font-medium text-ink-gray-9">{{ money(r.wonAmt) }}</td>
              <td class="px-4 py-2 text-right text-violet-700">{{ money(r.openAmt) }}</td>
              <td class="px-4 py-2 text-right text-ink-gray-7">{{ r.winRate }}%</td>
            </tr>
            <tr v-if="!ranking.length">
              <td colspan="5" class="px-4 py-6 text-center text-ink-gray-4">{{ __('Sin datos') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideTrophy from '~icons/lucide/trophy'
import { createResource, usePageMeta } from 'frappe-ui'
import { ref, computed } from 'vue'

const MONTHS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

const amountOptions = [
  { key: 'custom_solaer_revenue', label: 'Solaer Revenue' },
  { key: 'custom_ds_revenue', label: 'DS Revenue' },
  { key: 'deal_value', label: 'Valor de Oportunidad' },
]
const amount = ref('custom_solaer_revenue')
const year = ref(new Date().getFullYear())
const respFilter = ref('')

const dealsRes = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Deal',
    fields: [
      'name', 'deal_owner', 'status', 'closed_date', 'expected_closure_date',
      'deal_value', 'custom_ds_revenue', 'custom_solaer_revenue',
    ],
    limit_page_length: 0,
  },
  auto: true,
})
const deals = computed(() => dealsRes.data || [])
const loading = computed(() => dealsRes.loading)

const usersRes = createResource({
  url: 'frappe.client.get_list',
  params: { doctype: 'User', filters: { user_type: 'System User' }, fields: ['name', 'full_name'], limit_page_length: 0 },
  auto: true,
})
const userMap = computed(() => {
  const m = {}
  for (const u of usersRes.data || []) m[u.name] = u.full_name
  return m
})

const years = computed(() => {
  const set = new Set([new Date().getFullYear()])
  for (const d of deals.value) {
    for (const f of [d.closed_date, d.expected_closure_date]) {
      if (f) set.add(Number(String(f).slice(0, 4)))
    }
  }
  return [...set].sort((a, b) => b - a)
})

const ownerList = computed(() => {
  const set = new Set()
  for (const d of deals.value) if (d.deal_owner) set.add(d.deal_owner)
  return [...set].sort((a, b) => (userMap.value[a] || a).localeCompare(userMap.value[b] || b))
})

function amt(d) {
  return Number(d[amount.value]) || 0
}
function inYear(dateStr) {
  return dateStr && Number(String(dateStr).slice(0, 4)) === year.value
}
function passResp(d) {
  return !respFilter.value || d.deal_owner === respFilter.value
}
const isWon = (d) => d.status === 'Won'
const isLost = (d) => d.status === 'Lost'
const isOpen = (d) => !isWon(d) && !isLost(d)

// KPIs anuales de cierre (respeta responsable)
const kpi = computed(() => {
  let wonAmt = 0, wonCnt = 0, openAmt = 0, openCnt = 0, lostAmt = 0, lostCnt = 0
  for (const d of deals.value) {
    if (!passResp(d)) continue
    if (isWon(d) && inYear(d.closed_date)) { wonAmt += amt(d); wonCnt++ }
    else if (isLost(d) && inYear(d.closed_date || d.expected_closure_date)) { lostAmt += amt(d); lostCnt++ }
    else if (isOpen(d) && inYear(d.expected_closure_date)) { openAmt += amt(d); openCnt++ }
  }
  const ticket = wonCnt ? wonAmt / wonCnt : 0
  const closed = wonCnt + lostCnt
  const winRate = closed ? Math.round((wonCnt / closed) * 100) : 0
  return { wonAmt, wonCnt, openAmt, openCnt, lostAmt, lostCnt, ticket, winRate }
})

// Ventas (cerradas) y Pipeline por mes
const monthly = computed(() => {
  const arr = Array.from({ length: 12 }, () => ({ wonAmt: 0, wonCnt: 0, openAmt: 0, openCnt: 0 }))
  for (const d of deals.value) {
    if (!passResp(d)) continue
    if (isWon(d) && inYear(d.closed_date)) {
      const mi = Number(String(d.closed_date).slice(5, 7)) - 1
      if (mi >= 0 && mi < 12) { arr[mi].wonAmt += amt(d); arr[mi].wonCnt++ }
    } else if (isOpen(d) && inYear(d.expected_closure_date)) {
      const mi = Number(String(d.expected_closure_date).slice(5, 7)) - 1
      if (mi >= 0 && mi < 12) { arr[mi].openAmt += amt(d); arr[mi].openCnt++ }
    }
  }
  return arr
})
const maxMonth = computed(() => {
  let mx = 1
  for (const m of monthly.value) {
    if (m.wonAmt > mx) mx = m.wonAmt
    if (m.openAmt > mx) mx = m.openAmt
  }
  return mx
})
function barH(v) {
  const pct = (v / maxMonth.value) * 100
  return (v > 0 ? Math.max(2, pct) : 0) + '%'
}

// Ranking por responsable (ignora el filtro de responsable para mostrar a todos)
const ranking = computed(() => {
  const by = {}
  for (const d of deals.value) {
    const o = d.deal_owner || '—'
    const r = by[o] || (by[o] = { owner: o, wonAmt: 0, wonCnt: 0, openAmt: 0, lostCnt: 0 })
    if (isWon(d) && inYear(d.closed_date)) { r.wonAmt += amt(d); r.wonCnt++ }
    else if (isLost(d) && inYear(d.closed_date || d.expected_closure_date)) { r.lostCnt++ }
    else if (isOpen(d) && inYear(d.expected_closure_date)) { r.openAmt += amt(d) }
  }
  return Object.values(by)
    .map((r) => {
      const closed = r.wonCnt + r.lostCnt
      return { ...r, winRate: closed ? Math.round((r.wonCnt / closed) * 100) : 0 }
    })
    .filter((r) => r.wonCnt || r.openAmt || r.lostCnt)
    .sort((a, b) => b.wonAmt - a.wonAmt)
})

function money(v) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v || 0)
}

usePageMeta(() => ({ title: __('Dashboard Comercial') }))
</script>
