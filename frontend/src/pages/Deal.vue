<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template v-if="!errorTitle" #right-header>
      <CustomActions
        v-if="document._actions?.length"
        :actions="document._actions"
      />
      <CustomActions
        v-if="document.actions?.length"
        :actions="document.actions"
      />
      <EnrichFromWebsite
        doctype="CRM Deal"
        :docname="dealId"
        :website="doc.website"
        @done="onEnriched"
      />
      <AssignTo v-model="assignees.data" doctype="CRM Deal" :docname="dealId" />
      <Dropdown
        v-if="doc && document.statuses"
        :options="statuses"
        placement="right"
      >
        <template #default="{ open }">
          <Button
            v-if="doc.status"
            :label="statusLabel(doc.status)"
            :iconRight="open ? 'chevron-up' : 'chevron-down'"
          >
            <template #prefix>
              <IndicatorIcon :class="getDealStatus(doc.status).color" />
            </template>
          </Button>
        </template>
      </Dropdown>
    </template>
  </LayoutHeader>
  <div v-if="doc.name" class="flex h-full overflow-hidden">
    <div class="relative flex flex-1 flex-col overflow-hidden">
      <Tabs
        v-model="tabIndex"
        as="div"
        :tabs="tabs"
        class="flex flex-1 overflow-hidden flex-col [&_[role='tab']]:px-0 [&_[role='tab']]:shrink-0 [&_[role='tablist']]:px-5 [&_[role='tablist']::-webkit-scrollbar]:h-0 [&_[role='tablist']]:min-h-[45px] [&_[role='tablist']]:gap-7.5 [&_[role='tabpanel']:not([hidden])]:flex [&_[role='tabpanel']:not([hidden])]:grow [&_[role='tab']:nth-child(n+7)]:!hidden"
      >
        <template #tab-panel>
          <Activities
            ref="activities"
            v-model:reload="reload"
            v-model:tabIndex="tabIndex"
            doctype="CRM Deal"
            :docname="dealId"
            :tabs="tabs"
            @beforeSave="beforeStatusChange"
            @afterSave="reloadResources"
          />
        </template>
      </Tabs>
      <div
        v-if="moreTabs.length"
        class="absolute right-4 top-1.5 z-10"
      >
        <Dropdown :options="moreTabs" placement="bottom-end">
          <template #default="{ open }">
            <Button
              variant="ghost"
              :label="activeSecondaryLabel || __('Más')"
              :iconRight="open ? 'chevron-up' : 'chevron-down'"
              :class="activeSecondaryLabel ? 'text-ink-gray-9' : 'text-ink-gray-6'"
            />
          </template>
        </Dropdown>
      </div>
    </div>
    <Resizer side="right" class="flex flex-col justify-between border-l">
      <div
        class="flex h-[45px] cursor-copy items-center border-b px-5 py-2.5 text-lg-medium text-ink-gray-9"
        @click="copyToClipboard(doc.custom_numero_solaer || dealId)"
      >
        {{ doc.custom_numero_solaer || __(dealId) }}
      </div>
      <div class="flex items-center justify-start gap-5 border-b p-5">
        <Tooltip :text="__('Organization Logo')">
          <div class="group relative size-12">
            <Avatar
              size="3xl"
              class="size-12"
              :label="title"
              :image="doc.organization_logo || organization?.organization_logo"
            />
          </div>
        </Tooltip>
        <div class="flex flex-col gap-2.5 truncate text-ink-gray-9">
          <Tooltip :text="organization?.name || __('Set an Organization')">
            <div class="truncate text-3xl-medium uppercase">
              {{ title }}
            </div>
          </Tooltip>
          <div class="flex gap-1.5">
            <Button
              v-if="callEnabled"
              :tooltip="__('Make a Call')"
              :icon="PhoneIcon"
              @click="triggerCall"
            />

            <Button
              :tooltip="__('Send an Email')"
              :icon="Email2Icon"
              @click="
                doc.email
                  ? openEmailBox()
                  : toast.error(
                      __('Please set an email address to send emails'),
                    )
              "
            />

            <Button
              v-if="doc.organization"
              :tooltip="__('Open Organization')"
              :icon="ArrowUpRightIcon"
              @click="openOrganization"
            />

            <Button
              v-if="doc.organization"
              :tooltip="__('Editar organización')"
              icon="lucide-pencil"
              @click="openOrganization"
            />

            <Button
              :tooltip="__('Go to Website')"
              :icon="LinkIcon"
              @click="
                doc.website
                  ? openWebsite(doc.website)
                  : toast.error(__('Please set a website to visit'))
              "
            />

            <Button
              :tooltip="__('Attach a File')"
              :icon="AttachmentIcon"
              @click="showFilesUploader = true"
            />

            <Button
              v-if="canDelete"
              :tooltip="__('Delete')"
              variant="subtle"
              icon="lucide-trash-2"
              theme="red"
              @click="deleteDeal"
            />
          </div>
        </div>
      </div>
      <SLASection
        v-if="doc.sla_status"
        v-model="doc"
        @updateField="updateField"
      />
      <div
        v-if="sections.data"
        class="flex flex-1 flex-col overflow-y-auto"
      >
        <SidePanelLayout
          :sections="sections.data"
          :addContact="addContact"
          doctype="CRM Deal"
          :docname="dealId"
          @reload="sections.reload"
          @beforeFieldChange="beforeStatusChange"
          @afterFieldChange="reloadResources"
        >
          <template #actions="{ section }">
            <div v-if="section.name == 'contacts_section'" class="pr-2">
              <Link
                value=""
                doctype="Contact"
                :onCreate="
                  (value, close) => {
                    _contact = {
                      first_name: value,
                      company_name: doc.organization,
                    }
                    showContactModal = true
                    close()
                  }
                "
                @change="(e) => addContact(e)"
              >
                <template #target="{ togglePopover }">
                  <Button
                    class="h-7 px-3"
                    variant="ghost"
                    icon="lucide-plus"
                    @click="togglePopover()"
                  />
                </template>
              </Link>
            </div>
          </template>
          <template #default="{ section }">
            <div
              v-if="section.name == 'contacts_section'"
              class="contacts-area"
            >
              <div
                v-if="dealContacts?.loading && dealContacts?.data?.length == 0"
                class="flex min-h-20 flex-1 items-center justify-center gap-3 text-base text-ink-gray-4"
              >
                <LoadingIndicator class="h-4 w-4" />
                <span>{{ __('Loading...') }}</span>
              </div>
              <div
                v-for="(contact, i) in dealContacts.data"
                v-else-if="dealContacts?.data?.length"
                :key="contact.name"
              >
                <div class="px-2 pb-2.5" :class="[i == 0 ? 'pt-5' : 'pt-2.5']">
                  <CollapsibleSection :opened="contact.opened">
                    <template #header="{ opened, toggle }">
                      <div
                        class="flex cursor-pointer items-center justify-between gap-2 pr-1 text-base leading-5 text-ink-gray-7"
                      >
                        <div
                          class="flex h-7 items-center gap-2 truncate"
                          @click="toggle()"
                        >
                          <Avatar
                            :label="contact.full_name"
                            :image="contact.image"
                            size="md"
                          />
                          <div class="truncate">
                            {{ contact.full_name }}
                          </div>
                          <Badge
                            v-if="contact.is_primary"
                            class="ml-2"
                            variant="outline"
                            :label="__('Primary')"
                            theme="green"
                          />
                          <Badge
                            v-if="contactRoles[contact.name]?.rol"
                            class="ml-1"
                            variant="subtle"
                            :label="__(contactRoles[contact.name].rol)"
                            theme="blue"
                          />
                        </div>
                        <div class="flex items-center">
                          <Dropdown :options="contactOptions(contact)">
                            <Button
                              icon="lucide-more-horizontal"
                              class="text-ink-gray-5"
                              variant="ghost"
                            />
                          </Dropdown>
                          <Button
                            variant="ghost"
                            :tooltip="__('View Contact')"
                            :icon="ArrowUpRightIcon"
                            @click="
                              router.push({
                                name: 'Contact',
                                params: { contactId: contact.name },
                              })
                            "
                          />
                          <Button
                            variant="ghost"
                            class="transition-all duration-300 ease-in-out"
                            :class="{ 'rotate-90': opened }"
                            icon="lucide-chevron-right"
                            @click="toggle()"
                          />
                        </div>
                      </div>
                    </template>
                    <div class="flex flex-col gap-1.5 text-base">
                      <div
                        v-if="contact.email"
                        class="flex items-center gap-3 pb-1.5 pl-1 pt-4 text-ink-gray-8"
                      >
                        <Email2Icon class="h-4 w-4" />
                        {{ contact.email }}
                      </div>
                      <div
                        v-if="contact.mobile_no"
                        class="flex items-center gap-3 p-1 py-1.5 text-ink-gray-8"
                      >
                        <PhoneIcon class="h-4 w-4" />
                        {{ contact.mobile_no }}
                      </div>
                      <div
                        v-if="!contact.email && !contact.mobile_no"
                        class="flex items-center justify-center py-4 text-sm text-ink-gray-4"
                      >
                        {{ __('No Details Added') }}
                      </div>
                    </div>
                  </CollapsibleSection>
                </div>
                <div
                  v-if="i != dealContacts.data.length - 1"
                  class="mx-2 h-px border-t border-outline-elevation-2"
                />
              </div>
              <div
                v-else
                class="flex h-20 items-center justify-center text-base text-ink-gray-5"
              >
                {{ __('No Contacts Added') }}
              </div>
            </div>
          </template>
        </SidePanelLayout>
        <DealDataSidePanel
          v-if="activeTabName === 'Data'"
          :docname="dealId"
        />
      </div>
    </Resizer>
  </div>
  <ErrorPage
    v-else-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  />
  <OrganizationModal
    v-if="showOrganizationModal"
    v-model="showOrganizationModal"
    :data="_organization"
    :options="{
      redirect: false,
      afterInsert: (_doc) => updateField('organization', _doc.name),
    }"
  />
  <ContactModal
    v-if="showContactModal"
    v-model="showContactModal"
    :contact="_contact"
    :options="{
      redirect: false,
      afterInsert: (_doc) => addContact(_doc.name),
    }"
  />
  <FilesUploader
    v-model="showFilesUploader"
    doctype="CRM Deal"
    :docname="dealId"
    @after="
      () => {
        activities?.all_activities?.reload()
        changeTabTo('attachments')
      }
    "
  />
  <DeleteLinkedDocModal
    v-if="showDeleteLinkedDocModal"
    v-model="showDeleteLinkedDocModal"
    :doctype="'CRM Deal'"
    :docname="dealId"
    name="Deals"
  />
  <LostReasonModal
    v-if="showLostReasonModal"
    v-model="showLostReasonModal"
    doctype="CRM Deal"
    :document="document"
  />
</template>
<script setup>
import DeleteLinkedDocModal from '@/components/DeleteLinkedDocModal.vue'
import ErrorPage from '@/components/ErrorPage.vue'
import Icon from '@/components/Icon.vue'
import Resizer from '@/components/Resizer.vue'
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import PeopleIcon from '@/components/Icons/PeopleIcon.vue'
import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
import EventIcon from '@/components/Icons/EventIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import LinkIcon from '@/components/Icons/LinkIcon.vue'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import SuccessIcon from '@/components/Icons/SuccessIcon.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Activities from '@/components/Activities/Activities.vue'
import OrganizationModal from '@/components/Modals/OrganizationModal.vue'
import LostReasonModal from '@/components/Modals/LostReasonModal.vue'
import AssignTo from '@/components/AssignTo.vue'
import FilesUploader from '@/components/FilesUploader/FilesUploader.vue'
import ContactModal from '@/components/Modals/ContactModal.vue'
import Link from '@/components/Controls/Link.vue'
import CollapsibleSection from '@/components/CollapsibleSection.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import DealDataSidePanel from '@/components/DealDataSidePanel.vue'
import SLASection from '@/components/SLASection.vue'
import CustomActions from '@/components/CustomActions.vue'
import EnrichFromWebsite from '@/components/EnrichFromWebsite.vue'
import {
  openWebsite,
  setupCustomizations,
  copyToClipboard,
  isTranslatable,
} from '@/utils'
import { getView } from '@/utils/view'
import { getSettings } from '@/stores/settings'
import { globalStore } from '@/stores/global'
import { statusesStore } from '@/stores/statuses'
import { getMeta } from '@/stores/meta'
import { useDocument } from '@/data/document'
import { whatsappEnabled } from '@/composables/whatsapp'
import { callEnabled } from '@/composables/telephony'
import { useBroadcast } from '@/composables/useBroadcast'
import {
  createResource,
  Dropdown,
  Tooltip,
  Avatar,
  Tabs,
  Breadcrumbs,
  call,
  usePageMeta,
  toast,
} from 'frappe-ui'
import { useOnboarding } from 'frappe-ui/frappe'
import {
  ref,
  computed,
  h,
  onMounted,
  onBeforeUnmount,
  nextTick,
  watch,
} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useActiveTabManager } from '@/composables/useActiveTabManager'

const { on } = useBroadcast()
const { brand } = getSettings()
const { $dialog, $socket, makeCall } = globalStore()
const { statusOptions, getDealStatus } = statusesStore()
const { doctypeMeta } = getMeta('CRM Deal')

const { updateOnboardingStep, isOnboardingStepsCompleted } =
  useOnboarding('frappecrm')

const route = useRoute()
const router = useRouter()

function openOrganization() {
  if (doc.value?.organization)
    router.push({
      name: 'Organization',
      params: { organizationId: doc.value.organization },
    })
}

const props = defineProps({
  dealId: { type: String, required: true },
})

const errorTitle = ref('')
const errorMessage = ref('')
const showDeleteLinkedDocModal = ref(false)

const {
  triggerOnChange,
  triggerOnRender,
  assignees,
  permissions,
  document,
  scripts,
  error,
} = useDocument('CRM Deal', props.dealId)

const canDelete = computed(() => permissions.data?.permissions?.delete || false)

const doc = computed(() => document.doc || {})

watch(error, (err) => {
  if (err) {
    errorTitle.value = __(
      err.exc_type == 'DoesNotExistError'
        ? 'Document Not Found'
        : 'Error Occurred',
    )
    errorMessage.value = __(err.messages?.[0] || 'An Error Occurred')
  } else {
    errorTitle.value = ''
    errorMessage.value = ''
  }
})

watch(
  () => document.doc,
  async (_doc) => {
    if (scripts.data?.length) {
      let s = await setupCustomizations(scripts.data, {
        doc: _doc,
        $dialog,
        $socket,
        router,
        toast,
        updateField,
        createToast: toast.create,
        deleteDoc: deleteDeal,
        call,
      })
      document._actions = s.actions || []
      document._statuses = s.statuses || []
    }
  },
  { once: true },
)

const organizationDocument = ref(null)

watch(
  () => doc.value.organization,
  (org) => {
    if (org && !organizationDocument.value?.doc) {
      let { document: _organizationDocument } = useDocument(
        'CRM Organization',
        org,
      )
      organizationDocument.value = _organizationDocument
    }
  },
  { immediate: true },
)

const organization = computed(() => organizationDocument.value?.doc || {})

onMounted(async () => {
  $socket.on('crm_customer_created', () => {
    toast.success(__('Customer Created Successfully'))
  })
  if (document.doc) await triggerOnRender()
})

onBeforeUnmount(() => {
  $socket.off('crm_customer_created')
})

const reload = ref(false)
const showOrganizationModal = ref(false)
const showFilesUploader = ref(false)
const _organization = ref({})

const breadcrumbs = computed(() => {
  let items = [{ label: __('Deals'), route: { name: 'Deals' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'CRM Deal')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Deals',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: title.value,
    route: { name: 'Deal', params: { dealId: props.dealId } },
  })
  return items
})

const title = computed(() => {
  let t = doctypeMeta.value?.title_field || 'name'
  return doc.value?.[t] || props.dealId
})

const statuses = computed(() => {
  let customStatuses = document.statuses?.length
    ? document.statuses
    : document._statuses || []
  return statusOptions('deal', customStatuses, triggerStatusChange)
})

usePageMeta(() => {
  return {
    title: title.value,
    icon: brand.favicon,
  }
})

const tabs = computed(() => {
  // Primarios (visibles) primero; secundarios van al desplegable "Más".
  let tabOptions = [
    {
      name: 'Data',
      label: __('Data'),
      icon: DetailsIcon,
    },
    {
      name: 'Notes',
      label: __('Notes'),
      icon: NoteIcon,
    },
    {
      name: 'Attachments',
      label: __('Attachments'),
      icon: AttachmentIcon,
    },
    {
      name: 'Comments',
      label: __('Comments'),
      icon: CommentIcon,
    },
    {
      name: 'Interactions',
      label: __('Interacciones'),
      icon: PeopleIcon,
    },
    // --- secundarios (agrupados en "Más") ---
    {
      name: 'Tasks',
      label: __('Tasks'),
      icon: TaskIcon,
      secondary: true,
    },
    {
      name: 'Activity',
      label: __('Activity'),
      icon: ActivityIcon,
      secondary: true,
    },
    {
      name: 'Emails',
      label: __('Emails'),
      icon: EmailIcon,
      secondary: true,
    },
    {
      name: 'Events',
      label: __('Events'),
      icon: EventIcon,
      secondary: true,
    },
    {
      name: 'Calls',
      label: __('Calls'),
      icon: PhoneIcon,
      secondary: true,
    },
    {
      name: 'WhatsApp',
      label: __('WhatsApp'),
      icon: WhatsAppIcon,
      secondary: true,
      condition: () => whatsappEnabled.value,
    },
  ]
  return tabOptions.filter((tab) => (tab.condition ? tab.condition() : true))
})

// Opciones del desplegable "Más" (tabs secundarios)
const moreTabs = computed(() =>
  tabs.value
    .map((t, i) => ({ ...t, index: i }))
    .filter((t) => t.secondary)
    .map((t) => ({
      label: t.label,
      icon: h(t.icon, { class: 'h-4 w-4' }),
      onClick: () => (tabIndex.value = t.index),
    })),
)

// Si el tab activo es secundario, mostrar su nombre en el botón "Más"
const activeSecondaryLabel = computed(() => {
  const t = tabs.value[tabIndex.value]
  return t && t.secondary ? t.label : ''
})

const { tabIndex } = useActiveTabManager(tabs, 'lastDealTab')
const activeTabName = computed(() => tabs.value?.[tabIndex.value]?.name)

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  params: { doctype: 'CRM Deal' },
  transform: (data) => getParsedSections(data),
})

on('reload-deal-sections', () => sections.reload())

if (!sections.data) sections.fetch()

function getParsedSections(_sections) {
  _sections.forEach((section) => {
    if (section.name == 'contacts_section') return
    section.columns[0].fields.forEach((field) => {
      if (field.fieldname == 'organization') {
        field.create = (value, close) => {
          _organization.value.organization_name = value
          showOrganizationModal.value = true
          close()
        }
        field.link = (org) =>
          router.push({
            name: 'Organization',
            params: { organizationId: org },
          })
      }
    })
  })
  return _sections
}

const showContactModal = ref(false)
const _contact = ref({})

function contactOptions(contact) {
  let options = [
    {
      label: __('Remove'),
      icon: 'trash-2',
      onClick: () => removeContact(contact.name),
    },
  ]

  if (!contact.is_primary) {
    options.push({
      label: __('Set as Primary Contact'),
      icon: h(SuccessIcon, { class: 'h-4 w-4' }),
      onClick: () => setPrimaryContact(contact.name),
    })
  }

  const currentRole = contactRoles.value[contact.name]?.rol
  ;['Champion', 'Sponsor', 'Decision Maker'].forEach((rol) => {
    options.push({
      label: __(rol),
      icon: currentRole === rol ? 'check' : 'user',
      onClick: () =>
        setContactRole(contact.name, currentRole === rol ? '' : rol),
    })
  })

  return options
}

async function addContact(contact) {
  if (dealContacts.data?.find((c) => c.name === contact)) {
    toast.error(__('Contact Already Added'))
    return
  }

  let d = await call('crm.fcrm.doctype.crm_deal.crm_deal.add_contact', {
    deal: props.dealId,
    contact,
  })
  if (d) {
    dealContacts.reload()
    toast.success(__('Contact Added'))
  }
}

async function removeContact(contact) {
  let d = await call('crm.fcrm.doctype.crm_deal.crm_deal.remove_contact', {
    deal: props.dealId,
    contact,
  })
  if (d) {
    dealContacts.reload()
    toast.success(__('Contact Removed'))
  }
}

async function setPrimaryContact(contact) {
  let d = await call('crm.fcrm.doctype.crm_deal.crm_deal.set_primary_contact', {
    deal: props.dealId,
    contact,
  })
  if (d) {
    dealContacts.reload()
    toast.success(__('Primary Contact Set'))
  }
}

const contactRoles = ref({})

const dealContacts = createResource({
  url: 'crm.fcrm.doctype.crm_deal.api.get_deal_contacts',
  params: { name: props.dealId },
  cache: ['deal_contacts', props.dealId],
  transform: (data) => {
    data.forEach((contact) => {
      contact.opened = false
    })
    return data
  },
  onSuccess: () => loadContactRoles(),
})

if (!dealContacts.data) dealContacts.fetch()

async function loadContactRoles() {
  try {
    const rows = await call('frappe.client.get_list', {
      doctype: 'CRM Contacts',
      parent: 'CRM Deal',
      filters: { parenttype: 'CRM Deal', parent: props.dealId },
      fields: ['name', 'contact', 'custom_rol'],
      limit_page_length: 0,
    })
    const map = {}
    for (const r of rows) map[r.contact] = { rowName: r.name, rol: r.custom_rol }
    contactRoles.value = map
  } catch (e) {
    // ignore
  }
}

async function setContactRole(contact, rol) {
  try {
    let rowName = contactRoles.value[contact]?.rowName
    if (!rowName) {
      const rows = await call('frappe.client.get_list', {
        doctype: 'CRM Contacts',
        parent: 'CRM Deal',
        filters: { parenttype: 'CRM Deal', parent: props.dealId, contact },
        fields: ['name'],
        limit_page_length: 1,
      })
      rowName = rows?.[0]?.name
    }
    if (!rowName) {
      toast.error(__('No se encontró el contacto en la oportunidad'))
      return
    }
    await call('frappe.client.set_value', {
      doctype: 'CRM Contacts',
      name: rowName,
      fieldname: 'custom_rol',
      value: rol || null,
    })
    toast.success(__('Rol actualizado'))
    loadContactRoles()
  } catch (e) {
    toast.error(e.messages?.[0] || __('No se pudo actualizar el rol'))
  }
}

function triggerCall() {
  let primaryContact = dealContacts.data?.find((c) => c.is_primary)
  let mobile_no = primaryContact.mobile_no || null

  if (!primaryContact) {
    toast.error(__('No Primary Contact Set'))
    return
  }

  if (!mobile_no) {
    toast.error(__('No Mobile Number Set'))
    return
  }

  makeCall(mobile_no)
}

async function triggerStatusChange(value) {
  await triggerOnChange('status', value)
  setLostReason()
}

function updateField(name, value) {
  if (name == 'status' && !isOnboardingStepsCompleted.value) {
    updateOnboardingStep('change_deal_status')
  }

  value = Array.isArray(name) ? '' : value
  let oldValues = Array.isArray(name) ? {} : doc.value[name]

  if (Array.isArray(name)) {
    name.forEach((field) => (doc.value[field] = value))
  } else {
    doc.value[name] = value
  }

  document.save.submit(null, {
    onSuccess: () => (reload.value = true),
    onError: (err) => {
      if (Array.isArray(name)) {
        name.forEach((field) => (doc.value[field] = oldValues[field]))
      } else {
        doc.value[name] = oldValues
      }
      toast.error(err.messages?.[0] || __('Error updating field'))
    },
  })
}

function deleteDeal() {
  showDeleteLinkedDocModal.value = true
}

const activities = ref(null)

function openEmailBox() {
  let currentTab = tabs.value[tabIndex.value]
  if (!['Emails', 'Comments', 'Activities'].includes(currentTab.name)) {
    activities.value.changeTabTo('emails')
  }
  nextTick(() => (activities.value.emailBox.show = true))
}

function statusLabel(status) {
  if (isTranslatable('CRM Deal Status')) return __(status)
  return status
}

const showLostReasonModal = ref(false)

function setLostReason() {
  if (
    getDealStatus(document.doc.status).type !== 'Lost' ||
    (document.doc.lost_reason && document.doc.lost_reason !== 'Other') ||
    (document.doc.lost_reason === 'Other' && document.doc.lost_notes)
  ) {
    document.save.submit(null, {
      onSuccess: () => sections.reload(),
    })
    return
  }

  showLostReasonModal.value = true
}

function beforeStatusChange(data) {
  if (
    Object.hasOwn(data ?? {}, 'status') &&
    getDealStatus(data.status).type == 'Lost'
  ) {
    setLostReason()
  } else {
    document.save.submit(null, {
      onSuccess: () => reloadResources(data),
    })
  }
}

function onEnriched() {
  document.reload?.()
  sections.reload()
}

function reloadResources(data) {
  if (Object.hasOwn(data ?? {}, 'deal_owner')) {
    assignees.reload()
  }
  if (
    Object.hasOwn(data ?? {}, 'status') &&
    getDealStatus(data.status).type != 'Lost'
  ) {
    sections.reload()
  }
}
</script>
