<template>
  <component :is="props.as || 'div'" ref="scrollableDiv">
    <slot></slot>
  </component>
</template>
<script setup>
import { ref } from 'vue'

// Fade/mask deshabilitado a pedido: se dejan solo scroll y scrollbar oculto.
const props = defineProps({
  as: { type: String, default: 'div' },
  maskLength: { type: Number, default: 30 },
  orientation: { type: String, default: 'vertical' },
})

const scrollableDiv = ref(null)
</script>
<style scoped>
div {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
div::-webkit-scrollbar {
  display: none;
}
</style>
