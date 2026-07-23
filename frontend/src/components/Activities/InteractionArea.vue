<template>
  <div class="flex h-full flex-col">
    <!-- Lista de interacciones -->
    <div
      v-if="interactions.data?.length"
      class="flex-1 overflow-y-auto px-3 pt-5 sm:px-10"
    >
      <div
        v-for="(it, i) in interactions.data"
        :key="it.name"
        class="activity grid grid-cols-[30px_minmax(auto,1fr)] gap-2"
      >
        <div class="relative flex justify-center">
          <div
            class="z-10 flex h-7 w-7 items-center justify-center rounded-full bg-surface-gray-2 text-ink-gray-7"
          >
            <component :is="channelIcon(it.channel)" class="h-4 w-4" />
          </div>
          <div
            v-if="i != interactions.data.length - 1"
            class="absolute top-7 z-0 h-full border-l border-outline-gray-modals"
          />
        </div>
        <div class="mb-4">
          <div class="mb-1 flex items-center gap-2 text-base">
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
            <TimelineTimestamp
              class="ml-auto"
              :date="it.interaction_datetime || it.creation"
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
                class="!h-6 !w-6 text-ink-gray-5"
              />
            </Dropdown>
          </div>
          <div
            class="whitespace-pre-line rounded bg-surface-gray-1 px-3 py-[7.5px] text-base text-ink-gray-8"
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
      <component :is="channelIcon('')" class="h-8 w-8" />
      <span class="text-base">{{ __('Sin interacciones todavía') }}</span>
    </div>

    <!-- Compositor -->
    <div
      class="border-t border-outline-gray-modals bg-surface-white px-3 py-3 sm:px-10"
    >
      <div
        class="flex flex-col gap-2 rounded-lg border border-outline-gray-2 p-2"
      >
        <div class="flex gap-2">
          <FormControl
            class="flex-1"
            type="text"
            :placeholder="__('Persona')"
            v-model="form.person"
          />
          <FormControl
            class="w-40"
            type="select"
            :options="channelOptions"
            v-model="form.channel"
          />
        </div>
        <FormControl
          type="textarea"
          :rows="2"
          :placeholder="__('Escribe la interacción...')"
          v-model="form.message"
          @keydown.ctrl.enter.stop="addInteraction"
          @keydown.meta.enter.stop="addInteraction"
        />
        <div class="flex justify-end">
          <Button
            variant="solid"
            :label="__('Agregar')"
            :loading="interactions.insert.loading"
            @click="addInteraction"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import TimelineTimestamp from '@/components/Activities/TimelineTimestamp.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import LinkedinIcon from '@/components/Icons/LinkedinIcon.vue'
import PeopleIcon from '@/components/Icons/PeopleIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import {
  createListResource,
  Dropdown,
  Button,
  Badge,
  FormControl,
  toast,
} from 'frappe-ui'
import { reactive } from 'vue'

const props = defineProps({
  doctype: { type: String, default: 'CRM Lead' },
  docname: { type: String, required: true },
})

const channelOptions = [
  { label: __('Teléfono'), value: 'Telefono' },
  { label: __('Mail'), value: 'Mail' },
  { label: 'LinkedIn', value: 'LinkedIn' },
  { label: __('En persona'), value: 'En persona' },
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

const form = reactive({ person: '', channel: 'Telefono', message: '' })

const interactions = createListResource({
  doctype: 'CRM Interaction',
  cache: ['crm-interactions', props.doctype, props.docname],
  filters: {
    reference_doctype: props.doctype,
    reference_docname: props.docname,
  },
  fields: [
    'name',
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

function addInteraction() {
  if (!form.message?.trim()) {
    toast.error(__('Escribe un mensaje'))
    return
  }
  interactions.insert.submit(
    {
      reference_doctype: props.doctype,
      reference_docname: props.docname,
      person: form.person,
      channel: form.channel,
      message: form.message,
    },
    {
      onSuccess: () => {
        form.person = ''
        form.message = ''
        interactions.reload()
      },
      onError: (err) => {
        toast.error(err?.messages?.[0] || __('No se pudo guardar la interacción'))
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
