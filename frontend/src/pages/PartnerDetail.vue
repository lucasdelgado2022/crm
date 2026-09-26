<template>
  <LayoutHeader v-if="loaded">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>

  <div v-if="loaded" class="flex h-full">
    <div class="flex h-full w-[320px] flex-col overflow-hidden border-r">
      <div class="border-b">
        <div class="flex items-center gap-4 p-5">
          <Avatar size="3xl" class="h-15.5 w-15.5" :label="partnerName" />
          <div class="flex flex-col gap-1 truncate">
            <div class="truncate text-2xl font-semibold text-ink-gray-9">
              {{ partnerName }}
            </div>
            <div class="text-base text-ink-gray-5">{{ __('Partner') }}</div>
          </div>
        </div>
      </div>
      <div class="flex flex-col gap-3 p-5 text-base">
        <div class="flex items-center gap-2">
          <span class="w-20 text-ink-gray-5">{{ __('Pais') }}</span>
          <span class="text-ink-gray-8">{{ doc.country || '—' }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-20 text-ink-gray-5">{{ __('Web') }}</span>
          <a
            v-if="doc.website"
            :href="normalizedWeb"
            target="_blank"
            class="truncate text-ink-blue-link"
            >{{ doc.website }}</a
          >
          <span v-else class="text-ink-gray-8">—</span>
        </div>
        <Button
          class="mt-2"
          variant="subtle"
          :label="__('Editar datos')"
          @click="editPartner"
        />
      </div>
    </div>

    <Tabs
      v-model="tabIndex"
      as="div"
      :tabs="tabs"
      class="flex flex-1 flex-col overflow-hidden [&_[role='tablist']]:min-h-[45px] [&_[role='tablist']]:gap-7.5 [&_[role='tablist']]:px-5 [&_[role='tabpanel']:not([hidden])]:flex [&_[role='tabpanel']:not([hidden])]:grow"
    >
      <template #tab-item="{ tab, selected }">
        <button
          class="group flex items-center gap-2 border-b border-transparent py-2.5 text-base text-ink-gray-5 duration-300 ease-in-out hover:text-ink-gray-9"
          :class="{ 'text-ink-gray-9': selected }"
        >
          <component :is="tab.icon" v-if="tab.icon" class="h-5" />
          {{ __(tab.label) }}
          <Badge
            class="group-hover:bg-surface-gray-10"
            :class="[selected ? 'bg-surface-gray-10' : 'bg-gray-600']"
            variant="solid"
            theme="gray"
            size="sm"
          >
            {{ tab.count }}
          </Badge>
        </button>
      </template>
      <template #tab-panel="{ tab }">
        <div class="flex flex-1 flex-col overflow-hidden">
          <div class="flex justify-end gap-2 px-5 pt-3">
            <Link
              value=""
              :doctype="tab.key === 'software' ? 'Software' : 'CRM Organization'"
              @change="(name) => addExisting(tab.key, name)"
            >
              <template #target="{ togglePopover }">
                <Button variant="outline" @click="togglePopover()">
                  <template #prefix
                    ><FeatherIcon name="link" class="h-4"
                  /></template>
                  {{ __('Add Existing') }}
                </Button>
              </template>
            </Link>
          </div>

          <ListView
            v-if="tab.key === 'software' && softwareRows.length"
            class="mt-4 px-5"
            :columns="softwareColumns"
            :rows="softwareRows"
            row-key="name"
            :options="{
              selectable: false,
              showTooltip: false,
              getRowRoute: (row) => ({
                name: 'SoftwareDetail',
                params: { softwareId: row.name },
              }),
            }"
          >
            <template #cell="{ column, row, item }">
              <Button
                v-if="column.key === '_unlink'"
                variant="ghost"
                class="!h-6 !w-6"
                :tooltip="__('Desvincular')"
                @click.stop.prevent="unlink('software', row.name)"
              >
                <FeatherIcon name="x" class="h-4 w-4 text-ink-gray-6" />
              </Button>
              <div
                v-else-if="column.key === 'software'"
                class="flex items-center gap-2 truncate"
              >
                <Avatar size="sm" :label="row.name" />
                <span class="truncate">{{ row.name }}</span>
              </div>
              <div v-else class="truncate text-base">{{ item }}</div>
            </template>
          </ListView>

          <ListView
            v-else-if="tab.key === 'organizations' && orgRows.length"
            class="mt-4 px-5"
            :columns="orgColumns"
            :rows="orgRows"
            row-key="name"
            :options="{
              selectable: false,
              showTooltip: false,
              getRowRoute: (row) => ({
                name: 'Organization',
                params: { organizationId: row.name },
              }),
            }"
          >
            <template #cell="{ column, row, item }">
              <Button
                v-if="column.key === '_unlink'"
                variant="ghost"
                class="!h-6 !w-6"
                :tooltip="__('Desvincular')"
                @click.stop.prevent="unlink('organizations', row.name)"
              >
                <FeatherIcon name="x" class="h-4 w-4 text-ink-gray-6" />
              </Button>
              <div
                v-else-if="column.key === 'organization'"
                class="flex items-center gap-2 truncate"
              >
                <Avatar size="sm" :label="row.name" />
                <span class="truncate">{{ row.name }}</span>
              </div>
              <div v-else class="truncate text-base">{{ item }}</div>
            </template>
          </ListView>

          <div
            v-else
            class="flex flex-1 flex-col items-center justify-center text-ink-gray-4"
          >
            {{ __('Sin registros') }}
          </div>
        </div>
      </template>
    </Tabs>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import Link from '@/components/Controls/Link.vue'
import SoftwareIcon from '@/components/Icons/SoftwareIcon.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import { useDoctypeModal } from '@/composables/doctypeModal'
import {
  Breadcrumbs,
  Avatar,
  Badge,
  Tabs,
  ListView,
  FeatherIcon,
  call,
  toast,
  usePageMeta,
} from 'frappe-ui'
import { ref, computed, watch } from 'vue'

const props = defineProps({
  partnerId: { type: String, required: true },
})
const { showModal } = useDoctypeModal()

const doc = ref({})
const loaded = ref(false)
const softwareChild = ref([])
const orgChild = ref([])

const partnerName = computed(() => doc.value.partner_name || props.partnerId)

async function load() {
  const d = await call('frappe.client.get', {
    doctype: 'CRM Partner',
    name: props.partnerId,
  })
  doc.value = d
  softwareChild.value = d.software || []
  orgChild.value = d.organizations || []
  loaded.value = true
}
load()
watch(() => props.partnerId, load)

const breadcrumbs = computed(() => [
  { label: __('Partners'), route: { name: 'Partners' } },
  {
    label: partnerName.value,
    route: { name: 'PartnerDetail', params: { partnerId: props.partnerId } },
  },
])

const normalizedWeb = computed(() => {
  let w = doc.value.website || ''
  if (w && !/^https?:\/\//i.test(w)) w = 'https://' + w
  return w
})

const tabIndex = ref(0)
const tabs = [
  {
    label: 'Software',
    key: 'software',
    icon: SoftwareIcon,
    count: computed(() => softwareChild.value.length),
  },
  {
    label: 'Organizations',
    key: 'organizations',
    icon: OrganizationsIcon,
    count: computed(() => orgChild.value.length),
  },
]

const softwareRows = computed(() =>
  softwareChild.value.map((r) => ({ name: r.software, software: r.software })),
)
const softwareColumns = [
  { label: __('Software'), key: 'software', width: '24rem' },
  { label: '', key: '_unlink', width: '3rem' },
]

const orgRows = computed(() =>
  orgChild.value.map((r) => ({
    name: r.organization,
    organization: r.organization,
  })),
)
const orgColumns = [
  { label: __('Organization'), key: 'organization', width: '24rem' },
  { label: '', key: '_unlink', width: '3rem' },
]

async function addExisting(key, name) {
  if (!name) return
  const childType =
    key === 'software' ? 'CRM Partner Software' : 'CRM Partner Organization'
  const field = key === 'software' ? 'software' : 'organization'
  const current = (
    key === 'software' ? softwareChild.value : orgChild.value
  ).map((r) => r[field])
  if (current.includes(name)) {
    toast.error(__('Ya esta vinculado'))
    return
  }
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: childType,
        parenttype: 'CRM Partner',
        parent: props.partnerId,
        parentfield: key,
        [field]: name,
      },
    })
    toast.success(__('Vinculado'))
    load()
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error al vincular'))
  }
}

async function unlink(key, name) {
  const field = key === 'software' ? 'software' : 'organization'
  try {
    const d = await call('frappe.client.get', {
      doctype: 'CRM Partner',
      name: props.partnerId,
    })
    d[key] = (d[key] || []).filter((r) => r[field] !== name)
    await call('frappe.client.save', { doc: d })
    toast.success(__('Desvinculado'))
    load()
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error al desvincular'))
  }
}

function editPartner() {
  showModal({
    doctype: 'CRM Partner',
    name: props.partnerId,
    callbacks: { afterUpdate: load },
  })
}

usePageMeta(() => ({ title: partnerName.value || __('Partner') }))
</script>
