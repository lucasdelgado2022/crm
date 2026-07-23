<template>
  <div v-if="attachments.length">
    <div v-for="(attachment, i) in attachments" :key="attachment.name">
      <div
        class="activity flex justify-between gap-2 hover:bg-surface-sidebar rounded text-base p-2.5 cursor-pointer"
        @click="openFile(attachment)"
      >
        <div class="flex gap-2 truncate">
          <div
            class="size-11 bg-surface-base rounded overflow-hidden flex-shrink-0 flex justify-center items-center"
            :class="{ border: !isImage(attachment.file_type) }"
          >
            <img
              v-if="isImage(attachment.file_type)"
              class="size-full object-cover"
              :src="attachment.file_url"
              :alt="attachment.file_name"
            />
            <component
              :is="fileIcon(attachment.file_type)"
              v-else
              class="size-6 text-ink-gray-7"
            />
          </div>
          <div class="flex flex-col justify-center gap-1 truncate">
            <div class="text-base text-ink-gray-8 truncate">
              {{ attachment.file_name }}
            </div>
            <div class="mb-1 text-sm text-ink-gray-5">
              {{ convertSize(attachment.file_size) }}
            </div>
          </div>
        </div>
        <div class="flex flex-col items-end gap-2 flex-shrink-0">
          <TimelineTimestamp :date="attachment.creation" />
          <div class="flex gap-1">
            <Button
              :tooltip="
                attachment.is_private ? __('Make Public') : __('Make Private')
              "
              class="!size-5"
              @click.stop="
                togglePrivate(attachment.name, attachment.is_private)
              "
            >
              <template #icon>
                <FeatherIcon
                  :name="attachment.is_private ? 'lock' : 'unlock'"
                  class="size-3 text-ink-gray-7"
                />
              </template>
            </Button>
            <Button
              :tooltip="__('Delete Attachment')"
              class="!size-5"
              @click.stop="() => deleteAttachment(attachment.name)"
            >
              <template #icon>
                <span
                  class="lucide-trash-2 size-3 text-ink-gray-7"
                  aria-hidden="true"
                />
              </template>
            </Button>
          </div>
        </div>
      </div>
      <div
        v-if="i < attachments.length - 1"
        class="mx-2 h-px border-t border-outline-elevation-2"
      />
    </div>

    <!-- Modal de previsualizacion (PDF / imagenes) -->
    <Dialog v-model="showPreview" :options="{ size: '5xl' }">
      <template #body>
        <div class="p-4">
          <div class="mb-3 flex items-center justify-between gap-2">
            <div class="truncate text-lg font-semibold text-ink-gray-8">
              {{ previewFile?.file_name }}
            </div>
            <div class="flex gap-1 shrink-0">
              <Button
                :tooltip="__('Abrir en pestaña')"
                @click="openInTab"
              >
                <template #icon>
                  <FeatherIcon name="external-link" class="size-4" />
                </template>
              </Button>
              <Button :tooltip="__('Cerrar')" @click="showPreview = false">
                <template #icon>
                  <FeatherIcon name="x" class="size-4" />
                </template>
              </Button>
            </div>
          </div>
          <div
            v-if="previewFile"
            class="flex justify-center rounded bg-surface-gray-2"
          >
            <img
              v-if="isImage(previewFile.file_type)"
              :src="previewFile.file_url"
              :alt="previewFile.file_name"
              class="max-h-[78vh] max-w-full object-contain"
            />
            <iframe
              v-else
              :src="previewFile.file_url"
              class="h-[78vh] w-full rounded"
            />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>
<script setup>
import FileAudioIcon from '@/components/Icons/FileAudioIcon.vue'
import FileTextIcon from '@/components/Icons/FileTextIcon.vue'
import FileVideoIcon from '@/components/Icons/FileVideoIcon.vue'
import FilePdfIcon from '@/components/Icons/FilePdfIcon.vue'
import FileWordIcon from '@/components/Icons/FileWordIcon.vue'
import FileExcelIcon from '@/components/Icons/FileExcelIcon.vue'
import { globalStore } from '@/stores/global'
import { call, Dialog } from 'frappe-ui'
import { ref } from 'vue'
import TimelineTimestamp from '@/components/Activities/TimelineTimestamp.vue'
import { convertSize, isImage } from '@/utils'

defineProps({
  attachments: { type: Array, default: () => [] },
})

const emit = defineEmits(['reload'])

const { $dialog } = globalStore()

const showPreview = ref(false)
const previewFile = ref(null)

function canPreview(type) {
  let t = (type || '').toLowerCase()
  return isImage(type) || t === 'pdf'
}

function openFile(attachment) {
  if (canPreview(attachment.file_type)) {
    previewFile.value = attachment
    showPreview.value = true
  } else {
    window.open(attachment.file_url, '_blank')
  }
}

function openInTab() {
  if (previewFile.value) window.open(previewFile.value.file_url, '_blank')
}

function togglePrivate(fileName, isPrivate) {
  let changeTo = isPrivate ? __('public') : __('private')
  let title = __('Make attachment {0}', [changeTo])
  let message = __('Are you sure you want to make this attachment {0}?', [
    changeTo,
  ])
  $dialog({
    title,
    message,
    actions: [
      {
        label: __('Make {0}', [changeTo]),
        variant: 'solid',
        onClick: async (close) => {
          await call('frappe.client.set_value', {
            doctype: 'File',
            name: fileName,
            fieldname: {
              is_private: !isPrivate,
            },
          })
          emit('reload')
          close()
        },
      },
    ],
  })
}

function deleteAttachment(fileName) {
  $dialog({
    title: __('Delete Attachment'),
    message: __('Are you sure you want to delete this attachment?'),
    actions: [
      {
        label: __('Delete'),
        variant: 'solid',
        theme: 'red',
        onClick: async (close) => {
          await call('frappe.client.delete', {
            doctype: 'File',
            name: fileName,
          })
          emit('reload')
          close()
        },
      },
    ],
  })
}

function fileIcon(type) {
  if (!type) return FileTextIcon
  let t = type.toLowerCase()
  let audioExtentions = ['wav', 'mp3', 'ogg', 'flac', 'aac']
  let videoExtentions = ['mp4', 'avi', 'mkv', 'flv', 'mov']
  if (t === 'pdf') return FilePdfIcon
  if (['doc', 'docx'].includes(t)) return FileWordIcon
  if (['xls', 'xlsx', 'csv'].includes(t)) return FileExcelIcon
  if (audioExtentions.includes(t)) return FileAudioIcon
  if (videoExtentions.includes(t)) return FileVideoIcon
  return FileTextIcon
}
</script>
