<template>
  <LayoutHeader v-if="organization.doc">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <CustomActions
        v-if="organization._actions?.length"
        :actions="organization._actions"
      />
    </template>
  </LayoutHeader>
  <div v-if="organization.doc" ref="parentRef" class="flex h-full">
    <Resizer
      v-if="organization.doc"
      :parent="$refs.parentRef"
      class="flex h-full flex-col overflow-hidden border-r"
    >
      <div class="border-b">
        <FileUploader
          :validateFile="validateIsImageFile"
          @success="changeOrganizationImage"
        >
          <template #default="{ openFileSelector, error }">
            <div class="flex flex-col items-start justify-start gap-4 p-5">
              <div class="flex gap-4 items-center">
                <div class="group relative h-15.5 w-15.5">
                  <Avatar
                    size="3xl"
                    class="h-15.5 w-15.5"
                    :label="organization.doc.organization_name"
                    :image="organization.doc.organization_logo"
                  />
                  <component
                    :is="organization.doc.organization_logo ? Dropdown : 'div'"
                    v-bind="
                      organization.doc.organization_logo
                        ? {
                            options: [
                              {
                                icon: 'upload',
                                label: organization.doc.organization_logo
                                  ? __('Change Image')
                                  : __('Upload Image'),
                                onClick: openFileSelector,
                              },
                              {
                                icon: 'trash-2',
                                label: __('Remove Image'),
                                onClick: () => changeOrganizationImage(''),
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
                <div class="flex flex-col gap-2 truncate">
                  <div class="truncate text-3xl-medium text-ink-gray-9">
                    <span>{{ organization.doc.name }}</span>
                  </div>
                  <div
                    v-if="organization.doc.website"
                    class="flex items-center gap-1.5 text-base text-ink-gray-8"
                  >
                    <WebsiteIcon class="size-4" />
                    <span>{{ website(organization.doc.website) }}</span>
                  </div>
                  <ErrorMessage :message="__(error)" />
                </div>
              </div>
              <div class="flex gap-1.5">
                <Button
                  v-if="canDelete"
                  :label="__('Delete')"
                  theme="red"
                  size="sm"
                  iconLeft="trash-2"
                  @click="deleteOrganization()"
                />
                <Button
                  :tooltip="__('Open Website')"
                  icon="lucide-link"
                  @click="openWebsite"
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
          :sections="sections.data"
          doctype="CRM Organization"
          :docname="organization.doc.name"
          @reload="sections.reload"
          @beforeFieldChange="beforeFieldChange"
        />
      </div>
    </Resizer>
    <div class="flex flex-1 flex-col gap-4 overflow-hidden p-4 sm:p-5">
      <!-- Widget: Oportunidades -->
      <div class="flex min-h-0 flex-1 flex-col rounded-lg border">
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
              @change="(name) => addExisting('Deals', name)"
            >
              <template #target="{ togglePopover }">
                <Button variant="outline" @click="togglePopover()">
                  <template #prefix>
                    <FeatherIcon name="link" class="h-4" />
                  </template>
                  {{ __('Add Existing') }}
                </Button>
              </template>
            </Link>
            <Button variant="solid" @click="createNew('Deals')">
              <template #prefix>
                <FeatherIcon name="plus" class="h-4" />
              </template>
              {{ __('Create') }}
            </Button>
          </div>
        </div>
        <div
          v-if="dealStatusCounts.length"
          class="flex shrink-0 flex-wrap items-center gap-2 border-b px-4 py-2"
        >
          <button
            class="flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm"
            :class="
              dealStatusFilter === null
                ? 'border-outline-gray-3 bg-surface-gray-2 text-ink-gray-9'
                : 'border-outline-gray-2 text-ink-gray-6 hover:text-ink-gray-9'
            "
            @click="dealStatusFilter = null"
          >
            {{ __('Todos') }}
            <span class="text-ink-gray-5">{{ deals.data?.length || 0 }}</span>
          </button>
          <button
            v-for="s in dealStatusCounts"
            :key="s.status"
            class="flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm"
            :class="
              dealStatusFilter === s.status
                ? 'border-outline-gray-3 bg-surface-gray-2 text-ink-gray-9'
                : 'border-outline-gray-2 text-ink-gray-6 hover:text-ink-gray-9'
            "
            @click="
              dealStatusFilter = dealStatusFilter === s.status ? null : s.status
            "
          >
            <IndicatorIcon :class="s.color" />
            {{ s.status }}
            <span class="text-ink-gray-5">{{ s.count }}</span>
          </button>
        </div>
        <div class="min-h-0 flex-1 overflow-y-auto">
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

      <!-- Widget: Contacts -->
      <div class="flex min-h-0 flex-1 flex-col rounded-lg border">
        <div
          class="flex shrink-0 items-center justify-between gap-2 border-b px-4 py-3"
        >
          <div
            class="flex items-center gap-2 text-base font-semibold text-ink-gray-8"
          >
            <ContactsIcon class="h-5" />
            {{ __('Contacts') }}
            <Badge variant="subtle" theme="gray" size="sm">
              {{ contactRows.length }}
            </Badge>
          </div>
          <div class="flex gap-2">
            <Link
              value=""
              doctype="Contact"
              @change="(name) => addExisting('Contacts', name)"
            >
              <template #target="{ togglePopover }">
                <Button variant="outline" @click="togglePopover()">
                  <template #prefix>
                    <FeatherIcon name="link" class="h-4" />
                  </template>
                  {{ __('Add Existing') }}
                </Button>
              </template>
            </Link>
            <Button variant="solid" @click="createNew('Contacts')">
              <template #prefix>
                <FeatherIcon name="plus" class="h-4" />
              </template>
              {{ __('Create') }}
            </Button>
          </div>
        </div>
        <div class="min-h-0 flex-1 overflow-y-auto">
          <ContactsListView
            v-if="contactRows.length"
            class="py-2"
            :rows="contactRows"
            :columns="contactColumns"
            :options="{ selectable: false, showTooltip: false }"
          />
          <EmptyState v-else :icon="ContactsIcon" :name="__('Contacts')" />
        </div>
      </div>

      <!-- Widget: Software -->
      <div class="flex min-h-0 flex-1 flex-col rounded-lg border">
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
            <Dropdown :options="softwareLinkOptions">
              <Button variant="outline">
                <template #prefix>
                  <FeatherIcon name="link" class="h-4" />
                </template>
                {{ __('Add Existing') }}
                <template #suffix>
                  <FeatherIcon name="chevron-down" class="h-4" />
                </template>
              </Button>
            </Dropdown>
            <Dropdown :options="softwareCreateOptions">
              <Button variant="solid">
                <template #prefix>
                  <FeatherIcon name="plus" class="h-4" />
                </template>
                {{ __('Create') }}
                <template #suffix>
                  <FeatherIcon name="chevron-down" class="h-4" />
                </template>
              </Button>
            </Dropdown>
          </div>
        </div>
        <div class="min-h-0 flex-1 overflow-y-auto">
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
                @click.stop.prevent="unlinkSoftware(row)"
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
    :doctype="'CRM Organization'"
    :docname="props.organizationId"
    name="Organizations"
  />
  <DealModal
    v-if="showDealModal"
    v-model="showDealModal"
    :defaults="{ organization: props.organizationId }"
  />
  <ContactModal
    v-if="showContactModal"
    v-model="showContactModal"
    :contact="{ company_name: props.organizationId }"
    :options="{
      redirect: false,
      afterInsert: () => contacts.reload(),
    }"
  />
  <Dialog
    v-model="showLinkSoftwareDialog"
    :options="{ title: __('Add Existing') + ': ' + __(linkSoftwareLabel) }"
  >
    <template #body-content>
      <Link
        class="form-control"
        value=""
        :doctype="linkSoftwareDoctype"
        @change="(name) => linkSoftware(name)"
      />
    </template>
  </Dialog>
</template>

<script setup>
import ErrorPage from '@/components/ErrorPage.vue'
import Resizer from '@/components/Resizer.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import Icon from '@/components/Icon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import DealsListView from '@/components/ListViews/DealsListView.vue'
import ContactsListView from '@/components/ListViews/ContactsListView.vue'
import WebsiteIcon from '@/components/Icons/WebsiteIcon.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import DeleteLinkedDocModal from '@/components/DeleteLinkedDocModal.vue'
import DealModal from '@/components/Modals/DealModal.vue'
import ContactModal from '@/components/Modals/ContactModal.vue'
import Link from '@/components/Controls/Link.vue'
import CustomActions from '@/components/CustomActions.vue'
import { useDocument } from '@/data/document'
import { getSettings } from '@/stores/settings'
import { globalStore } from '@/stores/global'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { getView } from '@/utils/view'
import {
  validateIsImageFile,
  setupCustomizations,
  openWebsite as openExternalWebsite,
} from '@/utils'
import { timestampCell } from '@/composables/useTimelinePreferences'
import {
  Breadcrumbs,
  Avatar,
  FileUploader,
  Dropdown,
  Dialog,
  Tabs,
  ListView,
  FeatherIcon,
  createListResource,
  usePageMeta,
  createResource,
  toast,
  call,
} from 'frappe-ui'
import { useDoctypeModal } from '@/composables/doctypeModal'
import { useTelemetry } from 'frappe-ui/frappe'
import { computed, h, ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  organizationId: { type: String, required: true },
})

const { brand } = getSettings()
const { $dialog, $socket } = globalStore()
const { getUser } = usersStore()
const { getDealStatus } = statusesStore()
const { doctypeMeta } = getMeta('CRM Organization')
const { capture } = useTelemetry()

const route = useRoute()
const router = useRouter()

const errorTitle = ref('')
const errorMessage = ref('')

const showDeleteLinkedDocModal = ref(false)

const {
  document: organization,
  permissions,
  scripts,
  triggerOnRender,
} = useDocument('CRM Organization', props.organizationId)

const canDelete = computed(() => permissions.data?.permissions?.delete || false)

onMounted(async () => {
  if (organization.doc) await triggerOnRender()
})

const breadcrumbs = computed(() => {
  let items = [{ label: __('Organizations'), route: { name: 'Organizations' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(
      route.query.view,
      route.query.viewType,
      'CRM Organization',
    )
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Organizations',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: title.value,
    route: {
      name: 'Organization',
      params: { organizationId: props.organizationId },
    },
  })
  return items
})

const title = computed(() => {
  let t = doctypeMeta.value?.title_field || 'name'
  return organization.doc?.[t] || props.organizationId
})

usePageMeta(() => {
  return {
    title: title.value,
    icon: brand.favicon,
  }
})

async function deleteOrganization() {
  showDeleteLinkedDocModal.value = true
}

function changeOrganizationImage(file) {
  organization.setValue.submit({
    organization_logo: file?.file_url || null,
  })
}

function beforeFieldChange(data) {
  if (Object.hasOwn(data ?? {}, 'organization_name')) {
    call('frappe.client.rename_doc', {
      doctype: 'CRM Organization',
      old_name: props.organizationId,
      new_name: data.organization_name,
    }).then(() => {
      router.push({
        name: 'Organization',
        params: { organizationId: data.organization_name },
      })
    })
  } else {
    organization.save.submit()
  }
}

function website(url) {
  return url && url.replace(/^(?:https?:\/\/)?(?:www\.)?/i, '')
}

function openWebsite() {
  if (!organization.doc.website) {
    toast.error(__('No Website Found'))
    return
  }

  openExternalWebsite(organization.doc.website)
}

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'CRM Organization'],
  params: { doctype: 'CRM Organization' },
  auto: true,
  transform: (data) => getParsedSections(data),
})

function getParsedSections(_sections) {
  return _sections.map((section) => {
    section.columns = section.columns.map((column) => {
      column.fields = column.fields.map((field) => {
        if (field.fieldname === 'address') {
          return {
            ...field,
            create: (value, close) => {
              showAddressModal()
              close()
            },
            edit: (address) => showAddressModal(address),
          }
        } else {
          return field
        }
      })
      return column
    })
    return section
  })
}

const SoftwareIcon = {
  render: () => h(FeatherIcon, { name: 'monitor', class: 'h-5 w-5' }),
}

const deals = createListResource({
  type: 'list',
  doctype: 'CRM Deal',
  cache: ['deals', props.organizationId],
  fields: [
    'name',
    'organization',
    'currency',
    'annual_revenue',
    'status',
    'email',
    'mobile_no',
    'deal_owner',
    'modified',
  ],
  filters: {
    organization: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

const contacts = createListResource({
  type: 'list',
  doctype: 'Contact',
  cache: ['contacts', props.organizationId],
  fields: [
    'name',
    'full_name',
    'image',
    'email_id',
    'mobile_no',
    'custom_rol',
    'custom_puesto',
    'custom_relacion',
  ],
  filters: {
    company_name: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

const software = createListResource({
  type: 'list',
  doctype: 'Software',
  cache: ['software', props.organizationId],
  fields: ['name', 'software_name', 'modified'],
  filters: [
    ['Software Organization', 'organization', '=', props.organizationId],
  ],
  orderBy: 'modified desc',
  pageLength: 99,
  auto: true,
})

const procesos = createListResource({
  type: 'list',
  doctype: 'Procesos - Tecnologias',
  cache: ['procesos', props.organizationId],
  fields: ['name', 'nombre', 'modified'],
  filters: {
    organization: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 99,
  auto: true,
})

const dealStatusFilter = ref(null)

const dealStatusCounts = computed(() => {
  const counts = {}
  for (const d of deals.data || []) {
    if (!d.status) continue
    counts[d.status] = (counts[d.status] || 0) + 1
  }
  return Object.entries(counts).map(([status, count]) => ({
    status,
    count,
    color: getDealStatus(status)?.color,
  }))
})

const dealRows = computed(() => {
  let data = deals.data || []
  if (dealStatusFilter.value)
    data = data.filter((d) => d.status === dealStatusFilter.value)
  return data.map(getDealRowObject)
})
const contactRows = computed(() => contacts.data?.map(getContactRowObject) || [])
const softwareRows = computed(() => [
  ...(software.data?.map(getSoftwareRowObject) || []),
  ...(procesos.data?.map(getProcesoRowObject) || []),
])

const { getFormattedCurrency } = getMeta('CRM Deal')

function getSoftwareRowObject(sw) {
  return {
    name: 'sw-' + sw.name,
    software_name: sw.software_name,
    tipo: __('Software'),
    modified: timestampCell(sw.modified),
  }
}

function getProcesoRowObject(p) {
  return {
    name: 'pt-' + p.name,
    software_name: p.nombre,
    tipo: __('Proceso / Tecnología'),
    modified: timestampCell(p.modified),
  }
}

const softwareColumns = [
  {
    label: __('Nombre'),
    key: 'software_name',
    width: '16rem',
  },
  {
    label: __('Tipo'),
    key: 'tipo',
    width: '11rem',
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

async function unlinkSoftware(row) {
  try {
    if (String(row.name).startsWith('pt-')) {
      await call('frappe.client.set_value', {
        doctype: 'Procesos - Tecnologias',
        name: String(row.name).slice(3),
        fieldname: 'organization',
        value: '',
      })
      procesos.reload()
    } else {
      let doc = await call('frappe.client.get', {
        doctype: 'Software',
        name: String(row.name).slice(3),
      })
      doc.organizations = (doc.organizations || []).filter(
        (r) => r.organization !== props.organizationId,
      )
      await call('frappe.client.save', { doc: doc })
      software.reload()
    }
    toast.success(__('Desvinculado de la organización'))
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error al desvincular'))
  }
}

function getDealRowObject(deal) {
  return {
    name: deal.name,
    organization: {
      label: deal.organization,
      logo: organization.doc?.organization_logo,
    },
    annual_revenue: getFormattedCurrency('annual_revenue', deal),
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

function getContactRowObject(contact) {
  return {
    name: contact.name,
    full_name: {
      label: contact.full_name,
      image_label: contact.full_name,
      image: contact.image,
    },
    email: contact.email_id,
    mobile_no: contact.mobile_no,
    rol: contact.custom_rol,
    puesto: contact.custom_puesto,
    relacion: contact.custom_relacion,
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
    key: 'annual_revenue',
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
    label: __('Mobile No.'),
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

const contactColumns = [
  {
    label: __('Name'),
    key: 'full_name',
    width: '15rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '13rem',
  },
  {
    label: __('Phone'),
    key: 'mobile_no',
    width: '10rem',
  },
  {
    label: __('Rol'),
    key: 'rol',
    width: '11rem',
  },
  {
    label: __('Puesto'),
    key: 'puesto',
    width: '11rem',
  },
  {
    label: __('Relacion'),
    key: 'relacion',
    type: 'Rating',
    options: 5,
    width: '9rem',
  },
]

const { showModal } = useDoctypeModal()

const showDealModal = ref(false)
const showContactModal = ref(false)

function createNew(tabLabel) {
  if (tabLabel === 'Deals') {
    showDealModal.value = true
  } else {
    showContactModal.value = true
  }
}

const showLinkSoftwareDialog = ref(false)
const linkSoftwareDoctype = ref('Software')

const linkSoftwareLabel = computed(() =>
  linkSoftwareDoctype.value === 'Software'
    ? 'Software'
    : 'Proceso / Tecnología',
)

const softwareCreateOptions = [
  {
    label: __('Software'),
    onClick: () =>
      showModal({
        doctype: 'Software',
        callbacks: {
          afterInsert: async (d) => {
            await call('frappe.client.insert', {
              doc: {
                doctype: 'Software Organization',
                parenttype: 'Software',
                parent: d.name,
                parentfield: 'organizations',
                organization: props.organizationId,
              },
            })
            software.reload()
          },
        },
      }),
  },
  {
    label: __('Proceso / Tecnología'),
    onClick: () =>
      showModal({
        doctype: 'Procesos - Tecnologias',
        defaults: { organization: props.organizationId },
        callbacks: { afterInsert: () => procesos.reload() },
      }),
  },
]

const softwareLinkOptions = [
  {
    label: __('Software'),
    onClick: () => openLinkSoftwareDialog('Software'),
  },
  {
    label: __('Proceso / Tecnología'),
    onClick: () => openLinkSoftwareDialog('Procesos - Tecnologias'),
  },
]

function openLinkSoftwareDialog(doctype) {
  linkSoftwareDoctype.value = doctype
  showLinkSoftwareDialog.value = true
}

async function linkSoftware(name) {
  if (!name) return
  showLinkSoftwareDialog.value = false
  try {
    if (linkSoftwareDoctype.value === 'Software') {
      if (software.data?.find((s) => s.name === name)) {
        toast.error(__('Ya está vinculado a esta organización'))
        return
      }
      await call('frappe.client.insert', {
        doc: {
          doctype: 'Software Organization',
          parenttype: 'Software',
          parent: name,
          parentfield: 'organizations',
          organization: props.organizationId,
        },
      })
      software.reload()
    } else {
      await call('frappe.client.set_value', {
        doctype: linkSoftwareDoctype.value,
        name: name,
        fieldname: 'organization',
        value: props.organizationId,
      })
      procesos.reload()
    }
    toast.success(__('Linked to organization'))
  } catch (e) {
    toast.error(e.messages?.[0] || __('Error linking document'))
  }
}

async function addExisting(tabLabel, name) {
  if (!name) return
  try {
    if (tabLabel === 'Deals') {
      await call('frappe.client.set_value', {
        doctype: 'CRM Deal',
        name: name,
        fieldname: 'organization',
        value: props.organizationId,
      })
      deals.reload()
    } else {
      await call('frappe.client.set_value', {
        doctype: 'Contact',
        name: name,
        fieldname: 'company_name',
        value: props.organizationId,
      })
      contacts.reload()
    }
    toast.success(__('Linked to organization'))
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
        organization.doc.address = d.name
        organization.save.submit()
      },
    },
  })
}

// Setup custom actions from Form Scripts
watch(
  () => organization.doc,
  async (_doc) => {
    if (scripts.data?.length) {
      let s = await setupCustomizations(scripts.data, {
        doc: _doc,
        $dialog,
        $socket,
        router,
        toast,
        updateField: organization.setValue.submit,
        createToast: toast.create,
        deleteDoc: deleteOrganization,
        call,
      })
      organization._actions = s.actions || []
    }
  },
  { once: true },
)
</script>
