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

    <!-- Tablero Kanban por Status, tarjetas por Cierre -->
    <div v-if="columns.length" class="flex flex-1 gap-4 overflow-x-auto pb-2">
      <div
        v-for="col in columns"
        :key="col.status"
        class="flex w-72 shrink-0 flex-col rounded-lg bg-surface-gray-2"
      >
        <div class="shrink-0 px-3 pt-3">
          <div class="flex items-center justify-between gap-2">
            <span class="truncate font-semibold text-ink-gray-8">
              {{ col.status }}
            </span>
            <span class="shrink-0 text-sm text-ink-gray-6">
              {{ col.count }}
            </span>
          </div>
          <div class="mt-1 text-sm text-ink-gray-7">{{ fmt(col.amount) }}</div>
          <div class="mt-2 h-1.5 overflow-hidden rounded bg-surface-gray-4">
            <div
              class="h-full rounded"
              :style="{
                width: Math.max(col.pct, 3) + '%',
                backgroundColor: col.color,
              }"
            />
          </div>
        </div>
        <div class="flex flex-1 flex-col gap-2 overflow-y-auto p-3">
          <div
            v-for="d in col.deals"
            :key="d.name"
            class="cursor-pointer rounded-lg border bg-surface-white p-3 hover:shadow-sm"
            @click="openDeal(d.name)"
          >
            <div class="truncate font-medium text-ink-gray-9">
              {{ d.title }}
            </div>
            <div class="mt-0.5 text-sm text-ink-gray-7">
              {{ fmt(d.amount) }}
            </div>
            <div class="mt-2 flex items-center gap-2">
              <Badge v-if="d.product" variant="subtle" theme="blue" size="sm">
                {{ d.product }}
              </Badge>
              <div class="ml-auto flex items-center gap-2">
                <span class="text-xs text-ink-gray-5">{{ d.closeLabel }}</span>
                <Avatar
                  v-if="d.owner"
                  size="sm"
                  :label="d.owner.label"
                  :image="d.owner.image"
                  :title="d.owner.label"
                />
              </div>
            </div>
          </div>
          <div
            v-if="!col.deals.length"
            class="py-6 text-center text-xs text-ink-gray-4"
          >
            {{ __('Sin oportunidades') }}
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

// Traer TODAS las oportunidades (limit_page_length: 0), sin paginar,
// para que cada una aparezca en su columna de estado.
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
  const u = d.deal_owner ? getUser(d.deal_owner) : null
  return {
    name: d.name,
    title: d.organization || d.name,
    amount: d.annual_revenue || 0,
    product: d.custom_producto || '',
    closeLabel: closeLabel(d.expected_closure_date),
    owner: u ? { label: u.full_name, image: u.user_image } : null,
  }
}

const columns = computed(() => {
  const groups = {}
  for (const d of deals.data || []) {
    const s = d.status || '—'
    if (!groups[s]) groups[s] = []
    groups[s].push(d)
  }
  // Una columna por cada estado del funnel (aunque no tenga deals) + cualquier
  // estado presente en los datos que no esté en la lista.
  const allStatuses = (dealStatuses?.data || []).map((s) => s.name)
  const statusSet = [...new Set([...allStatuses, ...Object.keys(groups)])]
  const cols = statusSet.map((s) => {
    const list = groups[s] || []
    const sorted = list
      .slice()
      .sort((a, b) => {
        const av = a.expected_closure_date || '9999-12-31'
        const bv = b.expected_closure_date || '9999-12-31'
        return av < bv ? -1 : av > bv ? 1 : 0
      })
      .map(mapCard)
    const amount = list.reduce((x, d) => x + (d.annual_revenue || 0), 0)
    return {
      status: s,
      position: getDealStatus(s)?.position ?? 999,
      color: getDealStatus(s)?.color || '#8b8b8b',
      count: sorted.length,
      amount,
      deals: sorted,
    }
  })
  cols.sort((a, b) => a.position - b.position)
  const maxAmount = Math.max(1, ...cols.map((c) => c.amount))
  return cols.map((c) => ({
    ...c,
    pct: Math.round((c.amount / maxAmount) * 100),
  }))
})

function openDeal(name) {
  router.push({ name: 'Deal', params: { dealId: name } })
}

usePageMeta(() => ({ title: __('Pipeline') }))
</script>
