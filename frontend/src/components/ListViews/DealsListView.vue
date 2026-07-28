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
      doctype="CRM Deal"
    >
      <ListRowItem :item="item" :align="column.align" class="overflow-hidden">
        <template #prefix>
          <div
            v-if="column.key === '_assign'"
            class="flex items-center truncate"
          >
            <MultipleAvatar
              :avatars="item"
              size="sm"
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
          <div v-else-if="column.key === 'status'">
            <IndicatorIcon :class="item.color" />
          </div>
          <div v-else-if="['territory', 'industry'].includes(column.key)">
            <IndicatorIcon v-if="item?.color" :class="item.color" />
          </div>
          <div v-else-if="column.key === 'custom_producto' && getProductColor(item)">
            <IndicatorIcon :class="getProductColor(item)" />
          </div>
          <div v-else-if="column.key === 'organization'">
            <Avatar
              v-if="item.label"
              class="flex items-center"
              :image="item.logo"
              :label="item.label"
              size="sm"
            />
          </div>
          <div v-else-if="column.key === 'deal_owner'">
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
          <div v-else-if="column.key === '_liked_by'">
            <Button
              v-if="column.key == '_liked_by'"
              variant="ghosted"
              :class="isLiked(item) ? 'fill-red-500' : 'fill-white'"
              @click.stop.prevent="
                () => emit('likeDoc', { name: row.name, liked: isLiked(item) })
              "
            >
              <HeartIcon class="h-4 w-4" />
            </Button>
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
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import { productsStore } from '@/stores/products'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import RatingInput from '@/components/Controls/RatingInput.vue'
import ListBulkActions from '@/components/ListBulkActions.vue'
import ListRows from '@/components/ListViews/ListRows.vue'
import InlineEditCell from '@/components/ListViews/InlineEditCell.vue'
import { isTranslatable, formatDuration } from '@/utils'
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
} from 'frappe-ui'
import { sessionStore } from '@/stores/session'

const { getProduct } = productsStore()

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

const hasTotals = computed(
  () => Object.keys(props.columnTotals || {}).length > 0,
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
  'loadMore',
  'updatePageCount',
  'columnWidthUpdated',
  'applyFilter',
  'applyLikeFilter',
  'likeDoc',
  'selectionsChanged',
])

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
