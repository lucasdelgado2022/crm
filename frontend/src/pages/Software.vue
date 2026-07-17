<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs
        :items="[{ label: __('Software'), route: { name: 'Software' } }]"
      />
    </template>
    <template #right-header>
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="createSoftware"
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
      :placeholder="__('Buscar software...')"
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
      :options="{
        selectable: false,
        showTooltip: false,
        onRowClick: (row) => editSoftware(row.name),
      }"
    />
  </div>
  <div
    v-else
    class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
  >
    <SoftwareIcon class="h-10 w-10" />
    <div>{{ __('No hay software') }}</div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import SoftwareIcon from '@/components/Icons/SoftwareIcon.vue'
import { useDoctypeModal } from '@/composables/doctypeModal'
import { timestampCell } from '@/composables/useTimelinePreferences'
import {
  Breadcrumbs,
  FormControl,
  FeatherIcon,
  ListView,
  createListResource,
  call,
  usePageMeta,
} from 'frappe-ui'
import { ref, computed } from 'vue'

const { showModal } = useDoctypeModal()

const search = ref('')
const orgCounts = ref({})
const contactCounts = ref({})

const softwareList = createListResource({
  type: 'list',
  doctype: 'Software',
  cache: ['software-main-list'],
  fields: ['name', 'software_name', 'modified'],
  orderBy: 'modified desc',
  pageLength: 500,
  auto: true,
  onSuccess: () => loadCounts(),
})

async function loadCounts() {
  const build = (data) => {
    const map = {}
    for (const r of data || []) map[r.parent] = (map[r.parent] || 0) + 1
    return map
  }
  try {
    const orgs = await call('frappe.client.get_list', {
      doctype: 'Software Organization',
      filters: { parenttype: 'Software' },
      fields: ['parent'],
      limit_page_length: 0,
    })
    orgCounts.value = build(orgs)
  } catch (e) {
    orgCounts.value = {}
  }
  try {
    const contacts = await call('frappe.client.get_list', {
      doctype: 'Software Contact',
      filters: { parenttype: 'Software' },
      fields: ['parent'],
      limit_page_length: 0,
    })
    contactCounts.value = build(contacts)
  } catch (e) {
    contactCounts.value = {}
  }
}

const columns = [
  { label: __('Nombre'), key: 'software_name', width: '20rem' },
  { label: __('Organizaciones'), key: 'organizations', width: '10rem' },
  { label: __('Contactos'), key: 'contacts', width: '10rem' },
  { label: __('Última modificación'), key: 'modified', width: '12rem' },
]

const rows = computed(() => {
  let data = softwareList.data || []
  if (search.value) {
    const q = search.value.toLowerCase()
    data = data.filter((s) =>
      (s.software_name || '').toLowerCase().includes(q),
    )
  }
  return data.map((s) => ({
    name: s.name,
    software_name: s.software_name,
    organizations: orgCounts.value[s.name] || 0,
    contacts: contactCounts.value[s.name] || 0,
    modified: timestampCell(s.modified).timeAgo,
  }))
})

function reloadAll() {
  softwareList.reload()
}

function createSoftware() {
  showModal({
    doctype: 'Software',
    callbacks: { afterInsert: reloadAll },
  })
}

function editSoftware(name) {
  showModal({
    doctype: 'Software',
    name,
    callbacks: { afterInsert: reloadAll, afterSave: reloadAll },
  })
}

usePageMeta(() => ({ title: __('Software') }))
</script>
