<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs
        :items="[{ label: __('Partners'), route: { name: 'Partners' } }]"
      />
    </template>
    <template #right-header>
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="createPartner"
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
      :placeholder="__('Buscar partner...')"
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
        getRowRoute: (row) => ({
          name: 'PartnerDetail',
          params: { partnerId: row.name },
        }),
      }"
    />
  </div>
  <div
    v-else
    class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
  >
    <LucideHandshake class="h-10 w-10" />
    <div>{{ __('No hay partners') }}</div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideHandshake from '~icons/lucide/handshake'
import { useDoctypeModal } from '@/composables/doctypeModal'
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
const softwareCounts = ref({})
const orgCounts = ref({})

const partnerList = createListResource({
  type: 'list',
  doctype: 'CRM Partner',
  cache: ['partner-main-list'],
  fields: ['name', 'partner_name', 'country', 'website'],
  orderBy: 'partner_name asc',
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
    const sw = await call('frappe.client.get_list', {
      doctype: 'CRM Partner Software',
      filters: { parenttype: 'CRM Partner' },
      fields: ['parent'],
      limit_page_length: 0,
    })
    softwareCounts.value = build(sw)
  } catch (e) {
    softwareCounts.value = {}
  }
  try {
    const og = await call('frappe.client.get_list', {
      doctype: 'CRM Partner Organization',
      filters: { parenttype: 'CRM Partner' },
      fields: ['parent'],
      limit_page_length: 0,
    })
    orgCounts.value = build(og)
  } catch (e) {
    orgCounts.value = {}
  }
}

const columns = [
  { label: __('Nombre'), key: 'partner_name', width: '18rem' },
  { label: __('Pais'), key: 'country', width: '10rem' },
  { label: __('Software'), key: 'software', width: '9rem' },
  { label: __('Organizaciones'), key: 'organizations', width: '11rem' },
]

const rows = computed(() => {
  let data = partnerList.data || []
  if (search.value) {
    const q = search.value.toLowerCase()
    data = data.filter(
      (s) =>
        (s.partner_name || '').toLowerCase().includes(q) ||
        (s.country || '').toLowerCase().includes(q),
    )
  }
  return data.map((s) => ({
    name: s.name,
    partner_name: s.partner_name || s.name,
    country: s.country || '',
    software: softwareCounts.value[s.name] || 0,
    organizations: orgCounts.value[s.name] || 0,
  }))
})

function reloadAll() {
  partnerList.reload()
}

function createPartner() {
  showModal({
    doctype: 'CRM Partner',
    callbacks: { afterInsert: reloadAll },
  })
}

usePageMeta(() => ({ title: __('Partners') }))
</script>
