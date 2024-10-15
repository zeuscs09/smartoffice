<template>
  <div class="avatar" :class="sizeClass">
    <img v-if="imageUrl" :src="imageUrl" :alt="email" class="rounded-full" />
    <div v-else class="placeholder rounded-full bg-gray-200 flex items-center justify-center text-gray-600">
      <span class="text-center">{{ initials }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { createResource } from 'frappe-ui'

const props = defineProps<{
  email: string
  size?: 'sm' | 'md' | 'lg'
}>()

const imageUrl = ref('')
const initials = computed(() => {
  return props.email.split('@')[0].slice(0, 2).toUpperCase()
})

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'w-8 h-8'
    case 'lg': return 'w-12 h-12'
    default: return 'w-10 h-10'
  }
})

const userResource = createResource({
  url: 'smartoffice.api.util.get_avartar',
  params: {
    doctype: 'User',
    name: props.email,
  },
  auto: false,
})

onMounted(async () => {
  try {
    const userData = await userResource.submit()
    if (userData.user_image) {
      imageUrl.value = userData.user_image
    }
  } catch (error) {
    console.error('Error fetching user image:', error)
  }
})
</script>

<style scoped>
.avatar {
  overflow: hidden;
}
.placeholder {
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}
.placeholder span {
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}
</style>
