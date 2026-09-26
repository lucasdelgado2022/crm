<template>
  <div class="flex h-full flex-col">
    <!-- Compositor: una sola línea (arriba) -->
    <div
      class="border-b border-outline-gray-modals bg-surface-white px-3 py-3 sm:px-6"
    >
      <div
        class="flex flex-wrap items-center gap-2 rounded-lg border border-outline-gray-2 p-2"
      >
        <!-- Avatar del usuario (por defecto el actual, editable) -->
        <Dropdown :options="userOptions">
          <button
            type="button"
            class="shrink-0 rounded-full ring-offset-1 hover:ring-2 hover:ring-outline-gray-2"
            :title="__('Registrado por') + ': ' + agentName(form.agent || form.agent_ext)"
          >
            <UserAvatar :user="form.agent || form.agent_ext" size="lg" />
          </button>
        </Dropdown>

        <!-- Fecha (hoy por defecto, editable) -->
        <DatePicker
          class="w-[120px] shrink-0"
          variant="outline"
          :value="form.date"
          :format="'D MMM'"
          :clearable="false"
          @update:modelValue="(d) => (form.date = d || today())"
        >
          <template #suffix="{ togglePopover }">
            <span
              class="lucide-chevron-down h-4 w-4 cursor-pointer text-ink-gray-5"
              aria-hidden="true"
              @click="togglePopover"
            />
          </template>
        </DatePicker>

        <!-- Contacto (primary del lead/oportunidad por defecto) -->
        <Link
          v-model="form.contact"
          doctype="Contact"
          :filters="contactFilters"
          :placeholder="__('Contacto')"
        >
          <template #target="{ togglePopover }">
            <button
              class="flex h-8 w-[170px] shrink-0 items-center justify-between gap-1 rounded border border-outline-gray-2 bg-surface-white px-2.5 text-base"
              @click="togglePopover()"
            >
              <span
                class="truncate"
                :class="form.contact ? 'text-ink-gray-8' : 'text-ink-gray-4'"
              >
                {{ form.contact || __('Contacto') }}
              </span>
              <FeatherIcon
                name="chevron-down"
                class="h-4 w-4 shrink-0 text-ink-gray-5"
              />
            </button>
          </template>
        </Link>

        <!-- Texto corto -->
        <FormControl
          class="min-w-[140px] flex-1"
          type="text"
          :placeholder="__('Escribí una interacción...')"
          v-model="form.message"
          @keydown.enter.stop="addInteraction"
        />

        <Button
          variant="solid"
          :label="__('Agregar')"
          :loading="sending"
          @click="addInteraction"
        />
      </div>
      <!-- Próximo paso: item separado con responsable, contacto y mes futuro -->
      <div
        class="mt-2 flex flex-wrap items-center gap-2 rounded-lg border border-dashed border-outline-gray-2 p-2"
      >
        <span class="shrink-0 text-xs font-medium text-ink-gray-5">
          {{ __('Próximo paso') }}
        </span>
        <!-- Responsable asignado -->
        <Dropdown :options="pasoUserOptions">
          <button
            type="button"
            class="shrink-0 rounded-full ring-offset-1 hover:ring-2 hover:ring-outline-gray-2"
            :title="__('Responsable') + ': ' + agentName(form.paso_agent)"
          >
            <UserAvatar :user="form.paso_agent" size="md" />
          </button>
        </Dropdown>
        <FormControl
          class="min-w-[140px] flex-1"
          type="text"
          :placeholder="__('¿Cuál es el próximo paso?')"
          v-model="form.paso_texto"
        />
        <!-- Contacto -->
        <Link
          v-model="form.paso_contact"
          doctype="Contact"
          :filters="contactFilters"
          :placeholder="__('Contacto')"
        >
          <template #target="{ togglePopover }">
            <button
              class="flex h-8 w-[150px] shrink-0 items-center justify-between gap-1 rounded border border-outline-gray-2 bg-surface-white px-2.5 text-base"
              @click="togglePopover()"
            >
              <span
                class="truncate"
                :class="form.paso_contact ? 'text-ink-gray-8' : 'text-ink-gray-4'"
              >
                {{ form.paso_contact || __('Contacto') }}
              </span>
              <FeatherIcon
                name="chevron-down"
                class="h-4 w-4 shrink-0 text-ink-gray-5"
              />
            </button>
          </template>
        </Link>
        <DatePicker
          class="w-[140px] shrink-0"
          variant="outline"
          :value="form.paso_fecha"
          :format="'D MMM YYYY'"
          :placeholder="__('Fecha')"
          @update:modelValue="(d) => (form.paso_fecha = d || '')"
        >
          <template #suffix="{ togglePopover }">
            <span
              class="lucide-chevron-down h-4 w-4 cursor-pointer text-ink-gray-5"
              aria-hidden="true"
              @click="togglePopover"
            />
          </template>
        </DatePicker>
        <Button
          variant="subtle"
          :label="__('Agregar paso')"
          :loading="sendingPaso"
          @click="addPaso"
        />
      </div>
    </div>

    <!-- Lista de interacciones -->
    <div
      v-if="interactions.data?.length"
      class="flex flex-1 flex-col gap-3 overflow-y-auto px-3 py-4 sm:px-6"
    >
      <div
        v-for="it in interactions.data"
        :key="it.name"
        class="flex items-start gap-2.5"
      >
        <UserAvatar
          :user="it.custom_agent || it.custom_agent_nombre || it.owner"
          size="lg"
          class="mt-0.5 shrink-0"
        />
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2 text-sm">
            <Badge
              v-if="it.custom_es_proximo_paso"
              :label="__('Próximo paso')"
              theme="purple"
              variant="subtle"
              size="sm"
            />
            <span
              v-if="it.custom_es_proximo_paso"
              class="text-sm font-medium text-purple-600"
            >
              {{ fechaCompleta(it.interaction_datetime) }}
            </span>
            <TimelineTimestamp
              v-else
              :date="it.interaction_datetime || it.creation"
            />
            <Badge
              v-if="it.contact"
              :label="it.contact"
              theme="gray"
              variant="subtle"
              size="sm"
            />
            <Dropdown
              :options="[
                {
                  label: __('Eliminar'),
                  icon: 'trash-2',
                  onClick: () => removeInteraction(it.name),
                },
              ]"
            >
              <Button
                variant="ghost"
                icon="more-horizontal"
                class="!h-5 !w-5 text-ink-gray-5"
              />
            </Dropdown>
          </div>
          <div
            class="whitespace-pre-line text-base"
            :class="it.custom_es_proximo_paso ? 'font-medium text-purple-600' : 'text-ink-gray-8'"
          >
            {{ it.message }}
          </div>
        </div>
      </div>
    </div>
    <div
      v-else
      class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
    >
      <CommentIcon class="h-8 w-8" />
      <span class="text-base">{{ __('Sin interacciones todavía') }}</span>
    </div>

  </div>
</template>

<script setup>
import Link from '@/components/Controls/Link.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import TimelineTimestamp from '@/components/Activities/TimelineTimestamp.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/users'
import {
  createResource,
  createListResource,
  call,
  DatePicker,
  Dropdown,
  Button,
  Badge,
  FormControl,
  FeatherIcon,
  dayjs,
  toast,
} from 'frappe-ui'
import { reactive, ref, computed, h } from 'vue'

const props = defineProps({
  doctype: { type: String, default: 'CRM Lead' },
  docname: { type: String, required: true },
})

const { user: sessionUser } = sessionStore()
const { getUser, crmUsers, allUsers } = usersStore()

function today() {
  return dayjs().format('YYYY-MM-DD')
}

function agentName(u) {
  return getUser(u)?.full_name || u || __('Usuario')
}

// Muestra solo el mes (y año) de la fecha del próximo paso
const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sept', 'oct', 'nov', 'dic']
function mesLabel(s) {
  if (!s) return ''
  const d = dayjs(s)
  if (!d.isValid()) return ''
  return MESES[d.month()] + ' ' + d.year()
}
function fechaCompleta(s) {
  if (!s) return ''
  const d = dayjs(s)
  if (!d.isValid()) return ''
  return d.date() + ' ' + MESES[d.month()] + ' ' + d.year()
}

const sending = ref(false)
const leadOrg = ref('')

const form = reactive({
  agent: sessionUser,
  agent_ext: '',
  date: today(),
  contact: '',
  message: '',
  // Próximo paso (item separado): responsable + contacto + mes futuro
  paso_texto: '',
  paso_agent: sessionUser,
  paso_contact: '',
  paso_fecha: '',
})

// Agentes externos (no son usuarios del sistema): CRM Agente Externo
const externos = ref([])
createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'CRM Agente Externo',
    fields: ['name'],
    limit_page_length: 0,
    order_by: 'name asc',
  },
  auto: true,
  onSuccess: (d) => (externos.value = (d || []).map((x) => x.name)),
})

// Todos los usuarios del sistema (para elegir avatar), vía Server Script
// que no está limitado por rol como get_users del core.
const allUsersList = ref([])
createResource({
  url: 'interaction_users',
  auto: true,
  onSuccess: (d) => (allUsersList.value = Array.isArray(d) ? d : d?.message || []),
})
function userBase() {
  if (allUsersList.value?.length) return allUsersList.value
  if (allUsers.value?.length) return allUsers.value
  return crmUsers.value || []
}

const userOptions = computed(() => {
  const base = userBase()
  const internos = base
    .filter((u) => u.name !== 'Administrator' && u.name !== 'Guest')
    .map((u) => ({
      label: u.full_name || u.name,
      onClick: () => {
        form.agent = u.name
        form.agent_ext = ''
      },
      slots: { prefix: () => h(UserAvatar, { user: u.name, size: 'sm' }) },
    }))
  const ext = externos.value.map((n) => ({
    label: n + ' · ' + __('externo'),
    onClick: () => {
      form.agent_ext = n
      form.agent = ''
    },
    slots: { prefix: () => h(UserAvatar, { user: n, size: 'sm' }) },
  }))
  const addOpt = {
    label: '➕ ' + __('Agregar otro usuario…'),
    onClick: addExterno,
  }
  return internos.concat(ext).concat([addOpt])
})

// Opciones de responsable para el "próximo paso"
const pasoUserOptions = computed(() => {
  const base = userBase()
  return base
    .filter((u) => u.name !== 'Administrator' && u.name !== 'Guest')
    .map((u) => ({
      label: u.full_name || u.name,
      onClick: () => (form.paso_agent = u.name),
      slots: { prefix: () => h(UserAvatar, { user: u.name, size: 'sm' }) },
    }))
})

async function addExterno() {
  const nombre = (window.prompt(__('Nombre del usuario a agregar')) || '').trim()
  if (!nombre) return
  try {
    if (!externos.value.includes(nombre)) {
      await call('frappe.client.insert', {
        doc: { doctype: 'CRM Agente Externo', nombre },
      })
      externos.value.push(nombre)
    }
    form.agent_ext = nombre
    form.agent = ''
    toast.success(__('Usuario agregado'))
  } catch (e) {
    toast.error(__('No se pudo agregar el usuario'))
  }
}

const contactFilters = computed(() =>
  leadOrg.value ? { company_name: leadOrg.value } : {},
)

// Organizacion + contacto por defecto del lead/deal
createResource({
  url: 'frappe.client.get_value',
  params: {
    doctype: props.doctype,
    filters: props.docname,
    fieldname:
      props.doctype === 'CRM Lead'
        ? ['organization', 'custom_contact']
        : ['organization', 'contact'],
  },
  auto: ['CRM Lead', 'CRM Deal'].includes(props.doctype),
  onSuccess: (d) => {
    leadOrg.value = d?.organization || ''
    // Contacto primary por defecto: Deal.contact / Lead.custom_contact
    const primary =
      props.doctype === 'CRM Lead' ? d?.custom_contact : d?.contact
    if (primary && !form.contact) form.contact = primary
    if (primary && !form.paso_contact) form.paso_contact = primary
  },
})

const interactions = createListResource({
  doctype: 'CRM Interaction',
  cache: ['crm-interactions', props.doctype, props.docname],
  filters: {
    reference_doctype: props.doctype,
    reference_docname: props.docname,
  },
  fields: [
    'name',
    'contact',
    'custom_agent',
    'custom_agent_nombre',
    'message',
    'custom_es_proximo_paso',
    'interaction_datetime',
    'creation',
    'owner',
  ],
  orderBy: 'interaction_datetime asc',
  pageLength: 500,
  auto: true,
})

function buildDatetime() {
  const d = dayjs(form.date)
  // Si es hoy usamos la hora actual para conservar el orden; si no, mediodia
  if (d.isSame(dayjs(), 'day')) return dayjs().format('YYYY-MM-DD HH:mm:ss')
  return d.format('YYYY-MM-DD') + ' 12:00:00'
}

async function addInteraction() {
  if (!form.message?.trim()) {
    toast.error(__('Escribí una interacción'))
    return
  }
  sending.value = true
  interactions.insert.submit(
    {
      reference_doctype: props.doctype,
      reference_docname: props.docname,
      from_client: 1,
      contact: form.contact || null,
      custom_agent: form.agent_ext ? null : form.agent || sessionUser,
      custom_agent_nombre: form.agent_ext || null,
      channel: 'En persona',
      message: form.message,
      interaction_datetime: buildDatetime(),
    },
    {
      onSuccess: () => {
        form.message = ''
        form.date = today()
        interactions.reload()
        sending.value = false
      },
      onError: (err) => {
        sending.value = false
        toast.error(
          err?.messages?.[0] || __('No se pudo guardar la interacción'),
        )
      },
    },
  )
}

const sendingPaso = ref(false)
async function addPaso() {
  if (!form.paso_texto?.trim()) {
    toast.error(__('Escribí el próximo paso'))
    return
  }
  if (!form.paso_fecha) {
    toast.error(__('Elegí el mes del próximo paso'))
    return
  }
  sendingPaso.value = true
  interactions.insert.submit(
    {
      reference_doctype: props.doctype,
      reference_docname: props.docname,
      from_client: 0,
      contact: form.paso_contact || null,
      custom_agent: form.paso_agent || sessionUser,
      channel: 'En persona',
      custom_es_proximo_paso: 1,
      message: form.paso_texto,
      interaction_datetime: dayjs(form.paso_fecha).format('YYYY-MM-DD') + ' 09:00:00',
    },
    {
      onSuccess: () => {
        form.paso_texto = ''
        form.paso_fecha = ''
        interactions.reload()
        sendingPaso.value = false
      },
      onError: (err) => {
        sendingPaso.value = false
        toast.error(err?.messages?.[0] || __('No se pudo guardar el próximo paso'))
      },
    },
  )
}

function removeInteraction(name) {
  interactions.delete.submit(name, {
    onSuccess: () => interactions.reload(),
  })
}
</script>
