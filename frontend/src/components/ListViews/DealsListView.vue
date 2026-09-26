<template>
  <ListView
    :class="$attrs.class"
    :columns="columns"
    :rows="rows"
    :options="{
      getRowRoute: (row) => ({
        name: 'Deal',
        params: { dealId: row.name },
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
        @columnWidthUpdated="(e) => onColumnWidthUpdated(e, column)"
      >
        <Button
          v-if="column.key == '_liked_by'"
          variant="ghost"
          class="!h-4"
          @click="() => emit('applyLikeFilter')"
        >
          <HeartIcon
            class="h-4 w-4"
            :class="isLikeFilterApplied ? 'fill-red-500 text-red-500' : ''"
          />
        </Button>
      </ListHeaderItem>
    </ListHeader>
    <ListRows
      v-slot="{ idx, column, item, row }"
      :rows="rows"
      doctype="CRM Deal"
    >
      <ListRowItem :item="item" :align="column.align" class="overflow-hidden">
        <template #prefix>
          <div
            v-if="column.key === '_assign'"
            class="flex items-center gap-1.5"
          >
            <Tooltip
              v-if="ownerMap[row.name] || row.deal_owner"
              :text="__('Responsable') + ': ' + userLabel(ownerMap[row.name] || row.deal_owner)"
            >
              <div class="rounded-full">
                <UserAvatar
                  :user="ownerMap[row.name] || row.deal_owner"
                  size="sm"
                />
              </div>
            </Tooltip>
            <div
              v-if="(apoyoMap[row.name] || []).length"
              class="flex shrink-0 items-center -space-x-1.5"
            >
              <Tooltip
                v-for="u in apoyoMap[row.name] || []"
                :key="u"
                :text="__('Apoyo') + ': ' + userLabel(u)"
              >
                <div class="rounded-full">
                  <UserAvatar :user="u" size="sm" />
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
          <div v-else-if="column.key === 'custom_producto' && getProductColor(item)">
            <IndicatorIcon :class="getProductColor(item)" />
          </div>
          <div v-else-if="column.key === 'organization'" class="flex items-center gap-1.5">
            <Avatar
              v-if="item.label"
              class="flex items-center"
              :image="item.logo"
              :label="item.label"
              size="sm"
            />
          </div>
          <div
            v-else-if="column.key === 'deal_owner'"
            class="flex items-center gap-1.5"
          >
            <template v-if="row.deal_owner">
              <UserAvatar :user="row.deal_owner" size="sm" />
            </template>
          </div>
          <div v-else-if="column.key === 'mobile_no' && item">
            <PhoneIcon class="h-4 w-4" />
          </div>
        </template>
        <template #default="{ label }">
          <InlineEditCell
            :doctype="'CRM Deal'"
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
          <div
            v-else-if="column.key === '_age'"
            class="truncate text-base text-ink-gray-7"
          >
            {{ ageLabel(row.name) }}
          </div>
          <div
            v-else-if="column.key === 'custom_solaer_revenue'"
            class="truncate text-base"
          >
            <span
              v-if="item"
              class="rounded px-2 py-0.5 text-sm font-medium"
              style="background-color: #dbeafe; color: #1e3a8a"
            >
              {{ typeof item === 'object' ? item.label || item.value : item }}
            </span>
          </div>
          <div v-else-if="column.type === 'Check'">
            <FormControl
              type="checkbox"
              :modelValue="item"
              :disabled="true"
              class="text-ink-gray-9"
            />
          </div>
          <div v-else-if="column.key === '_liked_by'">
            <Button
              variant="ghost"
              @click.stop.prevent="
                () => emit('likeDoc', { name: row.name, liked: isLiked(item) })
              "
            >
              <HeartIcon
                class="h-4 w-4"
                :class="isLiked(item) ? 'fill-red-500 text-red-500' : ''"
              />
            </Button>
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
          <div v-else-if="column.key === 'status'" class="truncate text-base" @contextmenu="(e) => openCtx(e, column, item, row)">
            <span
              v-if="statusHl(item)"
              class="rounded px-2 py-0.5 text-sm font-medium"
              :style="statusHl(item)"
            >
              {{ typeof item === 'object' ? item.label || item.value : item }}
            </span>
            <span v-else>{{ typeof item === 'object' ? item.label || item.value : item }}</span>
          </div>
          <div
            v-else-if="label"
            class="truncate text-base"
            @contextmenu="(e) => openCtx(e, column, item, row)"
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
    <ContextFilterMenu ref="ctxMenu" />
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
  <div
    v-if="hasTotals"
    class="mx-3 grid items-center gap-4 border-t px-2 py-2.5 text-base font-semibold text-ink-gray-8 sm:mx-5"
    :style="{ gridTemplateColumns: totalsGridTemplate }"
  >
    <div v-if="options?.selectable !== false" />
    <div
      v-for="(col, i) in columns"
      :key="col.key"
      class="truncate"
      :class="
        ['right', 'end'].includes(col.align)
          ? 'justify-self-end'
          : 'justify-self-start'
      "
    >
      <span v-if="columnTotals[col.key]">{{ columnTotals[col.key] }}</span>
      <span v-else-if="i === 0" class="text-ink-gray-5">{{ __('Total') }}</span>
    </div>
  </div>
  <div
    v-if="hasAverages"
    class="mx-3 grid items-center gap-4 px-2 pb-2.5 text-sm font-medium text-ink-gray-6 sm:mx-5"
    :style="{ gridTemplateColumns: totalsGridTemplate }"
  >
    <div v-if="options?.selectable !== false" />
    <div
      v-for="(col, i) in columns"
      :key="col.key"
      class="truncate"
      :class="
        ['right', 'end'].includes(col.align)
          ? 'justify-self-end'
          : 'justify-self-start'
      "
    >
      <span v-if="columnAverages[col.key]">{{ columnAverages[col.key] }}</span>
      <span v-else-if="i === 0" class="text-ink-gray-5">{{ __('Promedio') }}</span>
    </div>
  </div>
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
  <ListBulkActions ref="listBulkActionsRef" v-model="list" doctype="CRM Deal" />
</template>

<script setup>
import HeartIcon from '@/components/Icons/HeartIcon.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import StatusHeaderFilter from '@/components/ListViews/StatusHeaderFilter.vue'
import { productsStore } from '@/stores/products'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import RatingInput from '@/components/Controls/RatingInput.vue'
import ListBulkActions from '@/components/ListBulkActions.vue'
import ListRows from '@/components/ListViews/ListRows.vue'
import ContextFilterMenu from '@/components/ContextFilterMenu.vue'
import InlineEditCell from '@/components/ListViews/InlineEditCell.vue'
import { isTranslatable, formatDuration } from '@/utils'

function statusHl(item) {
  const s = String((typeof item === 'object' ? item.label || item.value : item) || '').toLowerCase()
  if (['won', 'ganado', 'ganada'].includes(s)) return 'background-color:#dcfce7;color:#166534'
  if (['lost', 'perdido', 'perdida'].includes(s)) return 'background-color:#fee2e2;color:#991b1b'
  return null
}
import {
  Avatar,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListRowItem,
  ListSelectBanner,
  ListFooter,
  Dropdown,
  Tooltip,
  call,
} from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/users'

const { getProduct } = productsStore()
const { getUser } = usersStore()

function userLabel(u) {
  if (!u) return ''
  return getUser(u)?.full_name || u
}
function userImage(u) {
  if (!u) return ''
  return getUser(u)?.user_image || ''
}

function getProductColor(item) {
  const name = item && typeof item === 'object' ? item.label || item.value : item
  const p = name && getProduct(name)
  return p && p.color ? p.colorClass : ''
}
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  rows: { type: Array, required: true },
  columns: { type: Array, required: true },
  columnTotals: { type: Object, default: () => ({}) },
  columnAverages: { type: Object, default: () => ({}) },
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

// Equipo comercial por deal: Responsable (deal_owner) + Apoyo (custom_apoyo_comercial)
const apoyoMap = ref({})
const ownerMap = ref({})
const ageMap = ref({})
const tipoMap = ref({})

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
function tipoBadge(name) {
  const t = tipoMap.value[name] || ''
  if (/^renovaci/i.test(t)) return 'RN'
  if (/^nuevo/i.test(t)) return 'NEW'
  return ''
}

async function loadTeam() {
  const names = (props.rows || []).map((r) => r.name).filter(Boolean)
  if (!names.length) {
    apoyoMap.value = {}
    ownerMap.value = {}
    ageMap.value = {}
    tipoMap.value = {}
    return
  }
  try {
    const [apoyo, deals] = await Promise.all([
      call('frappe.client.get_list', {
        doctype: 'Apoyo Comercial User',
        parent: 'CRM Deal',
        filters: {
          parenttype: 'CRM Deal',
          parentfield: 'custom_apoyo_comercial',
          parent: ['in', names],
        },
        fields: ['parent', 'user'],
        limit_page_length: 0,
      }),
      call('frappe.client.get_list', {
        doctype: 'CRM Deal',
        filters: { name: ['in', names] },
        fields: ['name', 'deal_owner', 'creation', 'custom_tipo_oportunidad'],
        limit_page_length: 0,
      }),
    ])
    const am = {}
    for (const r of apoyo || []) (am[r.parent] ||= []).push(r.user)
    apoyoMap.value = am
    const om = {}
    const gm = {}
    const tm = {}
    for (const r of deals || []) {
      om[r.name] = r.deal_owner
      gm[r.name] = daysSince(r.creation)
      tm[r.name] = r.custom_tipo_oportunidad
    }
    ownerMap.value = om
    ageMap.value = gm
    tipoMap.value = tm
  } catch (e) {
    // silencioso: si falla, el cell queda vacío
  }
}
watch(
  () => (props.rows || []).map((r) => r.name).join(','),
  loadTeam,
  { immediate: true },
)

const hasTotals = computed(
  () => Object.keys(props.columnTotals || {}).length > 0,
)
const hasAverages = computed(
  () => Object.keys(props.columnAverages || {}).length > 0,
)
const totalsGridTemplate = computed(() => {
  const checkbox = props.options?.selectable !== false ? '14px ' : ''
  const cols = props.columns
    .map((col) => {
      const w = col.width || 1
      return typeof w === 'number' ? w + 'fr' : w
    })
    .join(' ')
  return checkbox + cols
})

const emit = defineEmits([
  'contextFilter',
  'loadMore',
  'updatePageCount',
  'columnWidthUpdated',
  'applyFilter',
  'applyLikeFilter',
  'likeDoc',
  'selectionsChanged',
  'statusFilter',
])

const route = useRoute()

const pageLengthCount = defineModel({ type: Number })
const list = defineModel('list', { type: Object })

function reloadList() {
  list.value?.reload?.()
}
function onColumnWidthUpdated({ width, save }, column) {
  column.width = width
  if (save) emit('columnWidthUpdated', column)
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

const ctxMenu = ref(null)
const CTX_FIELDS = ['organization', 'custom_producto', 'status']
function ctxDisplay(column, item, row) {
  if (item && typeof item === 'object') return item.label || item.value || row?.[column.key]
  return item != null && item !== '' ? item : row?.[column.key]
}
function openCtx(e, column, item, row) {
  if (!column || !CTX_FIELDS.includes(column.key)) return
  const raw = item && typeof item === 'object' ? (item.value ?? item.name ?? item.label) : item
  const value = raw != null && raw !== '' ? raw : row?.[column.key]
  e.preventDefault()
  e.stopPropagation()
  const disp = ctxDisplay(column, item, row)
  const options = []
  if (value !== undefined && value !== null && value !== '') {
    options.push({
      label: __('Filtrar por') + ' \u00ab' + disp + '\u00bb',
      onClick: () => emit('contextFilter', { fieldname: column.key, value, operator: 'eq' }),
    })
    options.push({
      label: __('Excluir') + ' \u00ab' + disp + '\u00bb',
      onClick: () => emit('contextFilter', { fieldname: column.key, value, operator: 'ne' }),
    })
  }
  options.push({
    label: __('Quitar filtro de este campo'),
    onClick: () => emit('contextFilter', { fieldname: column.key, value: null, operator: 'clear' }),
  })
  ctxMenu.value?.open({ x: e.clientX, y: e.clientY, options })
}

</script>
