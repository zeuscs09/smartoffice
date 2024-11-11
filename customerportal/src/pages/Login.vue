<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-gray-900">เข้าสู่ระบบ</h2>
      </div>

      <!-- แสดง Error Message ถ้ามี -->
      <div v-if="auth.error" class="bg-red-50 text-red-500 p-4 rounded-md text-sm">
        {{ auth.error }}
      </div>

      <!-- ส่วนกรอก Email -->
      <div v-if="!showOTPInput">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">อีเมล</label>
            <input
              v-model="email"
              type="email"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              :disabled="auth.requestOTP.loading"
            />
          </div>
          
          <button
            @click="handleRequestOTP"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            :disabled="auth.requestOTP.loading || !email"
          >
            <span v-if="auth.requestOTP.loading">กำลังส่ง OTP...</span>
            <span v-else>ขอรหัส OTP</span>
          </button>
        </div>
      </div>

      <!-- ส่วนกรอก OTP -->
      <div v-else class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">รหัส OTP</label>
          <input
            v-model="otp"
            type="text"
            maxlength="6"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            :disabled="auth.verifyOTP.loading"
          />
          <p class="mt-2 text-sm text-gray-500">
            ส่ง OTP ไปที่: {{ email }}
            <button 
              @click="showOTPInput = false"
              class="text-blue-600 hover:text-blue-500"
            >
              แก้ไข
            </button>
          </p>
        </div>

        <button
          @click="handleVerifyOTP"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          :disabled="auth.verifyOTP.loading || !otp"
        >
          <span v-if="auth.verifyOTP.loading">กำลังตรวจสอบ...</span>
          <span v-else>ยืนยัน OTP</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const email = ref('')
const otp = ref('')
const showOTPInput = ref(false)
const referenceCode = ref('')

// ดูการเปลี่ยนแปลงของ token
watch(() => auth.token, (newToken) => {
  console.log('Token changed:', newToken)
  console.log('localStorage token:', localStorage.getItem('customer_token'))
})

async function handleRequestOTP() {
  try {
    const response = await auth.requestOTP.submit({
      email: email.value
    })
    
    if (response.status === 'success') {
      showOTPInput.value = true
      referenceCode.value = response.reference_code
    }
  } catch (error) {
    console.error('Request OTP error:', error)
  }
}

async function handleVerifyOTP() {
  try {
    await auth.verifyOTP.submit({
      email: email.value,
      otp: otp.value,
      reference_code: referenceCode.value
    })
  } catch (error) {
    console.error('Verify OTP error:', error)
  }
}
</script>