<template>
  <LayoutHeader v-if="evento">
    <template #left-header>
      <div class="flex items-center gap-2">
        <Button variant="ghost" iconLeft="arrow-left" :label="__('Eventos')" @click="volver" />
        <span class="text-lg font-semibold text-ink-gray-8">{{ evento.titulo }}</span>
        <Badge variant="subtle" :theme="tipoTheme(evento.tipo)" size="sm">{{ evento.tipo }}</Badge>
        <Badge variant="subtle" :theme="estadoTheme(evento.estado)" size="sm">{{ evento.estado }}</Badge>
      </div>
    </template>
    <template #right-header>
      <Button iconLeft="edit" :label="__('Editar datos')" @click="openEdit" />
    </template>
  </LayoutHeader>

  <div v-if="evento" class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Datos + métricas -->
    <div class="mb-5 grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div class="rounded-lg border p-4 lg:col-span-1">
        <div class="mb-2 text-sm font-semibold text-ink-gray-8">{{ __('Datos') }}</div>
        <dl class="flex flex-col gap-1.5 text-sm">
          <div class="flex justify-between gap-2"><dt class="text-ink-gray-5">{{ __('Modalidad') }}</dt><dd class="text-ink-gray-8">{{ evento.modalidad || '—' }}</dd></div>
          <div class="flex justify-between gap-2"><dt class="text-ink-gray-5">{{ __('Inicio') }}</dt><dd class="text-ink-gray-8">{{ evento.fecha_inicio || '—' }}</dd></div>
          <div class="flex justify-between gap-2"><dt class="text-ink-gray-5">{{ __('Fin') }}</dt><dd class="text-ink-gray-8">{{ evento.fecha_fin || '—' }}</dd></div>
          <div class="flex justify-between gap-2"><dt class="text-ink-gray-5">{{ __('Ubicación') }}</dt><dd class="truncate text-ink-gray-8">{{ evento.ubicacion || '—' }}</dd></div>
          <div class="flex justify-between gap-2"><dt class="text-ink-gray-5">{{ __('Responsable') }}</dt><dd class="text-ink-gray-8">{{ evento.responsable || '—' }}</dd></div>
        </dl>
        <div v-if="evento.descripcion" class="mt-2 border-t pt-2 text-sm text-ink-gray-6">{{ evento.descripcion }}</div>
      </div>
      <div class="grid grid-cols-2 gap-4 lg:col-span-2 lg:grid-cols-4">
        <div class="rounded-lg border p-4"><div class="text-2xl font-semibold text-ink-gray-9">{{ evento.participantes?.length || 0 }}</div><div class="text-sm text-ink-gray-5">{{ __('Inscriptos') }}</div></div>
        <div class="rounded-lg border p-4"><div class="text-2xl font-semibold text-ink-gray-9">{{ asistieron }}</div><div class="text-sm text-ink-gray-5">{{ __('Asistieron') }}</div></div>
        <div class="rounded-lg border p-4"><div class="text-2xl font-semibold text-ink-gray-9">{{ evento.leads?.length || 0 }}</div><div class="text-sm text-ink-gray-5">{{ __('Leads') }}</div></div>
        <div class="rounded-lg border p-4"><div class="text-2xl font-semibold text-ink-gray-9">{{ evento.oportunidades?.length || 0 }}</div><div class="text-sm text-ink-gray-5">{{ __('Oportunidades') }}</div></div>
      </div>
    </div>

    <!-- Participantes -->
    <div class="mb-5 rounded-lg border">
      <div class="flex items-center justify-between gap-2 border-b px-4 py-3">
        <div class="text-base font-semibold text-ink-gray-8">{{ __('Participantes') }}</div>
        <div class="flex items-center gap-2">
          <div class="w-56"><Link doctype="Contact" :value="''" :placeholder="__('Agregar contacto...')" @change="addParticipante" /></div>
          <Button variant="subtle" iconLeft="plus" :label="__('Fila manual')" @click="addManual" />
        </div>
      </div>
      <table v-if="evento.participantes?.length" class="w-full text-sm">
        <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
          <tr>
            <th class="px-4 py-2 text-left font-medium">{{ __('Nombre') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Email') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Contacto') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Estado') }}</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(p, i) in evento.participantes" :key="i" class="border-b last:border-0">
            <td class="px-4 py-1.5"><input :value="p.participante_nombre" class="w-full rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 focus:outline-none" @change="(e) => setPart(i, 'participante_nombre', e.target.value)" /></td>
            <td class="px-3 py-1.5"><input :value="p.email" class="w-full rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 focus:outline-none" @change="(e) => setPart(i, 'email', e.target.value)" /></td>
            <td class="px-3 py-1.5">
              <a v-if="p.contact" :href="'/crm/contacts/' + encodeURIComponent(p.contact)" target="_blank" class="text-ink-blue-link">{{ p.contact }}</a>
              <span v-else class="text-ink-gray-4">—</span>
            </td>
            <td class="px-3 py-1.5">
              <select :value="p.estado" class="rounded border border-outline-gray-2 bg-surface-base px-1.5 py-0.5 focus:outline-none" @change="(e) => setPart(i, 'estado', e.target.value)">
                <option v-for="o in ESTADOS_PART" :key="o" :value="o">{{ o }}</option>
              </select>
            </td>
            <td class="px-3 py-1.5 text-right"><button :title="__('Quitar')" @click="removePart(i)"><FeatherIcon name="x" class="h-4 w-4 text-ink-gray-5 hover:text-ink-red-6" /></button></td>
          </tr>
        </tbody>
      </table>
      <div v-else class="px-4 py-6 text-center text-sm text-ink-gray-4">{{ __('Sin participantes') }}</div>
    </div>

    <!-- Leads + Oportunidades -->
    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div class="rounded-lg border">
        <div class="flex items-center justify-between gap-2 border-b px-4 py-3">
          <div class="text-base font-semibold text-ink-gray-8">{{ __('Leads asociados') }}</div>
          <div class="w-52"><Link doctype="CRM Lead" :value="''" :placeholder="__('Asociar lead...')" @change="addLead" /></div>
        </div>
        <div class="flex flex-col gap-1 p-3">
          <div v-for="(l, i) in evento.leads || []" :key="i" class="flex items-center justify-between gap-2 rounded bg-surface-gray-1 px-2 py-1 text-sm">
            <a :href="'/crm/leads/' + encodeURIComponent(l.lead)" target="_blank" class="truncate text-ink-blue-link">{{ labels[l.lead] || l.lead }}</a>
            <button :title="__('Quitar')" @click="removeLead(i)"><FeatherIcon name="x" class="h-3.5 w-3.5 text-ink-gray-5 hover:text-ink-red-6" /></button>
          </div>
          <div v-if="!(evento.leads && evento.leads.length)" class="py-2 text-center text-sm text-ink-gray-4">{{ __('Sin leads') }}</div>
        </div>
      </div>
      <div class="rounded-lg border">
        <div class="flex items-center justify-between gap-2 border-b px-4 py-3">
          <div class="text-base font-semibold text-ink-gray-8">{{ __('Oportunidades asociadas') }}</div>
          <div class="w-52"><Link doctype="CRM Deal" :value="''" :placeholder="__('Asociar oportunidad...')" @change="addOpp" /></div>
        </div>
        <div class="flex flex-col gap-1 p-3">
          <div v-for="(o, i) in evento.oportunidades || []" :key="i" class="flex items-center justify-between gap-2 rounded bg-surface-gray-1 px-2 py-1 text-sm">
            <a :href="'/crm/deals/' + encodeURIComponent(o.deal)" target="_blank" class="truncate text-ink-blue-link">{{ labels[o.deal] || o.deal }}</a>
            <button :title="__('Quitar')" @click="removeOpp(i)"><FeatherIcon name="x" class="h-3.5 w-3.5 text-ink-gray-5 hover:text-ink-red-6" /></button>
          </div>
          <div v-if="!(evento.oportunidades && evento.oportunidades.length)" class="py-2 text-center text-sm text-ink-gray-4">{{ __('Sin oportunidades') }}</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Editar datos -->
  <Dialog v-model="showEdit" :options="{ title: __('Editar evento'), size: 'lg' }">
    <template #body-content>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <FormControl type="text" :label="__('Título')" v-model="form.titulo" class="sm:col-span-2" />
        <FormControl type="select" :label="__('Tipo')" v-model="form.tipo" :options="TIPOS" />
        <FormControl type="select" :label="__('Modalidad')" v-model="form.modalidad" :options="MODALIDADES" />
        <FormControl type="date" :label="__('Fecha inicio')" v-model="form.fecha_inicio" />
        <FormControl type="date" :label="__('Fecha fin')" v-model="form.fecha_fin" />
        <FormControl type="select" :label="__('Estado')" v-model="form.estado" :options="ESTADOS" />
        <FormControl type="text" :label="__('Ubicación / Link')" v-model="form.ubicacion" />
        <div>
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Responsable') }}</div>
          <Link doctype="User" :value="form.responsable" @change="(v) => (form.responsable = v)" />
        </div>
        <FormControl type="textarea" :label="__('Descripción')" v-model="form.descripcion" class="sm:col-span-2" />
      </div>
    </template>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button @click="showEdit = false">{{ __('Cancelar') }}</Button>
        <Button variant="solid" :loading="saving" @click="saveEdit">{{ __('Guardar') }}</Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'
import { FeatherIcon, FormControl, Button, Badge, Dialog, call, toast, usePageMeta } from 'frappe-ui'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ eventoId: { type: String, required: true } })
const router = useRouter()

const TIPOS = ['Curso', 'Webinar', 'Feria', 'Conferencia', 'Otro']
const MODALIDADES = ['Presencial', 'Virtual', 'Híbrido']
const ESTADOS = ['Planificado', 'En curso', 'Finalizado', 'Cancelado']
const ESTADOS_PART = ['Inscripto', 'Confirmado', 'Asistió', 'No asistió']

const evento = ref(null)
const saving = ref(false)
const labels = ref({})

async function load() {
  evento.value = await call('frappe.client.get', { doctype: 'CRM Marketing Evento', name: props.eventoId })
  await loadLabels()
}
async function loadLabels() {
  const m = { ...labels.value }
  try {
    const leadIds = (evento.value.leads || []).map((l) => l.lead).filter(Boolean)
    if (leadIds.length) {
      const rows = await call('frappe.client.get_list', {
        doctype: 'CRM Lead', filters: { name: ['in', leadIds] },
        fields: ['name', 'lead_name', 'organization'], limit_page_length: 0,
      })
      for (const r of rows) m[r.name] = r.organization || r.lead_name || r.name
    }
    const dealIds = (evento.value.oportunidades || []).map((o) => o.deal).filter(Boolean)
    if (dealIds.length) {
      const rows = await call('frappe.client.get_list', {
        doctype: 'CRM Deal', filters: { name: ['in', dealIds] },
        fields: ['name', 'organization'], limit_page_length: 0,
      })
      for (const r of rows) m[r.name] = r.organization || r.name
    }
  } catch (e) {
    // ignore
  }
  labels.value = m
}
load()

const asistieron = computed(
  () => (evento.value?.participantes || []).filter((p) => p.estado === 'Asistió').length,
)

async function saveDoc() {
  saving.value = true
  try {
    evento.value = await call('frappe.client.save', { doc: evento.value })
    await loadLabels()
  } catch (e) {
    toast.error((e && e.messages && e.messages[0]) || __('No se pudo guardar'))
  } finally {
    saving.value = false
  }
}

// --- Participantes ---
async function addParticipante(contactName) {
  if (!contactName) return
  if ((evento.value.participantes || []).some((p) => p.contact === contactName)) {
    toast.info(__('El contacto ya está en la lista'))
    return
  }
  let nombre = contactName
  let email = ''
  try {
    const c = await call('frappe.client.get', { doctype: 'Contact', name: contactName })
    nombre = [c.first_name, c.last_name].filter(Boolean).join(' ') || c.name
    email = c.email_id || (c.email_ids && c.email_ids[0]?.email_id) || ''
  } catch (e) {
    // ignore
  }
  evento.value.participantes = evento.value.participantes || []
  evento.value.participantes.push({ contact: contactName, participante_nombre: nombre, email, estado: 'Inscripto' })
  await saveDoc()
}
function addManual() {
  evento.value.participantes = evento.value.participantes || []
  evento.value.participantes.push({ contact: '', participante_nombre: '', email: '', estado: 'Inscripto' })
}
async function setPart(i, field, val) {
  evento.value.participantes[i][field] = val
  await saveDoc()
}
async function removePart(i) {
  evento.value.participantes.splice(i, 1)
  await saveDoc()
}

// --- Leads ---
async function addLead(leadName) {
  if (!leadName) return
  if ((evento.value.leads || []).some((l) => l.lead === leadName)) return
  evento.value.leads = evento.value.leads || []
  evento.value.leads.push({ lead: leadName })
  await saveDoc()
}
async function removeLead(i) {
  evento.value.leads.splice(i, 1)
  await saveDoc()
}

// --- Oportunidades ---
async function addOpp(dealName) {
  if (!dealName) return
  if ((evento.value.oportunidades || []).some((o) => o.deal === dealName)) return
  evento.value.oportunidades = evento.value.oportunidades || []
  evento.value.oportunidades.push({ deal: dealName })
  await saveDoc()
}
async function removeOpp(i) {
  evento.value.oportunidades.splice(i, 1)
  await saveDoc()
}

// --- Editar datos ---
const showEdit = ref(false)
const form = ref({})
function openEdit() {
  const e = evento.value
  form.value = {
    titulo: e.titulo, tipo: e.tipo, modalidad: e.modalidad, estado: e.estado,
    fecha_inicio: e.fecha_inicio, fecha_fin: e.fecha_fin, ubicacion: e.ubicacion,
    responsable: e.responsable, descripcion: e.descripcion,
  }
  showEdit.value = true
}
async function saveEdit() {
  Object.assign(evento.value, form.value)
  showEdit.value = false
  await saveDoc()
}

function volver() {
  router.push({ name: 'MarketingEventos' })
}
function tipoTheme(t) {
  return { Curso: 'green', Webinar: 'blue', Feria: 'orange', Conferencia: 'purple' }[t] || 'gray'
}
function estadoTheme(e) {
  return { Planificado: 'gray', 'En curso': 'blue', Finalizado: 'green', Cancelado: 'red' }[e] || 'gray'
}

usePageMeta(() => ({ title: evento.value?.titulo || __('Evento') }))
</script>
