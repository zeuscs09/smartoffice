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
    <img v-if="imageUrls[0]" :src="imageUrls[0]" :alt="emails[0]" class="rounded-full w-full h-full object-cover tooltip tooltip-bottom" :data-tip="emails[0]" />
    <div v-else-if="isLoading" class="placeholder rounded-full bg-gray-100 w-full h-full flex items-center justify-center">
      <!-- เพิ่ม loading indicator -->
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-300"></div>
    </div>
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
import { ref, computed, watch, watchEffect } from 'vue'
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
const isLoading = ref(false)

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
  isLoading.value = true
  imageUrls.value = []
  if (!emails.value.length) {
    isLoading.value = false
    return
  }
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
          continue // ใช้ข้อมูลจาก cache และข้ามการเรียก API
        }
      }

      // ดึงข้อมูลจากเซิร์ฟเวอร์
      const userData = await userResource.submit({
        doctype: 'User',
        name: email,
      })
      const userImage = userData.user_image || ''

      imageUrls.value.push(userImage)
      // อัปเดต cache ด้วยข้อมูลใหม่
      localStorage.setItem(`avatar_${email}`, JSON.stringify({
        image: userImage,
        timestamp: Date.now()
      }))
    } catch (error) {
      console.error('เกิดข้อผิดพลาดในการดึงรูปภาพผู้ใช้:', error)
      imageUrls.value.push('')
    }
  }
  isLoading.value = false
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

// เปลี่ยนเป็น watchEffect เพื่อให้ทำงานเมื่อ emails เปลี่ยนแปลง
watchEffect(() => {
  if (emails.value.length > 0) {
    fetchUserImages()
  }
})
</script>

<style scoped>
.avatar-group {
  display: flex;
}
</style>
