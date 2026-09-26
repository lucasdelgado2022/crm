<template>
  <div>
    <div
      class="group flex flex-wrap items-center gap-1 min-h-8 p-1 rounded text-base bg-surface-gray-2 hover:bg-surface-gray-3 focus:border-outline-gray-4 focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-8 transition-colors w-full"
    >
      <Button
        v-for="value in parsedValues"
        ref="valuesRef"
        :key="value"
        :label="displayLabel(value)"
        theme="gray"
        variant="subtle"
        class="rounded border border-outline-gray-2 bg-surface-base focus-visible:ring-outline-gray-4"
        :style="pillStyle(value)"
        @keydown.delete.capture.stop="removeLastValue"
      >
        <template
          v-if="linkField && linkField.options === 'User'"
          #prefix
        >
          <UserAvatar :user="value" size="xs" />
        </template>
        <template #suffix>
          <span
            class="lucide-x h-3.5"
            aria-hidden="true"
            @click.stop="removeValue(value)"
          />
        </template>
      </Button>
      <div class="min-w-[100px] flex-1">
        <Link
          v-if="linkField"
          class="form-control flex-1 truncate cursor-text"
          :value="query"
          :filters="filters"
          :doctype="linkField.options"
          :onCreate="create"
          :hideMe="true"
          @change="(v) => addValue(v)"
        >
          <template #target="{ togglePopover }">
            <button
              class="w-full h-7 cursor-text"
              @click.stop="togglePopover"
            />
          </template>
          <template
            v-if="linkField.options === 'User'"
            #item-prefix="{ option }"
          >
            <UserAvatar class="mr-2" :user="option.value" size="sm" />
          </template>
          <template
            v-if="linkField.options === 'User'"
            #item-label="{ option }"
          >
            <div class="cursor-pointer text-ink-gray-9">
              {{ getUser(option.value)?.full_name || option.value }}
            </div>
          </template>
        </Link>
      </div>
    </div>
    <ErrorMessage v-if="error" class="mt-2 pl-2" :message="error" />
  </div>
</template>

<script setup>
import Link from '@/components/Controls/Link.vue'
import { usersStore } from '@/stores/users'
import UserAvatar from '@/components/UserAvatar.vue'
import { createDocument } from '@/composables/document'
import { getMeta } from '@/stores/meta'
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  doctype: { type: String, required: true },
  errorMessage: {
    type: Function,
    default: (value) => `${value} is an Invalid value`,
  },
})

const emit = defineEmits(['change'])

const { getFields } = getMeta(props.doctype)
const { getUser } = usersStore()
function displayLabel(value) {
  if (linkField.value && linkField.value.options === 'User') {
    return getUser(value)?.full_name || value
  }
  return value
}

// Paleta de capsulas de color (hex inline: independiente de Tailwind/JIT)
const PILL_COLORS = [
  { bg: '#dbeafe', fg: '#1e40af', bd: '#bfdbfe' }, // blue
  { bg: '#dcfce7', fg: '#166534', bd: '#bbf7d0' }, // green
  { bg: '#f3e8ff', fg: '#6b21a8', bd: '#e9d5ff' }, // purple
  { bg: '#fef3c7', fg: '#92400e', bd: '#fde68a' }, // amber
  { bg: '#fce7f3', fg: '#9d174d', bd: '#fbcfe8' }, // pink
  { bg: '#ccfbf1', fg: '#115e59', bd: '#99f6e4' }, // teal
  { bg: '#ffedd5', fg: '#9a3412', bd: '#fdba74' }, // orange
  { bg: '#e0e7ff', fg: '#3730a3', bd: '#c7d2fe' }, // indigo
]
function pillStyle(value) {
  // campos de usuario: mantener capsula base (con avatar), sin color
  if (linkField.value && linkField.value.options === 'User') {
    return {}
  }
  const str = String(value || '')
  let h = 0
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0
  const c = PILL_COLORS[h % PILL_COLORS.length]
  return {
    backgroundColor: c.bg,
    color: c.fg,
    borderColor: c.bd,
  }
}

const values = defineModel({ type: Array, default: () => [] })

const valuesRef = ref([])
const error = ref(null)
const query = ref('')

const linkField = ref('')

const filters = computed(() => {
  if (!linkField.value) return []
  return { name: ['not in', parsedValues.value] }
})

const parsedValues = computed(() => {
  getLinkField()
  if (!linkField.value) return []
  return values.value.map((row) => row[linkField.value.fieldname])
})

const getLinkField = () => {
  error.value = ''
  if (!linkField.value) {
    let fields = getFields()
    linkField.value = fields?.find((df) =>
      ['Link', 'User'].includes(df.fieldtype),
    )
    if (!linkField.value) {
      error.value =
        'Table MultiSelect requires a Table with atleast one Link field'
    }
  }
  return linkField.value
}

const addValue = (value) => {
  error.value = null

  if (values.value.some((row) => row[linkField.value.fieldname] === value)) {
    error.value = 'Value already exists'
    return
  }

  if (value) {
    values.value.push({ [linkField.value.fieldname]: value })
    emit('change', values.value)
    if (!error.value) {
      query.value = ''
    }
  }
}

const removeValue = (value) => {
  let _value = values.value.filter(
    (row) => row[linkField.value.fieldname] !== value,
  )
  emit('change', _value)
}

const removeLastValue = () => {
  if (query.value) return

  let valueRef = valuesRef.value[valuesRef.value.length - 1]?.$el
  if (document.activeElement === valueRef) {
    values.value.pop()
    emit('change', values.value)
    nextTick(() => {
      if (values.value.length) {
        valueRef = valuesRef.value[valuesRef.value.length - 1].$el
        valueRef?.focus()
      }
    })
  } else {
    valueRef?.focus()
  }
}

function create(value, close) {
  const callback = (d) => {
    if (d) addValue(d.name)
  }
  createDocument(linkField.value.options, value, close, callback)
}
</script>
