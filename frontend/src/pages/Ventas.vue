<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="[{ label: __('Resumen Ventas'), route: { name: 'Ventas' } }]" />
    </template>
  </LayoutHeader>

  <div class="flex flex-wrap items-center justify-between gap-2 px-3 py-3 sm:px-5">
    <div class="text-base text-ink-gray-6">
      {{ __('{0} oportunidades ganadas', [rowCount]) }}
    </div>
    <div class="flex flex-wrap items-center gap-2">
      <div class="flex items-center gap-1">
        <span class="text-xs text-ink-gray-5">{{ __('Ordenar') }}:</span>
        <select
          v-model="sortBy"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="cierre">{{ __('Cierre') }}</option>
          <option value="monto">{{ __('Monto') }}</option>
          <option value="responsable">{{ __('Responsable') }}</option>
          <option value="tipo">{{ __('Tipo') }}</option>
          <option value="organization">{{ __('Organización') }}</option>
          <option value="numop">{{ __('N° Oportunidad') }}</option>
        </select>
        <button
          class="flex h-8 w-8 items-center justify-center rounded-lg border border-outline-gray-2 text-ink-gray-6 hover:bg-surface-gray-2"
          :title="sortDir === 'asc' ? __('Ascendente') : __('Descendente')"
          @click="sortDir = sortDir === 'asc' ? 'desc' : 'asc'"
        >
          <FeatherIcon :name="sortDir === 'asc' ? 'arrow-up' : 'arrow-down'" class="h-4 w-4" />
        </button>
      </div>
      <div class="flex items-center gap-1">
        <span class="text-xs text-ink-gray-5">{{ __('Agrupar') }}:</span>
        <select
          v-model="groupBy"
          class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        >
          <option value="none">{{ __('Ninguno') }}</option>
          <option value="responsable">{{ __('Responsable') }}</option>
          <option value="tipo">{{ __('Tipo') }}</option>
          <option value="cierre">{{ __('Cierre') }}</option>
          <option value="organization">{{ __('Organización') }}</option>
        </select>
      </div>
      <select
        v-model.number="year"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
      >
        <option :value="null">{{ __('Todos los años') }}</option>
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>
      <select
        v-model="respFilter"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        :title="__('Responsable')"
      >
        <option value="">{{ __('Todos los responsables') }}</option>
        <option v-for="o in respOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
      </select>
      <select
        v-model="orgFilter"
        class="h-8 max-w-48 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        :title="__('Organización')"
      >
        <option value="">{{ __('Todas las organizaciones') }}</option>
        <option v-for="o in orgOptions" :key="o" :value="o">{{ o }}</option>
      </select>
      <FormControl
        class="w-40"
        type="text"
        :placeholder="__('N° Oportunidad')"
        v-model="numopFilter"
      />
      <FormControl
        class="w-52"
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

  <div v-if="rowCount" class="flex flex-1 flex-col overflow-y-auto">
    <!-- Sin agrupar -->
    <ListView
      v-if="!groups"
      class="px-3 sm:px-5"
      :columns="columns"
      :rows="rows"
      row-key="name"
      :options="listOptions"
    >
      <template #cell="{ column, row, item }">
        <Badge
          v-if="STATUS_KEYS.includes(column.key)"
          :theme="row[column.key].theme"
          variant="subtle"
          size="sm"
        >
          {{ row[column.key].label }}
        </Badge>
        <div
          v-else-if="column.key === 'responsable'"
          class="flex min-w-0 items-center gap-2"
        >
          <UserAvatar v-if="row.owner" :user="row.owner" size="sm" />
          <span class="truncate text-base">{{ row.responsable }}</span>
        </div>
        <div v-else class="truncate text-base">{{ item }}</div>
      </template>
    </ListView>

    <!-- Agrupado -->
    <template v-else>
      <div v-for="g in groups" :key="g.key" class="mb-2">
        <div
          class="flex items-center justify-between border-y bg-surface-gray-1 px-3 py-2 text-sm font-semibold text-ink-gray-8 sm:px-5"
        >
          <span>
            {{ g.label }}
            <span class="font-normal text-ink-gray-5">({{ g.rows.length }})</span>
          </span>
          <span class="text-ink-gray-6">{{ g.subtotal }}</span>
        </div>
        <ListView
          class="px-3 sm:px-5"
          :columns="columns"
          :rows="g.rows"
          row-key="name"
          :options="listOptions"
        >
          <template #cell="{ column, row, item }">
            <Badge
              v-if="STATUS_KEYS.includes(column.key)"
              :theme="row[column.key].theme"
              variant="subtle"
              size="sm"
            >
              {{ row[column.key].label }}
            </Badge>
            <div
              v-else-if="column.key === 'responsable'"
              class="flex min-w-0 items-center gap-2"
            >
              <UserAvatar v-if="row.owner" :user="row.owner" size="sm" />
              <span class="truncate text-base">{{ row.responsable }}</span>
            </div>
            <div v-else class="truncate text-base">{{ item }}</div>
          </template>
        </ListView>
      </div>
    </template>
  </div>
  <div
    v-else
    class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
  >
    <LucideHandshake class="h-10 w-10" />
    <div>{{ __('Sin oportunidades ganadas') }}</div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideHandshake from '~icons/lucide/handshake'
import UserAvatar from '@/components/UserAvatar.vue'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import {
  Breadcrumbs,
  FormControl,
  FeatherIcon,
  Badge,
  ListView,
  call,
  usePageMeta,
} from 'frappe-ui'
import { ref, computed } from 'vue'

const { getFormattedCurrency } = getMeta('CRM Deal')
const { getUser } = usersStore()

const STATUS_KEYS = ['entrega', 'factura', 'cobro', 'prov', 'comision']

const search = ref('')
const year = ref(null)
const sortBy = ref('cierre')
const sortDir = ref('desc')
const groupBy = ref('none')
const respFilter = ref('')
const orgFilter = ref('')
const numopFilter = ref('')
const deals = ref([])
const maps = ref({ entrega: {}, factura: {}, cobro: {}, prov: {}, comision: {} })

const listOptions = {
  selectable: false,
  showTooltip: false,
  getRowRoute: (row) => ({ name: 'VentaRelacion', params: { dealId: row.name } }),
}

async function loadAll() {
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
      'custom_numero_solaer',
      'annual_revenue',
      'closed_date',
      'custom_comisiones_data',
      'deal_owner',
      'custom_cierre_mes',
      'custom_tipo_oportunidad',
    ],
    limit_page_length: 0,
  })

  const groupByDeal = async (dt, key, extra, fields) => {
    try {
      const r = await call('frappe.client.get_list', {
        doctype: dt,
        filters: { ...(extra || {}), custom_crm_deal: ['is', 'set'] },
        fields,
        limit_page_length: 0,
        order_by: 'modified desc',
      })
      const m = {}
      for (const x of r) (m[x.custom_crm_deal] = m[x.custom_crm_deal] || []).push(x)
      maps.value[key] = m
    } catch (e) {
      maps.value[key] = {}
    }
  }
  await groupByDeal('Delivery Note', 'entrega', null, ['custom_crm_deal', 'status', 'docstatus'])
  await groupByDeal('Sales Invoice', 'factura', null, ['custom_crm_deal', 'status', 'docstatus'])
  await groupByDeal('Payment Entry', 'cobro', { payment_type: 'Receive' }, ['custom_crm_deal', 'status', 'docstatus'])
  await groupByDeal('Purchase Invoice', 'prov', null, ['custom_crm_deal', 'custom_estado_pago', 'docstatus'])
  const cm = {}
  for (const d of deals.value) {
    let arr = []
    try {
      arr = JSON.parse(d.custom_comisiones_data || '[]') || []
    } catch (e) {
      arr = []
    }
    cm[d.name] = arr
  }
  maps.value.comision = cm
}
loadAll()

const STATUS_MAP = {
  Draft: { label: __('Borrador'), theme: 'orange' },
  Paid: { label: __('Pagada'), theme: 'green' },
  Unpaid: { label: __('Impaga'), theme: 'red' },
  Overdue: { label: __('Vencida'), theme: 'red' },
  Completed: { label: __('Completada'), theme: 'green' },
  Submitted: { label: __('Confirmado'), theme: 'green' },
  'To Bill': { label: __('A facturar'), theme: 'blue' },
  'To Deliver': { label: __('A entregar'), theme: 'blue' },
  'To Deliver and Bill': { label: __('A entregar/facturar'), theme: 'blue' },
  Closed: { label: __('Cerrada'), theme: 'gray' },
}
const PAGO_THEME = { Pagado: 'green', Parcial: 'blue', Vencido: 'red', Pendiente: 'orange' }

function docInfo(list) {
  if (!list || !list.length) return { label: '—', theme: 'gray' }
  const latest = list[0]
  const st = latest.status || (latest.docstatus === 1 ? 'Completed' : 'Draft')
  return STATUS_MAP[st] || { label: st, theme: latest.docstatus === 1 ? 'blue' : 'orange' }
}
function provInfo(list) {
  if (!list || !list.length) return { label: '—', theme: 'gray' }
  const v = list[0].custom_estado_pago || 'Pendiente'
  return { label: v, theme: PAGO_THEME[v] || 'orange' }
}
function comisionInfo(arr) {
  if (!arr || !arr.length) return { label: '—', theme: 'gray' }
  const estados = arr.map((c) => c.estado || 'Pendiente')
  if (estados.every((e) => e === 'Pagado')) return { label: __('Pagado'), theme: 'green' }
  if (estados.some((e) => e === 'Pendiente')) return { label: __('Pendiente'), theme: 'orange' }
  return { label: __('Aprobado'), theme: 'blue' }
}

function fmt(v) {
  try {
    return getFormattedCurrency('annual_revenue', { annual_revenue: v || 0 })
  } catch (e) {
    return v || 0
  }
}

const columns = [
  { label: __('N° Oportunidad'), key: 'numop', width: '7.5rem' },
  { label: __('Organización'), key: 'organization', width: '14rem' },
  { label: __('Responsable'), key: 'responsable', width: '12rem' },
  { label: __('Tipo'), key: 'tipo', width: '11rem' },
  { label: __('Cierre'), key: 'cierre', width: '8rem' },
  { label: __('Monto'), key: 'monto', width: '9rem' },
  { label: __('Entrega'), key: 'entrega', width: '8rem' },
  { label: __('Factura'), key: 'factura', width: '8rem' },
  { label: __('Cobros'), key: 'cobro', width: '8rem' },
  { label: __('Pago Prov'), key: 'prov', width: '8rem' },
  { label: __('Comisiones'), key: 'comision', width: '8rem' },
]

const years = computed(() => {
  const s = new Set()
  for (const d of deals.value) if (d.closed_date) s.add(Number(String(d.closed_date).slice(0, 4)))
  return [...s].sort((a, b) => b - a)
})

const respOptions = computed(() => {
  const m = {}
  for (const d of deals.value) {
    if (!d.deal_owner) continue
    m[d.deal_owner] = getUser(d.deal_owner)?.full_name || d.deal_owner
  }
  return Object.entries(m)
    .map(([value, label]) => ({ value, label }))
    .sort((a, b) => a.label.localeCompare(b.label))
})
const orgOptions = computed(() => {
  const st = new Set()
  for (const d of deals.value) if (d.organization) st.add(d.organization)
  return [...st].sort((a, b) => a.localeCompare(b))
})

const rows = computed(() => {
  let data = deals.value
  if (year.value) {
    data = data.filter((d) => d.closed_date && Number(String(d.closed_date).slice(0, 4)) === year.value)
  }
  if (respFilter.value) data = data.filter((d) => d.deal_owner === respFilter.value)
  if (orgFilter.value) data = data.filter((d) => (d.organization || '') === orgFilter.value)
  if (numopFilter.value) {
    const nq = numopFilter.value.toLowerCase()
    data = data.filter((d) =>
      String(d.custom_numero_solaer || d.name || '').toLowerCase().includes(nq),
    )
  }
  if (search.value) {
    const q = search.value.toLowerCase()
    data = data.filter(
      (d) =>
        (d.organization || '').toLowerCase().includes(q) ||
        (d.custom_numero_solaer || d.name || '').toLowerCase().includes(q) ||
        (d.deal_owner ? getUser(d.deal_owner)?.full_name || d.deal_owner : '').toLowerCase().includes(q),
    )
  }
  const mapped = data.map((d) => ({
    name: d.name,
    numop: d.custom_numero_solaer || d.name,
    organization: d.organization || d.name,
    owner: d.deal_owner || '',
    responsable: d.deal_owner ? getUser(d.deal_owner)?.full_name || d.deal_owner : '',
    tipo: d.custom_tipo_oportunidad || '',
    cierre: d.custom_cierre_mes || '',
    monto: fmt(d.annual_revenue),
    _amt: Number(d.annual_revenue) || 0,
    _closed: d.closed_date || '',
    entrega: docInfo(maps.value.entrega[d.name]),
    factura: docInfo(maps.value.factura[d.name]),
    cobro: docInfo(maps.value.cobro[d.name]),
    prov: provInfo(maps.value.prov[d.name]),
    comision: comisionInfo(maps.value.comision[d.name]),
  }))
  const dir = sortDir.value === 'asc' ? 1 : -1
  mapped.sort((a, b) => {
    let va, vb
    if (sortBy.value === 'monto') {
      va = a._amt
      vb = b._amt
    } else if (sortBy.value === 'cierre') {
      va = a._closed
      vb = b._closed
    } else {
      va = String(a[sortBy.value] || '').toLowerCase()
      vb = String(b[sortBy.value] || '').toLowerCase()
    }
    if (va < vb) return -1 * dir
    if (va > vb) return 1 * dir
    return 0
  })
  return mapped
})

const rowCount = computed(() => rows.value.length)

const groups = computed(() => {
  if (groupBy.value === 'none') return null
  const m = new Map()
  for (const r of rows.value) {
    const key =
      (groupBy.value === 'responsable'
        ? r.responsable
        : groupBy.value === 'tipo'
          ? r.tipo
          : groupBy.value === 'cierre'
            ? r.cierre
            : r.organization) || '—'
    if (!m.has(key)) m.set(key, [])
    m.get(key).push(r)
  }
  return [...m.entries()].map(([key, rws]) => ({
    key,
    label: key,
    rows: rws,
    subtotal: fmt(rws.reduce((a, r) => a + r._amt, 0)),
  }))
})

usePageMeta(() => ({ title: __('Resumen Ventas') }))
</script>
