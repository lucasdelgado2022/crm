<template>
  <div class="flex flex-col rounded-lg border">
    <div class="flex items-center gap-2 border-b px-4 py-3 text-base font-semibold text-ink-gray-8">
      <FeatherIcon name="layers" class="h-5" />
      {{ __('Ecosistema Productivo') }}
    </div>
    <div class="flex flex-col divide-y">
      <div
        v-for="e in ECOSISTEMAS"
        :key="e.key"
        class="flex flex-wrap items-center gap-2 px-4 py-2.5"
      >
        <span class="w-40 shrink-0 text-sm font-bold text-blue-900">{{ e.label }}</span>
        <div class="flex flex-1 flex-wrap items-center gap-1.5">
          <span
            v-for="c in catsOf(e.key)"
            :key="c"
            class="group flex items-center gap-1 rounded-full border border-blue-300 bg-blue-100 py-0.5 pl-2.5 pr-1 text-xs font-semibold text-blue-900"
          >
            {{ c }}
            <button
              class="flex h-4 w-4 items-center justify-center rounded-full text-blue-700 hover:bg-red-500 hover:text-white"
              :title="__('Desasociar')"
              @click="askRemove(e, c)"
            >
              <FeatherIcon name="minus" class="h-3 w-3" />
            </button>
          </span>
          <Dropdown v-if="remaining(e.key).length" :options="addOptions(e)" placement="bottom-start">
            <button
              class="flex items-center gap-0.5 rounded-full border border-dashed border-blue-400 px-2 py-0.5 text-xs font-semibold text-blue-700 hover:bg-blue-50"
              :title="__('Agregar categoría')"
            >
              <FeatherIcon name="plus" class="h-3 w-3" />
              {{ __('Agregar') }}
            </button>
          </Dropdown>
          <span v-if="!catsOf(e.key).length && !remaining(e.key).length" class="text-xs text-ink-gray-4">—</span>
        </div>
      </div>
    </div>

    <!-- Confirmación de desasociar -->
    <Dialog
      v-model="showConfirm"
      :options="{
        title: __('Desasociar categoría'),
        message: pending
          ? __('¿Seguro que querés desasociar «{0}» de {1}?', [pending.cat, pending.label])
          : '',
        actions: [
          {
            label: __('Desasociar'),
            theme: 'red',
            variant: 'solid',
            onClick: confirmRemove,
          },
          { label: __('Cancelar'), onClick: () => (showConfirm = false) },
        ],
      }"
    />
  </div>
</template>

<script setup>
import { FeatherIcon, Dropdown, Dialog, call, toast } from 'frappe-ui'
import { ref, watch } from 'vue'

const props = defineProps({
  organizationId: { type: String, required: true },
})

const ECOSISTEMAS = [
  { key: 'custom_ecosistema_nuclear', label: 'Nuclear', cats: ['Nuclear Projects', 'EPC', 'Equipment', 'Engineering Services', 'Research', 'Education', 'Autoridad Regulatoria'] },
  { key: 'custom_ecosistema_oil_gas', label: 'Oil & Gas', cats: ['Exploration', 'Petrochemical', 'Equipment', 'EPC', 'Engineering Services', 'Transport', 'Academia Workforce', 'Safety'] },
  { key: 'custom_ecosistema_mineria', label: 'Minería', cats: ['Large Mining Owners Operators (OO)', 'Small-Medium Mining Owners Operators (OO)', 'Metals & Minerals', 'EPC - Engineering Procurement Construction', 'Equipment Providers', 'Engineering Services', 'Testing Inspection Certification', 'R&D - Research & Development', 'Academia Workforce'] },
  { key: 'custom_ecosistema_automotriz', label: 'Automotriz', cats: ['OEM', 'Electric OEM', 'Motos', 'Supplier Tier 1', 'Supplier Tier 2-3', 'Engineering Services', 'Robotics & Line Builders'] },
  { key: 'custom_ecosistema_maquinas_agro', label: 'Máquinas Agrícolas', cats: ['Tractores', 'Cozechadoras', 'Aditamentos', 'Equipment', 'Engineering Services', 'Traillers'] },
  { key: 'custom_ecosistema_cpg', label: 'CPG', cats: ['Alimentos', 'Bebidas', 'Plastic packaging', 'Engineering Services', 'Carton packaging', 'Metal Packaging', 'Matrices', 'Machine & Line Builders'] },
  { key: 'custom_ecosistema_ad', label: 'Aeroespacial & Defensa', cats: ['OEM', 'Equipment Supplier', 'Engineering Services', 'Startups', 'Control', 'Research', 'startups internacional', 'External', 'Defense admin', 'Academia', 'MRO'] },
  { key: 'custom_ecosistema_pesquero', label: 'Pesquero', cats: ['Pesca', 'Cria y Procesamiento', 'Machine & Line Builders', 'Equipment', 'Engineering Services', 'Bio', 'Astillero'] },
]

const vals = ref({})
const showConfirm = ref(false)
const pending = ref(null)

async function load() {
  try {
    const fields = ECOSISTEMAS.map((e) => e.key)
    const r = await call('frappe.client.get_value', {
      doctype: 'CRM Organization',
      filters: { name: props.organizationId },
      fieldname: fields,
    })
    vals.value = r || {}
  } catch (e) {
    vals.value = {}
  }
}
load()
watch(() => props.organizationId, load)

function catsOf(key) {
  return String(vals.value[key] || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}
function remaining(key) {
  const cur = catsOf(key)
  const e = ECOSISTEMAS.find((x) => x.key === key)
  return (e ? e.cats : []).filter((c) => !cur.includes(c))
}
function addOptions(e) {
  return remaining(e.key).map((opt) => ({
    label: opt,
    onClick: () => addCat(e.key, opt),
  }))
}
async function save(key, list) {
  const val = list.join(', ')
  const prev = vals.value[key]
  vals.value = { ...vals.value, [key]: val }
  try {
    await call('frappe.client.set_value', {
      doctype: 'CRM Organization',
      name: props.organizationId,
      fieldname: key,
      value: val,
    })
    toast.success(__('Ecosistema actualizado'))
  } catch (e) {
    vals.value = { ...vals.value, [key]: prev }
    toast.error(__('No se pudo actualizar'))
  }
}
async function addCat(key, cat) {
  if (!cat) return
  const cur = catsOf(key)
  if (cur.includes(cat)) return
  cur.push(cat)
  await save(key, cur)
}
function askRemove(e, cat) {
  pending.value = { key: e.key, cat, label: e.label }
  showConfirm.value = true
}
async function confirmRemove() {
  if (!pending.value) return
  const { key, cat } = pending.value
  showConfirm.value = false
  await save(key, catsOf(key).filter((c) => c !== cat))
  pending.value = null
}
</script>
