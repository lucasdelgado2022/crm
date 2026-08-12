<template>
  <LayoutHeader v-if="contact.doc">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <Button
        v-if="contact.doc?.company_name"
        :label="__('Open Organization')"
        iconLeft="briefcase"
        @click="openOrganization"
      />
      <CustomActions
        v-if="contact._actions?.length"
        :actions="contact._actions"
      />
    </template>
  </LayoutHeader>
  <div v-if="contact.doc" ref="parentRef" class="flex h-full">
    <Resizer
      v-if="contact.doc"
      :parent="$refs.parentRef"
      class="flex h-full flex-col overflow-hidden border-r"
    >
      <div class="border-b">
        <FileUploader
          :validateFile="validateIsImageFile"
          @success="changeContactImage"
        >
          <template #default="{ openFileSelector, error }">
            <div class="flex flex-col items-start justify-start gap-4 p-5">
              <div class="flex gap-4 items-center">
                <div class="group relative h-15.5 w-15.5">
                  <Avatar
                    size="3xl"
                    class="h-15.5 w-15.5"
                    :label="contact.doc.full_name"
                    :image="contact.doc.image"
                  />
                  <component
                    :is="contact.doc.image ? Dropdown : 'div'"
                    v-bind="
                      contact.doc.image
                        ? {
                            options: [
                              {
                                icon: 'upload',
                                label: contact.doc.image
                                  ? __('Change Image')
                                  : __('Upload Image'),
                                onClick: openFileSelector,
                              },
                              {
                                icon: 'trash-2',
                                label: __('Remove Image'),
                                onClick: () => changeContactImage(''),
                              },
                            ],
                          }
                        : { onClick: openFileSelector }
                    "
                    class="!absolute bottom-0 left-0 right-0"
                  >
                    <div
                      class="z-1 absolute bottom-0 left-0 right-0 flex h-14 cursor-pointer items-center justify-center rounded-b-full bg-black bg-opacity-40 pt-5 opacity-0 duration-300 ease-in-out group-hover:opacity-100"
                      style="
                        -webkit-clip-path: inset(22px 0 0 0);
                        clip-path: inset(22px 0 0 0);
                      "
                    >
                      <CameraIcon class="h-6 w-6 cursor-pointer text-white" />
                    </div>
                  </component>
                </div>
                <div class="flex flex-col gap-2 truncate text-ink-gray-9">
                  <div class="truncate text-3xl-medium">
                    <span v-if="contact.doc.salutation">
                      {{ contact.doc.salutation + ' ' }}
                    </span>
                    <span>{{ contact.doc.full_name }}</span>
                  </div>
                  <div
                    v-if="contact.doc.company_name"
                    class="flex items-center gap-1.5 text-base text-ink-gray-8"
                  >
                    {{ contact.doc.company_name }}
                  </div>
                  <ErrorMessage :message="__(error)" />
                </div>
              </div>
              <div class="flex gap-1.5">
                <Button
                  v-if="callEnabled && contact.doc.mobile_no"
                  :label="__('Make Call')"
                  size="sm"
                  :iconLeft="PhoneIcon"
                  @click="callEnabled && makeCall(contact.doc.mobile_no)"
                />
                <Button
                  v-if="canDelete"
                  :label="__('Delete')"
                  theme="red"
                  size="sm"
                  iconLeft="trash-2"
                  @click="deleteContact()"
                />
              </div>
            </div>
          </template>
        </FileUploader>
      </div>
      <div
        v-if="sections.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <SidePanelLayout
          :sections="parsedSections"
          doctype="Contact"
          :docname="contact.doc.name"
          @reload="sections.reload"
        />
      </div>
    </Resizer>
    <div class="flex flex-1 flex-col gap-4 overflow-hidden p-4 sm:p-5">
      <!-- Widget: Deals -->
      <div
        :class="
          widgetShown('Deals')
            ? 'flex min-h-0 flex-1 flex-col rounded-lg border'
            : 'flex shrink-0 flex-col rounded-lg border'
        "
      >
        <div
          class="flex shrink-0 items-center justify-between gap-2 border-b px-4 py-3"
        >
          <div
            class="flex items-center gap-2 text-base font-semibold text-ink-gray-8"
          >
            <DealsIcon class="h-5" />
            {{ __('Deals') }}
            <Badge variant="subtle" theme="gray" size="sm">
              {{ dealRows.length }}
            </Badge>
          </div>
          <div class="flex gap-2">
            <Link
              value=""
              doctype="CRM Deal"
              :onCreate="(v, close) => { createNewTabDoc('Deals'); close && close() }"
              @change="(name) => addExisting('Deals', name)"
            >
              <template #target="{ togglePopover }">
                <Button variant="outline" @click="togglePopover()">
                  <template #prefix>
                    <FeatherIcon name="link" class="h-4" />
                  </template>
                  {{ __('Add') }}
                </Button>
              </template>
            </Link>
            <Button
              variant="ghost"
              :tooltip="maxWidget === 'Deals' ? __('Restaurar') : __('Maximizar')"
              @click="toggleMax('Deals')"
            >
              <template #icon>
                <component
                  :is="maxWidget === 'Deals' ? MinimizeIcon : MaximizeIcon"
                  class="h-4 w-4"
                />
              </template>
            </Button>
          </div>
        </div>
        <div v-show="widgetShown('Deals')" class="min-h-0 flex-1 overflow-y-auto">
          <DealsListView
            v-if="dealRows.length"
            class="py-2"
            :rows="dealRows"
            :columns="dealColumns"
            :options="{ selectable: false, showTooltip: false }"
          />
          <EmptyState v-else :icon="DealsIcon" :name="__('Deals')" />
        </div>
      </div>

      <!-- Widget: Leads -->
      <div
        :class="
          widgetShown('Leads')
            ? 'flex min-h-0 flex-1 flex-col rounded-lg border'
            : 'flex shrink-0 flex-col rounded-lg border'
        "
      >
        <div
          class="flex shrink-0 items-center justify-between gap-2 border-b px-4 py-3"
        >
          <div
            class="flex items-center gap-2 text-base font-semibold text-ink-gray-8"
          >
            <LeadsIcon class="h-5" />
            {{ __('Leads') }}
            <Badge variant="subtle" theme="gray" size="sm">
              {{ leadRows.length }}
            </Badge>
          </div>
          <div class="flex gap-2">
            <Link
              value=""
              doctype="CRM Lead"
              :onCreate="(v, close) => { createNewTabDoc('Leads'); close && close() }"
              @change="(name) => addExisting('Leads', name)"
            >
              <template #target="{ togglePopover }">
                <Button variant="outline" @click="togglePopover()">
                  <template #prefix>
                    <FeatherIcon name="link" class="h-4" />
                  </template>
                  {{ __('Add') }}
                </Button>
              </template>
            </Link>
            <Button
              variant="ghost"
              :tooltip="maxWidget === 'Leads' ? __('Restaurar') : __('Maximizar')"
              @click="toggleMax('Leads')"
            >
              <template #icon>
                <component
                  :is="maxWidget === 'Leads' ? MinimizeIcon : MaximizeIcon"
                  class="h-4 w-4"
                />
              </template>
            </Button>
          </div>
        </div>
        <div v-show="widgetShown('Leads')" class="min-h-0 flex-1 overflow-y-auto">
          <LeadsListView
            v-if="leadRows.length"
            class="py-2"
            :rows="leadRows"
            :columns="leadColumns"
            :options="{ selectable: false, showTooltip: false }"
          />
          <EmptyState v-else :icon="LeadsIcon" :name="__('Leads')" />
        </div>
      </div>

      <!-- Widget: Software -->
      <div
        :class="
          widgetShown('Software')
            ? 'flex min-h-0 flex-1 flex-col rounded-lg border'
            : 'flex shrink-0 flex-col rounded-lg border'
        "
      >
        <div
          class="flex shrink-0 items-center justify-between gap-2 border-b px-4 py-3"
        >
          <div
            class="flex items-center gap-2 text-base font-semibold text-ink-gray-8"
          >
            <SoftwareIcon class="h-5" />
            {{ __('Software') }}
            <Badge variant="subtle" theme="gray" size="sm">
              {{ softwareRows.length }}
            </Badge>
          </div>
          <div class="flex gap-2">
            <Link
              value=""
              doctype="Software"
              :onCreate="(v, close) => { createNewTabDoc('Software'); close && close() }"
              @change="(name) => addExisting('Software', name)"
            >
              <template #target="{ togglePopover }">
                <Button variant="outline" @click="togglePopover()">
                  <template #prefix>
                    <FeatherIcon name="link" class="h-4" />
                  </template>
                  {{ __('Add') }}
                </Button>
              </template>
            </Link>
            <Button
              variant="ghost"
              :tooltip="
                maxWidget === 'Software' ? __('Restaurar') : __('Maximizar')
              "
              @click="toggleMax('Software')"
            >
              <template #icon>
                <component
                  :is="maxWidget === 'Software' ? MinimizeIcon : MaximizeIcon"
                  class="h-4 w-4"
                />
              </template>
            </Button>
          </div>
        </div>
        <div
          v-show="widgetShown('Software')"
          class="min-h-0 flex-1 overflow-y-auto"
        >
          <ListView
            v-if="softwareRows.length"
            class="px-4 py-2"
            :rows="softwareRows"
            :columns="softwareColumns"
            row-key="name"
            :options="{ selectable: false, showTooltip: false }"
          >
            <template #cell="{ item, row, column }">
              <Button
                v-if="column.key === '_unlink'"
                variant="ghost"
                class="!h-6 !w-6"
                :tooltip="__('Desvincular')"
                @click.stop.prevent="unlinkSoftwareFromContact(row)"
              >
                <FeatherIcon name="x" class="h-4 w-4 text-ink-gray-6" />
              </Button>
              <div v-else class="truncate text-base">
                {{ item?.timeAgo || item?.label || item }}
              </div>
            </template>
          </ListView>
          <EmptyState v-else :icon="SoftwareIcon" :name="__('Software')" />
        </div>
      </div>
    </div>
  </div>
  <ErrorPage
    v-else-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  />
  <DeleteLinkedDocModal
    v-if="showDeleteLinkedDocModal"
    v-model="showDeleteLinkedDocModal"
    :doctype="'Contact'"
    :docname="contact.doc.name"
    name="Contacts"
  />
  <DealModal
    v-if="showDealModal"
    v-model="showDealModal"
    :defaults="{
      contact: props.contactId,
      organization: contact.doc?.company_name,
    }"
  />
  <LeadModal
    v-if="showLeadModal"
    v-model="showLeadModal"
    :defaults="{
      custom_contact: props.contactId,
      salutation: contact.doc?.salutation,
      first_name: contact.doc?.first_name,
      last_name: contact.doc?.last_name,
      email: contact.doc?.email_id,
      mobile_no: contact.doc?.mobile_no,
      organization: contact.doc?.company_name,
    }"
  />
</template>

<script setup>
import ErrorPage from '@/components/ErrorPage.vue'
import Resizer from '@/components/Resizer.vue'
import Icon from '@/components/Icon.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import MaximizeIcon from '@/components/Icons/MaximizeIcon.vue'
import MinimizeIcon from '@/components/Icons/MinimizeIcon.vue'
import DealsListView from '@/components/ListViews/DealsListView.vue'
import LeadsListView from '@/components/ListViews/LeadsListView.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import DealModal from '@/components/Modals/DealModal.vue'
import LeadModal from '@/components/Modals/LeadModal.vue'
import Link from '@/components/Controls/Link.vue'
import CustomActions from '@/components/CustomActions.vue'
import { validateIsImageFile, setupCustomizations } from '@/utils'
import { useContactFields } from '@/composables/useContactFields'
import { timestampCell } from '@/composables/useTimelinePreferences'
import { getView } from '@/utils/view'
import { useDocument } from '@/data/document'
import { getSettings } from '@/stores/settings'
import { getMeta } from '@/stores/meta'
import { globalStore } from '@/stores/global.js'
import { usersStore } from '@/stores/users.js'
import { organizationsStore } from '@/stores/organizations.js'
import { statusesStore } from '@/stores/statuses'
import { callEnabled } from '@/composables/telephony'
import {
  Breadcrumbs,
  Avatar,
  FileUploader,
  Tabs,
  ListView,
  FeatherIcon,
  call,
  createResource,
  createListResource,
  usePageMeta,
  Dropdown,
  toast,
} from 'frappe-ui'
import { useDoctypeModal } from '@/composables/doctypeModal'
import { useTelemetry } from 'frappe-ui/frappe'
import { ref, computed, watch, onMounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import EmptyState from '@/components/ListViews/EmptyState.vue'

const { brand } = getSettings()
const { makeCall, $dialog, $socket } = globalStore()

const { getUser } = usersStore()
const { getOrganization } = organizationsStore()
const { getDealStatus, getLeadStatus } = statusesStore()
const { doctypeMeta } = getMeta('Contact')
const { capture } = useTelemetry()

const props = defineProps({
  contactId: { type: String, required: true },
})

const route = useRoute()
const router = useRouter()

function openOrganization() {
  if (contact.doc?.company_name)
    router.push({
      name: 'Organization',
      params: { organizationId: contact.doc.company_name },
    })
}

const errorTitle = ref('')
const errorMessage = ref('')

const {
  document: contact,
  permissions,
  scripts,
  triggerOnRender,
} = useDocument('Contact', props.contactId)

const canDelete = computed(() => permissions.data?.permissions?.delete || false)

const transformField = useContactFields(contact)

onMounted(async () => {
  if (contact.doc) await triggerOnRender()
})

const breadcrumbs = computed(() => {
  let items = [{ label: __('Contacts'), route: { name: 'Contacts' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'Contact')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Contacts',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: title.value,
    route: {
      name: 'Contact',
      params: { contactId: props.contactId },
      query: route.query,
    },
  })
  return items
})

const title = computed(() => {
  let t = doctypeMeta.value?.title_field || 'name'
  return contact.doc?.[t] || props.contactId
})

usePageMeta(() => {
  return {
    title: title.value,
    icon: brand.favicon,
  }
})
const showDeleteLinkedDocModal = ref(false)

// Maximizar widget (deja solo los encabezados de los demas)
const maxWidget = ref(null)
function toggleMax(key) {
  maxWidget.value = maxWidget.value === key ? null : key
}
function widgetShown(key) {
  return !maxWidget.value || maxWidget.value === key
}

async function deleteContact() {
  showDeleteLinkedDocModal.value = true
}

function changeContactImage(file) {
  contact.doc.image = file?.file_url || ''
  contact.save.submit(null, {
    onSuccess: () => {
      toast.success(__('Contact image updated'))
    },
  })
}

const SoftwareIcon = {
  render: () => h(FeatherIcon, { name: 'monitor', class: 'h-5 w-5' }),
}

const deals = createResource({
  url: 'crm.api.contact.get_linked_deals',
  cache: ['deals', props.contactId],
  params: { contact: props.contactId },
  auto: true,
})

const software = createListResource({
  type: 'list',
  doctype: 'Software',
  cache: ['software', props.contactId],
  fields: ['name', 'software_name', 'modified'],
  filters: [['Software Contact', 'contact', '=', props.contactId]],
  orderBy: 'modified desc',
  pageLength: 99,
  auto: true,
})

const leads = createListResource({
  type: 'list',
  doctype: 'CRM Lead',
  cache: ['leads', props.contactId],
  fields: [
    'name',
    'lead_name',
    'image',
    'first_name',
    'organization',
    'status',
    'email',
    'mobile_no',
    'modified',
  ],
  filters: {
    custom_contact: props.contactId,
  },
  orderBy: 'modified desc',
  pageLength: 99,
  auto: true,
})

const dealRows = computed(() =>
  deals.data ? deals.data.map((row) => getDealRowObject(row)) : [],
)
const leadRows = computed(() => leads.data?.map(getLeadRowObject) || [])
const softwareRows = computed(
  () => software.data?.map(getSoftwareRowObject) || [],
)

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'Contact'],
  params: { doctype: 'Contact' },
  auto: true,
})

const parsedSections = computed(() => {
  if (!sections.data) return []
  return sections.data.map((section) => ({
    ...section,
    columns: section.columns.map((column) => ({
      ...column,
      fields: column.fields.map((field) => {
        field.label = fieldLabelMap[field.fieldname] || field.label
        field.placeholder =
          fieldPlaceholderMap[field.fieldname] || field.placeholder
        return transformField(field, { showAddressModal })
      }),
    })),
  }))
})

const fieldLabelMap = {
  mobile_no: __('Mobile Number'),
  company_name: __('Organization'),
}

const fieldPlaceholderMap = {
  mobile_no: __('Add Mobile Number...'),
  company_name: __('Add Organization...'),
}

const { getFormattedCurrency } = getMeta('CRM Deal')

function getLeadRowObject(lead) {
  return {
    name: lead.name,
    lead_name: {
      label: lead.lead_name,
      image: lead.image,
      image_label: lead.first_name,
    },
    organization: lead.organization,
    status: {
      label: lead.status,
      color: getLeadStatus(lead.status)?.color,
    },
    email: lead.email,
    mobile_no: lead.mobile_no,
    modified: timestampCell(lead.modified),
  }
}

const leadColumns = [
  {
    label: __('Name'),
    key: 'lead_name',
    width: '12rem',
  },
  {
    label: __('Organization'),
    key: 'organization',
    width: '11rem',
  },
  {
    label: __('Status'),
    key: 'status',
    width: '10rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Mobile No.'),
    key: 'mobile_no',
    width: '11rem',
  },
  {
    label: __('Last Modified'),
    key: 'modified',
    width: '8rem',
  },
]

function getSoftwareRowObject(sw) {
  return {
    name: sw.name,
    software_name: sw.software_name,
    modified: timestampCell(sw.modified),
  }
}

const softwareColumns = [
  {
    label: __('Nombre'),
    key: 'software_name',
    width: '16rem',
  },
  {
    label: __('Last Modified'),
    key: 'modified',
    width: '10rem',
  },
  {
    label: '',
    key: '_unlink',
    width: '3rem',
  },
]

async function unlinkSoftwareFromContact(row) {
  try {
    let doc = await call('frappe.client.get', {
      doctype: 'Software',
      name: row.name,
    })
    doc.contacts = (doc.contacts || []).filter(
      (r) => r.contact !== props.contactId,
    )
    await call('frappe.client.save', { doc: doc })
    software.reload()
    toast.success(__('Desvinculado del contacto'))
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error al desvincular'))
  }
}

function getDealRowObject(deal) {
  return {
    name: deal.name,
    organization: {
      label: deal.organization,
      logo: getOrganization(deal.organization)?.organization_logo,
    },
    deal_value: getFormattedCurrency('deal_value', deal),
    status: {
      label: deal.status,
      color: getDealStatus(deal.status)?.color,
    },
    email: deal.email,
    mobile_no: deal.mobile_no,
    deal_owner: {
      label: deal.deal_owner && getUser(deal.deal_owner).full_name,
      ...(deal.deal_owner && getUser(deal.deal_owner)),
    },
    modified: timestampCell(deal.modified),
  }
}

const dealColumns = [
  {
    label: __('Organization'),
    key: 'organization',
    width: '11rem',
  },
  {
    label: __('Amount'),
    key: 'deal_value',
    align: 'right',
    width: '9rem',
  },
  {
    label: __('Status'),
    key: 'status',
    width: '10rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Mobile Number'),
    key: 'mobile_no',
    width: '11rem',
  },
  {
    label: __('Deal Owner'),
    key: 'deal_owner',
    width: '10rem',
  },
  {
    label: __('Last Modified'),
    key: 'modified',
    width: '8rem',
  },
]

const { showModal } = useDoctypeModal()

const showDealModal = ref(false)

const showLeadModal = ref(false)

function createNewTabDoc(tabLabel) {
  if (tabLabel === 'Deals') {
    showDealModal.value = true
  } else if (tabLabel === 'Leads') {
    showLeadModal.value = true
  } else {
    showModal({
      doctype: 'Software',
      callbacks: {
        afterInsert: async (d) => {
          await linkSoftwareToContact(d.name)
          software.reload()
        },
      },
    })
  }
}

async function linkSoftwareToContact(softwareName) {
  await call('frappe.client.insert', {
    doc: {
      doctype: 'Software Contact',
      parenttype: 'Software',
      parent: softwareName,
      parentfield: 'contacts',
      contact: props.contactId,
    },
  })
}

async function addExisting(tabLabel, name) {
  if (!name) return
  try {
    if (tabLabel === 'Deals') {
      if (deals.data?.find((d) => d.name === name)) {
        toast.error(__('Contact Already Added'))
        return
      }
      await call('crm.fcrm.doctype.crm_deal.crm_deal.add_contact', {
        deal: name,
        contact: props.contactId,
      })
      deals.reload()
    } else if (tabLabel === 'Leads') {
      if (leads.data?.find((l) => l.name === name)) {
        toast.error(__('Ya está vinculado a este contacto'))
        return
      }
      await call('frappe.client.set_value', {
        doctype: 'CRM Lead',
        name: name,
        fieldname: 'custom_contact',
        value: props.contactId,
      })
      leads.reload()
    } else {
      if (software.data?.find((s) => s.name === name)) {
        toast.error(__('Ya está vinculado a este contacto'))
        return
      }
      await linkSoftwareToContact(name)
      software.reload()
    }
    toast.success(__('Linked to contact'))
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error linking document'))
  }
}

function showAddressModal(_address) {
  showModal({
    name: _address || null,
    doctype: 'Address',
    callbacks: {
      afterInsert: (d) => {
        capture('address_created')
        contact.doc.address = d.name
        contact.save.submit()
      },
    },
  })
}

// Setup custom actions from Form Scripts
watch(
  () => contact.doc,
  async (_doc) => {
    if (scripts.data?.length) {
      let s = await setupCustomizations(scripts.data, {
        doc: _doc,
        $dialog,
        $socket,
        router,
        toast,
        updateField: contact.setValue.submit,
        createToast: toast.create,
        deleteDoc: deleteContact,
        call,
      })
      contact._actions = s.actions || []
    }
  },
  { once: true },
)
</script>
