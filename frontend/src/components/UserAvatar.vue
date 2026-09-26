<template>
  <Avatar
    v-if="img"
    shape="circle"
    :image="img"
    :label="fullName"
    :size="size"
    v-bind="$attrs"
  />
  <div
    v-else
    class="flex shrink-0 items-center justify-center rounded-full font-medium leading-none"
    :style="circleStyle"
    :title="fullName"
    v-bind="$attrs"
  >
    {{ initials }}
  </div>
</template>
<script setup>
import { usersStore } from '@/stores/users'
import { Avatar } from 'frappe-ui'
import { computed } from 'vue'
import { userInitials, userColor } from '@/utils'

const props = defineProps({
  user: { type: String, default: null },
  size: { type: String, default: 'md' },
})

const { getUser, getUserColor } = usersStore()
const fullName = computed(() => getUser(props.user)?.full_name || props.user || '')
const img = computed(() => getUser(props.user)?.user_image)
const initials = computed(() => userInitials(fullName.value))

const SIZES = { xs: 16, sm: 20, md: 24, lg: 28, xl: 32, '2xl': 40, '3xl': 48 }
const circleStyle = computed(() => {
  const px = SIZES[props.size] || 24
  return {
    width: px + 'px',
    height: px + 'px',
    fontSize: Math.round(px * 0.42) + 'px',
    backgroundColor: getUserColor(props.user) || userColor(props.user || fullName.value),
    color: '#fff',
  }
})
</script>
