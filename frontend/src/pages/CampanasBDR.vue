<template>
  <LayoutHeader>
    <template #left-header>
      <div class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8">
        <LucideMegaphone class="h-5 w-5" />
        {{ __('Campañas BDR') }}
      </div>
    </template>
  </LayoutHeader>
  <div class="flex h-full flex-col overflow-y-auto p-4 sm:p-6">
    <!-- Barra de filtros -->
    <div class="mb-4 flex flex-col gap-3">
      <div class="flex items-center justify-between gap-2">
        <div class="text-base text-ink-gray-6">
          {{ __('{0} organizaciones', [filteredRows.length]) }}
          <span v-if="selectedCampaign" class="text-ink-gray-5">
            · {{ selectedCampaign }}
          </span>
        </div>
        <FormControl
          class="w-64"
          type="text"
          :placeholder="__('Buscar organización...')"
          v-model="search"
        >
          <template #prefix>
            <FeatherIcon name="search" class="h-4 w-4 text-ink-gray-5" />
          </template>
        </FormControl>
      </div>
      <!-- Chips de campañas -->
      <div class="flex flex-wrap items-center gap-2">
        <button
          class="rounded-full border px-3 py-1 text-sm transition-colors"
          :class="
            !selectedCampaign
              ? 'border-blue-500 bg-blue-50 text-blue-700'
              : 'border-outline-gray-2 text-ink-gray-7 hover:bg-surface-gray-1'
          "
          @click="selectedCampaign = ''"
        >
          {{ __('Todas') }}
          <span class="ml-1 text-xs text-ink-gray-5">{{ orgs.length }}</span>
        </button>
        <button
          v-for="c in allCampaigns"
          :key="c.name"
          class="rounded-full border px-3 py-1 text-sm transition-colors"
          :class="
            selectedCampaign === c.name
              ? 'border-blue-500 bg-blue-50 text-blue-700'
              : 'border-outline-gray-2 text-ink-gray-7 hover:bg-surface-gray-1'
          "
          @click="selectedCampaign = selectedCampaign === c.name ? '' : c.name"
        >
          {{ c.name }}
          <span class="ml-1 text-xs text-ink-gray-5">{{ c.count }}</span>
        </button>
      </div>
    </div>

    <!-- Tabla -->
    <div v-if="filteredRows.length" class="overflow-x-auto rounded-lg border">
      <table class="w-full text-sm">
        <thead class="border-b bg-surface-gray-1 text-xs text-ink-gray-5">
          <tr>
            <th class="px-4 py-2 text-left font-medium">{{ __('Organización') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Campañas BDR') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('Industria') }}</th>
            <th class="px-3 py-2 text-left font-medium">{{ __('País') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="o in filteredRows"
            :key="o.name"
            class="cursor-pointer border-b last:border-0 hover:bg-surface-gray-1"
            @click="openOrg(o.name)"
          >
            <td class="px-4 py-2 font-medium text-ink-gray-8">{{ o.name }}</td>
            <td class="px-3 py-2">
              <div class="flex flex-wrap gap-1">
                <Badge
                  v-for="c in o.campaigns"
                  :key="c"
                  variant="subtle"
                  :theme="c === selectedCampaign ? 'blue' : 'gray'"
                  size="sm"
                >
                  {{ c }}
                </Badge>
              </div>
            </td>
            <td class="px-3 py-2 text-ink-gray-7">{{ o.industry || '—' }}</td>
            <td class="px-3 py-2 text-ink-gray-7">{{ o.territory || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div
      v-else
      class="flex flex-1 flex-col items-center justify-center gap-2 text-ink-gray-4"
    >
      <LucideMegaphone class="h-10 w-10" />
      <div>{{ __('Sin organizaciones en campañas BDR') }}</div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideMegaphone from '~icons/lucide/megaphone'
import { FeatherIcon, FormControl, Badge, call, usePageMeta } from 'frappe-ui'
import { ref, computed } from 'vue'

const search = ref('')
const selectedCampaign = ref('')
const orgs = ref([])

function parseList(v) {
  try {
    return JSON.parse(v || '[]') || []
  } catch (e) {
    return []
  }
}

async function load() {
  const rows = await call('frappe.client.get_list', {
    doctype: 'CRM Organization',
    filters: { custom_campanas_bdr_list: ['is', 'set'] },
    fields: ['name', 'custom_campanas_bdr_list', 'industry', 'territory'],
    limit_page_length: 0,
  })
  orgs.value = rows.map((o) => ({
    name: o.name,
    industry: o.industry,
    territory: o.territory,
    campaigns: parseList(o.custom_campanas_bdr_list),
  }))
}
load()

// Campañas únicas con conteo (para los chips)
const allCampaigns = computed(() => {
  const m = {}
  for (const o of orgs.value)
    for (const c of o.campaigns) m[c] = (m[c] || 0) + 1
  return Object.entries(m)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
})

const filteredRows = computed(() => {
  let arr = orgs.value
  if (selectedCampaign.value)
    arr = arr.filter((o) => o.campaigns.includes(selectedCampaign.value))
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    arr = arr.filter((o) => o.name.toLowerCase().includes(q))
  }
  return [...arr].sort((a, b) => a.name.localeCompare(b.name))
})

function openOrg(name) {
  window.location.href = '/crm/organizations/' + encodeURIComponent(name)
}

usePageMeta(() => ({ title: __('Campañas BDR') }))
</script>
