<template>
  <LayoutHeader v-if="softwareName">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>

  <div v-if="softwareName" ref="parentRef" class="flex h-full">
    <Resizer :parent="$refs.parentRef" class="flex h-full flex-col overflow-hidden border-r">
      <div class="border-b">
        <div class="flex items-center gap-4 p-5">
          <Avatar size="3xl" class="h-15.5 w-15.5" :label="softwareName" />
          <div class="flex flex-col gap-1 truncate">
            <div class="truncate text-2xl font-semibold text-ink-gray-9">
              {{ softwareName }}
            </div>
            <div class="text-base text-ink-gray-5">{{ __('Software') }}</div>
          </div>
        </div>
      </div>
      <div v-if="sections.data" class="flex flex-1 flex-col justify-between overflow-hidden">
        <SidePanelLayout
          :sections="sections.data"
          doctype="Software"
          :docname="props.softwareId"
          @reload="sections.reload"
        />
      </div>
    </Resizer>

    <Tabs
      v-model="tabIndex"
      as="div"
      :tabs="tabs"
      class="flex flex-1 overflow-hidden flex-col [&_[role='tablist']]:gap-7.5 [&_[role='tablist']]:px-5 [&_[role='tablist']::-webkit-scrollbar]:h-0 [&_[role='tablist']]:min-h-[45px] [&_[role='tabpanel']:not([hidden])]:flex [&_[role='tabpanel']:not([hidden])]:grow"
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
              :doctype="tab.label === 'Organizations' ? 'CRM Organization' : 'Contact'"
              @change="(name) => addExisting(tab.label, name)"
            >
              <template #target="{ togglePopover }">
                <Button variant="outline" @click="togglePopover()">
                  <template #prefix><FeatherIcon name="link" class="h-4" /></template>
                  {{ __('Add Existing') }}
                </Button>
              </template>
            </Link>
            <Button variant="solid" @click="createNew(tab.label)">
              <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
              {{ __('Create') }}
            </Button>
          </div>

          <ListView
            v-if="tab.label === 'Organizations' && orgRows.length"
            class="mt-4 px-5"
            :columns="orgColumns"
            :rows="orgRows"
            row-key="name"
            :options="{
              selectable: false,
              showTooltip: false,
              getRowRoute: (row) => ({ name: 'Organization', params: { organizationId: row.name } }),
            }"
          >
            <template #cell="{ column, row, item }">
              <Button
                v-if="column.key === '_unlink'"
                variant="ghost"
                class="!h-6 !w-6"
                :tooltip="__('Desvincular')"
                @click.stop.prevent="unlink('Organizations', row.name)"
              >
                <FeatherIcon name="x" class="h-4 w-4 text-ink-gray-6" />
              </Button>
              <div v-else-if="column.key === 'organization'" class="flex items-center gap-2 truncate">
                <Avatar size="sm" :label="row.name" />
                <span class="truncate">{{ row.name }}</span>
              </div>
              <div v-else class="truncate text-base">{{ item }}</div>
            </template>
          </ListView>

          <ListView
            v-else-if="tab.label === 'Contacts' && contactRows.length"
            class="mt-4 px-5"
            :columns="contactColumns"
            :rows="contactRows"
            row-key="name"
            :options="{
              selectable: false,
              showTooltip: false,
              getRowRoute: (row) => ({ name: 'Contact', params: { contactId: row.name } }),
            }"
          >
            <template #cell="{ column, row, item }">
              <Button
                v-if="column.key === '_unlink'"
                variant="ghost"
                class="!h-6 !w-6"
                :tooltip="__('Desvincular')"
                @click.stop.prevent="unlink('Contacts', row.name)"
              >
                <FeatherIcon name="x" class="h-4 w-4 text-ink-gray-6" />
              </Button>
              <div v-else-if="column.key === 'full_name'" class="flex items-center gap-2 truncate">
                <Avatar size="sm" :label="row.full_name" :image="row.image" />
                <span class="truncate">{{ row.full_name }}</span>
              </div>
              <div v-else class="truncate text-base">{{ item }}</div>
            </template>
          </ListView>

          <div v-else class="flex flex-1 flex-col items-center justify-center text-ink-gray-4">
            {{ __('Sin registros') }}
          </div>
        </div>
      </template>
    </Tabs>
  </div>

  <ContactModal
    v-if="showContactModal"
    v-model="showContactModal"
    :contact="{}"
    :options="{ redirect: false, afterInsert: (d) => linkNew('Contacts', d.name) }"
  />
  <OrganizationModal
    v-if="showOrganizationModal"
    v-model="showOrganizationModal"
    :options="{ redirect: false, afterInsert: (d) => linkNew('Organizations', d.name) }"
  />
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import Resizer from '@/components/Resizer.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import Link from '@/components/Controls/Link.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import ContactModal from '@/components/Modals/ContactModal.vue'
import OrganizationModal from '@/components/Modals/OrganizationModal.vue'
import {
  Breadcrumbs,
  Avatar,
  Badge,
  Tabs,
  ListView,
  FeatherIcon,
  createResource,
  call,
  toast,
  usePageMeta,
} from 'frappe-ui'
import { ref, computed, watch } from 'vue'

const props = defineProps({
  softwareId: { type: String, required: true },
})

const softwareName = ref('')
const orgChild = ref([])
const contactChild = ref([])
const contactDetails = ref({})

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'Software'],
  params: { doctype: 'Software' },
  auto: true,
})

async function loadSoftware() {
  const doc = await call('frappe.client.get', {
    doctype: 'Software',
    name: props.softwareId,
  })
  softwareName.value = doc.software_name || doc.name
  orgChild.value = doc.organizations || []
  contactChild.value = doc.contacts || []
  await loadContactDetails()
}

async function loadContactDetails() {
  const names = contactChild.value.map((r) => r.contact).filter(Boolean)
  if (!names.length) {
    contactDetails.value = {}
    return
  }
  const data = await call('frappe.client.get_list', {
    doctype: 'Contact',
    filters: { name: ['in', names] },
    fields: ['name', 'full_name', 'email_id', 'mobile_no', 'image'],
    limit_page_length: 0,
  })
  const map = {}
  for (const c of data) map[c.name] = c
  contactDetails.value = map
}

loadSoftware()
watch(() => props.softwareId, loadSoftware)

const breadcrumbs = computed(() => [
  { label: __('Software'), route: { name: 'Software' } },
  { label: softwareName.value, route: { name: 'SoftwareDetail', params: { softwareId: props.softwareId } } },
])

const tabIndex = ref(0)
const tabs = [
  {
    label: 'Organizations',
    icon: OrganizationsIcon,
    count: computed(() => orgChild.value.length),
  },
  {
    label: 'Contacts',
    icon: ContactsIcon,
    count: computed(() => contactChild.value.length),
  },
]

const orgRows = computed(() =>
  orgChild.value.map((r) => ({ name: r.organization, organization: r.organization })),
)
const orgColumns = [
  { label: __('Organization'), key: 'organization', width: '24rem' },
  { label: '', key: '_unlink', width: '3rem' },
]

const contactRows = computed(() =>
  contactChild.value.map((r) => {
    const d = contactDetails.value[r.contact] || {}
    return {
      name: r.contact,
      full_name: d.full_name || r.contact,
      email: d.email_id || '',
      mobile_no: d.mobile_no || '',
      image: d.image || '',
    }
  }),
)
const contactColumns = [
  { label: __('Name'), key: 'full_name', width: '16rem' },
  { label: __('Email'), key: 'email', width: '14rem' },
  { label: __('Mobile No.'), key: 'mobile_no', width: '11rem' },
  { label: '', key: '_unlink', width: '3rem' },
]

const showContactModal = ref(false)
const showOrganizationModal = ref(false)

function createNew(tabLabel) {
  if (tabLabel === 'Organizations') showOrganizationModal.value = true
  else showContactModal.value = true
}

async function addExisting(tabLabel, name) {
  if (!name) return
  const childType = tabLabel === 'Organizations' ? 'Software Organization' : 'Software Contact'
  const field = tabLabel === 'Organizations' ? 'organization' : 'contact'
  const parentfield = tabLabel === 'Organizations' ? 'organizations' : 'contacts'
  const current = tabLabel === 'Organizations' ? orgChild.value.map((r) => r.organization) : contactChild.value.map((r) => r.contact)
  if (current.includes(name)) {
    toast.error(__('Ya está vinculado'))
    return
  }
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: childType,
        parenttype: 'Software',
        parent: props.softwareId,
        parentfield,
        [field]: name,
      },
    })
    toast.success(__('Vinculado'))
    loadSoftware()
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error al vincular'))
  }
}

function linkNew(tabLabel, name) {
  addExisting(tabLabel, name)
}

async function unlink(tabLabel, name) {
  const parentfield = tabLabel === 'Organizations' ? 'organizations' : 'contacts'
  const field = tabLabel === 'Organizations' ? 'organization' : 'contact'
  try {
    const doc = await call('frappe.client.get', { doctype: 'Software', name: props.softwareId })
    doc[parentfield] = (doc[parentfield] || []).filter((r) => r[field] !== name)
    await call('frappe.client.save', { doc })
    toast.success(__('Desvinculado'))
    loadSoftware()
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error al desvincular'))
  }
}

usePageMeta(() => ({ title: softwareName.value || __('Software') }))
</script>
