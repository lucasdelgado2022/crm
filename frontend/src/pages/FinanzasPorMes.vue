<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <ChartIcon class="h-5 w-5" />
        {{ __('Finanzas por Mes') }}
      </div>
    </template>
    <template #right-header>
      <select
        v-model.number="year"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
      >
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>
    </template>
  </LayoutHeader>

  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Selector de vista -->
    <div class="mb-4 flex flex-wrap items-center gap-2">
      <div class="flex flex-wrap rounded-lg border border-outline-gray-2 p-0.5">
        <button
          v-for="(v, k) in VIEWS"
          :key="k"
          class="rounded-md px-3 py-1 text-sm font-medium transition"
          :class="
            view === k
              ? 'bg-surface-gray-3 text-ink-gray-9'
              : 'text-ink-gray-6 hover:text-ink-gray-9'
          "
          @click="view = k"
        >
          {{ v.label }}
        </button>
      </div>
    </div>

    <!-- Totales -->
    <div class="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="rounded-lg border p-3">
        <div class="text-xs text-ink-gray-5">{{ __('Total') }} {{ year }}</div>
        <div class="mt-0.5 text-xl font-semibold text-ink-gray-9">
          {{ money(yearTotal) }}
        </div>
      </div>
      <div
        v-for="s in seriesList"
        :key="s.key"
        class="rounded-lg border p-3"
      >
        <div class="flex items-center gap-1.5 text-xs text-ink-gray-5">
          <span class="h-2 w-2 rounded-sm" :style="{ backgroundColor: s.color }" />
          {{ s.label }}
        </div>
        <div class="mt-0.5 text-xl font-semibold" :style="{ color: s.color }">
          {{ money(seriesTotal(s.key)) }}
        </div>
      </div>
    </div>

    <!-- Gráfico de barras -->
    <div class="rounded-lg border p-4">
      <div class="mb-3 flex flex-wrap items-center gap-4 text-xs text-ink-gray-6">
        <span v-for="s in seriesList" :key="s.key" class="flex items-center gap-1.5">
          <span class="h-2.5 w-2.5 rounded-sm" :style="{ backgroundColor: s.color }" />
          {{ s.label }}
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
            {{ m.count ? moneyShort(m.total) + ' (' + m.count + ')' : '' }}
          </div>
          <div
            class="w-full overflow-hidden rounded-t transition-all"
            :class="selected === i ? 'ring-2 ring-ink-gray-4' : ''"
            :style="{ height: barHeight(m.total) }"
            :title="monthTitle(i, m)"
          >
            <div
              v-for="s in seriesList"
              :key="s.key"
              class="w-full transition-all hover:opacity-80"
              :style="{
                height: segPct(m.series[s.key].total, m.total) + '%',
                backgroundColor: s.color,
              }"
            />
          </div>
          <div class="mt-1.5 text-xs text-ink-gray-5">{{ MONTHS[i] }}</div>
        </div>
      </div>
    </div>

    <!-- Detalle de operaciones del mes seleccionado -->
    <div v-if="selected !== null" class="mt-5 rounded-lg border">
      <div class="flex items-center justify-between border-b px-4 py-3">
        <div class="text-sm font-semibold text-ink-gray-8">
          {{ MONTHS_FULL[selected] }} {{ year }}
          <span class="font-normal text-ink-gray-5"
            >({{ selectedDocs.length }})</span
          >
        </div>
        <button
          class="text-sm text-ink-gray-5 hover:text-ink-gray-8"
          @click="selected = null"
        >
          {{ __('Cerrar') }}
        </button>
      </div>
      <div v-if="selectedDocs.length" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
            <tr>
              <th class="px-4 py-2 text-left font-medium">
                {{ __('Documento') }}
              </th>
              <th class="px-4 py-2 text-left font-medium">{{ __('Tipo') }}</th>
              <th class="px-4 py-2 text-left font-medium">{{ __('Fecha') }}</th>
              <th class="px-4 py-2 text-right font-medium">{{ __('Monto') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="r in selectedDocs"
              :key="r.name"
              class="border-b last:border-0 hover:bg-surface-gray-1"
            >
              <td class="px-4 py-2">
                <a
                  :href="'/app/' + r.route + '/' + encodeURIComponent(r.name)"
                  target="_blank"
                  class="text-ink-blue-link"
                  >{{ r.name }}</a
                >
              </td>
              <td class="px-4 py-2">
                <span class="inline-flex items-center gap-1.5 text-ink-gray-7">
                  <span
                    class="h-2 w-2 rounded-sm"
                    :style="{ backgroundColor: r.color }"
                  />
                  {{ r.seriesLabel }}
                </span>
              </td>
              <td class="px-4 py-2 text-ink-gray-6">{{ r.date }}</td>
              <td class="px-4 py-2 text-right font-medium text-ink-gray-9">
                {{ money(r.amount) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="px-4 py-6 text-center text-sm text-ink-gray-4">
        {{ __('Sin operaciones') }}
      </div>
    </div>

    <!-- Tabla -->
    <div class="mt-5 overflow-x-auto rounded-lg border">
      <table class="w-full text-sm">
        <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
          <tr>
            <th class="px-4 py-2 text-left font-medium">{{ __('Mes') }}</th>
            <th
              v-for="s in seriesList"
              :key="s.key"
              class="px-4 py-2 text-right font-medium"
            >
              {{ s.label }}
            </th>
            <th class="px-4 py-2 text-right font-medium">{{ __('Total') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(m, i) in monthly"
            :key="i"
            class="border-b last:border-0 hover:bg-surface-gray-1"
          >
            <td class="px-4 py-2 text-ink-gray-8">{{ MONTHS_FULL[i] }}</td>
            <td
              v-for="s in seriesList"
              :key="s.key"
              class="px-4 py-2 text-right text-ink-gray-7"
            >
              {{ m.series[s.key].total ? money(m.series[s.key].total) : '—' }}
            </td>
            <td class="px-4 py-2 text-right font-medium text-ink-gray-9">
              {{ m.total ? money(m.total) : '—' }}
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="border-t bg-surface-gray-1 font-semibold">
            <td class="px-4 py-2 text-ink-gray-9">{{ __('Total') }}</td>
            <td
              v-for="s in seriesList"
              :key="s.key"
              class="px-4 py-2 text-right text-ink-gray-9"
            >
              {{ money(seriesTotal(s.key)) }}
            </td>
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
import { call, usePageMeta } from 'frappe-ui'
import { ref, computed, watch } from 'vue'

const MONTHS = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
const MONTHS_FULL = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

const VIEWS = {
  facturas: {
    label: __('Facturas'),
    series: [
      { key: 'fact', label: __('Facturas'), doctype: 'Sales Invoice', route: 'sales-invoice', dateField: 'posting_date', amount: 'grand_total', color: '#16a34a', filters: { custom_crm_deal: ['is', 'set'] } },
    ],
  },
  pagoprov: {
    label: __('Pago a Prov'),
    series: [
      { key: 'realizados', label: __('Realizados'), doctype: 'Purchase Invoice', route: 'purchase-invoice', dateField: 'posting_date', amount: 'grand_total', color: '#16a34a', filters: { custom_crm_deal: ['is', 'set'], custom_estado_pago: 'Pagado' } },
      { key: 'programados', label: __('Programados'), doctype: 'Purchase Invoice', route: 'purchase-invoice', dateField: 'posting_date', amount: 'grand_total', color: '#f59e0b', filters: { custom_crm_deal: ['is', 'set'], custom_estado_pago: ['in', ['Pendiente', 'Parcial', 'Vencido']] } },
    ],
  },
  pagos: {
    label: __('Pagos (realizados + programados)'),
    series: [
      { key: 'realizados', label: __('Realizados'), doctype: 'Purchase Invoice', route: 'purchase-invoice', dateField: 'custom_fecha_pago', amount: 'grand_total', color: '#16a34a', filters: { custom_crm_deal: ['is', 'set'], custom_estado_pago: 'Pagado' } },
      { key: 'programados', label: __('Programados'), doctype: 'Purchase Invoice', route: 'purchase-invoice', dateField: 'custom_fecha_pago', amount: 'grand_total', color: '#f59e0b', filters: { custom_crm_deal: ['is', 'set'], custom_estado_pago: ['in', ['Pendiente', 'Parcial', 'Vencido']] } },
    ],
  },
}

const view = ref('facturas')
const cfg = computed(() => VIEWS[view.value])
const seriesList = computed(() => cfg.value.series)
const year = ref(new Date().getFullYear())
const seriesData = ref({})
const loading = ref(false)
const selected = ref(null)
function selectBucket(i) {
  selected.value = selected.value === i ? null : i
}

async function load() {
  loading.value = true
  const out = {}
  for (const s of cfg.value.series) {
    try {
      out[s.key] = await call('frappe.client.get_list', {
        doctype: s.doctype,
        filters: { ...s.filters, [s.dateField]: ['is', 'set'] },
        fields: ['name', s.dateField, s.amount],
        limit_page_length: 0,
      })
    } catch (e) {
      out[s.key] = []
    }
  }
  seriesData.value = out
  loading.value = false
}
load()
watch(view, load)
watch([view, year], () => (selected.value = null))

const years = computed(() => {
  const s = new Set()
  for (const ser of cfg.value.series) {
    for (const d of seriesData.value[ser.key] || []) {
      if (d[ser.dateField]) s.add(Number(String(d[ser.dateField]).slice(0, 4)))
    }
  }
  s.add(new Date().getFullYear())
  return [...s].sort((a, b) => b - a)
})

const monthly = computed(() => {
  const arr = Array.from({ length: 12 }, () => {
    const series = {}
    for (const s of cfg.value.series) series[s.key] = { total: 0, count: 0 }
    return { total: 0, count: 0, series }
  })
  for (const s of cfg.value.series) {
    for (const d of seriesData.value[s.key] || []) {
      const dt = d[s.dateField]
      if (!dt) continue
      if (Number(String(dt).slice(0, 4)) !== year.value) continue
      const mi = Number(String(dt).slice(5, 7)) - 1
      if (mi < 0 || mi > 11) continue
      const val = Number(d[s.amount]) || 0
      arr[mi].series[s.key].total += val
      arr[mi].series[s.key].count += 1
      arr[mi].total += val
      arr[mi].count += 1
    }
  }
  return arr
})

function seriesTotal(key) {
  return monthly.value.reduce((a, m) => a + m.series[key].total, 0)
}

const selectedDocs = computed(() => {
  if (selected.value === null) return []
  const out = []
  for (const s of cfg.value.series) {
    for (const d of seriesData.value[s.key] || []) {
      const dt = d[s.dateField]
      if (!dt) continue
      if (Number(String(dt).slice(0, 4)) !== year.value) continue
      if (Number(String(dt).slice(5, 7)) - 1 !== selected.value) continue
      out.push({
        name: d.name,
        route: s.route,
        seriesLabel: s.label,
        color: s.color,
        date: dt,
        amount: Number(d[s.amount]) || 0,
      })
    }
  }
  return out.sort((a, b) => b.amount - a.amount)
})
const yearTotal = computed(() => monthly.value.reduce((a, m) => a + m.total, 0))
const maxMonth = computed(() => Math.max(1, ...monthly.value.map((m) => m.total)))

function barHeight(v) {
  const pct = (v / maxMonth.value) * 100
  return (v > 0 ? Math.max(2, pct) : 0) + '%'
}
function segPct(part, total) {
  if (!total) return 0
  return (part / total) * 100
}
function monthTitle(i, m) {
  let t = MONTHS[i] + ': ' + money(m.total)
  if (seriesList.value.length > 1) {
    t += ' — ' + seriesList.value.map((s) => s.label + ' ' + money(m.series[s.key].total)).join(' / ')
  }
  return t
}
function money(n) {
  return '$' + Math.round(Number(n) || 0).toLocaleString('es-AR')
}
function moneyShort(n) {
  const v = Number(n) || 0
  if (v >= 1000000) return '$' + (v / 1000000).toFixed(1) + 'M'
  if (v >= 1000) return '$' + Math.round(v / 1000) + 'k'
  return '$' + Math.round(v)
}

usePageMeta(() => ({ title: __('Finanzas por Mes') }))
</script>
