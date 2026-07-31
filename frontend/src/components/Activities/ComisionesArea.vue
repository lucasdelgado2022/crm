<template>
  <div class="flex h-full flex-col px-3 pb-4 pt-2 sm:px-10">
    <div class="mb-3 flex items-center justify-between gap-2">
      <div class="text-base text-ink-gray-6">
        {{ __('Comisiones — base de cálculo:') }}
        <span class="font-medium text-ink-gray-8">
          {{ fmt(base) }} ({{ __('Solaer Revenue') }})
        </span>
      </div>
      <Button
        variant="solid"
        :label="__('Agregar comisión')"
        iconLeft="plus"
        @click="addRow"
      />
    </div>

    <div v-if="rows.length" class="flex flex-col gap-2 overflow-y-auto">
      <!-- encabezado -->
      <div
        class="grid grid-cols-[1fr_5rem_7rem_9rem_2rem] items-center gap-2 px-1 text-xs font-medium text-ink-gray-5"
      >
        <div>{{ __('Vendedor (Sales Person)') }}</div>
        <div class="text-right">{{ __('%') }}</div>
        <div class="text-right">{{ __('Monto') }}</div>
        <div>{{ __('Estado pago') }}</div>
        <div></div>
      </div>
      <div
        v-for="(r, i) in rows"
        :key="i"
        class="grid grid-cols-[1fr_5rem_7rem_9rem_2rem] items-center gap-2 rounded-lg border border-outline-gray-2 p-2"
      >
        <Link
          class="form-control"
          doctype="Sales Person"
          :value="r.sales_person || ''"
          @change="(v) => update(i, 'sales_person', v)"
        />
        <FormControl
          type="number"
          class="text-right"
          :modelValue="r.porcentaje"
          @change="(e) => update(i, 'porcentaje', parseFloat(e.target.value) || 0)"
        />
        <div class="text-right text-base font-medium text-ink-gray-8">
          {{ fmt(monto(r)) }}
        </div>
        <FormControl
          type="select"
          :options="estados"
          :modelValue="r.estado"
          @change="(e) => update(i, 'estado', e.target.value)"
        />
        <Button variant="ghost" :tooltip="__('Eliminar')" @click="removeRow(i)">
          <template #icon>
            <span class="lucide-trash-2 size-4 text-ink-gray-6" />
          </template>
        </Button>
      </div>

      <!-- total -->
      <div
        class="mt-1 flex items-center justify-end gap-3 border-t border-outline-gray-2 px-1 pt-2 text-base"
      >
        <span class="text-ink-gray-6">{{ __('Total comisiones:') }}</span>
        <span class="font-semibold text-ink-gray-9">{{ fmt(total) }}</span>
      </div>
    </div>
    <div
      v-else
      class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
    >
      <span class="lucide-hand-coins size-8" />
      <span class="text-base">{{ __('Sin comisiones asignadas') }}</span>
    </div>

    <div class="mt-3 rounded-md bg-surface-gray-2 px-3 py-2 text-sm text-ink-gray-6">
      {{
        __(
          'La orden de pago en Payroll se generará cuando el módulo de Payroll (hrms) esté instalado.',
        )
      }}
    </div>
  </div>
</template>

<script setup>
import Link from '@/components/Controls/Link.vue'
import { FormControl, Button, call, toast } from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  doctype: { type: String, default: 'CRM Deal' },
  docname: { type: String, default: '' },
})

const rows = ref([])
const base = ref(0)
const estados = ['Pendiente', 'Aprobado', 'Pagado'].map((e) => ({
  label: e,
  value: e,
}))

function fmt(v) {
  const n = Number(v || 0)
  return 'USD ' + n.toLocaleString('es-AR', { maximumFractionDigits: 2 })
}
function monto(r) {
  return Math.round(((base.value || 0) * (parseFloat(r.porcentaje) || 0)) / 100 * 100) / 100
}
const total = computed(() => rows.value.reduce((a, r) => a + monto(r), 0))

async function load() {
  try {
    const v = await call('frappe.client.get_value', {
      doctype: props.doctype,
      filters: props.docname,
      fieldname: ['custom_comisiones_data', 'custom_solaer_revenue', 'annual_revenue'],
    })
    base.value = Number(v?.custom_solaer_revenue || v?.annual_revenue || 0)
    rows.value = JSON.parse(v?.custom_comisiones_data || '[]') || []
  } catch (e) {
    rows.value = []
  }
}

async function save() {
  try {
    // guardar tambien el monto calculado para que quede persistido
    const payload = rows.value.map((r) => ({
      sales_person: r.sales_person || '',
      porcentaje: parseFloat(r.porcentaje) || 0,
      monto: monto(r),
      estado: r.estado || 'Pendiente',
    }))
    await call('frappe.client.set_value', {
      doctype: props.doctype,
      name: props.docname,
      fieldname: 'custom_comisiones_data',
      value: JSON.stringify(payload),
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
  rows.value.push({
    sales_person: '',
    porcentaje: 0,
    monto: 0,
    estado: 'Pendiente',
  })
}
function removeRow(i) {
  rows.value.splice(i, 1)
  save()
}

onMounted(load)
</script>
