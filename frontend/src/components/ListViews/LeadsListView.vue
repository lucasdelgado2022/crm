<template>
  <ListView
    :class="$attrs.class"
    :columns="columns"
    :rows="rows"
    :options="{
      getRowRoute: (row) => ({
        name: 'Lead',
        params: { leadId: row.name },
        query: { view: route.query.view, viewType: route.params.viewType },
      }),
      selectable: options.selectable,
      showTooltip: options.showTooltip,
      resizeColumn: options.resizeColumn,
    }"
    row-key="name"
    @update:selections="(selections) => emit('selectionsChanged', selections)"
  >
    <ListHeader
      class="sm:mx-5 mx-3"
      @columnWidthUpdated="emit('columnWidthUpdated')"
    >
      <ListHeaderItem
        v-for="column in columns"
        :key="column.key"
        :item="column"
        @columnWidthUpdated="emit('columnWidthUpdated', column)"
      >
        <Button
          v-if="column.key == '_liked_by'"
          variant="ghosted"
          class="!h-4"
          :class="isLikeFilterApplied ? 'fill-red-500' : 'fill-white'"
          @click="() => emit('applyLikeFilter')"
        >
          <HeartIcon class="h-4 w-4" />
        </Button>
      </ListHeaderItem>
    </ListHeader>
    <ListRows
      v-slot="{ idx, column, item, row }"
      :rows="rows"
      doctype="CRM Lead"
    >
      <ListRowItem :item="item" :align="column.align" class="overflow-hidden">
        <template #prefix>
          <div
            v-if="column.key === '_assign'"
            class="flex items-center gap-1.5 truncate"
          >
            <Tooltip
              v-if="ownerMap[row.name] || row.lead_owner"
              :text="__('Responsable') + ': ' + userLabel(ownerMap[row.name] || row.lead_owner)"
            >
              <div class="flex items-center gap-1.5 truncate">
                <div class="rounded-full ring-2 ring-blue-500">
                  <Avatar
                    :image="userImage(ownerMap[row.name] || row.lead_owner)"
                    :label="userLabel(ownerMap[row.name] || row.lead_owner)"
                    size="sm"
                  />
                </div>
                <span class="truncate text-base text-ink-gray-8">
                  {{ userLabel(ownerMap[row.name] || row.lead_owner) }}
                </span>
              </div>
            </Tooltip>
            <div
              v-if="otherAssignees(item, ownerMap[row.name] || row.lead_owner).length"
              class="flex shrink-0 items-center -space-x-1.5"
            >
              <Tooltip
                v-for="u in otherAssignees(item, ownerMap[row.name] || row.lead_owner)"
                :key="u.name"
                :text="userLabel(u.name)"
              >
                <div class="rounded-full ring-2 ring-sky-300">
                  <Avatar :image="u.image" :label="u.label" size="sm" />
                </div>
              </Tooltip>
            </div>
          </div>
          <div v-else-if="column.key === 'status'">
            <IndicatorIcon :class="item.color" />
          </div>
          <div v-else-if="['territory', 'industry'].includes(column.key)">
            <IndicatorIcon v-if="item?.color" :class="item.color" />
          </div>
          <div v-else-if="column.key === 'lead_name'">
            <Avatar
              v-if="item.label"
              class="flex items-center"
              :image="item.image"
              :label="item.image_label"
              size="sm"
            />
          </div>
          <div v-else-if="column.key === 'lead_owner'">
            <Avatar
              v-if="item.full_name"
              class="flex items-center"
              :image="item.user_image"
              :label="item.full_name"
              size="sm"
            />
          </div>
          <div v-else-if="column.key === 'mobile_no' && item">
            <PhoneIcon class="h-4 w-4" />
          </div>
        </template>
        <template #default="{ label }">
          <InlineEditCell
            :doctype="'CRM Lead'"
            :name="row.name"
            :column="column"
            :disabled="idx === 0"
            @saved="reloadList"
          >
          <div
            v-if="
              [
                'modified',
                'creation',
                'first_response_time',
                'first_responded_on',
                'response_by',
              ].includes(column.key)
            "
            class="truncate text-base"
            @click="
              (event) =>
                emit('applyFilter', {
                  event,
                  idx,
                  column,
                  item,
                  firstColumn: columns[0],
                })
            "
          >
            <Tooltip :text="item.label">
              <div>{{ item.timeAgo }}</div>
            </Tooltip>
          </div>
          <div
            v-else-if="column.key === '_age'"
            class="truncate text-base text-ink-gray-7"
          >
            {{ ageLabel(row.name) }}
          </div>
          <div
            v-else-if="column.key === '_has_email'"
            class="flex items-center gap-1"
            :title="hasEmail(row.name) ? __('Tiene email') : __('Sin email')"
          >
            <EmailIcon class="h-4 w-4 text-ink-gray-6" />
            <FeatherIcon
              :name="hasEmail(row.name) ? 'check' : 'x'"
              class="h-3.5 w-3.5"
              :class="hasEmail(row.name) ? 'text-green-600' : 'text-red-600'"
            />
          </div>
          <div
            v-else-if="column.key === '_has_phone'"
            class="flex items-center gap-1"
            :title="hasPhone(row.name) ? __('Tiene teléfono') : __('Sin teléfono')"
          >
            <PhoneIcon class="h-4 w-4 text-ink-gray-6" />
            <FeatherIcon
              :name="hasPhone(row.name) ? 'check' : 'x'"
              class="h-3.5 w-3.5"
              :class="hasPhone(row.name) ? 'text-green-600' : 'text-red-600'"
            />
          </div>
          <div v-else-if="column.key === '_liked_by'">
            <Button
              v-if="column.key == '_liked_by'"
              variant="ghosted"
              :class="isLiked(item) ? 'fill-red-500' : 'fill-white'"
              @click.stop.prevent="
                () =>
                  emit('likeDoc', {
                    name: row.name,
                    liked: isLiked(item),
                  })
              "
            >
              <HeartIcon class="h-4 w-4" />
            </Button>
          </div>
          <div
            v-else-if="column.key === 'sla_status'"
            class="truncate text-base"
          >
            <Badge
              v-if="item.value"
              :variant="'subtle'"
              :theme="item.color"
              size="md"
              :label="item.value"
              @click="
                (event) =>
                  emit('applyFilter', {
                    event,
                    idx,
                    column,
                    item,
                    firstColumn: columns[0],
                  })
              "
            />
          </div>
          <div v-else-if="column.type === 'Check'">
            <FormControl
              type="checkbox"
              :modelValue="item"
              :disabled="true"
              class="text-ink-gray-9"
            />
          </div>
          <RatingInput
            v-else-if="column.type === 'Rating'"
            :value="item"
            class="!opacity-100 flex-nowrap overflow-auto"
            :disabled="true"
            :max="column.options || 5"
            @click="
              (event) =>
                emit('applyFilter', {
                  event,
                  idx,
                  column,
                  item,
                  firstColumn: columns[0],
                })
            "
          />
          <div
            v-else-if="label"
            class="truncate text-base"
            @click="
              (event) =>
                emit('applyFilter', {
                  event,
                  idx,
                  column,
                  item,
                  firstColumn: columns[0],
                })
            "
          >
            {{ getLabel(label, column) }}
          </div>
          </InlineEditCell>
        </template>
      </ListRowItem>
    </ListRows>
    <ListSelectBanner>
      <template #actions="{ selections, unselectAll }">
        <Dropdown
          :options="listBulkActionsRef.bulkActions(selections, unselectAll)"
        >
          <Button icon="lucide-more-horizontal" variant="ghost" />
        </Dropdown>
      </template>
    </ListSelectBanner>
  </ListView>
  <ListFooter
    v-if="pageLengthCount"
    v-model="pageLengthCount"
    class="border-t sm:px-5 px-3 py-2"
    :options="{
      rowCount: options.rowCount,
      totalCount: options.totalCount,
    }"
    @loadMore="emit('loadMore')"
  />
  <ListBulkActions ref="listBulkActionsRef" v-model="list" doctype="CRM Lead" />
</template>

<script setup>
import HeartIcon from '@/components/Icons/HeartIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import StatusHeaderFilter from '@/components/ListViews/StatusHeaderFilter.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import { FeatherIcon } from 'frappe-ui'
import RatingInput from '@/components/Controls/RatingInput.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import ListBulkActions from '@/components/ListBulkActions.vue'
import ListRows from '@/components/ListViews/ListRows.vue'
import InlineEditCell from '@/components/ListViews/InlineEditCell.vue'
import { isTranslatable, formatDuration } from '@/utils'
import {
  Avatar,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListSelectBanner,
  ListRowItem,
  ListFooter,
  Dropdown,
  Tooltip,
  call,
} from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/users'
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'

const { getUser } = usersStore()
function userLabel(u) {
  if (!u) return ''
  return getUser(u)?.full_name || u
}
function userImage(u) {
  if (!u) return ''
  return getUser(u)?.user_image || ''
}
function otherAssignees(assignees, owner) {
  return (assignees || []).filter((u) => u && u.name && u.name !== owner)
}

const ageMap = ref({})
const ownerMap = ref({})
const contactMap = ref({})
function daysSince(dt) {
  if (!dt) return null
  const created = new Date(String(dt).replace(' ', 'T'))
  if (isNaN(created)) return null
  const d = Math.floor((Date.now() - created.getTime()) / 86400000)
  return d < 0 ? 0 : d
}
function ageLabel(name) {
  const d = ageMap.value[name]
  if (d == null) return ''
  return d === 1 ? '1 día' : `${d} días`
}
function hasEmail(name) {
  return !!contactMap.value[name]?.email
}
function hasPhone(name) {
  return !!contactMap.value[name]?.phone
}
async function loadAges(rows) {
  const names = (rows || []).map((r) => r.name).filter(Boolean)
  if (!names.length) {
    ageMap.value = {}
    contactMap.value = {}
    ownerMap.value = {}
    return
  }
  try {
    const leads = await call('frappe.client.get_list', {
      doctype: 'CRM Lead',
      filters: { name: ['in', names] },
      fields: ['name', 'creation', 'email', 'mobile_no', 'lead_owner'],
      limit_page_length: 0,
    })
    const gm = {}
    const cm = {}
    const om = {}
    for (const r of leads || []) {
      gm[r.name] = daysSince(r.creation)
      cm[r.name] = {
        email: r.email,
        phone: r.mobile_no,
      }
      om[r.name] = r.lead_owner
    }
    ageMap.value = gm
    contactMap.value = cm
    ownerMap.value = om
  } catch (e) {
    // silencioso
  }
}

const props = defineProps({
  rows: { type: Array, required: true },
  columns: { type: Array, required: true },
  statusFilterOptions: { type: Array, default: () => [] },
  activeStatusFilter: { type: String, default: null },
  options: {
    type: Object,
    default: () => ({
      selectable: true,
      showTooltip: true,
      resizeColumn: false,
      totalCount: 0,
      rowCount: 0,
    }),
  },
})
const emit = defineEmits([
  'loadMore',
  'updatePageCount',
  'columnWidthUpdated',
  'applyFilter',
  'applyLikeFilter',
  'likeDoc',
  'selectionsChanged',
  'statusFilter',
])

watch(
  () => (props.rows || []).map((r) => r.name).join(','),
  () => loadAges(props.rows),
  { immediate: true },
)

const route = useRoute()

const pageLengthCount = defineModel({ type: Number })
const list = defineModel('list', { type: Object })

function reloadList() {
  list.value?.reload?.()
}

function getLabel(label, column) {
  if (column.type === 'Duration') return formatDuration(label)
  if (column.options && isTranslatable(column.options)) return __(label)
  return label
}

const isLikeFilterApplied = computed(() => {
  return list.value.params?.filters?._liked_by ? true : false
})

const { user } = sessionStore()

function isLiked(item) {
  if (item) {
    let likedByMe = JSON.parse(item)
    return likedByMe.includes(user)
  }
}

watch(pageLengthCount, (val, old_value) => {
  if (val === old_value) return
  emit('updatePageCount', val)
})

const listBulkActionsRef = ref(null)

defineExpose({
  customListActions: computed(
    () => listBulkActionsRef.value?.customListActions,
  ),
})
</script>
