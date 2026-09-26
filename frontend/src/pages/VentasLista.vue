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
    <div class="flex items-center gap-2">
      <template v-if="cfg.asociable">
        <label class="flex cursor-pointer items-center gap-1.5 text-sm text-ink-gray-7">
          <input v-model="verSinAsociar" type="checkbox" class="rounded" />
          {{ __('Sin asociar') }}
        </label>
        <Button variant="solid" @click="nuevoPagoProv">
          <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
          {{ __('Nuevo Pago Prov') }}
        </Button>
      </template>
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
        <div
          v-else-if="column.key === 'deal' && cfg.asociable"
          class="w-full"
          @click.stop
        >
          <Link
            doctype="CRM Deal"
            :value="row.deal"
            :placeholder="__('Asociar a venta...')"
            @change="(v) => setDeal(row.name, v)"
          />
        </div>
        <RouterLink
          v-else-if="column.key === 'deal' && row.deal"
          :to="{ name: 'VentaRelacion', params: { dealId: row.deal } }"
          class="truncate text-ink-blue-link"
          >{{ row.numop }}</RouterLink
        >
        <input
          v-else-if="column.key === 'numfactura'"
          type="text"
          :value="row.numfactura"
          :placeholder="__('N° factura')"
          class="w-full rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 text-sm text-ink-gray-8 focus:outline-none"
          @click.stop
          @change="(e) => setNumFactura(row.name, e.target.value)"
        />
        <a
          v-else-if="column.key === 'abrir'"
          :href="'/app/' + cfg.route + '/' + encodeURIComponent(row.name)"
          target="_blank"
          class="inline-flex h-7 w-7 items-center justify-center rounded hover:bg-surface-gray-2"
          :title="__('Abrir en ERP')"
          @click.stop
        >
          <FeatherIcon name="external-link" class="h-4 w-4 text-ink-gray-6" />
        </a>
        <div
          v-else-if="column.key === 'company'"
          class="w-full"
          @click.stop
        >
          <Link
            doctype="Company"
            :value="row.company"
            @change="(v) => setCompany(row.name, v)"
          />
        </div>
        <select
          v-else-if="column.key === 'estadopago'"
          :value="row.estadopago"
          class="w-full rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 text-sm text-ink-gray-8 focus:outline-none"
          @click.stop
          @change="(e) => setEstado(row.name, e.target.value)"
        >
          <option v-for="o in ESTADOS" :key="o" :value="o">{{ o }}</option>
        </select>
        <input
          v-else-if="column.key === 'fechapago'"
          type="date"
          :value="row.fechapago"
          class="w-full rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 text-sm text-ink-gray-8 focus:outline-none"
          @click.stop
          @change="(e) => setFecha(row.name, e.target.value)"
        />
        <div
          v-else-if="column.key === 'adjunto'"
          class="flex w-full items-center gap-1.5 rounded"
          :class="dropTarget === row.name ? 'bg-surface-blue-2 ring-1 ring-outline-blue-2' : ''"
          @drop.prevent="onDrop($event, row.name)"
          @dragover.prevent="dropTarget = row.name"
          @dragenter.prevent="dropTarget = row.name"
          @dragleave.prevent="dropTarget = null"
        >
          <button
            v-for="a in attByPi[row.name] || []"
            :key="a.name"
            :title="a.file_name"
            class="flex items-center gap-1 rounded px-1 py-0.5 hover:bg-surface-gray-3"
            @click.stop="openFile(a)"
          >
            <FilePdfIcon class="h-4 w-4" />
          </button>
          <span v-if="uploadingFor === row.name" class="text-xs text-ink-gray-5">
            {{ __('Subiendo…') }}
          </span>
          <button
            v-else
            class="flex items-center gap-1 rounded border border-dashed border-outline-gray-2 px-2 py-0.5 text-xs text-ink-gray-5 hover:bg-surface-gray-2"
            @click.stop="triggerUpload(row.name)"
          >
            <FeatherIcon name="paperclip" class="h-3.5 w-3.5" />
            {{ (attByPi[row.name] || []).length ? __('Otro') : __('Adjuntar') }}
          </button>
        </div>
        <button
          v-else-if="column.key === 'comentarios'"
          class="flex items-center gap-1 rounded border border-outline-gray-2 px-2 py-0.5 text-xs text-ink-gray-6 hover:bg-surface-gray-2"
          @click.stop="openComments(row.name)"
        >
          <FeatherIcon name="message-square" class="h-3.5 w-3.5" />
          <span v-if="(commentsByDoc[row.name] || []).length">
            {{ (commentsByDoc[row.name] || []).length }}
          </span>
          <span v-else>{{ __('Comentar') }}</span>
        </button>
        <select
          v-else-if="column.key === 'estadoentrega'"
          :value="row.estadoEntrega"
          class="w-full rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 text-sm text-ink-gray-8 focus:outline-none"
          @click.stop
          @change="(e) => setEstadoEntrega(row.name, e.target.value)"
        >
          <option v-for="o in ESTADOS_ENTREGA" :key="o" :value="o">{{ o }}</option>
        </select>
        <input
          v-else-if="column.key === 'fechacomprometida'"
          type="date"
          :value="row.fechaComprometida"
          class="w-full rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 text-sm text-ink-gray-8 focus:outline-none"
          @click.stop
          @change="(e) => setFechaComprometida(row.name, e.target.value)"
        />
        <div
          v-else-if="column.key === 'responsableentrega'"
          class="w-full"
          @click.stop
        >
          <Link
            doctype="HD Agent"
            :value="row.responsable"
            @change="(v) => setResponsable(row.name, v)"
          />
        </div>
        <div v-else-if="column.key === 'ordenhd'" @click.stop>
          <a
            v-if="row.hdTicket"
            :href="'/helpdesk/tickets/' + encodeURIComponent(row.hdTicket)"
            target="_blank"
            class="inline-flex items-center gap-1 rounded border border-outline-gray-2 px-2 py-0.5 text-xs text-ink-blue-link hover:bg-surface-gray-2"
            :title="__('Abrir en Help Desk')"
          >
            <FeatherIcon name="life-buoy" class="h-3.5 w-3.5" />
            #{{ row.hdTicket }}
            <span v-if="ticketStatus[row.hdTicket]" class="text-ink-gray-5">
              · {{ ticketStatus[row.hdTicket] }}
            </span>
          </a>
          <button
            v-else
            class="inline-flex items-center gap-1 rounded border border-dashed border-outline-gray-2 px-2 py-0.5 text-xs text-ink-gray-6 hover:bg-surface-gray-2"
            :disabled="creatingOrden === row.name"
            @click.stop="crearOrdenHD(row)"
          >
            <FeatherIcon name="plus" class="h-3.5 w-3.5" />
            {{ creatingOrden === row.name ? __('Creando…') : __('Crear orden') }}
          </button>
        </div>
        <select
          v-else-if="column.key === 'estadogestion'"
          :value="row.estadoGestion"
          class="w-full rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 text-sm text-ink-gray-8 focus:outline-none"
          @click.stop
          @change="(e) => setEstadoGestion(row.name, e.target.value)"
        >
          <option v-for="o in ESTADOS_FACT" :key="o" :value="o">{{ o || '—' }}</option>
        </select>
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

  <input
    ref="fileInput"
    type="file"
    accept="application/pdf,image/*"
    class="hidden"
    @change="onFileSelected"
  />

  <Dialog v-model="showPreview" :options="{ size: '5xl' }">
    <template #body>
      <div class="flex h-full flex-col p-4">
        <div class="mb-3 flex items-center justify-between gap-2">
          <div class="truncate text-base font-semibold text-ink-gray-8">
            {{ previewFile?.file_name }}
          </div>
          <div class="flex shrink-0 gap-2">
            <Button
              :tooltip="__('Abrir en pestaña')"
              icon="external-link"
              @click="openInTab"
            />
            <Button :tooltip="__('Cerrar')" icon="x" @click="showPreview = false" />
          </div>
        </div>
        <img
          v-if="previewFile && isImage(previewFile.file_type)"
          :src="previewFile.file_url"
          :alt="previewFile.file_name"
          class="max-h-[72vh] w-full rounded border object-contain"
        />
        <iframe
          v-else-if="previewFile"
          :src="previewFile.file_url"
          class="h-[72vh] w-full rounded border"
        />
      </div>
    </template>
  </Dialog>

  <!-- Comentarios -->
  <Dialog v-model="showComments" :options="{ size: 'lg' }">
    <template #body>
      <div class="p-4">
        <div class="mb-3 text-base font-semibold text-ink-gray-8">
          {{ __('Comentarios') }}
          <span class="font-normal text-ink-gray-5">· {{ commentsFor }}</span>
        </div>
        <div class="mb-3 max-h-72 space-y-2 overflow-y-auto">
          <div
            v-if="!(commentsByDoc[commentsFor] || []).length"
            class="py-4 text-center text-sm text-ink-gray-4"
          >
            {{ __('Sin comentarios') }}
          </div>
          <div
            v-for="cmt in commentsByDoc[commentsFor] || []"
            :key="cmt.name"
            class="rounded-lg border p-2"
          >
            <div class="flex items-center gap-2 text-xs text-ink-gray-5">
              <UserAvatar :user="cmt.comment_email || cmt.owner" size="xs" />
              <span class="font-medium text-ink-gray-7">
                {{ cmt.comment_by || userName(cmt.owner) }}
              </span>
              <span>·
                {{ cmt.creation ? String(cmt.creation).slice(0, 16).replace('T', ' ') : '' }}
              </span>
            </div>
            <div class="mt-1 text-sm text-ink-gray-8" v-html="cmt.content" />
          </div>
        </div>
        <div class="flex items-end gap-2">
          <textarea
            v-model="newComment"
            rows="2"
            :placeholder="__('Escribí un comentario...')"
            class="flex-1 rounded-lg border border-outline-gray-2 bg-surface-base px-2 py-1.5 text-sm text-ink-gray-8 focus:outline-none"
          />
          <Button
            variant="solid"
            :loading="savingComment"
            :disabled="!newComment.trim()"
            @click="addComment"
          >
            {{ __('Agregar') }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideReceipt from '~icons/lucide/receipt'
import FilePdfIcon from '@/components/Icons/FilePdfIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import { usersStore } from '@/stores/users'
import {
  Breadcrumbs,
  FormControl,
  FeatherIcon,
  ListView,
  Dialog,
  Button,
  call,
  toast,
  usePageMeta,
} from 'frappe-ui'
import { isImage } from '@/utils'
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'

const { getUser } = usersStore()
function userName(u) {
  return getUser(u)?.full_name || u
}

const props = defineProps({ tipo: { type: String, required: true } })

const ESTADOS = ['Pendiente', 'Pagado', 'Parcial', 'Vencido']
const TODAY = new Date().toISOString().slice(0, 10)
function daysBetween(a, b) {
  if (!a || !b) return ''
  return Math.round((new Date(b) - new Date(a)) / 86400000)
}

const CONFIGS = {
  entregas: { label: __('Entregas'), doctype: 'Delivery Note', route: 'delivery-note', amount: 'grand_total', hasStatus: true, entrega: true },
  facturas: { label: __('Facturas'), doctype: 'Sales Invoice', route: 'sales-invoice', amount: 'grand_total', hasStatus: true, invoiceNum: true, attach: true, estadoGestion: true },
  cobros: { label: __('Cobros'), doctype: 'Payment Entry', route: 'payment-entry', amount: 'paid_amount', hasStatus: true, extra: { payment_type: 'Receive' } },
  'pagos-prov': { label: __('Pagos Prov'), doctype: 'Purchase Invoice', route: 'purchase-invoice', amount: 'grand_total', hasStatus: true, prov: true, attach: true, hideDoc: true, asociable: true },
  impuestos: { label: __('Impuestos'), doctype: 'Journal Entry', route: 'journal-entry', amount: 'total_debit', hasStatus: false },
}
const cfg = computed(() => CONFIGS[props.tipo] || CONFIGS.entregas)

const ESTADOS_ENTREGA = ['Pendiente', 'En preparación', 'Despachada', 'Entregada']
const ESTADOS_FACT = ['', 'Pendiente', 'Enviada', 'Pagada', 'Vencida', 'Anulada']
const ticketStatus = ref({})
const creatingOrden = ref(null)

const search = ref('')
const data = ref([])
const attByPi = ref({})
const dealInfo = ref({})
const commentsByDoc = ref({})
const showComments = ref(false)
const commentsFor = ref('')
const newComment = ref('')
const savingComment = ref(false)

const verSinAsociar = ref(false)
async function load() {
  const c = cfg.value
  const fields = ['name', 'custom_crm_deal', c.amount]
  if (c.hasStatus) fields.push('status')
  if (c.doctype !== 'Journal Entry') fields.push('currency')
  if (c.prov) fields.push('posting_date', 'bill_date', 'due_date', 'custom_fecha_pago', 'custom_estado_pago', 'company')
  if (c.invoiceNum) fields.push('custom_numero_factura')
  if (c.entrega) fields.push('custom_estado_entrega', 'custom_fecha_comprometida', 'custom_responsable_entrega', 'custom_hd_ticket')
  if (c.estadoGestion) fields.push('custom_estado_gestion')
  try {
    data.value = await call('frappe.client.get_list', {
      doctype: c.doctype,
      filters: { ...(c.extra || {}), custom_crm_deal: ['is', c.asociable && verSinAsociar.value ? 'not set' : 'set'] },
      fields,
      limit_page_length: 0,
      order_by: 'modified desc',
    })
  } catch (e) {
    data.value = []
  }
  await loadDealInfo()
  await loadComments()
  if (c.attach) await loadAttachments()
  if (c.entrega) await loadTicketStatus()
}
load()
watch(() => props.tipo, load)

async function loadComments() {
  const names = (data.value || []).map((x) => x.name)
  if (!names.length) {
    commentsByDoc.value = {}
    return
  }
  try {
    const c = await call('frappe.client.get_list', {
      doctype: 'Comment',
      filters: {
        comment_type: 'Comment',
        reference_doctype: cfg.value.doctype,
        reference_name: ['in', names],
      },
      fields: ['name', 'reference_name', 'content', 'comment_by', 'comment_email', 'owner', 'creation'],
      limit_page_length: 0,
      order_by: 'creation asc',
    })
    const m = {}
    for (const x of c) (m[x.reference_name] = m[x.reference_name] || []).push(x)
    commentsByDoc.value = m
  } catch (e) {
    commentsByDoc.value = {}
  }
}
function openComments(name) {
  commentsFor.value = name
  newComment.value = ''
  showComments.value = true
}
async function addComment() {
  const text = newComment.value.trim()
  if (!text) return
  savingComment.value = true
  const me = getUser('sessionUser')
  try {
    await call('frappe.desk.form.utils.add_comment', {
      reference_doctype: cfg.value.doctype,
      reference_name: commentsFor.value,
      content: text,
      comment_email: me?.name,
      comment_by: me?.full_name || me?.name,
    })
    newComment.value = ''
    await loadComments()
    toast.success(__('Comentario agregado'))
  } catch (e) {
    toast.error(__('No se pudo agregar el comentario'))
  } finally {
    savingComment.value = false
  }
}

async function loadDealInfo() {
  const names = [...new Set((data.value || []).map((x) => x.custom_crm_deal).filter(Boolean))]
  if (!names.length) {
    dealInfo.value = {}
    return
  }
  try {
    const deals = await call('frappe.client.get_list', {
      doctype: 'CRM Deal',
      filters: { name: ['in', names] },
      fields: ['name', 'organization', 'custom_numero_solaer'],
      limit_page_length: 0,
    })
    const m = {}
    for (const d of deals) m[d.name] = d
    dealInfo.value = m
  } catch (e) {
    dealInfo.value = {}
  }
}

async function loadAttachments() {
  const names = (data.value || []).map((x) => x.name)
  if (!names.length) {
    attByPi.value = {}
    return
  }
  try {
    const files = await call('frappe.client.get_list', {
      doctype: 'File',
      filters: { attached_to_doctype: cfg.value.doctype, attached_to_name: ['in', names] },
      fields: ['name', 'file_name', 'file_url', 'file_type', 'attached_to_name'],
      limit_page_length: 0,
      order_by: 'creation desc',
    })
    const m = {}
    for (const f of files) (m[f.attached_to_name] = m[f.attached_to_name] || []).push(f)
    attByPi.value = m
  } catch (e) {
    attByPi.value = {}
  }
}

const columns = computed(() => {
  const c = cfg.value
  const base = []
  if (c.invoiceNum) {
    base.push({ label: __('N° Factura'), key: 'numfactura', width: '8rem' })
    base.push({ label: __('Abrir'), key: 'abrir', width: '5rem', align: 'center' })
  } else if (c.hideDoc) {
    base.push({ label: __('Abrir'), key: 'abrir', width: '5rem', align: 'center' })
  } else {
    base.push({ label: __('Documento'), key: 'name', width: '14rem' })
  }
  base.push({ label: __('Oportunidad'), key: 'deal', width: '7.5rem' })
  base.push({ label: __('Organización'), key: 'organization', width: '14rem' })
  base.push({ label: __('Monto'), key: 'monto', width: '10rem' })
  if (c.entrega) {
    base.push({ label: __('Estado entrega'), key: 'estadoentrega', width: '11rem' })
    base.push({ label: __('Fecha comprometida'), key: 'fechacomprometida', width: '10rem' })
    base.push({ label: __('Responsable'), key: 'responsableentrega', width: '13rem' })
    base.push({ label: __('Orden HD'), key: 'ordenhd', width: '12rem' })
  }
  if (c.prov) {
    base.push({ label: __('Company'), key: 'company', width: '13rem' })
    base.push({ label: __('Fecha de factura'), key: 'facturaDate', width: '9rem' })
    base.push({ label: __('Días de pago'), key: 'diasPago', width: '7rem' })
    base.push({ label: __('Edad'), key: 'edad', width: '6rem' })
    base.push({ label: __('Fecha de pago'), key: 'fechapago', width: '9rem' })
    base.push({ label: __('Estado del pago'), key: 'estadopago', width: '9rem' })
  } else if (c.hasStatus) {
    base.push({ label: __('Estado'), key: 'status', width: '9rem' })
  }
  if (c.estadoGestion)
    base.push({ label: __('Estado gestión'), key: 'estadogestion', width: '10rem' })
  if (c.attach)
    base.push({ label: __('Comprobante'), key: 'adjunto', width: '11rem' })
  base.push({ label: __('Comentarios'), key: 'comentarios', width: '10rem' })
  return base
})

const rows = computed(() => {
  const amt = cfg.value.amount
  let d = data.value
  if (search.value) {
    const q = search.value.toLowerCase()
    d = d.filter((x) => {
      const info = dealInfo.value[x.custom_crm_deal] || {}
      return (
        (x.name || '').toLowerCase().includes(q) ||
        (info.custom_numero_solaer || x.custom_crm_deal || '').toLowerCase().includes(q) ||
        (info.organization || '').toLowerCase().includes(q)
      )
    })
  }
  return d.map((x) => {
    const info = dealInfo.value[x.custom_crm_deal] || {}
    return {
      name: x.name,
      status: x.status || '',
      estadoEntrega: x.custom_estado_entrega || 'Pendiente',
      fechaComprometida: x.custom_fecha_comprometida || '',
      responsable: x.custom_responsable_entrega || '',
      hdTicket: x.custom_hd_ticket || '',
      estadoGestion: x.custom_estado_gestion || '',
      monto: x[amt] != null ? (x.currency || 'USD') + ' ' + Number(x[amt]).toLocaleString() : '',
      emision: x.posting_date || '',
      facturaDate: x.posting_date || '',
      company: x.company || '',
      moneda: x.currency || 'USD',
      diasPago: daysBetween(x.posting_date, x.due_date),
      edad: x.posting_date ? daysBetween(x.posting_date, TODAY) + ' d' : '',
      fechapago: x.custom_fecha_pago || '',
      estadopago: x.custom_estado_pago || 'Pendiente',
      numfactura: x.custom_numero_factura || '',
      deal: x.custom_crm_deal || '',
      numop: info.custom_numero_solaer || x.custom_crm_deal || '',
      organization: info.organization || '',
    }
  })
})

// ---------- edición inline ----------
async function setEstado(piName, value) {
  const row = data.value.find((x) => x.name === piName)
  if (row) row.custom_estado_pago = value
  try {
    await call('frappe.client.set_value', {
      doctype: cfg.value.doctype, name: piName,
      fieldname: 'custom_estado_pago', value,
    })
    toast.success(__('Estado actualizado'))
  } catch (e) {
    toast.error(__('No se pudo actualizar el estado'))
  }
}
async function setNumFactura(name, value) {
  const row = data.value.find((x) => x.name === name)
  if (row) row.custom_numero_factura = value
  try {
    await call('frappe.client.set_value', {
      doctype: cfg.value.doctype,
      name,
      fieldname: 'custom_numero_factura',
      value: value || null,
    })
    toast.success(__('N° de factura actualizado'))
  } catch (e) {
    toast.error(__('No se pudo actualizar'))
  }
}
async function setCompany(piName, value) {
  const row = data.value.find((x) => x.name === piName)
  if (row) row.company = value
  try {
    await call('frappe.client.set_value', {
      doctype: cfg.value.doctype,
      name: piName,
      fieldname: 'company',
      value: value || null,
    })
    toast.success(__('Company actualizada'))
  } catch (e) {
    toast.error(__('No se pudo actualizar la company'))
  }
}
async function setFecha(piName, value) {
  const row = data.value.find((x) => x.name === piName)
  if (row) row.custom_fecha_pago = value
  try {
    await call('frappe.client.set_value', {
      doctype: cfg.value.doctype, name: piName,
      fieldname: 'custom_fecha_pago', value: value || null,
    })
    toast.success(__('Fecha actualizada'))
  } catch (e) {
    toast.error(__('No se pudo actualizar la fecha'))
  }
}

// ---------- adjuntar / previsualizar ----------
const fileInput = ref(null)
const uploadingFor = ref(null)
const dropTarget = ref(null)
let pendingFor = null

function triggerUpload(piName) {
  pendingFor = piName
  fileInput.value?.click()
}
function onFileSelected(e) {
  const file = e.target.files?.[0]
  const target = pendingFor
  e.target.value = ''
  pendingFor = null
  if (file && target) uploadTo(target, file)
}
function onDrop(e, piName) {
  dropTarget.value = null
  const file = e.dataTransfer?.files?.[0]
  if (file) uploadTo(piName, file)
}
async function uploadTo(piName, file) {
  uploadingFor.value = piName
  try {
    const fd = new FormData()
    fd.append('file', file, file.name)
    fd.append('is_private', '1')
    fd.append('folder', 'Home/Attachments')
    fd.append('doctype', cfg.value.doctype)
    fd.append('docname', piName)
    const res = await fetch('/api/method/upload_file', {
      method: 'POST',
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token },
      body: fd,
    })
    if (!res.ok) throw new Error(await res.text())
    toast.success(__('Comprobante adjuntado'))
    await loadAttachments()
  } catch (err) {
    toast.error(__('No se pudo adjuntar el archivo'))
  } finally {
    uploadingFor.value = null
  }
}

const showPreview = ref(false)
const previewFile = ref(null)
function canPreview(type) {
  const t = (type || '').toLowerCase()
  return isImage(type) || t === 'pdf'
}
function openFile(att) {
  if (canPreview(att.file_type)) {
    previewFile.value = att
    showPreview.value = true
  } else {
    window.open(att.file_url, '_blank')
  }
}
function openInTab() {
  if (previewFile.value) window.open(previewFile.value.file_url, '_blank')
}

async function loadTicketStatus() {
  const names = (data.value || []).map((x) => x.custom_hd_ticket).filter(Boolean)
  if (!names.length) {
    ticketStatus.value = {}
    return
  }
  try {
    const rows = await call('frappe.client.get_list', {
      doctype: 'HD Ticket',
      filters: { name: ['in', names] },
      fields: ['name', 'status'],
      limit_page_length: 0,
    })
    const m = {}
    for (const r of rows) m[r.name] = r.status
    ticketStatus.value = m
  } catch (e) {
    ticketStatus.value = {}
  }
}

async function setEstadoGestion(name, value) {
  const row = data.value.find((x) => x.name === name)
  if (row) row.custom_estado_gestion = value
  try {
    await call('frappe.client.set_value', {
      doctype: cfg.value.doctype, name,
      fieldname: 'custom_estado_gestion', value: value || null,
    })
    toast.success(__('Estado de factura actualizado'))
  } catch (e) {
    toast.error(__('No se pudo actualizar'))
  }
}

async function setEstadoEntrega(name, value) {
  const row = data.value.find((x) => x.name === name)
  if (row) row.custom_estado_entrega = value
  try {
    await call('frappe.client.set_value', {
      doctype: cfg.value.doctype, name,
      fieldname: 'custom_estado_entrega', value,
    })
    toast.success(__('Estado de entrega actualizado'))
  } catch (e) {
    toast.error(__('No se pudo actualizar'))
  }
}

async function setFechaComprometida(name, value) {
  const row = data.value.find((x) => x.name === name)
  if (row) row.custom_fecha_comprometida = value
  try {
    await call('frappe.client.set_value', {
      doctype: cfg.value.doctype, name,
      fieldname: 'custom_fecha_comprometida', value: value || null,
    })
    toast.success(__('Fecha comprometida actualizada'))
  } catch (e) {
    toast.error(__('No se pudo actualizar'))
  }
}

async function setResponsable(name, value) {
  const row = data.value.find((x) => x.name === name)
  if (row) row.custom_responsable_entrega = value
  try {
    await call('frappe.client.set_value', {
      doctype: cfg.value.doctype, name,
      fieldname: 'custom_responsable_entrega', value: value || null,
    })
    toast.success(__('Responsable actualizado'))
  } catch (e) {
    toast.error(__('No se pudo actualizar'))
  }
}

async function crearOrdenHD(row) {
  if (creatingOrden.value) return
  creatingOrden.value = row.name
  try {
    const org = row.organization || ''
    const ticket = await call('frappe.client.insert', {
      doc: {
        doctype: 'HD Ticket',
        subject: __('Entrega') + ' ' + row.name + (org ? ' · ' + org : ''),
        description:
          __('Orden de entrega generada desde Ventas para el Delivery Note') +
          ' ' + row.name + '.',
        custom_delivery_note: row.name,
        raised_by: getUser('sessionUser')?.name || undefined,
      },
    })
    if (row.responsable) {
      try {
        await call('frappe.desk.form.assign_to.add', {
          doctype: 'HD Ticket',
          name: ticket.name,
          assign_to: JSON.stringify([row.responsable]),
        })
      } catch (e) {
        // asignación best-effort
      }
    }
    await call('frappe.client.set_value', {
      doctype: cfg.value.doctype, name: row.name,
      fieldname: 'custom_hd_ticket', value: ticket.name,
    })
    const d = data.value.find((x) => x.name === row.name)
    if (d) d.custom_hd_ticket = ticket.name
    ticketStatus.value = { ...ticketStatus.value, [ticket.name]: ticket.status || 'Open' }
    toast.success(__('Orden de entrega creada en Help Desk'))
  } catch (e) {
    toast.error(
      (e && e.messages && e.messages[0]) || __('No se pudo crear la orden'),
    )
  } finally {
    creatingOrden.value = null
  }
}

async function setDeal(piName, dealName) {
  const row = data.value.find((x) => x.name === piName)
  if (row) row.custom_crm_deal = dealName
  try {
    await call('frappe.client.set_value', {
      doctype: cfg.value.doctype,
      name: piName,
      fieldname: 'custom_crm_deal',
      value: dealName || null,
    })
    toast.success(dealName ? __('Asociado a la venta') : __('Desasociado'))
    load()
  } catch (e) {
    toast.error(__('No se pudo asociar'))
  }
}
function nuevoPagoProv() {
  window.open('/app/purchase-invoice/new', '_blank')
}
watch(verSinAsociar, load)

usePageMeta(() => ({ title: cfg.value.label }))
</script>
