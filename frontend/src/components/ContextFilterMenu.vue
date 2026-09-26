<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 z-[9999]"
      @click="close"
      @contextmenu.prevent="close"
    >
      <div
        class="absolute min-w-[210px] max-w-[320px] overflow-hidden rounded-lg py-1"
        :style="panelStyle"
        @click.stop
      >
        <button
          v-for="(o, i) in options"
          :key="i"
          type="button"
          class="flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm"
          :style="hover === i ? itemHoverStyle : itemStyle"
          @mouseenter="hover = i"
          @mouseleave="hover = -1"
          @click="select(o)"
        >
          <span class="truncate">{{ o.label }}</span>
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const pos = ref({ x: 0, y: 0 })
const options = ref([])
const hover = ref(-1)

const panelStyle = ref({
  left: '0px',
  top: '0px',
  backgroundColor: '#ffffff',
  border: '1px solid #e5e7eb',
  boxShadow: '0 10px 30px rgba(0,0,0,0.18)',
})
const itemStyle = { color: '#374151', backgroundColor: 'transparent' }
const itemHoverStyle = { color: '#111827', backgroundColor: '#f3f4f6' }

function open({ x, y, options: opts }) {
  options.value = opts || []
  hover.value = -1
  const vw = window.innerWidth
  const vh = window.innerHeight
  const w = 240
  const h = (options.value.length || 1) * 34 + 8
  const nx = Math.max(8, Math.min(x, vw - w - 8))
  const ny = Math.max(8, Math.min(y, vh - h - 8))
  panelStyle.value = { ...panelStyle.value, left: nx + 'px', top: ny + 'px' }
  visible.value = true
}
function close() {
  visible.value = false
}
function select(o) {
  close()
  if (o && typeof o.onClick === 'function') o.onClick()
}

defineExpose({ open, close })
</script>
