<template>
  <div class="flex h-full min-h-0 gap-4 p-4 sm:p-5">
    <!-- Menú lateral de navegación -->
    <div class="flex w-64 shrink-0 flex-col gap-1 overflow-y-auto border-r pr-2">
      <div class="mb-1 px-2 text-xs font-semibold uppercase tracking-wide text-ink-gray-5">
        {{ __('Customer Value Roadmap') }}
      </div>
      <button
        v-for="(sec, i) in SECTIONS"
        :key="sec.key"
        type="button"
        class="flex items-start gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors"
        :class="active === i ? 'bg-surface-gray-3 font-semibold text-ink-gray-9' : 'text-ink-gray-6 hover:bg-surface-gray-2'"
        @click="active = i"
      >
        <span
          class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-xs font-semibold"
          :class="active === i ? 'bg-blue-600 text-white' : 'bg-surface-gray-4 text-ink-gray-7'"
        >
          {{ i + 1 }}
        </span>
        <span class="leading-tight">{{ sec.label }}</span>
      </button>
    </div>

    <!-- Contenido de la sección activa -->
    <div class="flex min-h-0 flex-1 flex-col">
      <div class="mb-2 flex items-center justify-between gap-2">
        <div class="text-base font-semibold text-ink-gray-8">
          {{ active + 1 }}. {{ SECTIONS[active].label }}
        </div>
        <Button
          variant="solid"
          :label="__('Guardar')"
          :loading="saving"
          @click="save"
        />
      </div>
      <div class="min-h-0 flex-1 overflow-y-auto rounded-lg border p-3">
        <TextEditor
          :key="SECTIONS[active].key"
          :content="vals[SECTIONS[active].key] || ''"
          :editable="true"
          :editor-class="['prose-sm max-w-none min-h-[20rem]']"
          :placeholder="__('Escribí aquí...')"
          @change="onChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { TextEditor, Button, call, toast } from 'frappe-ui'
import { ref, watch } from 'vue'

const props = defineProps({
  organizationId: { type: String, required: true },
})

const SECTIONS = [
  { key: 'custom_cvr_customer_profile', label: 'Customer Profile' },
  { key: 'custom_cvr_positioning', label: 'Customer / 3DS Positioning & Relationship' },
  { key: 'custom_cvr_strategy', label: 'Customer Strategy & 3DS Value Proposition' },
  { key: 'custom_cvr_roadmap', label: 'Strategic Planning & Roadmap' },
  { key: 'custom_cvr_governance', label: 'Organization & Governance' },
  { key: 'custom_cvr_current_plan', label: 'Current Year Plan' },
]

const active = ref(0)
const vals = ref({})
const saving = ref(false)

async function load() {
  try {
    const r = await call('frappe.client.get_value', {
      doctype: 'CRM Organization',
      filters: { name: props.organizationId },
      fieldname: SECTIONS.map((s) => s.key),
    })
    vals.value = r || {}
  } catch (e) {
    vals.value = {}
  }
}
load()
watch(() => props.organizationId, () => { active.value = 0; load() })

function onChange(html) {
  vals.value = { ...vals.value, [SECTIONS[active.value].key]: html }
}

async function save() {
  const key = SECTIONS[active.value].key
  saving.value = true
  try {
    await call('frappe.client.set_value', {
      doctype: 'CRM Organization',
      name: props.organizationId,
      fieldname: key,
      value: vals.value[key] || '',
    })
    toast.success(__('Sección guardada'))
  } catch (e) {
    toast.error(__('No se pudo guardar'))
  } finally {
    saving.value = false
  }
}
</script>
