<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="[{ label: __('Ventas'), route: { name: 'Ventas' } }]" />
    </template>
  </LayoutHeader>

  <div class="flex items-center justify-between gap-2 px-3 py-3 sm:px-5">
    <div class="text-base text-ink-gray-6">
      {{ __('{0} oportunidades ganadas', [rows.length]) }}
    </div>
    <FormControl
      class="w-64"
      type="text"
      :placeholder="__('Buscar organización...')"
      v-model="search"
    >
      <template #prefix>
        <FeatherIcon name="search" class="h-4 w-4 text-ink-gray-5" />
      </template>
    </FormControl>
  </div>

  <div v-if="rows.length" class="flex flex-1 flex-col overflow-hidden">
    <ListView
      class="px-3 sm:px-5"
      :columns="columns"
      :rows="rows"
      row-key="name"
      :options="{
        selectable: false,
        showTooltip: false,
        getRowRoute: (row) => ({
          name: 'VentaRelacion',
          params: { dealId: row.name },
        }),
      }"
    />
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
import { getMeta } from '@/stores/meta'
import {
  Breadcrumbs,
  FormControl,
  FeatherIcon,
  ListView,
  createListResource,
  call,
  usePageMeta,
} from 'frappe-ui'
import { ref, reactive, computed } from 'vue'

const { getFormattedCurrency } = getMeta('CRM Deal')

const search = ref('')
const counts = reactive({
  delivery: {},
  invoice: {},
  cobro: {},
  prov: {},
  imp: {},
})

const deals = createListResource({
  type: 'list',
  doctype: 'CRM Deal',
  cache: ['ventas-won'],
  fields: ['name', 'organization', 'annual_revenue', 'deal_owner'],
  filters: {},
  pageLength: 0,
  auto: false,
})

async function loadAll() {
  const st = await call('frappe.client.get_list', {
    doctype: 'CRM Deal Status',
    filters: { type: 'Won' },
    fields: ['name'],
    limit_page_length: 0,
  })
  const wons = st.map((s) => s.name)
  deals.update({ filters: { status: ['in', wons] } })
  await deals.reload()
  const dealNames = (deals.data || []).map((d) => d.name)
  if (!dealNames.length) return

  const tally = async (dt, extra) => {
    try {
      const r = await call('frappe.client.get_list', {
        doctype: dt,
        filters: { ...(extra || {}), custom_crm_deal: ['in', dealNames] },
        fields: ['custom_crm_deal'],
        limit_page_length: 0,
      })
      const m = {}
      for (const x of r) m[x.custom_crm_deal] = (m[x.custom_crm_deal] || 0) + 1
      return m
    } catch (e) {
      return {}
    }
  }
  counts.delivery = await tally('Delivery Note')
  counts.invoice = await tally('Sales Invoice')
  counts.cobro = await tally('Payment Entry', { payment_type: 'Receive' })
  counts.prov = await tally('Purchase Invoice')
  counts.imp = await tally('Journal Entry')
}
loadAll()

function fmt(v) {
  try {
    return getFormattedCurrency('annual_revenue', { annual_revenue: v || 0 })
  } catch (e) {
    return v || 0
  }
}

const columns = [
  { label: __('Organización'), key: 'organization', width: '16rem' },
  { label: __('Monto'), key: 'monto', width: '9rem' },
  { label: __('Entregas'), key: 'delivery', width: '7rem', align: 'center' },
  { label: __('Facturas'), key: 'invoice', width: '7rem', align: 'center' },
  { label: __('Cobros'), key: 'cobro', width: '7rem', align: 'center' },
  { label: __('Pagos Prov'), key: 'prov', width: '8rem', align: 'center' },
  { label: __('Impuestos'), key: 'imp', width: '8rem', align: 'center' },
]

const rows = computed(() => {
  let data = deals.data || []
  if (search.value) {
    const q = search.value.toLowerCase()
    data = data.filter((d) => (d.organization || '').toLowerCase().includes(q))
  }
  return data.map((d) => ({
    name: d.name,
    organization: d.organization || d.name,
    monto: fmt(d.annual_revenue),
    delivery: counts.delivery[d.name] || 0,
    invoice: counts.invoice[d.name] || 0,
    cobro: counts.cobro[d.name] || 0,
    prov: counts.prov[d.name] || 0,
    imp: counts.imp[d.name] || 0,
  }))
})

usePageMeta(() => ({ title: __('Ventas') }))
</script>
