<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <MapIcon class="h-5 w-5" />
        {{ __('Roadmaps') }}
      </div>
    </template>
    <template #right-header>
      <Button variant="solid" :label="__('Nuevo roadmap')" @click="openNew">
        <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
      </Button>
      <Button variant="ghost" icon="refresh-cw" :tooltip="__('Actualizar')" :loading="loading" @click="load" />
    </template>
  </LayoutHeader>

  <div class="flex h-full min-h-0">
    <!-- Lista -->
    <div class="flex w-72 shrink-0 flex-col border-r">
      <div class="border-b px-3 py-2 text-xs font-medium uppercase tracking-wide text-ink-gray-5">
        {{ __('Organizaciones con roadmap') }} ({{ orgs.length }})
      </div>
      <div class="min-h-0 flex-1 overflow-y-auto p-2">
        <button
          v-for="o in orgs"
          :key="o.name"
          type="button"
          class="mb-1 flex w-full flex-col items-start gap-0.5 rounded-lg px-3 py-2 text-left transition-colors"
          :class="selected === o.name ? 'bg-surface-gray-3' : 'hover:bg-surface-gray-2'"
          @click="selected = o.name"
        >
          <span class="w-full truncate text-sm font-medium text-ink-gray-8">{{ o.label }}</span>
          <span class="text-xs text-ink-gray-5">{{ o.streams }} {{ __('streams') }} · {{ o.items }} {{ __('ítems') }}</span>
        </button>
        <div v-if="!loading && !orgs.length" class="px-3 py-6 text-center text-sm text-ink-gray-4">
          {{ __('No hay roadmaps todavía.') }}
        </div>
      </div>
    </div>

    <!-- Visor -->
    <div class="min-w-0 flex-1 overflow-hidden">
      <div v-if="selected" class="h-full overflow-hidden p-4 sm:p-5">
        <RoadmapOrg :key="selected" :organization-id="selected" />
      </div>
      <div v-else class="flex h-full items-center justify-center text-sm text-ink-gray-4">
        {{ __('Elegí un roadmap de la lista para verlo.') }}
      </div>
    </div>
  </div>

  <!-- Nuevo roadmap: seleccionar empresa -->
  <Dialog v-model="showNew" :options="{ title: __('Nuevo roadmap'), size: 'sm' }">
    <template #body-content>
      <div class="flex flex-col gap-2">
        <label class="text-sm text-ink-gray-6">{{ __('Empresa') }}</label>
        <Link doctype="CRM Organization" :value="newOrg" @change="(v) => (newOrg = v)" />
        <p class="text-xs text-ink-gray-4">{{ __('Se abrirá el roadmap de la empresa para agregar streams e ítems.') }}</p>
      </div>
    </template>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button :label="__('Cancelar')" @click="showNew = false" />
        <Button variant="solid" :label="__('Abrir')" :disabled="!newOrg" @click="crearRoadmap" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, FeatherIcon, Dialog, call, toast } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'
import RoadmapOrg from '@/components/RoadmapOrg.vue'
import Link from '@/components/Controls/Link.vue'
import MapIcon from '~icons/lucide/map'

const orgs = ref([])
const selected = ref(null)
const loading = ref(false)
const showNew = ref(false)
const newOrg = ref('')

function openNew() {
  newOrg.value = ''
  showNew.value = true
}
function crearRoadmap() {
  if (!newOrg.value) return
  const name = newOrg.value
  if (!orgs.value.some((o) => o.name === name)) {
    orgs.value.unshift({ name, label: name, streams: 0, items: 0 })
  }
  selected.value = name
  showNew.value = false
}

async function load() {
  loading.value = true
  try {
    const data = await call('frappe.client.get_list', {
      doctype: 'CRM Organization',
      fields: ['name', 'organization_name', 'custom_roadmap_data'],
      filters: { custom_roadmap_data: ['is', 'set'] },
      limit_page_length: 0,
      order_by: 'modified desc',
    })
    orgs.value = (data || []).map((d) => {
      let streams = 0, items = 0
      try {
        const j = JSON.parse(d.custom_roadmap_data || '{}')
        const st = Array.isArray(j.streams) ? j.streams : []
        streams = st.length
        items = st.reduce((a, s) => a + ((s.items || []).length), 0)
      } catch (e) { /* ignore */ }
      return { name: d.name, label: d.organization_name || d.name, streams, items }
    }).filter((o) => o.streams > 0)
    if (orgs.value.length && !orgs.value.some((o) => o.name === selected.value)) {
      selected.value = orgs.value[0].name
    }
  } catch (e) {
    toast.error(__('No se pudieron cargar los roadmaps'))
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>
