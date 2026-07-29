<template>
  <div class="flex h-full flex-col px-3 pb-4 pt-2 sm:px-10">
    <div class="mb-3 flex items-center justify-between">
      <div class="text-base text-ink-gray-6">
        {{ __('Roadmap de implementación') }}
      </div>
      <Button
        variant="solid"
        :label="__('Agregar etapa')"
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
          <span
            class="mt-2 size-2.5 shrink-0 rounded-full"
            :class="estadoColor(r.estado)"
          />
          <FormControl
            class="flex-1"
            :placeholder="__('Etapa / hito')"
            :modelValue="r.etapa"
            @change="(e) => update(i, 'etapa', e.target.value)"
          />
          <FormControl
            type="date"
            class="w-40"
            :modelValue="r.fecha"
            @change="(e) => update(i, 'fecha', e.target.value)"
          />
          <FormControl
            type="select"
            class="w-36"
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
        <div class="flex gap-2 pl-5">
          <FormControl
            class="w-52"
            :placeholder="__('Responsable')"
            :modelValue="r.responsable"
            @change="(e) => update(i, 'responsable', e.target.value)"
          />
          <FormControl
            class="flex-1"
            :placeholder="__('Descripción')"
            :modelValue="r.descripcion"
            @change="(e) => update(i, 'descripcion', e.target.value)"
          />
        </div>
      </div>
    </div>
    <div
      v-else
      class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
    >
      <span class="lucide-milestone size-8" />
      <span class="text-base">{{ __('Sin etapas cargadas') }}</span>
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
const estados = ['Pendiente', 'En curso', 'Completado'].map((e) => ({
  label: e,
  value: e,
}))

function estadoColor(estado) {
  if (estado === 'Completado') return 'bg-green-500'
  if (estado === 'En curso') return 'bg-amber-500'
  return 'bg-ink-gray-4'
}

async function load() {
  try {
    const v = await call('frappe.client.get_value', {
      doctype: props.doctype,
      filters: props.docname,
      fieldname: 'custom_roadmap_data',
    })
    rows.value = JSON.parse(v?.custom_roadmap_data || '[]') || []
  } catch (e) {
    rows.value = []
  }
}

async function save() {
  try {
    await call('frappe.client.set_value', {
      doctype: props.doctype,
      name: props.docname,
      fieldname: 'custom_roadmap_data',
      value: JSON.stringify(rows.value),
    })
  } catch (e) {
    toast.error(__('No se pudo guardar'))
  }
}

function update(i, field, value) {
  rows.value[i][field] = value
  if (field === 'fecha') rows.value.sort((a, b) => (a.fecha || '') > (b.fecha || '') ? 1 : -1)
  save()
}
function addRow() {
  rows.value.push({
    etapa: '',
    fecha: '',
    responsable: '',
    descripcion: '',
    estado: 'Pendiente',
  })
}
function removeRow(i) {
  rows.value.splice(i, 1)
  save()
}

onMounted(load)
</script>
