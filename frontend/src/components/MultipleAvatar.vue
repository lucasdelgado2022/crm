<template>
  <div
    v-if="avatars?.length"
    class="mr-1.5 flex cursor-pointer items-center"
    :class="[
      avatars?.length > 1 ? 'flex-row-reverse' : 'truncate [&>div]:truncate',
    ]"
  >
    <Tooltip v-if="avatars?.length == 1" :text="avatars[0].name">
      <Avatar
        v-if="avatars[0].image"
        shape="circle"
        :image="avatars[0].image"
        :label="avatars[0].label"
        :size="size"
      />
      <div
        v-else
        class="flex shrink-0 items-center justify-center rounded-full font-medium leading-none"
        :style="circleStyle(avatars[0])"
      >
        {{ ini(avatars[0].label) }}
      </div>
    </Tooltip>
    <Tooltip
      v-for="avatar in reverseAvatars"
      v-else
      :key="avatar.name"
      :text="avatar.name"
    >
      <Avatar
        v-if="avatar.image"
        class="user-avatar -mr-1.5 transform ring-2 ring-outline-base transition hover:z-10 hover:scale-110"
        shape="circle"
        :image="avatar.image"
        :label="avatar.label"
        :size="size"
        :data-name="avatar.name"
      />
      <div
        v-else
        class="user-avatar -mr-1.5 flex shrink-0 transform items-center justify-center rounded-full font-medium leading-none ring-2 ring-outline-base transition hover:z-10 hover:scale-110"
        :style="circleStyle(avatar)"
        :data-name="avatar.name"
      >
        {{ ini(avatar.label) }}
      </div>
    </Tooltip>
  </div>
</template>
<script setup>
import { Avatar, Tooltip } from 'frappe-ui'
import { computed } from 'vue'
import { userInitials, userColor } from '@/utils'

const props = defineProps({
  avatars: { type: Array, default: () => [] },
  size: { type: String, default: 'md' },
})
const reverseAvatars = computed(() => [...props.avatars].reverse())

const SIZES = { xs: 16, sm: 20, md: 24, lg: 28, xl: 32, '2xl': 40, '3xl': 48 }
function ini(label) {
  return userInitials(label)
}
function circleStyle(avatar) {
  const px = SIZES[props.size] || 24
  return {
    width: px + 'px',
    height: px + 'px',
    fontSize: Math.round(px * 0.42) + 'px',
    backgroundColor: userColor(avatar.name || avatar.label),
    color: '#fff',
  }
}
</script>
