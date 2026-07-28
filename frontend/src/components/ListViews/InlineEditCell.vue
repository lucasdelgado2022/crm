<template>
  <div class="group/edit flex w-full items-center gap-1 overflow-hidden">
    <template v-if="!editing">
      <slot />
      <button
        v-if="editable"
        class="ml-auto shrink-0 rounded p-0.5 opacity-0 transition-opacity duration-150 hover:bg-surface-gray-2 group-hover/edit:opacity-100"
        :title="__('Editar')"
        @click.stop.prevent="startEdit"
      >
        <FeatherIcon name="edit-2" class="h-3.5 w-3.5 text-ink-gray-5" />
      </button>
    </template>

    <div v-else class="w-full min-w-[7rem]" @click.stop.prevent>
      <FormControl
        v-if="editType === 'select'"
        type="select"
        size="sm"
        :options="selectOptions"
        :modelValue="editValue"
        @update:modelValue="(v) => onImmediate(v)"
        @keydown.esc="cancel"
      />
      <Link
        v-else-if="editType === 'link'"
        class="form-control"
        :doctype="column.options"
        :value="editValue || ''"
        @change="(v) => onImmediate(v)"
      />
      <FormControl
        v-else-if="editType === 'checkbox'"
        type="checkbox"
        :modelValue="!!editValue"
        @change="(e) => onImmediate(e.target.checked ? 1 : 0)"
      />
      <input
        v-else
        ref="inputEl"
        :type="
          editType === 'number'
            ? 'number'
            : editType === 'date'
              ? 'date'
              : 'text'
        "
        class="h-7 w-full rounded border border-outline-gray-3 bg-surface-base px-2 text-base text-ink-gray-8 focus:border-outline-gray-4 focus:outline-none focus:ring-0"
        v-model="editValue"
        @keydown.enter.stop.prevent="save"
        @keydown.esc.stop.prevent="cancel"
        @blur="save"
      />
    </div>
  </div>
</template>

<script setup>
import Link from '@/components/Controls/Link.vue'
import { FormControl, FeatherIcon, call, toast } from 'frappe-ui'
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  doctype: { type: String, required: true },
  name: { type: String, default: '' },
  column: { type: Object, required: true },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['saved'])

const EDITABLE = [
  'Data',
  'Small Text',
  'Text',
  'Select',
  'Link',
  'Int',
  'Float',
  'Currency',
  'Percent',
  'Check',
  'Date',
]
const BLOCKED_KEYS = [
  'name',
  'modified',
  'creation',
  'owner',
  '_assign',
  '_liked_by',
  '_email_count',
  '_comment_count',
  '_open_activities',
  'sla_status',
  'organization_logo',
  'image',
]

const editable = computed(() => {
  if (props.disabled || !props.name) return false
  if (BLOCKED_KEYS.includes(props.column.key)) return false
  return EDITABLE.includes(props.column.type)
})

const editType = computed(() => {
  const t = props.column.type
  if (t === 'Select') return 'select'
  if (t === 'Link') return 'link'
  if (t === 'Check') return 'checkbox'
  if (['Int', 'Float', 'Currency', 'Percent'].includes(t)) return 'number'
  if (t === 'Date') return 'date'
  return 'text'
})

const selectOptions = computed(() => {
  let opts = (props.column.options || '').split('\n')
  return opts.map((o) => ({ label: o || '—', value: o }))
})

const editing = ref(false)
const editValue = ref('')
const inputEl = ref(null)
let originalValue = ''

async function startEdit() {
  try {
    const res = await call('frappe.client.get_value', {
      doctype: props.doctype,
      filters: props.name,
      fieldname: props.column.key,
    })
    originalValue = res?.[props.column.key] ?? ''
    editValue.value = originalValue
    editing.value = true
    await nextTick()
    inputEl.value?.focus?.()
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo cargar el valor'))
  }
}

function onImmediate(v) {
  editValue.value = v
  save()
}

let saving = false
async function save() {
  if (saving || !editing.value) return
  let value = editValue.value
  if (value === originalValue) {
    editing.value = false
    return
  }
  saving = true
  try {
    await call('frappe.client.set_value', {
      doctype: props.doctype,
      name: props.name,
      fieldname: props.column.key,
      value: value === '' ? null : value,
    })
    editing.value = false
    toast.success(__('Guardado'))
    emit('saved')
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo guardar'))
  } finally {
    saving = false
  }
}

function cancel() {
  editing.value = false
}
</script>
