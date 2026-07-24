<template>
  <div class="flex h-full flex-col">
    <!-- Lista tipo chat -->
    <div
      v-if="interactions.data?.length"
      class="flex flex-1 flex-col gap-3 overflow-y-auto px-3 py-4 sm:px-8"
    >
      <div
        v-for="it in interactions.data"
        :key="it.name"
        class="flex w-full"
        :class="it.from_client ? 'justify-start' : 'justify-end'"
      >
        <div class="flex max-w-[82%] flex-col gap-1">
          <div
            class="flex items-center gap-2 text-sm"
            :class="it.from_client ? '' : 'flex-row-reverse'"
          >
            <component
              :is="channelIcon(it.channel)"
              class="h-3.5 w-3.5 text-ink-gray-5"
            />
            <span class="font-medium text-ink-gray-8">
              {{ it.person || __('Sin nombre') }}
            </span>
            <Badge
              v-if="it.channel"
              :label="__(channelLabel(it.channel))"
              theme="gray"
              variant="subtle"
              size="sm"
            />
            <TimelineTimestamp :date="it.interaction_datetime || it.creation" />
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
            class="whitespace-pre-line rounded-2xl px-3.5 py-2 text-base text-ink-gray-8"
            :class="
              it.from_client
                ? 'rounded-tl-sm bg-surface-gray-2'
                : 'rounded-tr-sm border border-outline-gray-2 bg-surface-white'
            "
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

    <!-- Compositor -->
    <div
      class="border-t border-outline-gray-modals bg-surface-white px-3 py-3 sm:px-8"
    >
      <div
        class="flex flex-col gap-2.5 rounded-lg border border-outline-gray-2 p-2.5"
      >
        <!-- Origen (Cliente/Nosotros) + canal -->
        <div class="flex items-center justify-between gap-2">
          <div class="flex rounded-md bg-surface-gray-2 p-0.5 text-sm">
            <button
              class="rounded px-3 py-1 transition"
              :class="
                form.from_client
                  ? 'bg-surface-white font-medium text-ink-gray-9 shadow-sm'
                  : 'text-ink-gray-6'
              "
              @click="form.from_client = true"
            >
              {{ __('Cliente') }}
            </button>
            <button
              class="rounded px-3 py-1 transition"
              :class="
                !form.from_client
                  ? 'bg-surface-white font-medium text-ink-gray-9 shadow-sm'
                  : 'text-ink-gray-6'
              "
              @click="form.from_client = false"
            >
              {{ __('Nosotros') }}
            </button>
          </div>

          <div class="flex shrink-0 items-center gap-1">
            <button
              v-for="ch in channelButtons"
              :key="ch.value"
              type="button"
              :title="ch.label"
              class="flex h-8 w-8 items-center justify-center rounded-md border transition"
              :class="
                form.channel === ch.value
                  ? 'border-outline-gray-3 bg-surface-gray-3 text-ink-gray-9'
                  : 'border-outline-gray-2 text-ink-gray-5 hover:bg-surface-gray-2'
              "
              @click="form.channel = ch.value"
            >
              <component :is="ch.icon" class="h-4 w-4" />
            </button>
          </div>
        </div>

        <!-- Selector de contacto (cliente) o nombre libre (nosotros): fila completa -->
        <Link
          v-if="form.from_client"
          v-model="form.contact"
          doctype="Contact"
          :filters="contactFilters"
          :placeholder="__('Contacto del cliente')"
        >
          <template #target="{ togglePopover }">
            <button
              class="flex h-8 w-full items-center justify-between gap-1 rounded border border-outline-gray-2 bg-surface-white px-2.5 text-base"
              @click="togglePopover()"
            >
              <span
                class="truncate"
                :class="form.contact ? 'text-ink-gray-8' : 'text-ink-gray-4'"
              >
                {{ form.contact || __('Elegí el contacto del cliente') }}
              </span>
              <FeatherIcon
                name="chevron-down"
                class="h-4 w-4 shrink-0 text-ink-gray-5"
              />
            </button>
          </template>
        </Link>
        <FormControl
          v-else
          type="text"
          :placeholder="__('Nombre de la persona (nuestro lado)')"
          v-model="form.person"
        />

        <!-- Mensaje (más alto) con control para agrandar -->
        <div class="relative">
          <FormControl
            type="textarea"
            :rows="expanded ? 10 : 4"
            :placeholder="__('Escribe la interacción...')"
            v-model="form.message"
            @keydown.ctrl.enter.stop="addInteraction"
            @keydown.meta.enter.stop="addInteraction"
          />
          <Button
            variant="ghost"
            class="!absolute right-1 top-1 !h-6 !w-6 text-ink-gray-5"
            :tooltip="expanded ? __('Reducir') : __('Agrandar')"
            :icon="expanded ? 'minimize-2' : 'maximize-2'"
            @click="expanded = !expanded"
          />
        </div>

        <div class="flex justify-end">
          <Button
            variant="solid"
            :label="__('Agregar')"
            :loading="sending"
            @click="addInteraction"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Link from '@/components/Controls/Link.vue'
import TimelineTimestamp from '@/components/Activities/TimelineTimestamp.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import LinkedinIcon from '@/components/Icons/LinkedinIcon.vue'
import PeopleIcon from '@/components/Icons/PeopleIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import {
  createResource,
  createListResource,
  call,
  Dropdown,
  Button,
  Badge,
  FormControl,
  FeatherIcon,
  toast,
} from 'frappe-ui'
import { reactive, ref, computed } from 'vue'

const props = defineProps({
  doctype: { type: String, default: 'CRM Lead' },
  docname: { type: String, required: true },
})

const channelButtons = [
  { label: __('Teléfono'), value: 'Telefono', icon: PhoneIcon },
  { label: __('Mail'), value: 'Mail', icon: Email2Icon },
  { label: 'LinkedIn', value: 'LinkedIn', icon: LinkedinIcon },
  { label: __('En persona'), value: 'En persona', icon: PeopleIcon },
]

function channelLabel(ch) {
  if (ch === 'Telefono') return 'Teléfono'
  return ch
}

function channelIcon(ch) {
  if (ch === 'Telefono') return PhoneIcon
  if (ch === 'Mail') return Email2Icon
  if (ch === 'LinkedIn') return LinkedinIcon
  if (ch === 'En persona') return PeopleIcon
  return CommentIcon
}

const expanded = ref(false)
const sending = ref(false)
const leadOrg = ref('')

const form = reactive({
  from_client: true,
  contact: '',
  person: '',
  channel: 'Telefono',
  message: '',
})

const contactFilters = computed(() =>
  leadOrg.value ? { company_name: leadOrg.value } : {},
)

// Info del lead/deal: organizacion + contacto por defecto (para filtrar el selector)
createResource({
  url: 'frappe.client.get_value',
  params: {
    doctype: props.doctype,
    filters: props.docname,
    fieldname:
      props.doctype === 'CRM Lead'
        ? ['organization', 'custom_contact']
        : ['organization'],
  },
  auto: ['CRM Lead', 'CRM Deal'].includes(props.doctype),
  onSuccess: (d) => {
    leadOrg.value = d?.organization || ''
    if (d?.custom_contact && !form.contact) form.contact = d.custom_contact
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
    'from_client',
    'contact',
    'person',
    'channel',
    'message',
    'interaction_datetime',
    'creation',
    'owner',
  ],
  orderBy: 'interaction_datetime asc',
  pageLength: 500,
  auto: true,
})

async function resolveContactName(contactName) {
  if (!contactName) return ''
  try {
    const d = await call('frappe.client.get_value', {
      doctype: 'Contact',
      filters: contactName,
      fieldname: ['first_name', 'last_name'],
    })
    return [d?.first_name, d?.last_name].filter(Boolean).join(' ').trim()
  } catch (e) {
    return contactName
  }
}

async function addInteraction() {
  if (!form.message?.trim()) {
    toast.error(__('Escribe un mensaje'))
    return
  }
  if (form.from_client && !form.contact) {
    toast.error(__('Elegí un contacto del cliente'))
    return
  }
  if (!form.from_client && !form.person?.trim()) {
    toast.error(__('Escribí el nombre'))
    return
  }
  sending.value = true
  // Nombre a mostrar
  let personName = form.person
  if (form.from_client) personName = await resolveContactName(form.contact)
  interactions.insert.submit(
    {
      reference_doctype: props.doctype,
      reference_docname: props.docname,
      from_client: form.from_client ? 1 : 0,
      contact: form.from_client ? form.contact : null,
      person: personName,
      channel: form.channel,
      message: form.message,
    },
    {
      onSuccess: () => {
        form.message = ''
        if (!form.from_client) form.person = ''
        expanded.value = false
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

function removeInteraction(name) {
  interactions.delete.submit(name, {
    onSuccess: () => interactions.reload(),
  })
}
</script>
