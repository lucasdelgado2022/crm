<template>
  <div class="flex flex-col gap-4 overflow-y-auto p-3 sm:p-5">
    <!-- Línea de tiempo de hitos financieros -->
    <div class="rounded-lg border p-4">
      <div class="mb-1 text-base font-semibold text-ink-gray-8">
        {{ __('Línea de tiempo') }}
      </div>
      <div class="mb-4 text-xs text-ink-gray-5">
        {{ __('Hitos: Orden de Compra · Pago a Prov · Impuestos · Cobros') }}
      </div>
      <div
        v-if="milestones.length"
        class="relative mx-3 mb-10 mt-8 h-1 rounded bg-outline-gray-3"
      >
        <div
          v-for="(m, i) in milestones"
          :key="i"
          class="absolute top-1/2"
          :style="{ left: m.pct + '%' }"
        >
          <div class="flex -translate-x-1/2 -translate-y-1/2 flex-col items-center">
            <span
              class="h-3.5 w-3.5 rounded-full ring-2 ring-white"
              :style="{ backgroundColor: m.color }"
              :title="m.label + ' · ' + m.short + ' · ' + money(m.amount)"
            />
          </div>
          <div
            class="absolute left-1/2 top-3 -translate-x-1/2 whitespace-nowrap text-center text-[10px] leading-tight text-ink-gray-6"
          >
            {{ m.short }}
          </div>
        </div>
      </div>
      <div v-else class="mb-3 text-sm text-ink-gray-4">
        {{ __('Sin hitos con fecha cargada') }}
      </div>
      <!-- Leyenda -->
      <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-ink-gray-6">
        <span v-for="t in MILESTONES" :key="t.key" class="flex items-center gap-1.5">
          <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: t.color }" />
          {{ t.label }}
        </span>
      </div>
    </div>

    <!-- Tarjetas de resumen por documento -->
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <div
        v-for="s in resumen"
        :key="s.key"
        class="flex flex-col gap-3 rounded-lg border p-4"
      >
        <div
          class="flex items-center gap-2 text-base font-semibold text-ink-gray-8"
        >
          <FeatherIcon :name="s.icon" class="h-5 w-5 text-ink-gray-6" />
          {{ s.label }}
        </div>
        <div class="flex items-center justify-between">
          <Badge :theme="s.theme" variant="subtle" size="lg">
            {{ s.estado }}
          </Badge>
          <span v-if="s.count" class="text-sm text-ink-gray-5">
            {{ __('{0} doc.', [s.count]) }}
          </span>
        </div>
        <div v-if="s.monto" class="text-sm text-ink-gray-6">
          {{ __('Monto') }}: {{ money(s.monto) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon, Badge, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'

const props = defineProps({
  doctype: { type: String, default: 'CRM Deal' },
  docname: { type: String, required: true },
})

const SECS = [
  { key: 'so', label: __('Orden de Compra Cliente'), doctype: 'Sales Order', icon: 'file-text', amount: 'grand_total', hasStatus: true },
  { key: 'dn', label: __('Entrega'), doctype: 'Delivery Note', icon: 'truck', amount: 'grand_total', hasStatus: true },
  { key: 'si', label: __('Factura'), doctype: 'Sales Invoice', icon: 'file', amount: 'grand_total', hasStatus: true },
  { key: 'pe', label: __('Cobros'), doctype: 'Payment Entry', icon: 'dollar-sign', amount: 'paid_amount', hasStatus: false, extra: { payment_type: 'Receive' } },
]

// Hitos con fecha para la línea de tiempo
const MILESTONES = [
  { key: 'oc', label: __('Orden de Compra'), doctype: 'Sales Order', dateField: 'transaction_date', amount: 'grand_total', color: '#3b82f6', filters: {} },
  { key: 'prov', label: __('Pago a Prov'), doctype: 'Purchase Invoice', dateField: 'custom_fecha_pago', amount: 'grand_total', color: '#ef4444', filters: {} },
  { key: 'imp', label: __('Impuestos'), doctype: 'Journal Entry', dateField: 'posting_date', amount: 'total_debit', color: '#f59e0b', filters: {} },
  { key: 'cob', label: __('Cobros'), doctype: 'Payment Entry', dateField: 'posting_date', amount: 'paid_amount', color: '#16a34a', filters: { payment_type: 'Receive' } },
]

const data = ref({})
const mdata = ref({})

async function load() {
  const out = {}
  for (const s of SECS) {
    const fields = ['name', 'docstatus', s.amount]
    if (s.hasStatus) fields.push('status')
    try {
      out[s.key] = await call('frappe.client.get_list', {
        doctype: s.doctype,
        filters: { ...(s.extra || {}), custom_crm_deal: props.docname },
        fields,
        limit_page_length: 0,
        order_by: 'modified desc',
      })
    } catch (e) {
      out[s.key] = []
    }
  }
  data.value = out
}

async function loadMilestones() {
  const out = {}
  for (const m of MILESTONES) {
    try {
      out[m.key] = await call('frappe.client.get_list', {
        doctype: m.doctype,
        filters: {
          ...(m.filters || {}),
          custom_crm_deal: props.docname,
          [m.dateField]: ['is', 'set'],
        },
        fields: ['name', m.dateField, m.amount],
        limit_page_length: 0,
      })
    } catch (e) {
      out[m.key] = []
    }
  }
  mdata.value = out
}

function init() {
  load()
  loadMilestones()
}
init()
watch(() => props.docname, init)

const MESES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
function fmtShort(d) {
  const s = String(d).slice(0, 10)
  const [y, m, day] = s.split('-')
  const idx = parseInt(m, 10) - 1
  return `${parseInt(day, 10)} ${MESES[idx] || m}`
}

const milestones = computed(() => {
  const evs = []
  for (const m of MILESTONES) {
    for (const r of mdata.value[m.key] || []) {
      const dt = String(r[m.dateField] || '').slice(0, 10)
      if (!dt) continue
      evs.push({ date: dt, color: m.color, label: m.label, amount: Number(r[m.amount]) || 0 })
    }
  }
  evs.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0))
  if (!evs.length) return []
  const min = new Date(evs[0].date).getTime()
  const max = new Date(evs[evs.length - 1].date).getTime()
  const span = Math.max(1, max - min)
  return evs.map((e) => ({
    ...e,
    pct: max === min ? 50 : ((new Date(e.date).getTime() - min) / span) * 100,
    short: fmtShort(e.date),
  }))
})

const STATUS_MAP = {
  Draft: { label: __('Borrador'), theme: 'orange' },
  Paid: { label: __('Pagada'), theme: 'green' },
  Unpaid: { label: __('Impaga'), theme: 'red' },
  Overdue: { label: __('Vencida'), theme: 'red' },
  Completed: { label: __('Completada'), theme: 'green' },
  'To Bill': { label: __('A facturar'), theme: 'blue' },
  'To Deliver': { label: __('A entregar'), theme: 'blue' },
  'To Deliver and Bill': { label: __('A entregar y facturar'), theme: 'blue' },
  Closed: { label: __('Cerrada'), theme: 'gray' },
  Return: { label: __('Devolución'), theme: 'gray' },
  'Credit Note Issued': { label: __('Nota de crédito'), theme: 'gray' },
}

function summarize(s) {
  const list = data.value[s.key] || []
  if (!list.length)
    return { key: s.key, label: s.label, icon: s.icon, estado: __('Sin generar'), theme: 'gray', count: 0, monto: 0 }
  const monto = list.reduce((a, d) => a + (Number(d[s.amount]) || 0), 0)
  const latest = list[0]
  let info
  if (!s.hasStatus) {
    info = latest.docstatus === 1 ? { label: __('Confirmado'), theme: 'green' } : { label: __('Borrador'), theme: 'orange' }
  } else {
    const st = latest.status || (latest.docstatus === 1 ? 'Completed' : 'Draft')
    info = STATUS_MAP[st] || { label: st, theme: latest.docstatus === 1 ? 'blue' : 'orange' }
  }
  return { key: s.key, label: s.label, icon: s.icon, estado: info.label, theme: info.theme, count: list.length, monto }
}

const resumen = computed(() => SECS.map(summarize))

function money(n) {
  return 'USD ' + Math.round(Number(n) || 0).toLocaleString('es-AR')
}
</script>
