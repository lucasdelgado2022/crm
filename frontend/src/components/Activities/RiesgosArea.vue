<template>
  <div class="flex h-full flex-col px-3 pb-4 pt-2 sm:px-10">
    <div class="mb-3 flex items-center justify-between">
      <div class="text-base text-ink-gray-6">
        {{ __('Riesgos identificados y su plan de mitigación') }}
      </div>
      <Button
        variant="solid"
        :label="__('Agregar riesgo')"
        iconLeft="plus"
        @click="addRow"
      />
    </div>

    <div v-if="rows.length" class="flex flex-col gap-3 overflow-y-auto">
      <div
        v-for="(r, i) in rows"
        :key="i"
        class="rounded-lg border border-outline-gray-2 p-3"
      >
        <div class="mb-2 flex items-start gap-2">
          <FormControl
            class="flex-1"
            :placeholder="__('Riesgo')"
            :modelValue="r.riesgo"
            @change="(e) => update(i, 'riesgo', e.target.value)"
          />
          <FormControl
            type="select"
            class="w-40"
            :options="estados"
            :modelValue="r.estado"
            @change="(e) => update(i, 'estado', e.target.value)"
          />
          <Button
            variant="ghost"
            :tooltip="__('Eliminar')"
            @click="removeRow(i)"
          >
            <template #icon>
              <span class="lucide-trash-2 size-4 text-ink-gray-6" />
            </template>
          </Button>
        </div>
        <FormControl
          type="textarea"
          :placeholder="__('Plan de mitigación')"
          :modelValue="r.mitigacion"
          :rows="2"
          @change="(e) => update(i, 'mitigacion', e.target.value)"
        />
      </div>
    </div>
    <div
      v-else
      class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
    >
      <span class="lucide-shield-alert size-8" />
      <span class="text-base">{{ __('Sin riesgos cargados') }}</span>
    </div>
  </div>
</template>

<script setup>
import { FormControl, Button, call, toast } from 'frappe-ui'
import { ref, onMounted } from 'vue'

const props = defineProps({
  doctype: { type: String, default: 'CRM Deal' },
  docname: { type: String, default: '' },
})

const rows = ref([])
const estados = ['Abierto', 'En curso', 'Mitigado', 'Cerrado'].map((e) => ({
  label: e,
  value: e,
}))

async function load() {
  try {
    const v = await call('frappe.client.get_value', {
      doctype: props.doctype,
      filters: props.docname,
      fieldname: 'custom_riesgos_data',
    })
    rows.value = JSON.parse(v?.custom_riesgos_data || '[]') || []
  } catch (e) {
    rows.value = []
  }
}

async function save() {
  try {
    await call('frappe.client.set_value', {
      doctype: props.doctype,
      name: props.docname,
      fieldname: 'custom_riesgos_data',
      value: JSON.stringify(rows.value),
    })
  } catch (e) {
    toast.error(__('No se pudo guardar'))
  }
}

function update(i, field, value) {
  rows.value[i][field] = value
  save()
}
function addRow() {
  rows.value.push({ riesgo: '', mitigacion: '', estado: 'Abierto' })
}
function removeRow(i) {
  rows.value.splice(i, 1)
  save()
}

onMounted(load)
</script>
