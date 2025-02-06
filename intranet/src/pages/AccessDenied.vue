<template>
  <UserLayout>
    <div class="flex flex-col items-center justify-center min-h-[80vh]">
      <div class="text-center">
        <h1 class="text-4xl font-bold text-error mb-4">
          Access Denied
        </h1>
        <p class="text-gray-600 mb-8">
          คุณไม่มีสิทธิ์เข้าถึงหน้านี้
        </p>
        <button 
          class="btn btn-primary"
          @click="router.push({ name: 'Home' })"
        >
          กลับหน้าหลัก
        </button>
      </div>
    </div>
  </UserLayout>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import UserLayout from '@/layouts/userLayout.vue'

const router = useRouter()
</script> 