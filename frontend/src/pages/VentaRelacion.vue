<template>
  <LayoutHeader v-if="!embedded">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>

  <div class="flex flex-col gap-4 overflow-y-auto p-3 sm:p-5">
    <!-- Resumen de la oportunidad -->
    <div v-if="!embedded" class="rounded-lg border p-4">
      <div class="text-lg font-semibold text-ink-gray-9">{{ dealTitle }}</div>
      <div class="mt-1 flex flex-wrap gap-4 text-sm text-ink-gray-6">
        <span>{{ __('Monto') }}: {{ fmt(deal.annual_revenue) }}</span>
        <span v-if="deal.custom_producto"
          >{{ __('Producto') }}: {{ deal.custom_producto }}</span
        >
        <span v-if="deal.territory"
          >{{ __('País del cliente') }}: {{ deal.territory }}</span
        >
        <span v-if="deal.deal_owner" class="flex items-center gap-1.5">
          {{ __('Responsable') }}:
          <UserAvatar :user="deal.deal_owner" size="xs" />
          {{ getUser(deal.deal_owner)?.full_name || deal.deal_owner }}
        </span>
        <a
          :href="'/crm/deals/' + encodeURIComponent(dealId)"
          class="text-ink-blue-link"
          >{{ __('Ver oportunidad') }}</a
        >
      </div>
    </div>

    <!-- Adjuntos de la oportunidad -->
    <div v-if="dealFiles.length" class="rounded-lg border p-4">
      <div class="mb-2 flex items-center gap-2 text-sm font-semibold text-ink-gray-8">
        <FeatherIcon name="paperclip" class="h-4 w-4" />
        {{ __('Adjuntos de la oportunidad') }}
      </div>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="f in dealFiles"
          :key="f.name"
          class="flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm"
          :class="f.custom_destacado ? 'border-amber-300 bg-amber-50' : 'border-outline-gray-2'"
        >
          <button
            :title="f.custom_destacado ? __('Quitar destacado') : __('Destacar')"
            @click="toggleDestacado(f)"
          >
            <FeatherIcon
              name="star"
              class="h-3.5 w-3.5"
              :class="f.custom_destacado ? 'text-amber-500' : 'text-ink-gray-4'"
            />
          </button>
          <button
            class="max-w-48 truncate text-left text-ink-blue-link hover:underline"
            @click="openFile(f)"
          >
            {{ f.file_name }}
          </button>
        </div>
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
          <Button
            variant="solid"
            @click="sec.key === 'so' ? openSoModal() : createNew(sec)"
          >
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
              <template v-if="sec.key === 'so'">
                <button
                  v-for="a in attByDoc[r.name] || []"
                  :key="a.name"
                  :title="a.file_name"
                  class="flex items-center rounded p-0.5 hover:bg-surface-gray-3"
                  @click.stop.prevent="openFile(a)"
                >
                  <FeatherIcon name="file-text" class="h-3.5 w-3.5 text-ink-blue-link" />
                </button>
                <button
                  class="flex items-center gap-1 rounded border border-dashed border-outline-gray-2 px-1.5 py-0.5 text-xs text-ink-gray-5 hover:bg-surface-gray-2"
                  :title="__('Adjuntar comprobante')"
                  @click.stop.prevent="triggerUpload(r.name)"
                >
                  <FeatherIcon name="paperclip" class="h-3 w-3" />
                  {{ uploadingFor === r.name ? __('Subiendo…') : __('Adjuntar') }}
                </button>
              </template>
            </span>
          </a>
        </div>
        <div v-else class="px-2 py-3 text-sm text-ink-gray-4">
          {{ __('Sin documentos') }}
        </div>
      </div>
    </div>
      <!-- Comisiones (solo en la vista de Ventas, no en el tab del CRM) -->
      <div v-if="!embedded" class="rounded-lg border">
        <div class="border-b px-4 py-3 text-base font-semibold text-ink-gray-8">
          {{ __('Comisiones') }}
        </div>
        <div class="p-2">
          <ComisionesArea doctype="CRM Deal" :docname="dealId" />
        </div>
      </div>
  <Dialog
    v-model="showSoModal"
    :options="{ title: __('Crear Orden de Compra Cliente'), size: '3xl' }"
  >
    <template #body-content>
      <div class="flex flex-col gap-3">
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <div class="mb-1 text-xs text-ink-gray-5">{{ __('Cliente') }}</div>
            <Link
              class="form-control"
              doctype="Customer"
              :value="soForm.customer"
              @change="(v) => (soForm.customer = v)"
            />
          </div>
          <div>
            <div class="mb-1 text-xs text-ink-gray-5">{{ __('Company') }}</div>
            <Link
              class="form-control"
              doctype="Company"
              :value="soForm.company"
              @change="(v) => (soForm.company = v)"
            />
          </div>
          <FormControl
            type="date"
            :label="__('Fecha')"
            v-model="soForm.transaction_date"
          />
          <FormControl
            type="date"
            :label="__('Entrega')"
            v-model="soForm.delivery_date"
          />
        </div>

        <div class="rounded-lg border">
          <div class="flex items-center justify-between border-b px-3 py-2">
            <span class="text-sm font-semibold text-ink-gray-8">{{ __('Ítems') }}</span>
            <Button variant="subtle" iconLeft="plus" :label="__('Agregar ítem')" @click="addSoItem" />
          </div>
          <table class="w-full text-sm">
            <thead class="text-xs text-ink-gray-5">
              <tr>
                <th class="px-2 py-1 text-left font-medium">{{ __('Ítem') }}</th>
                <th class="w-20 px-2 py-1 text-right font-medium">{{ __('Cant.') }}</th>
                <th class="w-28 px-2 py-1 text-right font-medium">{{ __('Precio USD') }}</th>
                <th class="w-28 px-2 py-1 text-right font-medium">{{ __('Total') }}</th>
                <th class="w-8"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(it, i) in soForm.items" :key="i" class="border-t">
                <td class="px-2 py-1">
                  <Link
                    class="form-control"
                    doctype="Item"
                    :value="it.item_code"
                    @change="(v) => (it.item_code = v)"
                  />
                </td>
                <td class="px-2 py-1">
                  <input
                    type="number"
                    class="w-full rounded border border-outline-gray-2 bg-surface-base px-1 py-0.5 text-right focus:outline-none"
                    v-model.number="it.qty"
                  />
                </td>
                <td class="px-2 py-1">
                  <input
                    type="number"
                    class="w-full rounded border border-outline-gray-2 bg-surface-base px-1 py-0.5 text-right focus:outline-none"
                    v-model.number="it.rate"
                  />
                </td>
                <td class="px-2 py-1 text-right text-ink-gray-8">
                  {{ usd((Number(it.qty) || 0) * (Number(it.rate) || 0)) }}
                </td>
                <td class="px-2 py-1 text-right">
                  <button @click="soForm.items.splice(i, 1)">
                    <FeatherIcon name="x" class="h-4 w-4 text-ink-gray-5 hover:text-ink-red-6" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="text-right text-sm font-semibold text-ink-gray-9">
          {{ __('Total') }}: {{ usd(soTotal) }}
        </div>

        <div>
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Adjunto (opcional)') }}</div>
          <input type="file" @change="(e) => (soForm.file = e.target.files[0])" />
        </div>
      </div>
    </template>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button @click="showSoModal = false">{{ __('Cancelar') }}</Button>
        <Button variant="solid" :loading="creatingSo" @click="createSalesOrder">
          {{ __('Crear orden') }}
        </Button>
      </div>
    </template>
  </Dialog>
  <Dialog
    v-model="showPreview"
    :options="{ title: previewFile?.file_name || __('Adjunto'), size: '4xl' }"
  >
    <template #body-content>
      <div class="flex flex-col gap-2">
        <iframe
          v-if="isPdf(previewFile)"
          :src="previewFile.file_url"
          class="h-[70vh] w-full rounded border"
        ></iframe>
        <img
          v-else-if="isImage(previewFile)"
          :src="previewFile.file_url"
          class="max-h-[70vh] w-full rounded object-contain"
        />
        <div v-else class="py-10 text-center text-sm text-ink-gray-5">
          {{ __('Vista previa no disponible para este tipo de archivo.') }}
        </div>
        <a
          v-if="previewFile"
          :href="previewFile.file_url"
          target="_blank"
          class="text-sm text-ink-blue-link"
          >{{ __('Abrir en pestaña nueva') }}</a
        >
      </div>
    </template>
  </Dialog>
  <input
    ref="soFileInput"
    type="file"
    class="hidden"
    @change="onSoFilePicked"
  />
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { usersStore } from '@/stores/users'
import ComisionesArea from '@/components/Activities/ComisionesArea.vue'
import { getMeta } from '@/stores/meta'
import {
  Breadcrumbs,
  Badge,
  FeatherIcon,
  Button,
  Dialog,
  FormControl,
  call,
  toast,
  usePageMeta,
} from 'frappe-ui'
import { reactive, ref, computed, watch } from 'vue'

const props = defineProps({
  dealId: { type: String, required: true },
  embedded: { type: Boolean, default: false },
})
const { getFormattedCurrency } = getMeta('CRM Deal')

const deal = ref({})
const dealTitle = computed(() => deal.value.organization || props.dealId)

const { getUser } = usersStore()
const dealFiles = ref([])
async function loadDealFiles() {
  try {
    dealFiles.value = await call('frappe.client.get_list', {
      doctype: 'File',
      filters: { attached_to_doctype: 'CRM Deal', attached_to_name: props.dealId },
      fields: ['name', 'file_name', 'file_url', 'custom_destacado'],
      limit_page_length: 0,
      order_by: 'custom_destacado desc, creation desc',
    })
  } catch (e) {
    dealFiles.value = []
  }
}
async function toggleDestacado(f) {
  const nv = f.custom_destacado ? 0 : 1
  f.custom_destacado = nv
  try {
    await call('frappe.client.set_value', {
      doctype: 'File',
      name: f.name,
      fieldname: 'custom_destacado',
      value: nv,
    })
    dealFiles.value = [...dealFiles.value].sort(
      (a, b) => (b.custom_destacado ? 1 : 0) - (a.custom_destacado ? 1 : 0),
    )
    toast.success(nv ? __('Destacado') : __('Quitado de destacados'))
  } catch (e) {
    f.custom_destacado = nv ? 0 : 1
    toast.error(__('No se pudo actualizar'))
  }
}

async function loadDeal() {
  try {
    deal.value = await call('frappe.client.get', {
      doctype: 'CRM Deal',
      name: props.dealId,
    })
  } catch (e) {
    deal.value = {}
  }
  loadDealFiles()
}

const breadcrumbs = computed(() => [
  { label: __('Ventas'), route: { name: 'Ventas' } },
  {
    label: dealTitle.value,
    route: { name: 'VentaRelacion', params: { dealId: props.dealId } },
  },
])

const sections = [
  { key: 'so', label: __('Orden de Compra Cliente'), doctype: 'Sales Order', route: 'sales-order', fields: ['name', 'status', 'grand_total', 'currency'] },
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
  if (sec.key === 'so') await loadSoAttachments()
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

const attByDoc = reactive({})
const uploadingFor = ref(null)
const soFileInput = ref(null)
let soUploadTarget = null

async function loadSoAttachments() {
  for (const k in attByDoc) delete attByDoc[k]
  const names = (data['so'] || []).map((r) => r.name)
  if (!names.length) return
  try {
    const files = await call('frappe.client.get_list', {
      doctype: 'File',
      filters: { attached_to_doctype: 'Sales Order', attached_to_name: ['in', names] },
      fields: ['name', 'file_name', 'file_url', 'attached_to_name'],
      limit_page_length: 0,
    })
    for (const f of files)
      (attByDoc[f.attached_to_name] = attByDoc[f.attached_to_name] || []).push(f)
  } catch (e) {
    // ignore
  }
}
function triggerUpload(name) {
  soUploadTarget = name
  if (soFileInput.value) soFileInput.value.click()
}
async function onSoFilePicked(e) {
  const file = e.target.files && e.target.files[0]
  if (!file || !soUploadTarget) return
  const target = soUploadTarget
  uploadingFor.value = target
  try {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('doctype', 'Sales Order')
    fd.append('docname', target)
    fd.append('is_private', '1')
    const res = await fetch('/api/method/upload_file', {
      method: 'POST',
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
      body: fd,
    })
    if (!res.ok) throw new Error('upload failed')
    toast.success(__('Comprobante adjuntado'))
    await loadSoAttachments()
  } catch (err) {
    toast.error(__('No se pudo adjuntar'))
  } finally {
    uploadingFor.value = null
    soUploadTarget = null
    e.target.value = ''
  }
}
const showPreview = ref(false)
const previewFile = ref(null)
function openFile(a) {
  previewFile.value = a
  showPreview.value = true
}
function isPdf(f) {
  return !!(f && /\.pdf(\?|$)/i.test(f.file_url || f.file_name || ''))
}
function isImage(f) {
  return !!(f && /\.(png|jpe?g|gif|webp|svg|bmp)(\?|$)/i.test(f.file_url || f.file_name || ''))
}

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

const showSoModal = ref(false)
const creatingSo = ref(false)
const soForm = ref({ customer: '', company: 'Grupo Solaer', transaction_date: '', delivery_date: '', items: [], file: null })
function isoDate(dt) {
  const p = (n) => String(n).padStart(2, '0')
  return dt.getFullYear() + '-' + p(dt.getMonth() + 1) + '-' + p(dt.getDate())
}
function usd(v) {
  return 'USD ' + Number(v || 0).toLocaleString()
}
const soTotal = computed(() =>
  (soForm.value.items || []).reduce(
    (a, it) => a + (Number(it.qty) || 0) * (Number(it.rate) || 0),
    0,
  ),
)
function addSoItem() {
  soForm.value.items.push({ item_code: '', qty: 1, rate: 0 })
}
function openSoModal() {
  const today = new Date()
  const d14 = new Date(Date.now() + 14 * 86400000)
  soForm.value = {
    customer: '',
    company: 'Grupo Solaer',
    transaction_date: isoDate(today),
    delivery_date: isoDate(d14),
    items: [{ item_code: '', qty: 1, rate: 0 }],
    file: null,
  }
  const org = deal.value.organization
  if (org) {
    call('frappe.client.get_value', {
      doctype: 'Customer',
      filters: { name: org },
      fieldname: 'name',
    })
      .then((r) => {
        if (r && r.name) soForm.value.customer = r.name
      })
      .catch(() => {})
  }
  showSoModal.value = true
}
async function createSalesOrder() {
  const f = soForm.value
  if (!f.customer) {
    toast.error(__('Elegí un cliente'))
    return
  }
  const items = (f.items || []).filter((it) => it.item_code)
  if (!items.length) {
    toast.error(__('Agregá al menos un ítem'))
    return
  }
  creatingSo.value = true
  try {
    const doc = await call('frappe.client.insert', {
      doc: {
        doctype: 'Sales Order',
        customer: f.customer,
        company: f.company || 'Grupo Solaer',
        currency: 'USD',
        conversion_rate: 1,
        price_list_currency: 'USD',
        plc_conversion_rate: 1,
        selling_price_list: 'Standard Selling',
        order_type: 'Sales',
        transaction_date: f.transaction_date,
        delivery_date: f.delivery_date,
        custom_crm_deal: props.dealId,
        items: items.map((it) => ({
          item_code: it.item_code,
          qty: Number(it.qty) || 1,
          rate: Number(it.rate) || 0,
          delivery_date: f.delivery_date,
        })),
      },
    })
    if (f.file) {
      try {
        const fd = new FormData()
        fd.append('file', f.file)
        fd.append('doctype', 'Sales Order')
        fd.append('docname', doc.name)
        fd.append('is_private', '1')
        await fetch('/api/method/upload_file', {
          method: 'POST',
          headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
          body: fd,
        })
      } catch (e) {
        // adjunto best-effort
      }
    }
    toast.success(__('Orden de compra creada'))
    showSoModal.value = false
    const so = sections.find((x) => x.key === 'so')
    if (so) loadSection(so)
  } catch (e) {
    toast.error((e && e.messages && e.messages[0]) || __('No se pudo crear la orden'))
  } finally {
    creatingSo.value = false
  }
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

if (!props.embedded)
  usePageMeta(() => ({ title: dealTitle.value || __('Venta') }))
</script>
