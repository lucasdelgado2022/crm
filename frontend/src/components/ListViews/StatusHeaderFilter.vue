<template>
  <div ref="root" class="flex items-center">
    <button
      ref="btn"
      class="flex items-center gap-1 truncate text-sm text-ink-gray-5 hover:text-ink-gray-8"
      @click.stop.prevent="toggle"
    >
      <span class="truncate">{{ label }}</span>
      <span
        v-if="active"
        class="h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500"
      />
      <FeatherIcon name="chevron-down" class="h-3 w-3 shrink-0" />
    </button>
    <Teleport to="body">
      <div
        v-if="open"
        ref="panel"
        class="fixed z-[100] max-h-80 w-60 overflow-y-auto rounded-lg border border-outline-gray-2 bg-surface-base py-1 shadow-lg"
        :style="panelStyle"
      >
        <button
          class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-ink-gray-8 hover:bg-surface-gray-2"
          :class="active === null ? 'bg-surface-gray-2' : ''"
          @click.stop.prevent="select(null)"
        >
          <span class="flex-1 truncate text-left">{{ __('Todos') }}</span>
          <span class="font-bold text-ink-gray-9">{{ total }}</span>
        </button>
        <button
          v-for="o in options"
          :key="o.status"
          class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-ink-gray-8 hover:bg-surface-gray-2"
          :class="active === o.status ? 'bg-surface-gray-2' : ''"
          @click.stop.prevent="select(o.status)"
        >
          <IndicatorIcon :class="o.color" class="shrink-0" />
          <span class="flex-1 truncate text-left">{{ o.status }}</span>
          <span class="font-bold text-ink-gray-9">{{ o.count }}</span>
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import { FeatherIcon } from 'frappe-ui'
import { onClickOutside } from '@vueuse/core'
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  label: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  active: { type: String, default: null },
})

const emit = defineEmits(['select'])

const root = ref(null)
const btn = ref(null)
const panel = ref(null)
const open = ref(false)
const coords = ref({ top: 0, left: 0 })

const total = computed(() =>
  props.options.reduce((a, o) => a + (o.count || 0), 0),
)

const panelStyle = computed(() => ({
  top: coords.value.top + 'px',
  left: coords.value.left + 'px',
}))

function toggle() {
  if (open.value) {
    open.value = false
    return
  }
  const rect = btn.value?.getBoundingClientRect()
  if (rect) {
    const width = 240
    let left = rect.left
    if (left + width > window.innerWidth - 8)
      left = Math.max(8, window.innerWidth - width - 8)
    coords.value = { top: rect.bottom + 4, left }
  }
  open.value = true
}

onClickOutside(
  root,
  () => (open.value = false),
  { ignore: [panel] },
)

function select(status) {
  emit('select', status)
  open.value = false
}
</script>
