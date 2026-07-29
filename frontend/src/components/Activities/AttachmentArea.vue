<template>
  <div v-if="currentAttachments.length">
    <div v-for="(attachment, i) in currentAttachments" :key="attachment.name">
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
            <div class="flex items-center gap-1.5 truncate">
              <span class="text-base text-ink-gray-8 truncate">
                {{ attachment.file_name }}
              </span>
              <span
                v-if="versionNo(attachment) > 1"
                class="shrink-0 rounded bg-surface-gray-3 px-1.5 py-0.5 text-xs font-medium text-ink-gray-7"
              >
                v{{ versionNo(attachment) }}
              </span>
            </div>
            <div class="mb-1 truncate text-sm text-ink-gray-5">
              {{ convertSize(attachment.file_size) }}
              <span v-if="attachment.owner">
                · {{ ownerName(attachment.owner) }}</span
              >
              <button
                v-if="versionNo(attachment) > 1"
                class="ml-1 text-ink-gray-6 underline hover:text-ink-gray-9"
                @click.stop="toggleVersions(attachment.name)"
              >
                {{
                  expanded[attachment.name]
                    ? __('ocultar versiones')
                    : __('ver {0} versiones anteriores', [versionNo(attachment) - 1])
                }}
              </button>
            </div>
          </div>
        </div>
        <div class="flex flex-col items-end gap-2 flex-shrink-0">
          <TimelineTimestamp :date="attachment.creation" />
          <div class="flex gap-1">
            <Button
              :tooltip="__('Subir nueva versión')"
              class="!size-5"
              @click.stop="() => triggerNewVersion(attachment.name)"
            >
              <template #icon>
                <span
                  class="lucide-upload size-3 text-ink-gray-7"
                  aria-hidden="true"
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
      <!-- versiones anteriores -->
      <div
        v-if="expanded[attachment.name]"
        class="ml-14 mb-1 flex flex-col gap-1 border-l border-outline-gray-2 pl-3"
      >
        <div
          v-for="prev in previousVersions(attachment)"
          :key="prev.name"
          class="flex items-center justify-between gap-2 rounded px-2 py-1 text-sm hover:bg-surface-sidebar cursor-pointer"
          @click="openFile(prev)"
        >
          <div class="flex items-center gap-2 truncate text-ink-gray-6">
            <span class="shrink-0 rounded bg-surface-gray-2 px-1.5 py-0.5 text-xs">
              v{{ versionNo(prev) }}
            </span>
            <span class="truncate">{{ prev.file_name }}</span>
          </div>
          <TimelineTimestamp :date="prev.creation" class="shrink-0" />
        </div>
      </div>
      <div
        v-if="i < currentAttachments.length - 1"
        class="mx-2 h-px border-t border-outline-elevation-2"
      />
    </div>
    <input
      ref="versionInput"
      type="file"
      class="hidden"
      @change="onNewVersionSelected"
    />

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
import { usersStore } from '@/stores/users'
import { call, Dialog, toast } from 'frappe-ui'
import { ref, computed } from 'vue'
import TimelineTimestamp from '@/components/Activities/TimelineTimestamp.vue'
import { convertSize, isImage } from '@/utils'

const props = defineProps({
  attachments: { type: Array, default: () => [] },
  doctype: { type: String, default: '' },
  docname: { type: String, default: '' },
})

const emit = defineEmits(['reload'])

const { $dialog } = globalStore()
const { getUser } = usersStore()

function ownerName(owner) {
  if (!owner) return ''
  return getUser(owner)?.full_name || owner
}

// ---- Versionado de documentos ----
// Cada File puede apuntar a su version anterior via custom_previous_version.
const byName = computed(() =>
  Object.fromEntries((props.attachments || []).map((a) => [a.name, a])),
)
// nombres de archivos que fueron reemplazados (son version anterior de otro)
const supersededNames = computed(
  () =>
    new Set(
      (props.attachments || [])
        .map((a) => a.custom_previous_version)
        .filter(Boolean),
    ),
)
// solo se muestran las versiones actuales (no reemplazadas)
const currentAttachments = computed(() =>
  (props.attachments || []).filter((a) => !supersededNames.value.has(a.name)),
)
// cadena [mas vieja ... actual]
function versionChain(att) {
  const chain = []
  const seen = new Set()
  let cur = att
  while (cur && !seen.has(cur.name)) {
    chain.unshift(cur)
    seen.add(cur.name)
    cur = cur.custom_previous_version
      ? byName.value[cur.custom_previous_version]
      : null
  }
  return chain
}
function versionNo(att) {
  return versionChain(att).length
}
function previousVersions(att) {
  // todas menos la actual, de mas nueva a mas vieja
  return versionChain(att).slice(0, -1).reverse()
}

const expanded = ref({})
function toggleVersions(name) {
  expanded.value = { ...expanded.value, [name]: !expanded.value[name] }
}

// subir nueva version
const versionInput = ref(null)
const pendingVersionFor = ref(null)
function triggerNewVersion(name) {
  pendingVersionFor.value = name
  versionInput.value?.click()
}
async function onNewVersionSelected(event) {
  const file = event.target.files?.[0]
  const prevName = pendingVersionFor.value
  event.target.value = ''
  if (!file || !prevName) return
  try {
    const fd = new FormData()
    fd.append('file', file, file.name)
    fd.append('is_private', '0')
    fd.append('folder', 'Home/Attachments')
    fd.append('doctype', props.doctype)
    fd.append('docname', props.docname)
    const res = await fetch('/api/method/upload_file', {
      method: 'POST',
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token },
      body: fd,
    })
    if (!res.ok) throw new Error(await res.text())
    const data = await res.json()
    const newName = data?.message?.name
    if (newName) {
      await call('frappe.client.set_value', {
        doctype: 'File',
        name: newName,
        fieldname: 'custom_previous_version',
        value: prevName,
      })
    }
    toast.success(__('Nueva versión subida'))
    emit('reload')
  } catch (e) {
    toast.error(__('No se pudo subir la nueva versión'))
  } finally {
    pendingVersionFor.value = null
  }
}

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
