<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Contacts" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="contactsListView?.customListActions"
        :actions="contactsListView.customListActions"
      />
      <select
        v-model="campanaFilter"
        class="h-8 rounded-lg border border-outline-gray-2 bg-surface-base px-2 text-sm text-ink-gray-8 focus:outline-none"
        @change="applyContactFilters"
      >
        <option value="">{{ __('Todas las campañas') }}</option>
        <option v-for="c in campanaOptions" :key="c" :value="c">{{ c }}</option>
      </select>
      <div class="relative">
        <button
          type="button"
          class="flex h-8 items-center gap-1.5 rounded-lg border border-outline-gray-2 bg-surface-base px-2.5 text-sm text-ink-gray-8 hover:border-outline-gray-3"
          @click="mlOpen = !mlOpen"
        >
          {{ __('Lista de Marketing') }}
          <span v-if="mlSelected.length" class="rounded-full bg-blue-100 px-1.5 text-xs font-semibold text-blue-700">{{ mlSelected.length }}</span>
          <span class="text-xs text-ink-gray-5">{{ mlOpen ? '▴' : '▾' }}</span>
        </button>
        <div v-if="mlOpen" class="fixed inset-0 z-40" @click="mlOpen = false" />
        <div
          v-if="mlOpen"
          class="absolute right-0 z-50 mt-1 w-64 rounded-lg border border-outline-gray-2 p-2 shadow-lg"
          style="background-color: var(--surface-modal, var(--surface-white, #ffffff))"
        >
          <input
            v-model="mlSearch"
            type="text"
            :placeholder="__('Buscar o crear...')"
            class="mb-1 w-full rounded border border-outline-gray-2 bg-surface-base px-2 py-1 text-sm text-ink-gray-8 focus:outline-none"
            @keydown.enter="createMl"
          />
          <button v-if="mlCanCreate" type="button" class="mb-1 w-full truncate rounded px-2 py-1 text-left text-xs text-blue-600 hover:bg-surface-gray-2" @click="createMl">
            ＋ {{ __('Crear') }} “{{ mlSearch.trim() }}”
          </button>
          <div class="max-h-56 overflow-y-auto">
            <label v-for="l in mlFilteredOptions" :key="l" class="flex cursor-pointer items-center gap-2 rounded px-2 py-1 text-sm text-ink-gray-7 hover:bg-surface-gray-2">
              <input type="checkbox" :checked="mlSelected.includes(l)" @change="toggleMl(l)" />
              <span class="truncate">{{ l }}</span>
            </label>
            <div v-if="!mlFilteredOptions.length" class="px-2 py-2 text-xs text-ink-gray-4">{{ __('Sin listas.') }}</div>
          </div>
          <div class="mt-2 flex justify-between border-t pt-2">
            <button type="button" class="text-xs text-ink-gray-6 hover:text-ink-gray-9" @click="clearMl">{{ __('Limpiar') }}</button>
            <button type="button" class="text-xs font-medium text-blue-600" @click="mlOpen = false">{{ __('Listo') }}</button>
          </div>
        </div>
      </div>
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="showContactModal = true"
      />
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="contacts"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Contact"
  />
  <ContactsListView
    v-if="contacts.data && rows.length"
    ref="contactsListView"
    v-model="contacts.data.page_length_count"
    v-model:list="contacts"
    :rows="rows"
    :columns="columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: contacts.data.row_count,
      totalCount: contacts.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <EmptyState
    v-else-if="contacts.data && !rows.length"
    name="Contacts"
    :icon="ContactsIcon"
  />
  <ContactModal
    v-if="showContactModal"
    v-model="showContactModal"
    :contact="{}"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import ContactModal from '@/components/Modals/ContactModal.vue'
import ContactsListView from '@/components/ListViews/ContactsListView.vue'
import EmptyState from '@/components/ListViews/EmptyState.vue'
import ViewControls from '@/components/ViewControls.vue'
import { getMeta } from '@/stores/meta'
import { organizationsStore } from '@/stores/organizations.js'
import { formatDate } from '@/utils'
import { timestampCell } from '@/composables/useTimelinePreferences'
import { ref, computed, onMounted } from 'vue'
import { call, toast } from 'frappe-ui'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('Contact')
const { getOrganization } = organizationsStore()

const showContactModal = ref(false)

const contactsListView = ref(null)

// contacts data is loaded in the ViewControls component
const contacts = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)
const campanaFilter = ref('')
const campanaOptions = ref([])
const mlOpen = ref(false)
const mlSearch = ref('')
const mlOptions = ref([])
const mlSelected = ref([])
const mlFilteredOptions = computed(() => {
  const q = mlSearch.value.trim().toLowerCase()
  return mlOptions.value.filter((o) => !q || o.toLowerCase().includes(q))
})
const mlCanCreate = computed(() => {
  const v = mlSearch.value.trim()
  return !!v && !mlOptions.value.some((o) => o.toLowerCase() === v.toLowerCase())
})
async function loadCampanas() {
  try {
    const d = await call('frappe.client.get_list', { doctype: 'CRM Campana', fields: ['name'], limit_page_length: 0, order_by: 'name asc' })
    campanaOptions.value = (d || []).map((x) => x.name)
  } catch (e) { /* ignore */ }
}
async function loadMl() {
  try {
    // Opciones tomadas de los valores realmente usados en el campo Select
    // "Lista de Marketing" (custom_lista_marketing) de los contactos.
    const d = await call('frappe.client.get_list', { doctype: 'Contact', fields: ['custom_lista_marketing'], filters: { custom_lista_marketing: ['is', 'set'] }, group_by: 'custom_lista_marketing', order_by: 'custom_lista_marketing asc', limit_page_length: 0 })
    mlOptions.value = (d || []).map((x) => x.custom_lista_marketing).filter(Boolean)
  } catch (e) { /* ignore */ }
}
async function createMl() {
  const v = mlSearch.value.trim()
  if (!v || !mlCanCreate.value) return
  try {
    await call('frappe.client.insert', { doc: { doctype: 'CRM Lista Marketing', lista: v } })
    mlOptions.value.push(v)
    mlSearch.value = ''
    toggleMl(v)
  } catch (e) { toast.error(__('No se pudo crear la lista')) }
}
function toggleMl(l) {
  const i = mlSelected.value.indexOf(l)
  if (i >= 0) mlSelected.value.splice(i, 1)
  else mlSelected.value.push(l)
  applyContactFilters()
}
function clearMl() { mlSelected.value = []; applyContactFilters() }
async function applyContactFilters() {
  const f = { ...(contacts.value?.params?.filters || {}) }
  const sets = []
  if (campanaFilter.value) {
    try {
      const p = await call('frappe.client.get_list', { doctype: 'Contact', filters: [['CRM Contact Campana', 'campana', '=', campanaFilter.value]], fields: ['name'], limit_page_length: 0 })
      sets.push(new Set((p || []).map((x) => x.name)))
    } catch (e) { sets.push(new Set()) }
  }
  if (mlSelected.value.length) {
    try {
      const p = await call('frappe.client.get_list', { doctype: 'Contact', filters: [['custom_lista_marketing', 'in', mlSelected.value]], fields: ['name'], limit_page_length: 0 })
      sets.push(new Set((p || []).map((x) => x.name)))
    } catch (e) { sets.push(new Set()) }
  }
  if (sets.length) {
    let names = [...sets[0]]
    for (let i = 1; i < sets.length; i++) names = names.filter((n) => sets[i].has(n))
    f.name = ['in', names.length ? names : ['__none__']]
  } else {
    delete f.name
  }
  viewControls.value?.updateFilter(f)
}
onMounted(loadCampanas)
onMounted(loadMl)

const rows = computed(() => {
  if (
    !contacts.value?.data?.data ||
    !['list', 'group_by'].includes(contacts.value.data.view_type)
  )
    return []
  return contacts.value?.data.data.map((contact) => {
    let _rows = {}
    contacts.value?.data.rows.forEach((row) => {
      _rows[row] = contact[row]

      let fieldType = contacts.value?.data.columns?.find(
        (col) => (col.key || col.value) == row,
      )?.type

      if (
        fieldType &&
        ['Date', 'Datetime'].includes(fieldType) &&
        !['modified', 'creation'].includes(row)
      ) {
        _rows[row] = formatDate(contact[row], '', true, fieldType == 'Datetime')
      }

      if (fieldType && fieldType == 'Currency') {
        _rows[row] = getFormattedCurrency(row, contact)
      }

      if (fieldType && fieldType == 'Float') {
        _rows[row] = getFormattedFloat(row, contact)
      }

      if (fieldType && fieldType == 'Percent') {
        _rows[row] = getFormattedPercent(row, contact)
      }

      if (row == 'full_name') {
        _rows[row] = {
          label: contact.full_name,
          image_label: contact.full_name,
          image: contact.image,
        }
      } else if (row == 'company_name') {
        _rows[row] = {
          label: contact.company_name,
          logo: getOrganization(contact.company_name)?.organization_logo,
        }
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = timestampCell(contact[row])
      }
    })
    return _rows
  })
})

const columns = computed(() => {
  let _columns = contacts.value?.data?.columns || []

  // Set align right for last column
  if (_columns.length) {
    _columns = _columns.map((col, index) => {
      if (index === _columns.length - 1) {
        return { ...col, align: 'right' }
      }
      return col
    })
  }

  return _columns
})
</script>
