<template>
  <div class="flex shrink-0 flex-col border-t">
    <button
      class="flex items-center gap-2 px-5 py-3 text-base font-semibold text-ink-gray-8"
      @click="open = !open"
    >
      <CommentIcon class="h-4 w-4" />
      {{ __('Comentarios') }}
      <Badge variant="subtle" theme="gray" size="sm">{{ commentList.length }}</Badge>
      <FeatherIcon :name="open ? 'chevron-up' : 'chevron-down'" class="ml-auto h-4 w-4" />
    </button>
    <div v-show="open" class="flex flex-col">
      <div class="flex max-h-64 flex-col gap-3 overflow-y-auto px-5 pb-3">
        <CommentArea
          v-for="c in commentList"
          :key="c.name"
          :activity="c"
          @reload="comments.reload()"
        />
        <div v-if="!commentList.length" class="py-3 text-center text-sm text-ink-gray-4">
          {{ __('Sin comentarios') }}
        </div>
      </div>
      <div class="border-t p-3">
        <textarea
          v-model="newComment"
          rows="2"
          class="w-full resize-none rounded border border-outline-gray-2 bg-surface-white px-2 py-1.5 text-sm text-ink-gray-8 focus:outline-none focus:ring-1 focus:ring-outline-gray-3"
          :placeholder="__('Escribí un comentario...')"
          @keydown.enter.exact.prevent="submit"
        />
        <div class="mt-2 flex justify-end">
          <Button
            variant="solid"
            :label="__('Comentar')"
            :loading="saving"
            :disabled="!newComment.trim()"
            @click="submit"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import CommentArea from '@/components/Activities/CommentArea.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import { FeatherIcon, Badge, Button, createResource, call, toast } from 'frappe-ui'
import { usersStore } from '@/stores/users'
import { sessionStore } from '@/stores/session'
import { computed, ref } from 'vue'

const props = defineProps({
  dealId: { type: String, required: true },
})

const open = ref(true)
const newComment = ref('')
const saving = ref(false)
const { getUser } = usersStore()
const { user } = sessionStore()

const comments = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Comment',
    filters: {
      reference_doctype: 'CRM Deal',
      reference_name: props.dealId,
      comment_type: 'Comment',
    },
    fields: ['name', 'content', 'owner', 'creation'],
    order_by: 'creation asc',
    limit_page_length: 0,
  },
  auto: true,
})

const commentList = computed(() =>
  (comments.data || []).map((c) => ({
    ...c,
    owner_name: getUser(c.owner)?.full_name || c.owner,
  })),
)

function escapeHtml(t) {
  return t
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
}

async function submit() {
  const text = newComment.value.trim()
  if (!text || saving.value) return
  saving.value = true
  try {
    await call('frappe.desk.form.utils.add_comment', {
      reference_doctype: 'CRM Deal',
      reference_name: props.dealId,
      content: escapeHtml(text),
      comment_email: user,
      comment_by: getUser(user)?.full_name || user,
    })
    newComment.value = ''
    comments.reload()
  } catch (e) {
    toast.error((e && e.messages && e.messages[0]) || __('No se pudo comentar'))
  } finally {
    saving.value = false
  }
}
</script>
