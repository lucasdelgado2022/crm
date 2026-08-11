<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs
        :items="[
          {
            label: __('Procesos / Tecnologias'),
            route: { name: 'ProcesosTecnologias' },
          },
        ]"
      />
    </template>
    <template #right-header>
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="createItem"
      />
    </template>
  </LayoutHeader>

  <div class="flex items-center justify-between gap-2 px-3 py-3 sm:px-5">
    <div class="text-base text-ink-gray-6">
      {{ __('{0} registros', [rows.length]) }}
    </div>
    <FormControl
      class="w-64"
      type="text"
      :placeholder="__('Buscar...')"
      v-model="search"
    >
      <template #prefix>
        <FeatherIcon name="search" class="h-4 w-4 text-ink-gray-5" />
      </template>
    </FormControl>
  </div>

  <div v-if="rows.length" class="flex flex-1 flex-col overflow-hidden">
    <ListView
      class="px-3 sm:px-5"
      :columns="columns"
      :rows="rows"
      row-key="name"
      :options="{ selectable: false, showTooltip: false }"
    >
      <template #cell="{ column, row, item }">
        <Button
          v-if="column.key === '_edit'"
          variant="ghost"
          class="!h-6 !w-6"
          :tooltip="__('Editar')"
          @click.stop.prevent="editItem(row.name)"
        >
          <FeatherIcon name="edit-2" class="h-4 w-4 text-ink-gray-6" />
        </Button>
        <div v-else class="truncate text-base">{{ item }}</div>
      </template>
    </ListView>
  </div>
  <div
    v-else
    class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
  >
    <LucideWorkflow class="h-10 w-10" />
    <div>{{ __('Sin registros') }}</div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideWorkflow from '~icons/lucide/workflow'
import { useDoctypeModal } from '@/composables/doctypeModal'
import {
  Breadcrumbs,
  FormControl,
  FeatherIcon,
  ListView,
  createListResource,
  usePageMeta,
} from 'frappe-ui'
import { ref, computed } from 'vue'

const { showModal } = useDoctypeModal()

const search = ref('')

const list = createListResource({
  type: 'list',
  doctype: 'CRM Proceso Tecnologia',
  cache: ['proceso-tec-list'],
  fields: ['name', 'title', 'tipo', 'description'],
  orderBy: 'title asc',
  pageLength: 500,
  auto: true,
})

const columns = [
  { label: __('Nombre'), key: 'title', width: '18rem' },
  { label: __('Tipo'), key: 'tipo', width: '10rem' },
  { label: __('Descripcion'), key: 'description', width: '28rem' },
  { label: '', key: '_edit', width: '3rem' },
]

const rows = computed(() => {
  let data = list.data || []
  if (search.value) {
    const q = search.value.toLowerCase()
    data = data.filter((s) => (s.title || '').toLowerCase().includes(q))
  }
  return data.map((s) => ({
    name: s.name,
    title: s.title || s.name,
    tipo: s.tipo || '',
    description: s.description || '',
  }))
})

function reloadAll() {
  list.reload()
}

function createItem() {
  showModal({
    doctype: 'CRM Proceso Tecnologia',
    callbacks: { afterInsert: reloadAll },
  })
}

function editItem(name) {
  showModal({
    doctype: 'CRM Proceso Tecnologia',
    name,
    callbacks: { afterUpdate: reloadAll },
  })
}

usePageMeta(() => ({ title: __('Procesos / Tecnologias') }))
</script>
