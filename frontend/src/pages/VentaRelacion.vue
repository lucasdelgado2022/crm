<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>

  <div class="flex flex-col gap-4 overflow-y-auto p-3 sm:p-5">
    <!-- Resumen de la oportunidad -->
    <div class="rounded-lg border p-4">
      <div class="text-lg font-semibold text-ink-gray-9">{{ dealTitle }}</div>
      <div class="mt-1 flex flex-wrap gap-4 text-sm text-ink-gray-6">
        <span>{{ __('Monto') }}: {{ fmt(deal.annual_revenue) }}</span>
        <span v-if="deal.custom_producto"
          >{{ __('Producto') }}: {{ deal.custom_producto }}</span
        >
        <span v-if="deal.deal_owner"
          >{{ __('Responsable') }}: {{ deal.deal_owner }}</span
        >
        <a
          :href="'/crm/deals/' + encodeURIComponent(dealId)"
          class="text-ink-blue-link"
          >{{ __('Ver oportunidad') }}</a
        >
      </div>
    </div>

    <!-- Cadena de documentos -->
    <div v-for="sec in sections" :key="sec.key" class="rounded-lg border">
      <div class="flex items-center justify-between gap-2 border-b px-4 py-3">
        <div
          class="flex items-center gap-2 text-base font-semibold text-ink-gray-8"
        >
          {{ sec.label }}
          <Badge variant="subtle" theme="gray" size="sm">
            {{ (data[sec.key] || []).length }}
          </Badge>
        </div>
        <div class="flex gap-2">
          <Link
            :doctype="sec.doctype"
            value=""
            @change="(v) => linkExisting(sec, v)"
          >
            <template #target="{ togglePopover }">
              <Button variant="outline" @click="togglePopover()">
                <template #prefix>
                  <FeatherIcon name="link" class="h-4" />
                </template>
                {{ __('Vincular') }}
              </Button>
            </template>
          </Link>
          <Button variant="solid" @click="createNew(sec)">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4" />
            </template>
            {{ __('Crear') }}
          </Button>
        </div>
      </div>
      <div class="p-2">
        <div v-if="(data[sec.key] || []).length" class="flex flex-col">
          <a
            v-for="r in data[sec.key]"
            :key="r.name"
            :href="'/app/' + sec.route + '/' + encodeURIComponent(r.name)"
            target="_blank"
            class="flex items-center justify-between gap-2 rounded px-2 py-1.5 hover:bg-surface-gray-2"
          >
            <span class="truncate text-sm text-ink-gray-8">{{ r.name }}</span>
            <span
              class="flex shrink-0 items-center gap-3 text-sm text-ink-gray-6"
            >
              <Badge v-if="r.status" variant="subtle" size="sm">
                {{ r.status }}
              </Badge>
              <span v-if="amountOf(r)">{{ amountOf(r) }}</span>
            </span>
          </a>
        </div>
        <div v-else class="px-2 py-3 text-sm text-ink-gray-4">
          {{ __('Sin documentos') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'
import { getMeta } from '@/stores/meta'
import {
  Breadcrumbs,
  Badge,
  FeatherIcon,
  call,
  toast,
  usePageMeta,
} from 'frappe-ui'
import { reactive, ref, computed, watch } from 'vue'

const props = defineProps({ dealId: { type: String, required: true } })
const { getFormattedCurrency } = getMeta('CRM Deal')

const deal = ref({})
const dealTitle = computed(() => deal.value.organization || props.dealId)

async function loadDeal() {
  try {
    deal.value = await call('frappe.client.get', {
      doctype: 'CRM Deal',
      name: props.dealId,
    })
  } catch (e) {
    deal.value = {}
  }
}

const breadcrumbs = computed(() => [
  { label: __('Ventas'), route: { name: 'Ventas' } },
  {
    label: dealTitle.value,
    route: { name: 'VentaRelacion', params: { dealId: props.dealId } },
  },
])

const sections = [
  { key: 'quotation', label: __('Quotation'), doctype: 'Quotation', route: 'quotation', fields: ['name', 'status', 'grand_total', 'currency'] },
  { key: 'so', label: __('Sales Order'), doctype: 'Sales Order', route: 'sales-order', fields: ['name', 'status', 'grand_total', 'currency'] },
  { key: 'dn', label: __('Orden de Entrega'), doctype: 'Delivery Note', route: 'delivery-note', fields: ['name', 'status', 'grand_total', 'currency'] },
  { key: 'si', label: __('Factura'), doctype: 'Sales Invoice', route: 'sales-invoice', fields: ['name', 'status', 'grand_total', 'currency'] },
  { key: 'cobro', label: __('Ingreso de Pago Cliente'), doctype: 'Payment Entry', route: 'payment-entry', fields: ['name', 'status', 'paid_amount'], extra: { payment_type: 'Receive' } },
  { key: 'pi', label: __('Pagos Proveedores'), doctype: 'Purchase Invoice', route: 'purchase-invoice', fields: ['name', 'status', 'grand_total', 'currency'] },
  { key: 'je', label: __('Impuestos'), doctype: 'Journal Entry', route: 'journal-entry', fields: ['name', 'total_debit', 'voucher_type'] },
]

const data = reactive({})

function filtersFor(sec) {
  if (sec.doctype === 'Quotation') {
    return { quotation_to: 'CRM Deal', party_name: props.dealId }
  }
  return { ...(sec.extra || {}), custom_crm_deal: props.dealId }
}

async function loadSection(sec) {
  try {
    data[sec.key] = await call('frappe.client.get_list', {
      doctype: sec.doctype,
      filters: filtersFor(sec),
      fields: sec.fields,
      limit_page_length: 0,
      order_by: 'modified desc',
    })
  } catch (e) {
    data[sec.key] = []
  }
}

function loadAll() {
  sections.forEach(loadSection)
}

loadDeal()
loadAll()
watch(
  () => props.dealId,
  () => {
    loadDeal()
    loadAll()
  },
)

function fmt(v) {
  try {
    return getFormattedCurrency('annual_revenue', { annual_revenue: v || 0 })
  } catch (e) {
    return v || 0
  }
}

function amountOf(r) {
  const v = r.grand_total ?? r.paid_amount ?? r.total_debit ?? 0
  if (!v) return ''
  return (r.currency ? r.currency + ' ' : '') + Number(v).toLocaleString()
}

function createNew(sec) {
  let url
  if (sec.doctype === 'Quotation') {
    url =
      '/app/quotation/new?quotation_to=' +
      encodeURIComponent('CRM Deal') +
      '&party_name=' +
      encodeURIComponent(props.dealId)
  } else {
    url =
      '/app/' +
      sec.route +
      '/new?custom_crm_deal=' +
      encodeURIComponent(props.dealId)
    if (sec.extra?.payment_type) url += '&payment_type=' + sec.extra.payment_type
  }
  window.open(url, '_blank')
}

async function linkExisting(sec, name) {
  if (!name) return
  try {
    if (sec.doctype === 'Quotation') {
      await call('frappe.client.set_value', {
        doctype: 'Quotation',
        name,
        fieldname: { quotation_to: 'CRM Deal', party_name: props.dealId },
      })
    } else {
      await call('frappe.client.set_value', {
        doctype: sec.doctype,
        name,
        fieldname: 'custom_crm_deal',
        value: props.dealId,
      })
    }
    toast.success(__('Vinculado'))
    loadSection(sec)
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error al vincular'))
  }
}

usePageMeta(() => ({ title: dealTitle.value || __('Venta') }))
</script>
