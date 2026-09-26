<template>
  <!-- The notifications panel is absolutely positioned at `left: 100%`, so it
       needs a positioning context that is not the Sidebar itself (Sidebar sets
       overflow-x-hidden, which would clip the panel away).

       It also paints the sidebar surface: Sidebar's own `bg-surface-sidebar` is
       transparent in dark mode, and nothing behind it sets a background, so the
       column falls through to the white page canvas. The token cannot be
       overridden on the Sidebar element itself — `bg-surface-sidebar` is emitted
       after `bg-surface-gray-1` in the utilities layer and would win. -->
  <div class="relative flex h-full bg-surface-gray-1">
    <Sidebar
      v-model:collapsed="isSidebarCollapsed"
      :disable-collapse="mobile"
      :width="mobile ? '260px' : undefined"
      class="border-r border-outline-gray-1"
    >
      <div class="flex h-full flex-col p-2">
        <UserDropdown :isCollapsed="isCollapsed" />

        <!-- overflow-y-auto forces overflow-x to clip too, which would slice the
             active row's shadow. Widen the scroll box to the sidebar edges and
             pad the content back in so the shadow has room. -->
        <div class="-mx-2 mt-2 flex flex-1 flex-col gap-1 overflow-y-auto px-2">
          <SidebarItem :label="__('Buscar')" @click="showSearch = true">
            <template #prefix>
              <SearchIcon class="size-4 text-ink-gray-7" />
            </template>
          </SidebarItem>
          <SidebarItem
            id="notifications-btn"
            :label="__('Notifications')"
            :to="mobile ? { name: 'Notifications' } : undefined"
            :active="mobile && activeItem === 'Notifications'"
            @click="onNotificationsClick"
          >
            <template #prefix>
              <span class="relative grid size-4 place-items-center">
                <NotificationsIcon class="size-4 text-ink-gray-7" />
                <span
                  v-if="isCollapsed && unreadNotificationsCount"
                  class="absolute -right-1 -top-1 size-1.5 rounded-full bg-surface-gray-9 ring-1 ring-[var(--surface-gray-1)]"
                />
              </span>
            </template>
            <template #suffix>
              <Badge
                v-if="unreadNotificationsCount"
                class="mr-2"
                :label="unreadNotificationsCount"
                variant="subtle"
              />
            </template>
          </SidebarItem>

          <!-- Separador entre Notificaciones y las secciones (Seguimiento...) -->
          <div class="mx-2 my-1.5 border-t border-outline-gray-2" />

          <CollapsibleSection
            v-for="section in allViews"
            :key="section.name"
            :label="section.name"
            :hideLabel="section.hideLabel"
            :opened="section.opened"
          >
            <template #header="{ opened, hide, toggle }">
              <SidebarLabel
                v-if="!hide"
                divider
                class="mb-1 mt-4 select-none"
                :class="!isCollapsed && 'cursor-pointer'"
                @click="toggle()"
              >
                <span class="flex items-center gap-1.5">
                  <span
                    class="lucide-chevron-right -ml-0.5 size-4 shrink-0 text-ink-gray-9 transition-transform duration-300 ease-in-out"
                    :class="{ 'rotate-90': opened }"
                    aria-hidden="true"
                  />
                  <span class="truncate">{{ __(section.name) }}</span>
                </span>
              </SidebarLabel>
            </template>
            <nav class="flex flex-col gap-1">
              <template v-for="link in section.views" :key="link.key">
                <div
                  v-if="link.separator"
                  class="mx-2 my-1.5 border-t border-outline-gray-2"
                />
                <SidebarItem
                  v-else
                  :to="link.to"
                  :label="__(link.label)"
                  :active="activeItem === link.key"
                  @click="selectItem($event, link)"
                >
                  <template #prefix>
                    <Icon :icon="link.icon" class="size-4 text-ink-gray-7" />
                  </template>
                  <Tooltip
                    :text="__(link.label)"
                    placement="right"
                    :hoverDelay="1.5"
                    :disabled="isCollapsed"
                  >
                    <span class="truncate text-sm">{{ __(link.label) }}</span>
                  </Tooltip>
                </SidebarItem>
              </template>
            </nav>
          </CollapsibleSection>
        </div>

        <div v-if="!mobile" class="mt-auto flex flex-col gap-1 pt-2">
          <div class="mb-1 flex flex-col gap-2">
            <SignupBanner
              v-if="isDemoSite"
              :isSidebarCollapsed="isCollapsed"
              :afterSignup="() => capture('signup_from_demo_site')"
            />
            <TrialBanner
              v-if="isFCSite"
              :isSidebarCollapsed="isCollapsed"
              :afterUpgrade="() => capture('upgrade_plan_from_trial_banner')"
            />
            <GettingStartedBanner
              v-if="!isOnboardingStepsCompleted"
              :isSidebarCollapsed="isCollapsed"
            />
          </div>
          <SidebarItem
            v-if="isManager() && isDemoDataCreated"
            :label="__('Clear Demo Data')"
            class="!text-ink-red-6 hover:!bg-surface-red-2"
            @click="() => clearDemoData()"
          >
            <template #prefix>
              <BrushCleaningIcon class="size-4" />
            </template>
          </SidebarItem>
          <SidebarItem
            v-if="isOnboardingStepsCompleted"
            :label="__('Help')"
            @click="toggleHelpModal"
          >
            <template #prefix>
              <HelpIcon class="size-4 text-ink-gray-7" />
            </template>
          </SidebarItem>
          <SidebarItem
            :label="isCollapsed ? __('Expand') : __('Collapse')"
            @click="isSidebarCollapsed = !isSidebarCollapsed"
          >
            <template #prefix>
              <CollapseSidebar
                class="size-4 text-ink-gray-7 duration-300 ease-in-out"
                :class="{ '[transform:rotateY(180deg)]': isCollapsed }"
              />
            </template>
          </SidebarItem>
          <SidebarItem :label="__('Sugerencias')" @click="showSugModal = true">
            <template #prefix>
              <LucideLightbulb class="size-4 text-ink-gray-7" />
            </template>
          </SidebarItem>
        </div>
      </div>
    </Sidebar>
    <Notifications v-if="!mobile" />
    <Dialog v-model="showSugModal" :options="{ size: 'lg' }">
      <template #body>
        <div class="p-4">
          <div class="mb-3 text-base font-semibold text-ink-gray-8">
            {{ __('Sugerencias') }}
          </div>
          <select
            v-model="sugPagina"
            class="mb-2 w-full rounded-lg border border-outline-gray-2 bg-surface-base px-2 py-1.5 text-sm text-ink-gray-8 focus:outline-none"
          >
            <option value="">{{ __('Página relacionada (opcional)') }}</option>
            <option v-for="p in pageOptions" :key="p" :value="p">{{ p }}</option>
          </select>
          <textarea
            v-model="sugText"
            rows="4"
            :placeholder="__('Contanos tu sugerencia o mejora...')"
            class="w-full rounded-lg border border-outline-gray-2 bg-surface-base px-2 py-1.5 text-sm text-ink-gray-8 focus:outline-none"
          />
          <div class="mt-3 flex justify-end gap-2">
            <Button @click="showSugModal = false">{{ __('Cancelar') }}</Button>
            <Button
              variant="solid"
              :loading="savingSug"
              :disabled="!sugText.trim()"
              @click="submitSug"
            >
              {{ __('Enviar') }}
            </Button>
          </div>
        </div>
      </template>
    </Dialog>
  </div>

  <template v-if="!mobile">
    <Settings />
    <GlobalSearch v-model="showSearch" />
    <HelpModal
      v-if="showHelpModal"
      v-model="showHelpModal"
      v-model:articles="articles"
      :logo="CRMLogo"
      :afterSkip="(step) => capture('onboarding_step_skipped_' + step)"
      :afterSkipAll="() => capture('onboarding_steps_skipped')"
      :afterReset="(step) => capture('onboarding_step_reset_' + step)"
      :afterResetAll="() => capture('onboarding_steps_reset')"
      docsLink="https://docs.frappe.io/crm"
    />
    <IntermediateStepModal
      v-model="showIntermediateModal"
      :currentStep="currentStep"
    />
  </template>
</template>

<script setup>
import BrushCleaningIcon from '~icons/lucide/brush-cleaning'
import LucideLightbulb from '~icons/lucide/lightbulb'
import LucideLayoutDashboard from '~icons/lucide/layout-dashboard'
import LucideBell from '~icons/lucide/bell'
import LucidePackage from '~icons/lucide/package'
import LucideAward from '~icons/lucide/award'
import LucideMegaphone from '~icons/lucide/megaphone'
import LucideChartPie from '~icons/lucide/chart-pie'
import LucideCalendarHeart from '~icons/lucide/calendar-heart'
import LucidePlane from '~icons/lucide/plane'
import LucideFilter from '~icons/lucide/filter'
import LucideHandshake from '~icons/lucide/handshake'
import LucideWorkflow from '~icons/lucide/workflow'
import LucideReceipt from '~icons/lucide/receipt'
import LucideTruck from '~icons/lucide/truck'
import LucideFileText from '~icons/lucide/file-text'
import LucideBanknote from '~icons/lucide/banknote'
import LucideCreditCard from '~icons/lucide/credit-card'
import LucideLandmark from '~icons/lucide/landmark'
import LucideLifeBuoy from '~icons/lucide/life-buoy'
import LucideGraduationCap from '~icons/lucide/graduation-cap'
import LucideCalendarClock from '~icons/lucide/calendar-clock'
import LucideChartColumn from '~icons/lucide/chart-column'
import LucideBuilding2 from '~icons/lucide/building-2'
import LucideNetwork from '~icons/lucide/network'
import LucideMap from '~icons/lucide/map'
import LucideListChecks from '~icons/lucide/list-checks'
import SoftwareIcon from '@/components/Icons/SoftwareIcon.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import GlobalSearch from '@/components/GlobalSearch.vue'
import SearchIcon from '@/components/Icons/SearchIcon.vue'
import CRMLogo from '@/components/Icons/CRMLogo.vue'
import InviteIcon from '@/components/Icons/InviteIcon.vue'
import ConvertIcon from '@/components/Icons/ConvertIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import StepsIcon from '@/components/Icons/StepsIcon.vue'
import CollapsibleSection from '@/components/CollapsibleSection.vue'
import Icon from '@/components/Icon.vue'
import PinIcon from '@/components/Icons/PinIcon.vue'
import UserDropdown from '@/components/UserDropdown.vue'
import SquareAsterisk from '@/components/Icons/SquareAsterisk.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import CalendarIcon from '@/components/Icons/CalendarIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import CollapseSidebar from '@/components/Icons/CollapseSidebar.vue'
import NotificationsIcon from '@/components/Icons/NotificationsIcon.vue'
import HelpIcon from '@/components/Icons/HelpIcon.vue'
import Notifications from '@/components/Notifications.vue'
import Settings from '@/components/Settings/Settings.vue'
import { viewsStore } from '@/stores/views'
import {
  unreadNotificationsCount,
  notificationsStore,
} from '@/stores/notifications'
import { usersStore } from '@/stores/users'
import { sessionStore } from '@/stores/session'
import {
  showSettings,
  activeSettingsPage,
  mobileSidebarOpened,
} from '@/composables/settings'
import { showChangePasswordModal } from '@/composables/modals'
import { useBroadcast } from '@/composables/useBroadcast.js'
import { call, toast, Dialog, Button, Sidebar, SidebarItem, SidebarLabel, Tooltip } from 'frappe-ui'
import {
  SignupBanner,
  TrialBanner,
  HelpModal,
  GettingStartedBanner,
  useOnboarding,
  showHelpModal,
  minimize,
  IntermediateStepModal,
  useTelemetry,
} from 'frappe-ui/frappe'
import router from '@/router'
import { useStorage } from '@vueuse/core'
import { useDemoData } from '@/composables/demoData'
import { ref, reactive, computed, markRaw, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  mobile: { type: Boolean, default: false },
})

const route = useRoute()

const { getPinnedViews, getPublicViews } = viewsStore()
const { toggle: toggleNotificationPanel } = notificationsStore()
const { capture } = useTelemetry()
const { clearDemoData, isDemoDataCreated } = useDemoData()
const { send } = useBroadcast()

const showSearch = ref(false)
function onSearchKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
    e.preventDefault()
    showSearch.value = true
  }
}
onMounted(() => window.addEventListener('keydown', onSearchKeydown))

const isSidebarCollapsed = useStorage('isSidebarCollapsed', false)

// The mobile drawer pins the sidebar open, so it is never visually collapsed
// even when the stored rail state says otherwise.
const isCollapsed = computed(() => isSidebarCollapsed.value && !props.mobile)

const isFCSite = ref(window.is_fc_site)
const isDemoSite = ref(window.is_demo_site)

const links = [
  // Grupo 1: seguimiento / cierres / ventas
  {
    label: 'Seguimiento',
    icon: LucideListChecks,
    to: 'Seguimiento',
  },
  {
    label: 'Cierres (Calendario)',
    icon: LucideCalendarClock,
    to: 'CalendarioCierres',
  },
  { separator: true },
  // Grupo 2: pipeline
  {
    label: 'Deals',
    icon: DealsIcon,
    to: 'Deals',
  },
  {
    label: 'Leads',
    icon: LeadsIcon,
    to: 'Leads',
  },
  { separator: true },
  // Grupo 3: cuentas
  {
    label: 'Organizations',
    icon: OrganizationsIcon,
    to: 'Organizations',
  },
  {
    label: 'Contacts',
    icon: ContactsIcon,
    to: 'Contacts',
  },
  {
    label: 'Ecosistemas Productivos',
    icon: LucideNetwork,
    to: 'Ecosistema',
  },
  {
    label: 'Oferta Comercial',
    icon: LucidePackage,
    to: 'OfertaComercial',
  },
]

const moreLinks = [
  {
    label: 'Alertas',
    icon: LucideBell,
    to: 'Alertas',
  },
  {
    label: 'Sugerencias',
    icon: LucideLightbulb,
    to: 'SugerenciasAdmin',
    condition: () => isAdmin(),
  },
  {
    label: 'Software',
    icon: SoftwareIcon,
    to: 'Software',
  },
  {
    label: 'Partners',
    icon: LucideHandshake,
    to: 'Partners',
  },
  {
    label: 'Procesos / Tecnologías',
    icon: LucideWorkflow,
    to: 'ProcesosTecnologias',
  },
  {
    label: 'Pipeline',
    icon: LucideFilter,
    to: 'Pipeline',
  },
  {
    label: 'Tasks',
    icon: TaskIcon,
    to: 'Tasks',
  },
  {
    label: 'Helpdesk',
    icon: LucideLifeBuoy,
    href: '/helpdesk',
  },
]

function mapLink(link) {
  if (link.href) {
    return {
      label: link.label,
      icon: link.icon,
      key: 'ext-' + link.href,
      href: link.href,
    }
  }
  return {
    label: link.label,
    icon: link.icon,
    key: link.to,
    to: { name: link.to },
  }
}

function filterLinks(arr) {
  let out = arr
    .filter((link) => (link.condition ? link.condition() : true))
    .map((link) => (link.separator ? { separator: true } : mapLink(link)))
  // Limpia separadores sobrantes (al inicio, al final o consecutivos)
  const cleaned = []
  for (const it of out) {
    if (it.separator && (!cleaned.length || cleaned[cleaned.length - 1].separator))
      continue
    cleaned.push(it)
  }
  while (cleaned.length && cleaned[cleaned.length - 1].separator) cleaned.pop()
  let n = 0
  for (const it of cleaned) if (it.separator) it.key = 'sep-' + n++
  return cleaned
}

const ventasLinks = [
  {
    label: 'Ventas',
    icon: LucideReceipt,
    to: 'Ventas',
  },
  {
    label: 'Entregas',
    icon: LucideTruck,
    to: 'VentasEntregas',
  },
  {
    label: 'Facturas',
    icon: LucideFileText,
    to: 'VentasFacturas',
  },
  {
    label: 'Cobros',
    icon: LucideBanknote,
    to: 'VentasCobros',
  },
  {
    label: 'Pagos Prov',
    icon: LucideCreditCard,
    to: 'VentasPagosProv',
  },
  {
    label: 'Impuestos',
    icon: LucideLandmark,
    to: 'VentasImpuestos',
  },
]

const marketingLinks = [
  {
    label: 'Eventos',
    icon: LucideCalendarHeart,
    to: 'MarketingEventos',
  },
  {
    label: 'Planificación de Viajes',
    icon: LucidePlane,
    to: 'PlanificacionViajes',
  },
  {
    label: 'Campañas BDR',
    icon: LucideMegaphone,
    to: 'CampanasBDR',
  },
  {
    label: 'Casos de Referencia',
    icon: LucideAward,
    to: 'CasosReferencia',
  },
]

const planLinks = [
  {
    label: 'Planificación de Ventas',
    icon: LucideBanknote,
    to: 'PlanificacionVentas',
    condition: () => isAdmin(),
  },
  {
    label: 'Roadmaps',
    icon: LucideMap,
    to: 'Roadmaps',
    condition: () => isAdmin(),
  },
]

// Dashboards (solo admins): Ventas por Mes + Dashboards
const dashboardsLinks = [
  {
    label: 'Ventas por Mes',
    icon: LucideChartColumn,
    to: 'VentasPorMes',
    condition: () => isAdmin() && !props.mobile,
  },
  {
    label: 'Dashboards',
    icon: LucideLayoutDashboard,
    to: 'Dashboard',
    condition: () => isAdmin() && !props.mobile,
  },
]

// Marketing solo visible para admins y para la usuaria de marketing (Rosa de los Santos)
const MARKETING_USER = 'rosadelossantos@solaeringenieria.com'
function canSeeMarketing() {
  return isAdmin() || user === MARKETING_USER
}

const allViews = computed(() => {
  let _views = [
    {
      name: 'All Views',
      hideLabel: true,
      opened: true,
      views: filterLinks(links),
    },
    {
      name: 'Más',
      opened: false,
      views: filterLinks(moreLinks),
    },
  ]
  if (canSeeMarketing()) {
    _views.splice(1, 0, {
      name: 'Marketing',
      opened: false,
      views: filterLinks(marketingLinks),
    })
  }
  // Plan (incluye Roadmaps): solo admins
  const _planViews = isAdmin() ? filterLinks(planLinks) : []
  if (_planViews.length) {
    _views.splice(1, 0, { name: 'Plan', opened: true, views: _planViews })
  }
  // Dashboards: solo admins
  const _dashViews = isAdmin() ? filterLinks(dashboardsLinks) : []
  if (_dashViews.length) {
    _views.splice(1, 0, { name: 'Dashboards', opened: false, views: _dashViews })
  }
  if (getPublicViews().length) {
    _views.push({
      name: 'Public Views',
      opened: true,
      views: parseView(getPublicViews()),
    })
  }

  if (getPinnedViews().length) {
    _views.push({
      name: 'Pinned Views',
      opened: true,
      views: parseView(getPinnedViews()),
    })
  }
  return _views
})

function parseView(views) {
  return views.map((view) => {
    return {
      label: view.label,
      icon: getIcon(view.route_name, view.icon),
      key: view.name,
      to: {
        name: view.route_name,
        params: { viewType: view.type || 'list' },
        query: { view: view.name },
      },
    }
  })
}

function getIcon(routeName, icon) {
  if (icon) return icon

  switch (routeName) {
    case 'Leads':
      return LeadsIcon
    case 'Deals':
      return DealsIcon
    case 'Contacts':
      return ContactsIcon
    case 'Organizations':
      return OrganizationsIcon
    case 'Notes':
      return NoteIcon
    case 'Call Logs':
      return PhoneIcon
    default:
      return PinIcon
  }
}

// A saved view's key is its name; a plain nav item's key is its route name.
function currentRouteKey() {
  return route.query.view || route.name
}

// Set the highlight on click rather than waiting for the route, since route
// components are lazily imported and the first visit waits on a chunk fetch.
// Modified clicks open a new tab without navigating this one, so they must not
// move the highlight here.
const activeItem = ref(currentRouteKey())

function selectItem(event, link) {
  if (
    event.metaKey ||
    event.ctrlKey ||
    event.shiftKey ||
    event.altKey ||
    event.button === 1
  ) {
    return
  }
  if (link.href) {
    window.open(link.href, '_blank')
    if (props.mobile) {
      mobileSidebarOpened.value = false
    }
    return
  }
  activeItem.value = link.key
  // Selecting the row for the route already open leaves the URL unchanged, so
  // the drawer's navigation watcher never fires. Close it here too.
  if (props.mobile) {
    mobileSidebarOpened.value = false
  }
}

watch(
  () => [route.name, route.query.view],
  () => (activeItem.value = currentRouteKey()),
)

function onNotificationsClick(event) {
  if (props.mobile) {
    selectItem(event, 'Notifications')
  } else {
    toggleNotificationPanel()
  }
}

const showSugModal = ref(false)
const sugText = ref('')
const sugPagina = ref('')
const savingSug = ref(false)
const pageOptions = computed(() => {
  const all = [...links, ...marketingLinks, ...moreLinks, ...planLinks]
  return [...new Set(all.map((l) => l.label).filter(Boolean))]
})
async function submitSug() {
  if (!sugText.value.trim()) return
  savingSug.value = true
  try {
    await call('frappe.client.insert', {
      doc: {
        doctype: 'CRM Sugerencia',
        mensaje: sugText.value,
        pagina: sugPagina.value || window.location?.pathname || '',
      },
    })
    sugText.value = ''
    sugPagina.value = ''
    showSugModal.value = false
    toast.success(__('¡Gracias por tu sugerencia!'))
  } catch (e) {
    toast.error(__('No se pudo enviar la sugerencia'))
  } finally {
    savingSug.value = false
  }
}

function toggleHelpModal() {
  showHelpModal.value = minimize.value ? true : !showHelpModal.value
  minimize.value = !showHelpModal.value
}

// onboarding
const { user } = sessionStore()
const { users, isManager, isAdmin } = usersStore()
const { isOnboardingStepsCompleted, setUp } = useOnboarding('frappecrm')

async function getFirstLead() {
  let firstLead = localStorage.getItem('firstLead' + user)
  if (firstLead) return firstLead
  return await call('crm.api.onboarding.get_first_lead')
}

async function getFirstDeal() {
  let firstDeal = localStorage.getItem('firstDeal' + user)
  if (firstDeal) return firstDeal
  return await call('crm.api.onboarding.get_first_deal')
}

const showIntermediateModal = ref(false)
const currentStep = ref({})

const steps = reactive([
  {
    name: 'setup_your_password',
    title: __('Setup your password'),
    icon: markRaw(SquareAsterisk),
    completed: false,
    onClick: () => {
      minimize.value = true
      showChangePasswordModal.value = true
      capture('onboarding_step_clicked_setup_password')
    },
  },
  {
    name: 'create_first_lead',
    title: __('Create your first lead'),
    icon: markRaw(LeadsIcon),
    completed: false,
    onClick: () => {
      minimize.value = true
      router.push({ name: 'Leads' })
      send('trigger_lead_create', true)
      capture('onboarding_step_clicked_create_first_lead')
    },
  },
  {
    name: 'invite_your_team',
    title: __('Invite your team'),
    icon: markRaw(InviteIcon),
    completed: false,
    onClick: () => {
      minimize.value = true
      showSettings.value = true
      activeSettingsPage.value = 'Invite User'
      capture('onboarding_step_clicked_invite_your_team')
    },
    condition: () => isManager(),
  },
  {
    name: 'convert_lead_to_deal',
    title: __('Convert lead to deal'),
    icon: markRaw(ConvertIcon),
    completed: false,
    dependsOn: 'create_first_lead',
    onClick: async () => {
      minimize.value = true
      capture('onboarding_step_clicked_convert_lead_to_deal')
      currentStep.value = {
        title: __('Convert lead to deal'),
        buttonLabel: __('Convert'),
        videoURL: '/assets/crm/videos/convertToDeal.mov',
        onClick: async () => {
          showIntermediateModal.value = false
          currentStep.value = {}

          let lead = await getFirstLead()
          if (lead) {
            router.push({ name: 'Lead', params: { leadId: lead } })
          } else {
            router.push({ name: 'Leads' })
          }
        },
      }
      showIntermediateModal.value = true
    },
  },
  {
    name: 'create_first_task',
    title: __('Create your first task'),
    icon: markRaw(TaskIcon),
    completed: false,
    onClick: async () => {
      minimize.value = true
      let deal = await getFirstDeal()
      capture('onboarding_step_clicked_create_first_task')

      if (deal) {
        router.push({
          name: 'Deal',
          params: { dealId: deal },
          hash: '#tasks',
        })
      } else {
        router.push({ name: 'Tasks' })
      }
    },
  },
  {
    name: 'create_first_note',
    title: __('Create your first note'),
    icon: markRaw(NoteIcon),
    completed: false,
    onClick: async () => {
      minimize.value = true
      let deal = await getFirstDeal()
      capture('onboarding_step_clicked_create_first_note')

      if (deal) {
        router.push({
          name: 'Deal',
          params: { dealId: deal },
          hash: '#notes',
        })
      } else {
        router.push({ name: 'Notes' })
      }
    },
  },
  {
    name: 'add_first_comment',
    title: __('Add your first comment'),
    icon: markRaw(CommentIcon),
    completed: false,
    dependsOn: 'create_first_lead',
    onClick: async () => {
      minimize.value = true
      let deal = await getFirstDeal()
      capture('onboarding_step_clicked_add_first_comment')

      if (deal) {
        router.push({
          name: 'Deal',
          params: { dealId: deal },
          hash: '#comments',
        })
      } else {
        router.push({ name: 'Leads' })
      }
    },
  },
  {
    name: 'send_first_email',
    title: __('Send email'),
    icon: markRaw(EmailIcon),
    completed: false,
    dependsOn: 'create_first_lead',
    onClick: async () => {
      minimize.value = true
      let deal = await getFirstDeal()
      capture('onboarding_step_clicked_send_first_email')

      if (deal) {
        router.push({
          name: 'Deal',
          params: { dealId: deal },
          hash: '#emails',
        })
      } else {
        router.push({ name: 'Leads' })
      }
    },
  },
  {
    name: 'change_deal_status',
    title: __('Change deal status'),
    icon: markRaw(StepsIcon),
    completed: false,
    dependsOn: 'convert_lead_to_deal',
    onClick: async () => {
      minimize.value = true
      capture('onboarding_step_clicked_change_deal_status')

      currentStep.value = {
        title: __('Change deal status'),
        buttonLabel: __('Change'),
        videoURL: '/assets/crm/videos/changeDealStatus.mov',
        onClick: async () => {
          showIntermediateModal.value = false
          currentStep.value = {}

          let deal = await getFirstDeal()
          if (deal) {
            router.push({
              name: 'Deal',
              params: { dealId: deal },
              hash: '#activity',
            })
          } else {
            router.push({ name: 'Leads' })
          }
        },
      }
      showIntermediateModal.value = true
    },
  },
])

onMounted(async () => {
  if (props.mobile) return

  await users.promise

  const filteredSteps = steps.filter((step) => {
    if (step.condition) {
      return step.condition()
    }
    return true
  })

  setUp(filteredSteps)
})

// help center
const articles = ref([
  {
    title: __('Introduction'),
    opened: false,
    subArticles: [
      { name: 'introduction', title: __('Introduction') },
      { name: 'setting-up', title: __('Setting Up') },
    ],
  },
  {
    title: __('Settings'),
    opened: false,
    subArticles: [
      { name: 'profile', title: __('Profile') },
      { name: 'custom-branding', title: __('Custom Branding') },
      { name: 'home-actions', title: __('Home Actions') },
      { name: 'invite-users', title: __('Invite Users') },
    ],
  },
  {
    title: __('Masters'),
    opened: false,
    subArticles: [
      { name: 'lead', title: __('Lead') },
      { name: 'deal', title: __('Deal') },
      { name: 'contact', title: __('Contact') },
      { name: 'organization', title: __('Organization') },
      { name: 'note', title: __('Note') },
      { name: 'task', title: __('Task') },
      { name: 'call-log', title: __('Call Log') },
      { name: 'email-template', title: __('Email Template') },
    ],
  },
  {
    title: __('Capturing Leads'),
    opened: false,
    subArticles: [{ name: 'web-form', title: __('Web Form') }],
  },
  {
    title: __('Views'),
    opened: false,
    subArticles: [
      { name: 'view', title: __('Saved View') },
      { name: 'public-view', title: __('Public View') },
      { name: 'pinned-view', title: __('Pinned View') },
    ],
  },
  {
    title: __('Other Features'),
    opened: false,
    subArticles: [
      { name: 'email-communication', title: __('Email Communication') },
      { name: 'comment', title: __('Comment') },
      { name: 'data', title: __('Data') },
      { name: 'service-level-agreement', title: __('Service Level Agreement') },
      { name: 'assignment-rule', title: __('Assignment Rule') },
      { name: 'notification', title: __('Notification') },
    ],
  },
  {
    title: __('Customization'),
    opened: false,
    subArticles: [
      { name: 'custom-fields', title: __('Custom Fields') },
      { name: 'custom-actions', title: __('Custom Actions') },
      { name: 'custom-statuses', title: __('Custom Statuses') },
      { name: 'custom-list-actions', title: __('Custom List Actions') },
      { name: 'quick-entry-layout', title: __('Quick Entry Layout') },
    ],
  },
  {
    title: __('Integration'),
    opened: false,
    subArticles: [
      { name: 'twilio', title: __('Twilio') },
      { name: 'exotel', title: __('Exotel') },
      { name: 'whatsapp', title: __('WhatsApp') },
      { name: 'erpnext', title: __('ERPNext') },
    ],
  },
  {
    title: __('Frappe CRM mobile'),
    opened: false,
    subArticles: [
      { name: 'mobile-app-installation', title: __('Mobile App Installation') },
    ],
  },
])
</script>
