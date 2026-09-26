<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs
        :items="[{ label: __('Comisiones'), route: { name: 'Comisiones' } }]"
      />
    </template>
  </LayoutHeader>

  <div class="flex items-center justify-between gap-2 px-3 py-3 sm:px-5">
    <div class="text-base text-ink-gray-6">
      {{ __('{0} comisiones', [rows.length]) }}
      <span v-if="totalMonto" class="ml-2 font-medium text-ink-gray-8">
        · {{ __('Total') }}: {{ fmt(totalMonto) }}
      </span>
    </div>
    <div class="flex items-center gap-2">
      <select
        v-model="estadoFilter"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
      >
        <option value="">{{ __('Todos los estados') }}</option>
        <option v-for="e in ESTADOS" :key="e" :value="e">{{ e }}</option>
      </select>
      <select
        v-model.number="year"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
      >
        <option :value="null">{{ __('Todos los años') }}</option>
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>
      <FormControl
        class="w-56"
        type="text"
        :placeholder="__('Buscar...')"
        v-model="search"
      >
        <template #prefix>
          <FeatherIcon name="search" class="h-4 w-4 text-ink-gray-5" />
        </template>
      </FormControl>
    </div>
  </div>

  <div class="flex-1 overflow-auto px-3 pb-5 sm:px-5">
    <table v-if="rows.length" class="w-full text-sm">
      <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
        <tr>
          <th class="px-3 py-2 text-left font-medium">
            {{ __('Organización') }}
          </th>
          <th class="px-3 py-2 text-left font-medium">{{ __('Vendedor') }}</th>
          <th class="px-3 py-2 text-right font-medium">{{ __('%') }}</th>
          <th class="px-3 py-2 text-right font-medium">{{ __('Comisión') }}</th>
          <th class="px-3 py-2 text-left font-medium">{{ __('Estado') }}</th>
          <th class="px-3 py-2 text-left font-medium">{{ __('Año') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(r, i) in rows"
          :key="i"
          class="cursor-pointer border-b last:border-0 hover:bg-surface-gray-1"
          @click="openDeal(r.deal)"
        >
          <td class="px-3 py-2 text-ink-gray-8">{{ r.organization }}</td>
          <td class="px-3 py-2 text-ink-gray-7">{{ r.sales_person || '—' }}</td>
          <td class="px-3 py-2 text-right text-ink-gray-7">
            {{ r.porcentaje || 0 }}%
          </td>
          <td class="px-3 py-2 text-right font-medium text-ink-gray-9">
            {{ fmt(r.monto) }}
          </td>
          <td class="px-3 py-2">
            <Badge variant="subtle" :theme="estadoTheme(r.estado)" size="sm">
              {{ r.estado || 'Pendiente' }}
            </Badge>
          </td>
          <td class="px-3 py-2 text-ink-gray-6">{{ r.year || '—' }}</td>
        </tr>
      </tbody>
    </table>
    <div
      v-else
      class="flex flex-1 flex-col items-center justify-center gap-2 py-16 text-ink-gray-4"
    >
      <LucideHandCoins class="h-10 w-10" />
      <div>{{ __('Sin comisiones asignadas') }}</div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideHandCoins from '~icons/lucide/hand-coins'
import { getMeta } from '@/stores/meta'
import {
  Breadcrumbs,
  FormControl,
  FeatherIcon,
  Badge,
  call,
  usePageMeta,
} from 'frappe-ui'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { getFormattedCurrency } = getMeta('CRM Deal')

const ESTADOS = ['Pendiente', 'Aprobado', 'Pagado']
const search = ref('')
const year = ref(null)
const estadoFilter = ref('')
const all = ref([])

async function load() {
  const st = await call('frappe.client.get_list', {
    doctype: 'CRM Deal Status',
    filters: { type: 'Won' },
    fields: ['name'],
    limit_page_length: 0,
  })
  const wons = st.map((s) => s.name)
  const deals = await call('frappe.client.get_list', {
    doctype: 'CRM Deal',
    filters: { status: ['in', wons], custom_comisiones_data: ['is', 'set'] },
    fields: ['name', 'organization', 'closed_date', 'custom_comisiones_data'],
    limit_page_length: 0,
  })
  const out = []
  for (const d of deals) {
    let arr = []
    try {
      arr = JSON.parse(d.custom_comisiones_data || '[]') || []
    } catch (e) {
      arr = []
    }
    const yr = d.closed_date ? Number(String(d.closed_date).slice(0, 4)) : null
    for (const c of arr) {
      out.push({
        deal: d.name,
        organization: d.organization || d.name,
        sales_person: c.sales_person || '',
        porcentaje: c.porcentaje || 0,
        monto: Number(c.monto) || 0,
        estado: c.estado || 'Pendiente',
        year: yr,
      })
    }
  }
  all.value = out
}
load()

const years = computed(() => {
  const s = new Set()
  for (const r of all.value) if (r.year) s.add(r.year)
  return [...s].sort((a, b) => b - a)
})

const rows = computed(() => {
  let data = all.value
  if (year.value) data = data.filter((r) => r.year === year.value)
  if (estadoFilter.value)
    data = data.filter((r) => r.estado === estadoFilter.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    data = data.filter(
      (r) =>
        (r.organization || '').toLowerCase().includes(q) ||
        (r.sales_person || '').toLowerCase().includes(q),
    )
  }
  return data
})

const totalMonto = computed(() =>
  rows.value.reduce((a, r) => a + (Number(r.monto) || 0), 0),
)

function fmt(v) {
  try {
    return getFormattedCurrency('annual_revenue', { annual_revenue: v || 0 })
  } catch (e) {
    return v || 0
  }
}
function estadoTheme(e) {
  return e === 'Pagado' ? 'green' : e === 'Aprobado' ? 'blue' : 'orange'
}
function openDeal(name) {
  router.push({ name: 'VentaRelacion', params: { dealId: name } })
}

usePageMeta(() => ({ title: __('Comisiones') }))
</script>
