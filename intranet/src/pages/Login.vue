<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="card w-full max-w-sm shadow-lg bg-white">
      <div class="card-body">
        <h2 class="card-title text-center">Login to Smart Office</h2>
        <!-- เพิ่มการแสดงข้อความแจ้งเตือน -->
        <div v-if="errorMessage" class="alert alert-error shadow-lg">
          <div>
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span>{{ errorMessage }}</span>
          </div>
        </div>
        <form class="space-y-4" @submit.prevent="submit">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Email</span>
            </label>
            <input
              type="text"
              name="email"
              placeholder="johndoe@email.com"
              class="input input-bordered w-full"
              required
            />
          </div>
          <div class="form-control">
            <label class="label">
              <span class="label-text">Password</span>
            </label>
            <input
              type="password"
              name="password"
              placeholder="••••••"
              class="input input-bordered w-full"
              required
            />
          </div>
          <div class="form-control mt-6">
            <button
              type="submit"
              class="btn btn-primary w-full"
              :class="{ loading: session.login.loading }"
            >
              Login
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { session } from '../data/session'

const errorMessage = ref('')

async function submit(e: Event) {
  e.preventDefault()
  const formData = new FormData(e.target as HTMLFormElement)
  try {
    await session.login.submit({
      email: formData.get('email') as string,
      password: formData.get('password') as string,
    })
    errorMessage.value = '' // ล้างข้อความแจ้งเตือนเมื่อ login สำเร็จ
  } catch (error: any) {
    if (error.message === 'Invalid login credentials') {
      errorMessage.value = 'อีเมลหรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง'
    } else {
      errorMessage.value = 'เกิดข้อผิดพลาดในการเข้าสู่ระบบ กรุณาลองใหม่ภายหลัง'
    }
  }
}
</script>

<style scoped>
/* คุณสามารถเพิ่มสไตล์เพิ่มเติมได้ที่นี่ */
</style>
