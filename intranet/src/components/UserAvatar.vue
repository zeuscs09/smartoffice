<template>
  <div v-if="emails.length > 1" class="avatar-group -space-x-6 rtl:space-x-reverse">
    <div v-for="(email, index) in emails" :key="index" class="avatar">
      <div :class="[sizeClass, 'flex items-center justify-center overflow-hidden']">
        <img v-if="imageUrls[index]" :src="imageUrls[index]" :alt="email" class="rounded-full w-full h-full object-cover" />
        <div v-else class="placeholder rounded-full bg-gray-200 w-full h-full flex items-center justify-center text-gray-600 p-2">
          <span>{{ getInitials(email) }}</span>
        </div>
      </div>
    </div>
  </div>
  <div v-else-if="emails.length === 1" :class="[sizeClass, 'avatar flex items-center justify-center overflow-hidden']">
    <img v-if="imageUrls[0]" :src="imageUrls[0]" :alt="emails[0]" class="rounded-full w-full h-full object-cover" />
    <div v-else class="placeholder rounded-full bg-gray-200 w-full h-full flex items-center justify-center text-gray-600 p-2">
      <span>{{ getInitials(emails[0]) }}</span>
    </div>
  </div>
  <div v-else :class="[sizeClass, 'avatar flex items-center justify-center overflow-hidden']">
    <div class="placeholder rounded-full bg-gray-200 w-full h-full flex items-center justify-center text-gray-600 p-2">
      <span>N/A</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'

const props = defineProps<{
  email: string | undefined
  size?: 'sm' | 'md' | 'lg'
}>()

const emails = computed(() => {
  if (!props.email) return []
  return props.email.split(',').map(e => e.trim()).filter(Boolean)
})
const imageUrls = ref<string[]>([])

const getInitials = (email: string) => {
  return email.split('@')[0].slice(0, 2).toUpperCase()
}

const sizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'w-8 h-8'
    case 'lg': return 'w-12 h-12'
    default: return 'w-10 h-10'
  }
})

const userResource = createResource({
  url: 'smartoffice.api.util.get_avartar',
  auto: false,
})

const CACHE_EXPIRATION = 2 * 24 * 60 * 60 * 1000 // 2 วันในหน่วยมิลลิวินาที

const fetchUserImages = async () => {
  imageUrls.value = []
  if (!emails.value.length) return
  for (const email of emails.value) {
    if (!email) {
      imageUrls.value.push('')
      continue
    }
    try {
      // ตรวจสอบ cache ก่อน
      const cachedData = localStorage.getItem(`avatar_${email}`)
      if (cachedData) {
        const { image, timestamp } = JSON.parse(cachedData)
        if (Date.now() - timestamp < CACHE_EXPIRATION) {
          imageUrls.value.push(image)
          continue
        }
      }

      const userData = await userResource.submit({
        doctype: 'User',
        name: email,
      })
      const userImage = userData.user_image || ''
      imageUrls.value.push(userImage)
      // บันทึกลงใน cache พร้อมเวลาปัจจุบัน
      localStorage.setItem(`avatar_${email}`, JSON.stringify({
        image: userImage,
        timestamp: Date.now()
      }))
    } catch (error) {
      console.error('Error fetching user image:', error)
      imageUrls.value.push('')
    }
  }
}

// ฟังก์ชันสำหรับล้าง cache ที่หมดอายุ
const clearExpiredCache = () => {
  Object.keys(localStorage).forEach(key => {
    if (key.startsWith('avatar_')) {
      const cachedData = localStorage.getItem(key)
      if (cachedData) {
        const { timestamp } = JSON.parse(cachedData)
        if (Date.now() - timestamp >= CACHE_EXPIRATION) {
          localStorage.removeItem(key)
        }
      }
    }
  })
}

// เรียกใช้ฟังก์ชันล้าง cache ที่หมดอายุเมื่อคอมโพเนนต์ถูกโหลด
clearExpiredCache()

watch(() => props.email, fetchUserImages, { immediate: true })
</script>

<style scoped>
.avatar-group {
  display: flex;
}
</style>
