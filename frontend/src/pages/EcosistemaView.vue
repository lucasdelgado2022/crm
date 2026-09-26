<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <LucideNetwork class="h-5 w-5" />
        {{ __('Ecosistema Productivo') }}
      </div>
    </template>
  </LayoutHeader>

  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Selectores -->
    <div class="mb-4 flex flex-wrap items-center gap-2">
      <select
        v-model="selectedEco"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm font-medium text-ink-gray-8 focus:outline-none"
      >
        <option v-for="e in ECOSISTEMAS" :key="e.key" :value="e.key">
          {{ e.label }}
        </option>
      </select>
      <select
        v-model="paisFilter"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
      >
        <option value="">{{ __('Todos los países') }}</option>
        <option v-for="p in paises" :key="p" :value="p">{{ p }}</option>
      </select>
      <FormControl
        class="w-56"
        type="text"
        :placeholder="__('Buscar empresa...')"
        v-model="search"
      >
        <template #prefix><FeatherIcon name="search" class="h-4 w-4 text-ink-gray-5" /></template>
      </FormControl>
      <span class="text-sm text-ink-gray-5">
        {{ __('{0} empresas', [totalOrgs]) }}
      </span>
    </div>

    <div v-if="loading" class="flex flex-1 items-center justify-center text-ink-gray-4">
      {{ __('Cargando ecosistema...') }}
    </div>

    <!-- Filas por categoría (tipo de participación) -->
    <div v-else class="flex flex-col gap-3">
      <div
        v-for="cat in categories"
        :key="cat"
        class="flex flex-col overflow-hidden rounded-lg border sm:flex-row"
      >
        <!-- Etiqueta de categoría -->
        <div
          class="flex shrink-0 items-center justify-between gap-2 border-b border-blue-200 bg-blue-100 px-3 py-3 text-sm font-bold text-blue-900 sm:w-52 sm:border-b-0 sm:border-r"
        >
          <span>{{ cat }}</span>
          <Badge variant="solid" theme="blue" size="sm">{{ orgsInCat(cat).length }}</Badge>
        </div>
        <!-- Empresas (slots) + agregar -->
        <div class="flex flex-1 flex-wrap items-center gap-2 p-3">
          <div
            v-for="o in orgsInCat(cat)"
            :key="o.name"
            class="flex items-center gap-1.5 rounded-full border bg-surface-white py-1 pl-3 pr-1.5 text-sm text-ink-gray-8 shadow-sm"
          >
            <span class="cursor-pointer hover:underline" @click="openOrg(o.name)">
              {{ o.organization_name || o.name }}
            </span>
            <button
              class="text-ink-gray-4 hover:text-ink-red-6"
              :title="__('Quitar de {0}', [cat])"
              @click="removeOrg(o, cat)"
            >
              <FeatherIcon name="x" class="h-3.5 w-3.5" />
            </button>
          </div>
          <div class="w-56" @click.stop>
            <Link
              doctype="CRM Organization"
              :value="''"
              :placeholder="__('+ Agregar empresa')"
              @change="(v) => v && addOrg(cat, v)"
            />
          </div>
        </div>
      </div>
      <div v-if="!categories.length" class="py-8 text-center text-sm text-ink-gray-4">
        {{ __('Este ecosistema no tiene categorías configuradas') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'
import LucideNetwork from '~icons/lucide/network'
import { FeatherIcon, FormControl, Badge, call, toast, usePageMeta } from 'frappe-ui'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Ecosistemas + sus categorías (tipos de participación) = opciones del Select
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
const ECO_FIELDS = ECOSISTEMAS.map((e) => e.key)

const selectedEco = ref('custom_ecosistema_nuclear')
const paisFilter = ref('')
const search = ref('')
const orgs = ref([])
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    orgs.value = await call('frappe.client.get_list', {
      doctype: 'CRM Organization',
      fields: ['name', 'organization_name', 'territory', ...ECO_FIELDS],
      limit_page_length: 0,
      order_by: 'organization_name asc',
    })
  } catch (e) {
    orgs.value = []
  }
  loading.value = false
}
load()

const currentEco = computed(() => ECOSISTEMAS.find((e) => e.key === selectedEco.value) || ECOSISTEMAS[0])
const categories = computed(() => currentEco.value.cats)

const paises = computed(() => {
  const s = new Set()
  for (const o of orgs.value) if (o[selectedEco.value] && o.territory) s.add(o.territory)
  return [...s].sort((a, b) => String(a).localeCompare(String(b)))
})

function matchesFilters(o) {
  if (paisFilter.value && (o.territory || '') !== paisFilter.value) return false
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    if (!(o.organization_name || o.name || '').toLowerCase().includes(q)) return false
  }
  return true
}
function catsOf(o) {
  return String(o[selectedEco.value] || '')
    .split(',')
    .map((c) => c.trim())
    .filter(Boolean)
}
function orgsInCat(cat) {
  return orgs.value.filter((o) => catsOf(o).includes(cat) && matchesFilters(o))
}
const totalOrgs = computed(
  () => orgs.value.filter((o) => o[selectedEco.value] && matchesFilters(o)).length,
)

async function addOrg(cat, orgName) {
  if (!orgName) return
  const field = selectedEco.value
  try {
    const res = await call('frappe.client.get_value', {
      doctype: 'CRM Organization',
      filters: { name: orgName },
      fieldname: field,
    })
    const current = String((res && res[field]) || '')
      .split(',')
      .map((c) => c.trim())
      .filter(Boolean)
    if (current.includes(cat)) {
      toast.info(__('Ya estaba en {0}', [cat]))
      return
    }
    current.push(cat)
    await call('frappe.client.set_value', {
      doctype: 'CRM Organization',
      name: orgName,
      fieldname: field,
      value: current.join(', '),
    })
    toast.success(__('Empresa agregada a {0}', [cat]))
    load()
  } catch (e) {
    toast.error((e && e.messages && e.messages[0]) || __('No se pudo agregar'))
  }
}
async function removeOrg(o, cat) {
  const field = selectedEco.value
  const prev = o[field]
  const val = catsOf(o).filter((c) => c !== cat).join(', ')
  o[field] = val // optimista
  try {
    await call('frappe.client.set_value', {
      doctype: 'CRM Organization',
      name: o.name,
      fieldname: field,
      value: val,
    })
    toast.success(__('Empresa quitada de {0}', [cat]))
    load()
  } catch (e) {
    o[field] = prev
    toast.error(__('No se pudo quitar'))
  }
}
function openOrg(name) {
  router.push({ name: 'Organization', params: { organizationId: name } })
}

usePageMeta(() => ({ title: __('Ecosistema Productivo') }))
</script>
