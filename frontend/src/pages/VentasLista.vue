<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs
        :items="[
          { label: __('Ventas'), route: { name: 'Ventas' } },
          { label: cfg.label, route: {} },
        ]"
      />
    </template>
  </LayoutHeader>

  <div class="flex items-center justify-between gap-2 px-3 py-3 sm:px-5">
    <div class="text-base text-ink-gray-6">
      {{ __('{0} registros', [rows.length]) }}
    </div>
    <FormControl
      class="w-64"
      type="text"
      :placeholder="__('Buscar...')"
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
      :options="{ selectable: false, showTooltip: false }"
    >
      <template #cell="{ column, row, item }">
        <a
          v-if="column.key === 'name'"
          :href="'/app/' + cfg.route + '/' + encodeURIComponent(row.name)"
          target="_blank"
          class="truncate text-ink-blue-link"
          >{{ row.name }}</a
        >
        <RouterLink
          v-else-if="column.key === 'deal' && row.deal"
          :to="{ name: 'VentaRelacion', params: { dealId: row.deal } }"
          class="truncate text-ink-blue-link"
          >{{ row.deal }}</RouterLink
        >
        <div v-else class="truncate text-base">{{ item }}</div>
      </template>
    </ListView>
  </div>
  <div
    v-else
    class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
  >
    <LucideReceipt class="h-10 w-10" />
    <div>{{ __('Sin registros vinculados al CRM') }}</div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideReceipt from '~icons/lucide/receipt'
import {
  Breadcrumbs,
  FormControl,
  FeatherIcon,
  ListView,
  call,
  usePageMeta,
} from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({ tipo: { type: String, required: true } })

const CONFIGS = {
  entregas: { label: __('Entregas'), doctype: 'Delivery Note', route: 'delivery-note', amount: 'grand_total', hasStatus: true },
  facturas: { label: __('Facturas'), doctype: 'Sales Invoice', route: 'sales-invoice', amount: 'grand_total', hasStatus: true },
  cobros: { label: __('Cobros'), doctype: 'Payment Entry', route: 'payment-entry', amount: 'paid_amount', hasStatus: true, extra: { payment_type: 'Receive' } },
  'pagos-prov': { label: __('Pagos Prov'), doctype: 'Purchase Invoice', route: 'purchase-invoice', amount: 'grand_total', hasStatus: true },
  impuestos: { label: __('Impuestos'), doctype: 'Journal Entry', route: 'journal-entry', amount: 'total_debit', hasStatus: false },
}
const cfg = computed(() => CONFIGS[props.tipo] || CONFIGS.entregas)

const search = ref('')
const data = ref([])

async function load() {
  const c = cfg.value
  const fields = ['name', 'custom_crm_deal', c.amount]
  if (c.hasStatus) fields.push('status')
  try {
    data.value = await call('frappe.client.get_list', {
      doctype: c.doctype,
      filters: { ...(c.extra || {}), custom_crm_deal: ['is', 'set'] },
      fields,
      limit_page_length: 0,
      order_by: 'modified desc',
    })
  } catch (e) {
    data.value = []
  }
}
load()
watch(() => props.tipo, load)

const columns = computed(() => {
  const base = [{ label: __('Documento'), key: 'name', width: '16rem' }]
  if (cfg.value.hasStatus) base.push({ label: __('Estado'), key: 'status', width: '9rem' })
  base.push({ label: __('Monto'), key: 'monto', width: '10rem' })
  base.push({ label: __('Oportunidad'), key: 'deal', width: '16rem' })
  return base
})

const rows = computed(() => {
  const amt = cfg.value.amount
  let d = data.value
  if (search.value) {
    const q = search.value.toLowerCase()
    d = d.filter(
      (x) =>
        (x.name || '').toLowerCase().includes(q) ||
        (x.custom_crm_deal || '').toLowerCase().includes(q),
    )
  }
  return d.map((x) => ({
    name: x.name,
    status: x.status || '',
    monto: x[amt] != null ? Number(x[amt]).toLocaleString() : '',
    deal: x.custom_crm_deal || '',
  }))
})

usePageMeta(() => ({ title: cfg.value.label }))
</script>
