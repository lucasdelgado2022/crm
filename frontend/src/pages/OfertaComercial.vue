<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <LucideLibrary class="h-5 w-5" />
        {{ __('Catálogo de Oferta Comercial') }}
      </div>
    </template>
    <template #right-header>
      <Button variant="solid" @click="openAdd(null)">
        <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
        {{ __('Nuevo catálogo') }}
      </Button>
    </template>
  </LayoutHeader>

  <div class="flex h-full overflow-hidden">
    <!-- Árbol -->
    <div class="w-2/5 shrink-0 overflow-y-auto border-r p-2 sm:w-1/3">
      <div class="mb-2 px-2">
        <FormControl
          type="text"
          :placeholder="__('Buscar en el catálogo...')"
          v-model="search"
        >
          <template #prefix>
            <FeatherIcon name="search" class="h-4 w-4 text-ink-gray-5" />
          </template>
        </FormControl>
      </div>
      <div
        v-for="row in visibleRows"
        :key="row.name"
        class="group flex cursor-pointer items-center gap-2 rounded py-2 pr-1 text-base hover:bg-surface-gray-2"
        :class="selected === row.name ? 'bg-surface-gray-3' : ''"
        :style="{ paddingLeft: 8 + row.depth * 22 + 'px' }"
        @click="select(row.name)"
      >
        <button
          class="flex h-4 w-4 shrink-0 items-center justify-center text-ink-gray-5"
          @click.stop="toggle(row.name)"
        >
          <FeatherIcon
            v-if="hasChildren(row.name)"
            :name="expanded.has(row.name) ? 'chevron-down' : 'chevron-right'"
            class="h-4 w-4"
          />
        </button>
        <span
          class="h-2 w-2 shrink-0 rounded-sm"
          :style="{ backgroundColor: typeColor(row.node_type) }"
        />
        <span class="flex-1 truncate text-ink-gray-8">{{ row.titulo }}</span>
        <Badge
          v-if="row.node_type === 'Producto CRM' && row.estado_crm"
          :theme="estadoTheme(row.estado_crm)"
          variant="subtle"
          size="sm"
        >
          {{ row.estado_crm }}
        </Badge>
        <button
          v-if="childType(row.node_type)"
          class="hidden h-5 w-5 shrink-0 items-center justify-center rounded text-ink-gray-5 hover:bg-surface-gray-3 group-hover:flex"
          :title="__('Agregar')"
          @click.stop="openAdd(row.name)"
        >
          <FeatherIcon name="plus" class="h-3.5 w-3.5" />
        </button>
      </div>
      <div v-if="!visibleRows.length" class="p-4 text-center text-sm text-ink-gray-4">
        {{ __('Sin nodos') }}
      </div>
    </div>

    <!-- Detalle -->
    <div v-if="node" class="flex flex-1 flex-col overflow-y-auto p-4 sm:p-6">
      <div class="flex items-start justify-between gap-2">
        <div>
          <div class="flex items-center gap-2">
            <span
              class="h-2.5 w-2.5 rounded-sm"
              :style="{ backgroundColor: typeColor(node.node_type) }"
            />
            <span class="text-xs uppercase tracking-wide text-ink-gray-5">
              {{ typeLabel(node.node_type) }}
            </span>
            <Badge
              v-if="node.node_type === 'Producto CRM' && node.estado_crm"
              :theme="estadoTheme(node.estado_crm)"
              variant="subtle"
              size="sm"
            >
              {{ node.estado_crm }}
            </Badge>
          </div>
          <div class="mt-1 text-xl font-semibold text-ink-gray-9">
            {{ node.titulo }}
          </div>
          <div class="mt-1 text-xs text-ink-gray-5">{{ breadcrumb }}</div>
        </div>
        <div class="flex shrink-0 gap-2">
          <Button
            v-if="childType(node.node_type)"
            variant="subtle"
            @click="openAdd(node.name)"
          >
            <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
            {{ typeLabel(childType(node.node_type)) }}
          </Button>
          <Button variant="subtle" @click="openEdit(node)">
            {{ __('Editar') }}
          </Button>
          <Button variant="subtle" theme="red" @click="delNode(node)">
            <FeatherIcon name="trash-2" class="h-4 w-4" />
          </Button>
        </div>
      </div>

      <!-- Links a producto -->
      <div
        v-if="node.crm_product || node.erpnext_item"
        class="mt-3 flex flex-wrap gap-2 text-sm"
      >
        <a
          v-if="node.crm_product"
          :href="'/app/crm-product/' + encodeURIComponent(node.crm_product)"
          target="_blank"
          class="rounded border px-2 py-1 text-ink-blue-link"
        >
          {{ __('Producto CRM') }}: {{ node.crm_product }}
        </a>
        <a
          v-if="node.erpnext_item"
          :href="'/app/item/' + encodeURIComponent(node.erpnext_item)"
          target="_blank"
          class="rounded border px-2 py-1 text-ink-blue-link"
        >
          {{ __('Item ERP') }}: {{ node.erpnext_item }}
        </a>
      </div>

      <!-- Descripción -->
      <div class="mt-4 rounded-lg border p-4">
        <div class="mb-2 text-sm font-semibold text-ink-gray-7">
          {{ __('Descripción') }}
        </div>
        <div
          v-if="node.descripcion"
          class="prose-sm max-w-none text-sm text-ink-gray-8"
          v-html="node.descripcion"
        />
        <div v-else class="text-sm text-ink-gray-4">{{ __('Sin descripción') }}</div>
      </div>

      <!-- Adjuntos -->
      <div class="mt-4 rounded-lg border p-4">
        <div class="mb-2 flex items-center justify-between">
          <div class="text-sm font-semibold text-ink-gray-7">
            {{ __('Adjuntos') }}
          </div>
          <button
            class="flex items-center gap-1 rounded border border-dashed border-outline-gray-2 px-2 py-1 text-xs text-ink-gray-5 hover:bg-surface-gray-2"
            @click="triggerUpload"
          >
            <FeatherIcon name="paperclip" class="h-3.5 w-3.5" /> {{ __('Adjuntar PDF') }}
          </button>
        </div>
        <div
          class="flex flex-wrap gap-2 rounded"
          :class="dropping ? 'bg-surface-blue-2 ring-1 ring-outline-blue-2' : ''"
          @drop.prevent="onDrop"
          @dragover.prevent="dropping = true"
          @dragleave.prevent="dropping = false"
        >
          <div
            v-for="a in attachments"
            :key="a.name"
            class="flex items-center gap-1 rounded border px-1.5 py-1 text-sm hover:bg-surface-gray-2"
          >
            <button class="flex items-center gap-1.5" @click="openFile(a)">
              <FilePdfIcon class="h-4 w-4" />
              <span class="max-w-[14rem] truncate">{{ a.file_name }}</span>
            </button>
            <button
              class="ml-0.5 text-ink-gray-4 hover:text-ink-gray-7"
              :title="__('Reemplazar por nueva versión')"
              @click.stop="replaceAttachment(a)"
            >
              <FeatherIcon name="refresh-cw" class="h-3.5 w-3.5" />
            </button>
          </div>
          <span v-if="!attachments.length" class="py-2 text-sm text-ink-gray-4">
            {{ __('Arrastrá un PDF o hacé clic en "Adjuntar PDF"') }}
          </span>
        </div>
      </div>

      <!-- Comentarios -->
      <div class="mt-4 rounded-lg border p-4">
        <div class="mb-2 text-sm font-semibold text-ink-gray-7">
          {{ __('Comentarios') }}
        </div>
        <div class="mb-3 space-y-2">
          <div v-if="!comments.length" class="text-sm text-ink-gray-4">
            {{ __('Sin comentarios') }}
          </div>
          <div v-for="c in comments" :key="c.name" class="rounded-lg border p-2">
            <div class="flex items-center gap-2 text-xs text-ink-gray-5">
              <UserAvatar :user="c.comment_email || c.owner" size="xs" />
              <span class="font-medium text-ink-gray-7">
                {{ c.comment_by || userName(c.owner) }}
              </span>
              <span>· {{ String(c.creation).slice(0, 16).replace('T', ' ') }}</span>
            </div>
            <div class="mt-1 text-sm text-ink-gray-8" v-html="c.content" />
          </div>
        </div>
        <div class="flex items-end gap-2">
          <textarea
            v-model="newComment"
            rows="2"
            :placeholder="__('Escribí un comentario...')"
            class="flex-1 rounded-lg border border-outline-gray-2 bg-surface-base px-2 py-1.5 text-sm text-ink-gray-8 focus:outline-none"
          />
          <Button
            variant="solid"
            :loading="savingComment"
            :disabled="!newComment.trim()"
            @click="addComment"
          >
            {{ __('Agregar') }}
          </Button>
        </div>
      </div>
    </div>
    <div
      v-else
      class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
    >
      <LucideLibrary class="h-10 w-10" />
      <div>{{ __('Seleccioná un nodo del catálogo') }}</div>
    </div>
  </div>

  <input
    ref="fileInput"
    type="file"
    accept="application/pdf,image/*"
    class="hidden"
    @change="onFileSelected"
  />

  <input
    ref="replaceInput"
    type="file"
    accept="application/pdf,image/*"
    class="hidden"
    @change="onReplaceSelected"
  />

  <!-- Preview -->
  <Dialog v-model="showPreview" :options="{ size: '5xl' }">
    <template #body>
      <div class="flex h-full flex-col p-4">
        <div class="mb-3 flex items-center justify-between gap-2">
          <div class="truncate text-base font-semibold text-ink-gray-8">
            {{ previewFile?.file_name }}
          </div>
          <div class="flex shrink-0 gap-2">
            <Button icon="external-link" @click="openInTab" />
            <Button icon="x" @click="showPreview = false" />
          </div>
        </div>
        <img
          v-if="previewFile && isImage(previewFile.file_type)"
          :src="previewFile.file_url"
          class="max-h-[72vh] w-full rounded border object-contain"
        />
        <iframe
          v-else-if="previewFile"
          :src="previewFile.file_url"
          class="h-[72vh] w-full rounded border"
        />
      </div>
    </template>
  </Dialog>

  <!-- Add / Edit -->
  <Dialog v-model="showForm" :options="{ size: 'lg' }">
    <template #body>
      <div class="p-4">
        <div class="mb-3 text-base font-semibold text-ink-gray-8">
          {{ formTitle }}
        </div>
        <div class="space-y-3">
        <FormControl v-model="form.titulo" :label="__('Título')" />
        <FormControl
          v-if="form.node_type === 'Producto CRM'"
          type="select"
          :label="__('Estado')"
          v-model="form.estado_crm"
          :options="['', 'Maduro', 'En Desarrollo', 'Explorar']"
        />
        <div v-if="form.node_type === 'Producto CRM'">
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Producto CRM (opcional)') }}</div>
          <Link doctype="CRM Product" :value="form.crm_product" @change="(v) => (form.crm_product = v)" />
        </div>
        <div v-if="form.node_type === 'Producto ERP'">
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Item de ERPNext') }}</div>
          <Link doctype="Item" :value="form.erpnext_item" @change="(v) => (form.erpnext_item = v)" />
        </div>
        <div>
          <div class="mb-1 text-xs text-ink-gray-5">{{ __('Descripción') }}</div>
          <textarea
            v-model="form.descripcion"
            rows="4"
            class="w-full rounded-lg border border-outline-gray-2 bg-surface-base px-2 py-1.5 text-sm focus:outline-none"
          />
        </div>
        </div>
        <div class="mt-4 flex justify-end gap-2">
          <Button @click="showForm = false">{{ __('Cancelar') }}</Button>
          <Button
            variant="solid"
            :loading="savingForm"
            :disabled="!form.titulo.trim()"
            @click="saveForm"
          >
            {{ __('Guardar') }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideLibrary from '~icons/lucide/library'
import FilePdfIcon from '@/components/Icons/FilePdfIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import { usersStore } from '@/stores/users'
import {
  FeatherIcon,
  FormControl,
  Badge,
  Dialog,
  Button,
  call,
  toast,
  usePageMeta,
} from 'frappe-ui'
import { isImage } from '@/utils'
import { ref, reactive, computed } from 'vue'

const DT = 'CRM Catalogo Nodo'
const CHILD = {
  Catalogo: 'Grupo',
  Grupo: 'Categoria',
  Categoria: 'Producto CRM',
  'Producto CRM': 'Producto ERP',
}
const TYPE_COLOR = {
  Catalogo: '#4f46e5',
  Grupo: '#0891b2',
  Categoria: '#16a34a',
  'Producto CRM': '#f59e0b',
  'Producto ERP': '#db2777',
}
const TYPE_LABEL = {
  Catalogo: 'Catálogo',
  Grupo: 'Grupo',
  Categoria: 'Categoría',
  'Producto CRM': 'Producto CRM',
  'Producto ERP': 'Producto ERP',
}
function typeLabel(t) {
  return TYPE_LABEL[t] || t
}

const { getUser } = usersStore()
function userName(u) {
  return getUser(u)?.full_name || u
}

const nodes = ref([])
const selected = ref(null)
const expanded = reactive(new Set())
const search = ref('')

async function loadNodes() {
  nodes.value = await call('frappe.client.get_list', {
    doctype: DT,
    fields: ['name', 'titulo', 'node_type', 'parent_nodo', 'orden', 'estado_crm', 'crm_product', 'erpnext_item', 'descripcion'],
    limit_page_length: 0,
    order_by: 'orden asc, titulo asc',
  })
  // desplegar por defecto solo los catálogos (muestra el nivel 1 / grupos)
  for (const n of nodes.value) if (n.node_type === 'Catalogo') expanded.add(n.name)
}
loadNodes()

const byParent = computed(() => {
  const m = {}
  for (const n of nodes.value) (m[n.parent_nodo || ''] = m[n.parent_nodo || ''] || []).push(n)
  return m
})
function childrenOf(name) {
  return byParent.value[name || ''] || []
}
function hasChildren(name) {
  return childrenOf(name).length > 0
}
function childType(t) {
  return CHILD[t] || null
}
function typeColor(t) {
  return TYPE_COLOR[t] || '#64748b'
}
function estadoTheme(e) {
  return e === 'Maduro' ? 'green' : e === 'En Desarrollo' ? 'blue' : 'orange'
}

const nodeMap = computed(() => Object.fromEntries(nodes.value.map((n) => [n.name, n])))
const node = computed(() => (selected.value ? nodeMap.value[selected.value] : null))

const breadcrumb = computed(() => {
  if (!node.value) return ''
  const parts = []
  let cur = node.value
  const seen = new Set()
  while (cur && cur.parent_nodo && !seen.has(cur.name)) {
    seen.add(cur.name)
    const p = nodeMap.value[cur.parent_nodo]
    if (!p) break
    parts.unshift(p.titulo)
    cur = p
  }
  return parts.join(' › ')
})

// Filtro: si hay búsqueda, mostrar nodos que matchean + sus ancestros
const matchSet = computed(() => {
  if (!search.value.trim()) return null
  const q = search.value.toLowerCase()
  const keep = new Set()
  for (const n of nodes.value) {
    if ((n.titulo || '').toLowerCase().includes(q)) {
      let cur = n
      const seen = new Set()
      while (cur && !seen.has(cur.name)) {
        keep.add(cur.name)
        seen.add(cur.name)
        cur = cur.parent_nodo ? nodeMap.value[cur.parent_nodo] : null
      }
    }
  }
  return keep
})

const visibleRows = computed(() => {
  const out = []
  const ms = matchSet.value
  const walk = (parent, depth) => {
    for (const n of childrenOf(parent)) {
      if (ms && !ms.has(n.name)) continue
      out.push({ ...n, depth })
      if (ms || expanded.has(n.name)) walk(n.name, depth + 1)
    }
  }
  walk('', 0)
  return out
})

function toggle(name) {
  if (expanded.has(name)) expanded.delete(name)
  else expanded.add(name)
}
function select(name) {
  selected.value = name
  if (hasChildren(name)) expanded.add(name)
  loadAttachments()
  loadComments()
}

// ---------- Add / Edit ----------
const showForm = ref(false)
const savingForm = ref(false)
const editing = ref(null)
const form = reactive({ titulo: '', node_type: 'Catalogo', parent_nodo: '', estado_crm: '', crm_product: '', erpnext_item: '', descripcion: '' })
const formTitle = computed(() =>
  editing.value ? __('Editar') + ' ' + form.node_type : __('Nuevo') + ' ' + form.node_type,
)

function openAdd(parentName) {
  editing.value = null
  const parent = parentName ? nodeMap.value[parentName] : null
  const nt = parent ? CHILD[parent.node_type] : 'Catalogo'
  Object.assign(form, { titulo: '', node_type: nt, parent_nodo: parentName || '', estado_crm: '', crm_product: '', erpnext_item: '', descripcion: '' })
  showForm.value = true
}
function openEdit(n) {
  editing.value = n.name
  Object.assign(form, {
    titulo: n.titulo || '', node_type: n.node_type, parent_nodo: n.parent_nodo || '',
    estado_crm: n.estado_crm || '', crm_product: n.crm_product || '', erpnext_item: n.erpnext_item || '', descripcion: n.descripcion || '',
  })
  showForm.value = true
}
async function saveForm() {
  if (!form.titulo.trim()) return
  savingForm.value = true
  try {
    if (editing.value) {
      await call('frappe.client.set_value', {
        doctype: DT, name: editing.value,
        fieldname: { titulo: form.titulo, estado_crm: form.estado_crm, crm_product: form.crm_product, erpnext_item: form.erpnext_item, descripcion: form.descripcion },
      })
    } else {
      const siblings = childrenOf(form.parent_nodo)
      await call('frappe.client.insert', {
        doc: {
          doctype: DT, titulo: form.titulo, node_type: form.node_type, parent_nodo: form.parent_nodo,
          orden: siblings.length, estado_crm: form.estado_crm, crm_product: form.crm_product, erpnext_item: form.erpnext_item, descripcion: form.descripcion,
        },
      })
      if (form.parent_nodo) expanded.add(form.parent_nodo)
    }
    showForm.value = false
    await loadNodes()
    toast.success(__('Guardado'))
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo guardar'))
  } finally {
    savingForm.value = false
  }
}
async function delNode(n) {
  if (childrenOf(n.name).length) {
    toast.error(__('Eliminá primero los nodos hijos'))
    return
  }
  if (!window.confirm(__('¿Eliminar "{0}"?', [n.titulo]))) return
  try {
    await call('frappe.client.delete', { doctype: DT, name: n.name })
    if (selected.value === n.name) selected.value = null
    await loadNodes()
    toast.success(__('Eliminado'))
  } catch (e) {
    toast.error(__('No se pudo eliminar'))
  }
}

// ---------- Adjuntos ----------
const attachments = ref([])
const fileInput = ref(null)
const dropping = ref(false)
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
function triggerUpload() {
  fileInput.value?.click()
}
function onFileSelected(e) {
  const f = e.target.files?.[0]
  e.target.value = ''
  if (f) uploadFile(f)
}
function onDrop(e) {
  dropping.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) uploadFile(f)
}
async function uploadFile(file) {
  if (!selected.value) return false
  try {
    const fd = new FormData()
    fd.append('file', file, file.name)
    fd.append('is_private', '1')
    fd.append('folder', 'Home/Attachments')
    fd.append('doctype', DT)
    fd.append('docname', selected.value)
    const res = await fetch('/api/method/upload_file', {
      method: 'POST',
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token },
      body: fd,
    })
    if (!res.ok) throw new Error(await res.text())
    toast.success(__('Adjuntado'))
    await loadAttachments()
    return true
  } catch (e) {
    toast.error(__('No se pudo adjuntar'))
    return false
  }
}
const replaceInput = ref(null)
const replaceTarget = ref(null)
function replaceAttachment(a) {
  replaceTarget.value = a
  replaceInput.value?.click()
}
async function onReplaceSelected(e) {
  const f = e.target.files?.[0]
  e.target.value = ''
  const old = replaceTarget.value
  replaceTarget.value = null
  if (!f || !old) return
  const ok = await uploadFile(f)
  if (!ok) return
  try {
    await call('frappe.client.delete', { doctype: 'File', name: old.name })
  } catch (err) {
    // noop
  }
  toast.success(__('Reemplazado por nueva versión'))
  await loadAttachments()
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
function openInTab() {
  if (previewFile.value) window.open(previewFile.value.file_url, '_blank')
}

// ---------- Comentarios ----------
const comments = ref([])
const newComment = ref('')
const savingComment = ref(false)
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
  savingComment.value = true
  const me = getUser('sessionUser')
  try {
    await call('frappe.desk.form.utils.add_comment', {
      reference_doctype: DT,
      reference_name: selected.value,
      content: text,
      comment_email: me?.name,
      comment_by: me?.full_name || me?.name,
    })
    newComment.value = ''
    await loadComments()
    toast.success(__('Comentario agregado'))
  } catch (e) {
    toast.error(__('No se pudo comentar'))
  } finally {
    savingComment.value = false
  }
}

usePageMeta(() => ({ title: __('Oferta Comercial') }))
</script>
