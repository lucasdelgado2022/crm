<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs
        :items="[{ label: __('Pipeline'), route: { name: 'Pipeline' } }]"
      />
    </template>
    <template #right-header>
      <Button
        variant="subtle"
        :label="__('Limpiar filtros')"
        @click="clearFilters"
      />
    </template>
  </LayoutHeader>

  <div class="flex flex-1 flex-col gap-4 overflow-hidden p-4 sm:p-5">
    <!-- Filtros -->
    <div class="grid shrink-0 grid-cols-1 gap-3 sm:grid-cols-3 lg:grid-cols-5">
      <FormControl type="date" :label="__('Cierre desde')" v-model="filters.from" />
      <FormControl type="date" :label="__('Cierre hasta')" v-model="filters.to" />
      <div>
        <div class="mb-1.5 text-xs text-ink-gray-5">{{ __('Status') }}</div>
        <Link
          doctype="CRM Deal Status"
          :value="filters.status"
          :placeholder="__('Todos')"
          @change="(v) => (filters.status = v || '')"
        />
      </div>
      <div>
        <div class="mb-1.5 text-xs text-ink-gray-5">{{ __('Producto') }}</div>
        <Link
          doctype="CRM Product"
          :value="filters.product"
          :placeholder="__('Todos')"
          @change="(v) => (filters.product = v || '')"
        />
      </div>
      <div>
        <div class="mb-1.5 text-xs text-ink-gray-5">
          {{ __('Responsable comercial') }}
        </div>
        <Link
          doctype="User"
          :value="filters.deal_owner"
          :placeholder="__('Todos')"
          @change="(v) => (filters.deal_owner = v || '')"
        />
      </div>
    </div>

    <!-- Resumen -->
    <div class="shrink-0 text-sm text-ink-gray-6">
      {{ totalCount }} {{ __('oportunidades') }} ·
      {{ __('Total') }} {{ fmt(totalAmount) }} ·
      {{ __('Pipeline abierto') }} {{ fmt(openAmount) }}
    </div>

    <!-- Tablero swimlanes: fila por Responsable × columnas por Estado -->
    <div v-if="swimlanes.length" class="flex-1 overflow-auto pb-2">
      <div class="inline-block min-w-full align-top">
        <!-- Encabezado de columnas (estados) -->
        <div class="grid gap-2 border-b pb-2" :style="gridStyle">
          <div
            class="sticky left-0 z-20 bg-surface-white px-2 py-2 text-xs font-semibold uppercase tracking-wide text-ink-gray-5"
          >
            {{ __('Responsable') }}
          </div>
          <div
            v-for="s in statusList"
            :key="s.status"
            class="flex items-center gap-2 px-2 py-2"
          >
            <span
              class="h-2.5 w-2.5 shrink-0 rounded-full"
              :style="{ backgroundColor: s.color }"
            />
            <span class="truncate text-sm font-semibold text-ink-gray-8">
              {{ s.status }}
            </span>
          </div>
        </div>

        <!-- Swimlanes -->
        <div
          v-for="lane in swimlanes"
          :key="lane.key"
          class="grid gap-2 border-b py-2"
          :style="gridStyle"
        >
          <div
            class="sticky left-0 z-10 flex flex-col justify-start gap-1 bg-surface-white px-2 py-1"
          >
            <div class="flex items-center gap-2">
              <Avatar
                size="sm"
                :label="lane.owner.label"
                :image="lane.owner.image"
                :title="lane.owner.label"
              />
              <span class="truncate text-sm font-medium text-ink-gray-9">
                {{ lane.owner.label }}
              </span>
            </div>
            <span class="text-xs text-ink-gray-5">
              {{ lane.count }} · {{ fmt(lane.total) }}
            </span>
          </div>
          <div
            v-for="s in statusList"
            :key="s.status"
            class="flex flex-col gap-2 rounded-lg bg-surface-gray-2 p-2"
          >
            <div
              v-for="d in lane.byStatus[s.status] || []"
              :key="d.name"
              class="cursor-pointer rounded-lg border bg-surface-white p-2 hover:shadow-sm"
              @click="openDeal(d.name)"
            >
              <div class="truncate text-sm font-medium text-ink-gray-9">
                {{ d.title }}
              </div>
              <div class="mt-0.5 text-xs text-ink-gray-7">{{ fmt(d.amount) }}</div>
              <div class="mt-1 flex items-center gap-2">
                <Badge v-if="d.product" variant="subtle" theme="blue" size="sm">
                  {{ d.product }}
                </Badge>
                <span class="ml-auto text-[10px] text-ink-gray-5">
                  {{ d.closeLabel }}
                </span>
              </div>
            </div>
            <div
              v-if="!(lane.byStatus[s.status] || []).length"
              class="py-2 text-center text-[10px] text-ink-gray-3"
            >
              —
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      v-else
      class="flex flex-1 items-center justify-center text-sm text-ink-gray-4"
    >
      {{ __('Sin oportunidades para los filtros') }}
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'
import { statusesStore } from '@/stores/statuses'
import { usersStore } from '@/stores/users'
import { getMeta } from '@/stores/meta'
import {
  Breadcrumbs,
  FormControl,
  Badge,
  Avatar,
  createResource,
  usePageMeta,
} from 'frappe-ui'
import { reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { getDealStatus, dealStatuses } = statusesStore()
const { getUser } = usersStore()
const { getFormattedCurrency } = getMeta('CRM Deal')

const MESES = [
  'Ene',
  'Feb',
  'Mar',
  'Abr',
  'May',
  'Jun',
  'Jul',
  'Ago',
  'Sep',
  'Oct',
  'Nov',
  'Dic',
]

const filters = reactive({
  from: '',
  to: '',
  status: '',
  product: '',
  deal_owner: '',
})

function buildFilters() {
  const f = {}
  if (filters.status) f.status = filters.status
  if (filters.product) f.custom_producto = filters.product
  if (filters.deal_owner) f.deal_owner = filters.deal_owner
  if (filters.from && filters.to)
    f.expected_closure_date = ['between', [filters.from, filters.to]]
  else if (filters.from) f.expected_closure_date = ['>=', filters.from]
  else if (filters.to) f.expected_closure_date = ['<=', filters.to]
  return f
}

const deals = createResource({
  url: 'frappe.client.get_list',
  makeParams() {
    return {
      doctype: 'CRM Deal',
      fields: [
        'name',
        'organization',
        'status',
        'deal_owner',
        'custom_producto',
        'expected_closure_date',
        'annual_revenue',
      ],
      filters: buildFilters(),
      order_by: 'expected_closure_date asc',
      limit_page_length: 0,
    }
  },
  auto: true,
})

watch(
  filters,
  () => {
    deals.reload()
  },
  { deep: true },
)

function clearFilters() {
  filters.from = ''
  filters.to = ''
  filters.status = ''
  filters.product = ''
  filters.deal_owner = ''
}

function fmt(v) {
  try {
    return getFormattedCurrency('annual_revenue', { annual_revenue: v || 0 })
  } catch (e) {
    return v || 0
  }
}

function closeLabel(date) {
  if (!date) return '—'
  const s = String(date)
  const [y, m] = s.split('-')
  const idx = parseInt(m, 10) - 1
  if (isNaN(idx)) return s
  return (MESES[idx] || m) + ' ' + y.slice(2)
}

const isClosed = (status) =>
  status === 'Won' ||
  status === 'Lost' ||
  status === 'Ganado' ||
  status === 'Perdido'

const totalCount = computed(() => (deals.data || []).length)
const totalAmount = computed(() =>
  (deals.data || []).reduce((a, d) => a + (d.annual_revenue || 0), 0),
)
const openAmount = computed(() =>
  (deals.data || [])
    .filter((d) => !isClosed(d.status))
    .reduce((a, d) => a + (d.annual_revenue || 0), 0),
)

function mapCard(d) {
  return {
    name: d.name,
    title: d.organization || d.name,
    amount: d.annual_revenue || 0,
    product: d.custom_producto || '',
    closeLabel: closeLabel(d.expected_closure_date),
  }
}

// Columnas = estados (ordenados por posición del funnel)
const statusList = computed(() => {
  const present = new Set((deals.data || []).map((d) => d.status || '—'))
  const all = (dealStatuses?.data || []).map((s) => s.name)
  const set = [...new Set([...all, ...present])]
  return set
    .map((s) => ({
      status: s,
      position: getDealStatus(s)?.position ?? 999,
      color: getDealStatus(s)?.color || '#8b8b8b',
    }))
    .sort((a, b) => a.position - b.position)
})

// Filas = responsables (deal_owner). Cada fila agrupa sus deals por estado.
const swimlanes = computed(() => {
  const lanes = {}
  for (const d of deals.data || []) {
    const key = d.deal_owner || '__none__'
    if (!lanes[key]) lanes[key] = { key, deals: [] }
    lanes[key].deals.push(d)
  }
  const arr = Object.values(lanes).map((lane) => {
    const u = lane.key !== '__none__' ? getUser(lane.key) : null
    const byStatus = {}
    for (const s of statusList.value) byStatus[s.status] = []
    for (const d of lane.deals) {
      const s = d.status || '—'
      if (!byStatus[s]) byStatus[s] = []
      byStatus[s].push(mapCard(d))
    }
    const total = lane.deals.reduce((a, d) => a + (d.annual_revenue || 0), 0)
    return {
      key: lane.key,
      owner: u
        ? { label: u.full_name, image: u.user_image }
        : { label: __('Sin responsable'), image: '' },
      count: lane.deals.length,
      total,
      byStatus,
    }
  })
  arr.sort((a, b) => b.total - a.total)
  return arr
})

const gridStyle = computed(() => ({
  gridTemplateColumns: `12rem repeat(${statusList.value.length}, 18rem)`,
}))

function openDeal(name) {
  router.push({ name: 'Deal', params: { dealId: name } })
}

usePageMeta(() => ({ title: __('Pipeline') }))
</script>
