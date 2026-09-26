<template>
  <div class="flex flex-col gap-4 overflow-y-auto p-3 sm:p-5">
    <!-- Requerimiento (texto enriquecido) -->
    <div class="rounded-lg border">
      <div class="flex items-center justify-between border-b px-4 py-3">
        <div class="text-base font-semibold text-ink-gray-8">
          {{ __('Requerimiento') }}
        </div>
        <Button
          variant="solid"
          :label="__('Guardar')"
          :loading="saving"
          @click="save"
        />
      </div>
      <div class="p-3">
        <TextEditor
          :content="reqText"
          :editable="true"
          :editor-class="['prose-sm max-w-none min-h-[10rem]']"
          :placeholder="__('Describí el requerimiento del cliente...')"
          @change="reqText = $event"
        />
      </div>
    </div>

    <!-- Adjuntos del requerimiento -->
    <div class="rounded-lg border">
      <div class="flex items-center justify-between border-b px-4 py-3">
        <div class="flex items-center gap-2 text-base font-semibold text-ink-gray-8">
          <FeatherIcon name="paperclip" class="h-4 w-4" />
          {{ __('Adjuntos del requerimiento') }}
          <Badge variant="subtle" theme="gray" size="sm">{{ files.length }}</Badge>
        </div>
        <Button
          variant="subtle"
          :label="__('Adjuntar')"
          iconLeft="plus"
          @click="fileInput?.click()"
        />
      </div>
      <div class="p-3">
        <div
          class="flex flex-col gap-2 rounded-lg border-2 border-dashed p-3 transition-colors"
          :class="dropping ? 'border-blue-400 bg-blue-50' : 'border-outline-gray-3'"
          @dragover.prevent="dropping = true"
          @dragleave.prevent="dropping = false"
          @drop.prevent="onDrop"
        >
          <div
            v-for="f in files"
            :key="f.name"
            class="flex items-center justify-between gap-2 rounded border bg-surface-white px-2 py-1 text-sm"
          >
            <button class="flex min-w-0 items-center gap-1.5" @click="openFile(f)">
              <FeatherIcon name="file" class="h-4 w-4 shrink-0 text-ink-gray-5" />
              <span class="truncate text-ink-gray-8">{{ f.file_name }}</span>
            </button>
            <button
              class="shrink-0 text-ink-gray-4 hover:text-ink-red-6"
              :title="__('Eliminar')"
              @click="removeFile(f)"
            >
              <FeatherIcon name="x" class="h-4 w-4" />
            </button>
          </div>
          <div v-if="!files.length" class="py-4 text-center text-sm text-ink-gray-4">
            {{ __('Arrastrá archivos acá o usá "Adjuntar"') }}
          </div>
        </div>
        <input ref="fileInput" type="file" multiple class="hidden" @change="onPick" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon, Badge, Button, TextEditor, call, toast } from 'frappe-ui'
import { ref, watch } from 'vue'

const props = defineProps({
  doctype: { type: String, default: 'CRM Deal' },
  docname: { type: String, required: true },
})

const reqText = ref('')
const saving = ref(false)
const files = ref([])
const dropping = ref(false)
const fileInput = ref(null)

async function loadReq() {
  try {
    const v = await call('frappe.client.get_value', {
      doctype: 'CRM Deal',
      filters: { name: props.docname },
      fieldname: 'custom_requerimiento',
    })
    reqText.value = (v && v.custom_requerimiento) || ''
  } catch (e) {
    reqText.value = ''
  }
}

async function loadFiles() {
  try {
    files.value = await call('frappe.client.get_list', {
      doctype: 'File',
      filters: {
        attached_to_doctype: 'CRM Deal',
        attached_to_name: props.docname,
        custom_es_requerimiento: 1,
      },
      fields: ['name', 'file_name', 'file_url', 'file_type'],
      limit_page_length: 0,
    })
  } catch (e) {
    files.value = []
  }
}

function init() {
  loadReq()
  loadFiles()
}
init()
watch(() => props.docname, init)

async function save() {
  saving.value = true
  try {
    await call('frappe.client.set_value', {
      doctype: 'CRM Deal',
      name: props.docname,
      fieldname: 'custom_requerimiento',
      value: reqText.value,
    })
    toast.success(__('Requerimiento guardado'))
  } catch (e) {
    toast.error(__('No se pudo guardar'))
  } finally {
    saving.value = false
  }
}

function onPick(e) {
  const fs = Array.from(e.target.files || [])
  e.target.value = ''
  uploadAll(fs)
}
function onDrop(e) {
  dropping.value = false
  uploadAll(Array.from(e.dataTransfer.files || []))
}
async function uploadAll(list) {
  for (const file of list) await uploadOne(file)
  await loadFiles()
}
async function uploadOne(file) {
  try {
    const fd = new FormData()
    fd.append('file', file, file.name)
    fd.append('is_private', '1')
    fd.append('doctype', 'CRM Deal')
    fd.append('docname', props.docname)
    const res = await fetch('/api/method/upload_file', {
      method: 'POST',
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
      body: fd,
    })
    if (!res.ok) throw new Error('upload')
    const j = await res.json()
    const fname = j && j.message && j.message.name
    if (fname) {
      await call('frappe.client.set_value', {
        doctype: 'File',
        name: fname,
        fieldname: 'custom_es_requerimiento',
        value: 1,
      })
    }
  } catch (e) {
    toast.error(__('No se pudo adjuntar'))
  }
}
async function removeFile(f) {
  try {
    await call('frappe.client.delete', { doctype: 'File', name: f.name })
    await loadFiles()
  } catch (e) {
    toast.error(__('No se pudo eliminar'))
  }
}
function openFile(f) {
  window.open(f.file_url, '_blank')
}
</script>
