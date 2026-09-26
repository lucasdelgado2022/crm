<template>
  <div class="flex flex-col gap-4">
    <!-- Widget: Organigrama (arriba) -->
    <div class="flex flex-col rounded-lg border">
      <div class="flex items-center gap-2 border-b px-4 py-3 text-base font-semibold text-ink-gray-8">
        <FeatherIcon name="git-merge" class="h-4 w-4" />
        {{ __('Organigrama') }}
      </div>
      <div v-if="loading" class="flex h-64 items-center justify-center text-ink-gray-4">
        {{ __('Cargando...') }}
      </div>
      <div v-else-if="!contactos.length" class="flex h-64 flex-col items-center justify-center gap-2 text-ink-gray-4">
        <FeatherIcon name="git-merge" class="h-7 w-7" />
        {{ __('Sin contactos para armar el organigrama') }}
      </div>
      <div v-else class="og-tree overflow-auto p-4">
        <ul class="og-root-ul">
          <OrgNode v-for="n in rootNodes" :key="n.id" :node="n" />
        </ul>
      </div>
    </div>

    <!-- Widget: Contactos (abajo) -->
    <div class="flex flex-col rounded-lg border">
      <div class="flex flex-wrap items-center gap-2 border-b px-4 py-3 text-base font-semibold text-ink-gray-8">
        <FeatherIcon name="users" class="h-4 w-4" />
        {{ __('Contactos') }}
        <Badge variant="subtle" theme="gray" size="sm">{{ contactosFiltrados.length }}</Badge>
        <div class="ml-auto">
          <FormControl
            type="text"
            size="sm"
            :placeholder="__('Buscar contacto...')"
            v-model="contactSearch"
            class="w-52"
          />
        </div>
      </div>
      <div class="grid max-h-[28rem] grid-cols-1 gap-x-6 overflow-y-auto sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="c in contactosFiltrados" :key="c.name" class="border-b px-3 py-2">
          <div class="text-sm font-medium text-ink-gray-8">{{ c.fullName }}</div>
          <div v-if="c.custom_puesto" class="text-xs text-ink-gray-5">{{ c.custom_puesto }}</div>
          <div class="mt-1 flex items-center gap-1.5" @click.stop>
            <span class="text-xs text-ink-gray-5">{{ __('Reporta a') }}:</span>
            <div class="min-w-0 flex-1">
              <Link
                doctype="Contact"
                :value="c.custom_reporta_a"
                :filters="{ company_name: organizationId, name: ['!=', c.name] }"
                :placeholder="__('—')"
                @change="(v) => setReportaA(c.name, v)"
              />
            </div>
          </div>
        </div>
        <div v-if="!contactosFiltrados.length" class="col-span-full px-3 py-6 text-center text-sm text-ink-gray-4">
          {{ contactSearch ? __('Sin resultados') : __('Sin contactos') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import OrgNode from './OrgNode.vue'
import Link from '@/components/Controls/Link.vue'
import { FeatherIcon, Badge, FormControl, call, toast } from 'frappe-ui'
import { ref, computed } from 'vue'

const props = defineProps({
  organizationId: { type: String, required: true },
  organizationName: { type: String, default: '' },
})

const contactos = ref([])
const loading = ref(true)
const contactSearch = ref('')

async function load() {
  loading.value = true
  try {
    const rows = await call('frappe.client.get_list', {
      doctype: 'Contact',
      filters: { company_name: props.organizationId },
      fields: ['name', 'first_name', 'last_name', 'custom_puesto', 'custom_reporta_a'],
      limit_page_length: 0,
      order_by: 'first_name asc',
    })
    contactos.value = rows.map((c) => ({
      ...c,
      fullName: [c.first_name, c.last_name].filter(Boolean).join(' ') || c.name,
    }))
  } catch (e) {
    contactos.value = []
  }
  loading.value = false
}
load()

const contactosFiltrados = computed(() => {
  const q = contactSearch.value.trim().toLowerCase()
  if (!q) return contactos.value
  return contactos.value.filter(
    (c) =>
      (c.fullName || '').toLowerCase().includes(q) ||
      (c.custom_puesto || '').toLowerCase().includes(q),
  )
})

async function setReportaA(contactName, managerName) {
  const c = contactos.value.find((x) => x.name === contactName)
  if (c) c.custom_reporta_a = managerName || null
  try {
    await call('frappe.client.set_value', {
      doctype: 'Contact',
      name: contactName,
      fieldname: 'custom_reporta_a',
      value: managerName || null,
    })
    toast.success(__('Actualizado'))
  } catch (e) {
    toast.error(__('No se pudo actualizar'))
  }
}

// Árbol: bosque de raíces. Los que no reportan a nadie quedan sueltos (sin raíz sintética).
const rootNodes = computed(() => {
  const byId = {}
  for (const c of contactos.value)
    byId[c.name] = { id: c.name, name: c.fullName, puesto: c.custom_puesto || '', children: [] }
  const roots = []
  for (const c of contactos.value) {
    const node = byId[c.name]
    const mgr = c.custom_reporta_a
    if (mgr && byId[mgr] && mgr !== c.name) byId[mgr].children.push(node)
    else roots.push(node)
  }
  return roots
})
</script>

<style scoped>
.og-root-ul {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1.5rem 1rem;
  list-style: none;
  margin: 0;
  padding: 0;
  min-width: max-content;
}
/* Raíces de nivel superior: sin conectores hacia un padre inexistente */
.og-root-ul > :deep(li) {
  padding-top: 0;
}
.og-root-ul > :deep(li)::before,
.og-root-ul > :deep(li)::after {
  display: none !important;
  border: 0 !important;
}
</style>
