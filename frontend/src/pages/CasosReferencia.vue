<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <LucideAward class="h-5 w-5" />
        {{ __('Casos de Referencia') }}
      </div>
    </template>
    <template #right-header>
      <Button variant="solid" @click="nuevo">
        <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
        {{ __('Nuevo caso') }}
      </Button>
    </template>
  </LayoutHeader>

  <div class="flex h-full overflow-hidden">
    <!-- Lista -->
    <div class="w-2/5 shrink-0 overflow-y-auto border-r p-2 sm:w-1/3">
      <FormControl
        class="mb-2"
        type="text"
        :placeholder="__('Buscar...')"
        v-model="search"
      >
        <template #prefix>
          <FeatherIcon name="search" class="h-4 w-4 text-ink-gray-5" />
        </template>
      </FormControl>
      <div
        v-for="c in filtered"
        :key="c.name"
        class="mb-1.5 cursor-pointer rounded-lg border p-3 hover:bg-surface-gray-1"
        :class="selected === c.name ? 'border-outline-gray-3 bg-surface-gray-2' : ''"
        @click="selectCase(c.name)"
      >
        <div class="flex items-center justify-between gap-2">
          <div class="truncate font-medium text-ink-gray-8">{{ c.titulo }}</div>
          <Badge
            :theme="c.estado_publicacion === 'Publico' ? 'green' : 'gray'"
            variant="subtle"
            size="sm"
          >
            {{ c.estado_publicacion === 'Publico' ? 'Público' : 'Interno' }}
          </Badge>
        </div>
        <div class="mt-0.5 truncate text-sm text-ink-gray-6">
          {{ c.organizacion || '—' }}
        </div>
        <div v-if="c.resumen" class="mt-1 line-clamp-2 text-xs text-ink-gray-5">
          {{ c.resumen }}
        </div>
      </div>
      <div v-if="!filtered.length" class="p-4 text-center text-sm text-ink-gray-4">
        {{ __('Sin casos') }}
      </div>
    </div>

    <!-- Detalle / Form -->
    <div v-if="editing" class="flex flex-1 flex-col overflow-y-auto p-4 sm:p-6">
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <FormControl v-model="form.titulo" class="sm:col-span-2" :label="__('Título')" />
        <div>
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Oportunidad') }}</div>
          <Link doctype="CRM Deal" :value="form.oportunidad" @change="onDeal" />
        </div>
        <FormControl v-model="form.organizacion" :label="__('Organización')" />
        <div>
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Industria') }}</div>
          <Link doctype="CRM Industry" :value="form.industria" @change="(v) => (form.industria = v)" />
        </div>
        <FormControl v-model="form.producto" :label="__('Producto')" />
        <FormControl
          type="select"
          :label="__('Visibilidad')"
          v-model="form.estado_publicacion"
          :options="['Interno', 'Publico']"
        />
        <FormControl type="date" :label="__('Fecha')" v-model="form.fecha" />
        <div>
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Responsable') }}</div>
          <Link doctype="User" :value="form.responsable" @change="(v) => (form.responsable = v)" />
        </div>
      </div>

      <div class="mt-3 grid grid-cols-1 gap-3">
        <FormControl type="textarea" :rows="2" :label="__('Resumen')" v-model="form.resumen" />
        <FormControl type="textarea" :rows="3" :label="__('Problema / Desafío')" v-model="form.problema" />
        <FormControl type="textarea" :rows="3" :label="__('Solución')" v-model="form.solucion" />
        <FormControl type="textarea" :rows="3" :label="__('Beneficios')" v-model="form.beneficios" />
        <FormControl type="textarea" :rows="3" :label="__('KPI / Resultados')" v-model="form.kpi" />
      </div>

      <div class="mt-4 flex justify-end gap-2">
        <Button
          v-if="selected"
          theme="red"
          variant="subtle"
          @click="delCase"
        >
          <FeatherIcon name="trash-2" class="h-4 w-4" />
        </Button>
        <Button @click="cancel">{{ __('Cancelar') }}</Button>
        <Button variant="solid" :loading="saving" :disabled="!form.titulo.trim()" @click="save">
          {{ __('Guardar') }}
        </Button>
      </div>

      <!-- Adjuntos + Comentarios (solo guardados) -->
      <template v-if="selected">
        <div class="mt-5 rounded-lg border p-4">
          <div class="mb-2 flex items-center justify-between">
            <div class="text-sm font-semibold text-ink-gray-7">{{ __('Adjuntos') }}</div>
            <button
              class="flex items-center gap-1 rounded border border-dashed border-outline-gray-2 px-2 py-1 text-xs text-ink-gray-5 hover:bg-surface-gray-2"
              @click="fileInput?.click()"
            >
              <FeatherIcon name="paperclip" class="h-3.5 w-3.5" /> {{ __('Adjuntar') }}
            </button>
          </div>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="a in attachments"
              :key="a.name"
              class="flex items-center gap-1.5 rounded border px-2 py-1 text-sm hover:bg-surface-gray-2"
              @click="openFile(a)"
            >
              <FilePdfIcon class="h-4 w-4" />
              <span class="max-w-[14rem] truncate">{{ a.file_name }}</span>
            </button>
            <span v-if="!attachments.length" class="py-1 text-sm text-ink-gray-4">
              {{ __('Sin adjuntos') }}
            </span>
          </div>
        </div>

        <div class="mt-4 rounded-lg border p-4">
          <div class="mb-2 text-sm font-semibold text-ink-gray-7">{{ __('Comentarios') }}</div>
          <div class="mb-3 space-y-2">
            <div v-if="!comments.length" class="text-sm text-ink-gray-4">{{ __('Sin comentarios') }}</div>
            <div v-for="cm in comments" :key="cm.name" class="rounded-lg border p-2">
              <div class="flex items-center gap-2 text-xs text-ink-gray-5">
                <UserAvatar :user="cm.comment_email || cm.owner" size="xs" />
                <span class="font-medium text-ink-gray-7">{{ cm.comment_by || userName(cm.owner) }}</span>
                <span>· {{ String(cm.creation).slice(0, 16).replace('T', ' ') }}</span>
              </div>
              <div class="mt-1 text-sm text-ink-gray-8" v-html="cm.content" />
            </div>
          </div>
          <div class="flex items-end gap-2">
            <textarea
              v-model="newComment"
              rows="2"
              :placeholder="__('Comentario...')"
              class="flex-1 rounded-lg border border-outline-gray-2 bg-surface-base px-2 py-1.5 text-sm focus:outline-none"
            />
            <Button variant="solid" :disabled="!newComment.trim()" @click="addComment">
              {{ __('Agregar') }}
            </Button>
          </div>
        </div>
      </template>
    </div>
    <div v-else class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4">
      <LucideAward class="h-10 w-10" />
      <div>{{ __('Elegí un caso o creá uno nuevo') }}</div>
    </div>
  </div>

  <input ref="fileInput" type="file" accept="application/pdf,image/*" class="hidden" @change="onFileSelected" />

  <Dialog v-model="showPreview" :options="{ size: '5xl' }">
    <template #body>
      <div class="flex h-full flex-col p-4">
        <div class="mb-3 flex items-center justify-between gap-2">
          <div class="truncate text-base font-semibold text-ink-gray-8">{{ previewFile?.file_name }}</div>
          <Button icon="x" @click="showPreview = false" />
        </div>
        <img v-if="previewFile && isImage(previewFile.file_type)" :src="previewFile.file_url" class="max-h-[72vh] w-full rounded border object-contain" />
        <iframe v-else-if="previewFile" :src="previewFile.file_url" class="h-[72vh] w-full rounded border" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideAward from '~icons/lucide/award'
import FilePdfIcon from '@/components/Icons/FilePdfIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import { usersStore } from '@/stores/users'
import { FeatherIcon, FormControl, Badge, Dialog, Button, call, toast, usePageMeta } from 'frappe-ui'
import { isImage } from '@/utils'
import { ref, reactive, computed } from 'vue'

const DT = 'CRM Caso Referencia'
const { getUser } = usersStore()
function userName(u) {
  return getUser(u)?.full_name || u
}

const cases = ref([])
const selected = ref(null)
const editing = ref(false)
const saving = ref(false)
const search = ref('')
const empty = () => ({ titulo: '', oportunidad: '', organizacion: '', industria: '', producto: '', estado_publicacion: 'Interno', fecha: '', resumen: '', problema: '', solucion: '', beneficios: '', kpi: '', responsable: '' })
const form = reactive(empty())

async function loadCases() {
  cases.value = await call('frappe.client.get_list', {
    doctype: DT,
    fields: ['name', 'titulo', 'organizacion', 'estado_publicacion', 'resumen'],
    limit_page_length: 0,
    order_by: 'modified desc',
  })
}
loadCases()

const filtered = computed(() => {
  if (!search.value.trim()) return cases.value
  const q = search.value.toLowerCase()
  return cases.value.filter(
    (c) => (c.titulo || '').toLowerCase().includes(q) || (c.organizacion || '').toLowerCase().includes(q),
  )
})

function nuevo() {
  selected.value = null
  Object.assign(form, empty())
  editing.value = true
  attachments.value = []
  comments.value = []
}
async function selectCase(name) {
  selected.value = name
  editing.value = true
  const doc = await call('frappe.client.get', { doctype: DT, name })
  Object.assign(form, empty(), {
    titulo: doc.titulo || '', oportunidad: doc.oportunidad || '', organizacion: doc.organizacion || '',
    industria: doc.industria || '', producto: doc.producto || '', estado_publicacion: doc.estado_publicacion || 'Interno',
    fecha: doc.fecha || '', resumen: doc.resumen || '', problema: doc.problema || '', solucion: doc.solucion || '',
    beneficios: doc.beneficios || '', kpi: doc.kpi || '', responsable: doc.responsable || '',
  })
  loadAttachments()
  loadComments()
}
function cancel() {
  editing.value = false
  selected.value = null
}
async function onDeal(v) {
  form.oportunidad = v
  if (v) {
    try {
      const d = await call('frappe.client.get_value', { doctype: 'CRM Deal', filters: v, fieldname: ['organization', 'industry'] })
      if (d?.organization && !form.organizacion) form.organizacion = d.organization
      if (d?.industry && !form.industria) form.industria = d.industry
    } catch (e) {}
  }
}
async function save() {
  if (!form.titulo.trim()) return
  saving.value = true
  try {
    const payload = { ...form }
    if (selected.value) {
      await call('frappe.client.set_value', { doctype: DT, name: selected.value, fieldname: payload })
    } else {
      const doc = await call('frappe.client.insert', { doc: { doctype: DT, ...payload } })
      selected.value = doc.name
      loadAttachments()
      loadComments()
    }
    await loadCases()
    toast.success(__('Guardado'))
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo guardar'))
  } finally {
    saving.value = false
  }
}
async function delCase() {
  if (!selected.value || !window.confirm(__('¿Eliminar este caso?'))) return
  try {
    await call('frappe.client.delete', { doctype: DT, name: selected.value })
    cancel()
    await loadCases()
    toast.success(__('Eliminado'))
  } catch (e) {
    toast.error(__('No se pudo eliminar'))
  }
}

// Adjuntos
const attachments = ref([])
const fileInput = ref(null)
async function loadAttachments() {
  attachments.value = []
  if (!selected.value) return
  try {
    attachments.value = await call('frappe.client.get_list', {
      doctype: 'File',
      filters: { attached_to_doctype: DT, attached_to_name: selected.value },
      fields: ['name', 'file_name', 'file_url', 'file_type'],
      limit_page_length: 0,
      order_by: 'creation desc',
    })
  } catch (e) {
    attachments.value = []
  }
}
function onFileSelected(e) {
  const f = e.target.files?.[0]
  e.target.value = ''
  if (f) uploadFile(f)
}
async function uploadFile(file) {
  if (!selected.value) return
  try {
    const fd = new FormData()
    fd.append('file', file, file.name)
    fd.append('is_private', '1')
    fd.append('folder', 'Home/Attachments')
    fd.append('doctype', DT)
    fd.append('docname', selected.value)
    const res = await fetch('/api/method/upload_file', { method: 'POST', headers: { 'X-Frappe-CSRF-Token': window.csrf_token }, body: fd })
    if (!res.ok) throw new Error(await res.text())
    toast.success(__('Adjuntado'))
    await loadAttachments()
  } catch (e) {
    toast.error(__('No se pudo adjuntar'))
  }
}
const showPreview = ref(false)
const previewFile = ref(null)
function openFile(a) {
  const t = (a.file_type || '').toLowerCase()
  if (isImage(a.file_type) || t === 'pdf') {
    previewFile.value = a
    showPreview.value = true
  } else {
    window.open(a.file_url, '_blank')
  }
}

// Comentarios
const comments = ref([])
const newComment = ref('')
async function loadComments() {
  comments.value = []
  if (!selected.value) return
  try {
    comments.value = await call('frappe.client.get_list', {
      doctype: 'Comment',
      filters: { comment_type: 'Comment', reference_doctype: DT, reference_name: selected.value },
      fields: ['name', 'content', 'comment_by', 'comment_email', 'owner', 'creation'],
      limit_page_length: 0,
      order_by: 'creation asc',
    })
  } catch (e) {
    comments.value = []
  }
}
async function addComment() {
  const text = newComment.value.trim()
  if (!text || !selected.value) return
  const me = getUser('sessionUser')
  try {
    await call('frappe.desk.form.utils.add_comment', {
      reference_doctype: DT, reference_name: selected.value, content: text,
      comment_email: me?.name, comment_by: me?.full_name || me?.name,
    })
    newComment.value = ''
    await loadComments()
  } catch (e) {
    toast.error(__('No se pudo comentar'))
  }
}

usePageMeta(() => ({ title: __('Casos de Referencia') }))
</script>
