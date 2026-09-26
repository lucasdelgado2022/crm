<template>
  <div class="flex flex-col gap-4 overflow-y-auto p-3 sm:p-5">
    <div
      v-for="sec in sections"
      :key="sec.key"
      class="rounded-lg border"
    >
      <div
        class="flex items-center justify-between gap-2 border-b px-4 py-3"
      >
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
          {{ __('Sin documentos vinculados') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Link from '@/components/Controls/Link.vue'
import { Badge, FeatherIcon, call, toast } from 'frappe-ui'
import { reactive } from 'vue'

const props = defineProps({
  doctype: { type: String, default: 'CRM Deal' },
  docname: { type: String, required: true },
})

const sections = [
  {
    key: 'quotation',
    label: __('Quotation'),
    doctype: 'Quotation',
    route: 'quotation',
    fields: ['name', 'status', 'grand_total', 'currency'],
  },
  {
    key: 'sales_order',
    label: __('Sales Order'),
    doctype: 'Sales Order',
    route: 'sales-order',
    fields: ['name', 'status', 'grand_total', 'currency'],
  },
  {
    key: 'sales_invoice',
    label: __('Sales Invoice'),
    doctype: 'Sales Invoice',
    route: 'sales-invoice',
    fields: ['name', 'status', 'grand_total', 'currency'],
  },
  {
    key: 'purchase_invoice',
    label: __('Purchase Invoice'),
    doctype: 'Purchase Invoice',
    route: 'purchase-invoice',
    fields: ['name', 'status', 'grand_total', 'currency'],
  },
  {
    key: 'payment_entry',
    label: __('Payment Entry'),
    doctype: 'Payment Entry',
    route: 'payment-entry',
    fields: ['name', 'status', 'paid_amount'],
  },
]

const data = reactive({})

function filtersFor(sec) {
  if (sec.doctype === 'Quotation') {
    return { quotation_to: 'CRM Deal', party_name: props.docname }
  }
  return { custom_crm_deal: props.docname }
}

async function loadSection(sec) {
  try {
    const rows = await call('frappe.client.get_list', {
      doctype: sec.doctype,
      filters: filtersFor(sec),
      fields: sec.fields,
      limit_page_length: 0,
      order_by: 'modified desc',
    })
    data[sec.key] = rows
  } catch (e) {
    data[sec.key] = []
  }
}

function loadAll() {
  sections.forEach(loadSection)
}
loadAll()

function amountOf(r) {
  const v = r.grand_total ?? r.paid_amount ?? 0
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
      encodeURIComponent(props.docname)
  } else {
    url =
      '/app/' +
      sec.route +
      '/new?custom_crm_deal=' +
      encodeURIComponent(props.docname)
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
        fieldname: { quotation_to: 'CRM Deal', party_name: props.docname },
      })
    } else {
      await call('frappe.client.set_value', {
        doctype: sec.doctype,
        name,
        fieldname: 'custom_crm_deal',
        value: props.docname,
      })
    }
    toast.success(__('Vinculado al deal'))
    loadSection(sec)
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error al vincular'))
  }
}
</script>
