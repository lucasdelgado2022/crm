<template>
  <div class="flex flex-col divide-y border-t">
    <!-- Notas -->
    <div class="p-4">
      <div class="mb-3 flex items-center justify-between">
        <div class="text-base font-semibold text-ink-gray-8">
          {{ __('Notes') }}
        </div>
        <Button
          variant="ghost"
          icon="plus"
          :tooltip="__('Add Note')"
          @click="modalRef?.showNote()"
        />
      </div>
      <div v-if="notes.length" class="grid grid-cols-1 gap-3">
        <div
          v-for="note in notes"
          :key="note.name"
          @click="modalRef?.showNote(note)"
        >
          <NoteArea v-model="activities" :note="note" />
        </div>
      </div>
      <div v-else class="text-sm text-ink-gray-4">
        {{ __('Sin notas') }}
      </div>
    </div>

    <!-- Adjuntos -->
    <div class="p-4">
      <div class="mb-3 flex items-center justify-between">
        <div class="text-base font-semibold text-ink-gray-8">
          {{ __('Attachments') }}
        </div>
        <Button
          variant="ghost"
          icon="plus"
          :tooltip="__('Attach a File')"
          @click="showFilesUploader = true"
        />
      </div>
      <AttachmentArea
        v-if="attachments.length"
        :attachments="attachments"
        @reload="activities.reload()"
      />
      <div v-else class="text-sm text-ink-gray-4">
        {{ __('Sin adjuntos') }}
      </div>
    </div>

    <AllModals
      ref="modalRef"
      v-model="activities"
      :doctype="'CRM Deal'"
      :doc="{ name: docname }"
    />
    <FilesUploader
      v-model="showFilesUploader"
      doctype="CRM Deal"
      :docname="docname"
      @after="() => activities.reload()"
    />
  </div>
</template>

<script setup>
import NoteArea from '@/components/Activities/NoteArea.vue'
import AttachmentArea from '@/components/Activities/AttachmentArea.vue'
import AllModals from '@/components/Activities/AllModals.vue'
import FilesUploader from '@/components/FilesUploader/FilesUploader.vue'
import { Button, createResource } from 'frappe-ui'
import { computed, ref } from 'vue'

const props = defineProps({
  docname: { type: String, required: true },
})

const modalRef = ref(null)
const showFilesUploader = ref(false)

// Comparte el cache con las pestañas (mismo key) para mantenerse sincronizado.
const activities = createResource({
  url: 'crm.api.activities.get_activities',
  params: { name: props.docname },
  cache: ['activity', props.docname],
  auto: true,
  transform: ([versions, calls, notes, tasks, attachments]) => {
    return { versions, calls, notes, tasks, attachments }
  },
})

const notes = computed(() => activities.data?.notes || [])
const attachments = computed(() => activities.data?.attachments || [])
</script>
