<template>
  <div class="flex h-full flex-col">
    <header
      class="flex flex-wrap items-center justify-between gap-3 border-b px-5 py-3.5"
    >
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-9">
        <AttachmentIcon class="h-5 w-5" />
        {{ __('Attachments') }}
        <Badge variant="subtle" theme="gray" size="sm">{{
          filteredRows.length
        }}</Badge>
      </div>
      <div class="flex items-center gap-2">
        <FormControl
          class="w-40"
          type="select"
          :options="formatOptions"
          v-model="formatFilter"
        />
        <Link
          class="w-52"
          doctype="CRM Organization"
          v-model="orgFilter"
          :placeholder="__('Organización')"
        >
          <template #target="{ togglePopover }">
            <button
              class="flex h-8 w-52 items-center justify-between gap-1 rounded border border-outline-gray-2 bg-surface-white px-2.5 text-base"
              @click="togglePopover()"
            >
              <span
                class="truncate"
                :class="orgFilter ? 'text-ink-gray-8' : 'text-ink-gray-4'"
              >
                {{ orgFilter || __('Organización') }}
              </span>
              <FeatherIcon
                name="chevron-down"
                class="h-4 w-4 shrink-0 text-ink-gray-5"
              />
            </button>
          </template>
        </Link>
        <Button
          v-if="formatFilter || orgFilter"
          variant="ghost"
          :label="__('Limpiar')"
          @click="clearFilters"
        />
      </div>
    </header>

    <div class="flex-1 overflow-y-auto p-4 sm:px-8">
      <div v-if="files.loading || deals.loading" class="py-10 text-center text-ink-gray-4">
        {{ __('Loading...') }}
      </div>
      <div v-else-if="filteredRows.length" class="mx-auto max-w-4xl">
        <div
          v-for="att in filteredRows"
          :key="att.name"
          class="flex cursor-pointer items-center justify-between gap-3 rounded p-2.5 hover:bg-surface-gray-1"
          @click="openFile(att)"
        >
          <div class="flex min-w-0 items-center gap-3">
            <div
              class="flex size-11 shrink-0 items-center justify-center overflow-hidden rounded border bg-surface-base"
            >
              <img
                v-if="isImage(att.file_type)"
                :src="att.file_url"
                class="size-full object-cover"
                :alt="att.file_name"
              />
              <component :is="fileIcon(att.file_type)" v-else class="size-6" />
            </div>
            <div class="min-w-0">
              <div class="truncate text-base text-ink-gray-8">
                {{ att.file_name }}
              </div>
              <div class="truncate text-sm text-ink-gray-5">
                <span v-if="att.orgLabel" class="uppercase">{{
                  att.orgLabel
                }}</span>
                <span v-if="att.orgLabel"> · </span>{{ att.dealLabel }} ·
                {{ convertSize(att.file_size) }}
              </div>
            </div>
          </div>
          <div class="flex shrink-0 items-center gap-3">
            <Badge
              :label="att.formatLabel"
              theme="gray"
              variant="subtle"
              size="sm"
            />
            <span class="hidden text-sm text-ink-gray-5 sm:block">{{
              ownerName(att.owner)
            }}</span>
          </div>
        </div>
      </div>
      <div
        v-else
        class="flex h-full flex-col items-center justify-center gap-2 text-ink-gray-4"
      >
        <AttachmentIcon class="h-8 w-8" />
        <span class="text-base">{{ __('Sin adjuntos') }}</span>
      </div>
    </div>

    <Dialog v-model="showPreview" :options="{ size: '5xl' }">
      <template #body>
        <div class="p-4">
          <div class="mb-3 flex items-center justify-between gap-2">
            <div class="truncate text-lg font-semibold text-ink-gray-8">
              {{ previewFile?.file_name }}
            </div>
            <div class="flex shrink-0 gap-1">
              <Button :tooltip="__('Abrir en pestaña')" @click="openInTab">
                <template #icon
                  ><FeatherIcon name="external-link" class="size-4"
                /></template>
              </Button>
              <Button :tooltip="__('Cerrar')" @click="showPreview = false">
                <template #icon
                  ><FeatherIcon name="x" class="size-4"
                /></template>
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
              class="max-h-[78vh] max-w-full object-contain"
              :alt="previewFile.file_name"
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
import Link from '@/components/Controls/Link.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import FileTextIcon from '@/components/Icons/FileTextIcon.vue'
import FileAudioIcon from '@/components/Icons/FileAudioIcon.vue'
import FileVideoIcon from '@/components/Icons/FileVideoIcon.vue'
import FilePdfIcon from '@/components/Icons/FilePdfIcon.vue'
import FileWordIcon from '@/components/Icons/FileWordIcon.vue'
import FileExcelIcon from '@/components/Icons/FileExcelIcon.vue'
import { usersStore } from '@/stores/users'
import { createListResource, Dialog, Button, Badge, FormControl, FeatherIcon } from 'frappe-ui'
import { isImage, convertSize } from '@/utils'
import { ref, computed } from 'vue'

const { getUser } = usersStore()

const formatFilter = ref('')
const orgFilter = ref('')
const showPreview = ref(false)
const previewFile = ref(null)

const formatOptions = [
  { label: __('Todos los formatos'), value: '' },
  { label: 'PDF', value: 'pdf' },
  { label: 'Word', value: 'word' },
  { label: 'Excel', value: 'excel' },
  { label: __('Imagen'), value: 'image' },
  { label: __('Otro'), value: 'other' },
]

const files = createListResource({
  doctype: 'File',
  cache: 'deal-attachments',
  filters: { attached_to_doctype: 'CRM Deal' },
  fields: [
    'name',
    'file_name',
    'file_type',
    'file_url',
    'file_size',
    'is_private',
    'creation',
    'owner',
    'attached_to_name',
  ],
  orderBy: 'creation desc',
  pageLength: 99999,
  auto: true,
})

const deals = createListResource({
  doctype: 'CRM Deal',
  cache: 'deals-for-attachments',
  fields: ['name', 'organization', 'custom_numero_solaer'],
  pageLength: 99999,
  auto: true,
})

const dealMap = computed(() => {
  const m = {}
  for (const d of deals.data || []) m[d.name] = d
  return m
})

function formatKey(type) {
  let t = (type || '').toLowerCase()
  if (t === 'pdf') return 'pdf'
  if (['doc', 'docx'].includes(t)) return 'word'
  if (['xls', 'xlsx', 'csv'].includes(t)) return 'excel'
  if (isImage(type)) return 'image'
  return 'other'
}

function formatLabel(type) {
  return { pdf: 'PDF', word: 'Word', excel: 'Excel', image: __('Imagen'), other: __('Otro') }[
    formatKey(type)
  ]
}

const rows = computed(() =>
  (files.data || []).map((f) => {
    const deal = dealMap.value[f.attached_to_name]
    return {
      ...f,
      orgLabel: deal?.organization || '',
      dealLabel: deal?.custom_numero_solaer || f.attached_to_name,
      formatLabel: formatLabel(f.file_type),
      _fmt: formatKey(f.file_type),
    }
  }),
)

const filteredRows = computed(() =>
  rows.value.filter((r) => {
    if (formatFilter.value && r._fmt !== formatFilter.value) return false
    if (orgFilter.value && r.orgLabel !== orgFilter.value) return false
    return true
  }),
)

function fileIcon(type) {
  let t = (type || '').toLowerCase()
  if (t === 'pdf') return FilePdfIcon
  if (['doc', 'docx'].includes(t)) return FileWordIcon
  if (['xls', 'xlsx', 'csv'].includes(t)) return FileExcelIcon
  if (['wav', 'mp3', 'ogg', 'flac', 'aac'].includes(t)) return FileAudioIcon
  if (['mp4', 'avi', 'mkv', 'flv', 'mov'].includes(t)) return FileVideoIcon
  return FileTextIcon
}

function ownerName(owner) {
  return owner ? getUser(owner)?.full_name || owner : ''
}

function canPreview(type) {
  return isImage(type) || (type || '').toLowerCase() === 'pdf'
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

function clearFilters() {
  formatFilter.value = ''
  orgFilter.value = ''
}
</script>
