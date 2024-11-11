<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="card w-full max-w-sm shadow-lg bg-white">
      <div class="card-body">
        <h2 class="card-title text-center">Customer Portal Login</h2>
        
        <div v-if="errorMessage" class="alert alert-error shadow-lg">
          <div>
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ errorMessage }}</span>
          </div>
        </div>

        <!-- ขั้นตอนที่ 1: กรอกอีเมล -->
        <div v-if="!showOTPInput">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Email</span>
            </label>
            <input
              type="email"
              v-model="email"
              placeholder="your@email.com"
              class="input input-bordered w-full"
              required
            />
          </div>
          <div class="form-control mt-6">
            <button
              @click="requestOTP"
              class="btn btn-primary w-full"
              :class="{ loading: isLoading }"
              :disabled="isLoading || !isValidEmail"
            >
              Request OTP
            </button>
          </div>
        </div>

        <!-- ขั้นตอนที่ 2: กรอก OTP -->
        <div v-else>
          <div class="form-control">
            <label class="label">
              <span class="label-text">Enter OTP</span>
            </label>
            <div class="text-sm text-gray-600 mb-2">
              Reference Code: <span class="font-medium">{{ referenceCode }}</span>
            </div>
            <input
              type="text"
              v-model="otp"
              placeholder="Enter 6-digit OTP"
              class="input input-bordered w-full text-center tracking-widest text-xl"
              maxlength="6"
              required
            />
            <label class="label">
              <span class="label-text-alt">OTP sent to {{ email }}</span>
              <span 
                class="label-text-alt link link-primary cursor-pointer"
                @click="resendOTP"
              >
                Resend OTP
              </span>
            </label>
          </div>
          <div class="form-control mt-6">
            <button
              @click="verifyOTP"
              class="btn btn-primary w-full"
              :class="{ loading: isLoading }"
              :disabled="isLoading || otp.length !== 6"
            >
              Verify OTP
            </button>
            <button
              @click="showOTPInput = false"
              class="btn btn-ghost mt-2"
              :disabled="isLoading"
            >
              Change Email
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios, { AxiosError } from 'axios'

type OTPResponse = {
  message: {
    message: string
    status: string
    reference_code: string
    token?: string
  }
}

// แก้ไข type สำหรับ verify OTP response
type VerifyOTPResponse = {
  message: {
    message: string
    status: string
    token: string
  }
}

const router = useRouter()
const email = ref<string>('')
const otp = ref<string>('')
const showOTPInput = ref<boolean>(false)
const isLoading = ref<boolean>(false)
const errorMessage = ref<string>('')
const referenceCode = ref<string>('')

const isValidEmail = computed(() => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)
})

const handleAPIError = (error: unknown) => {
  if (error instanceof AxiosError) {
    return error.response?.data?.message || 'เกิดข้อผิดพลาดในการเชื่อมต่อ'
  }
  return 'เกิดข้อผิดพลาดที่ไม่ทราบสาเหตุ'
}

const requestOTP = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    
    const { data } = await axios.post<OTPResponse>('/api/method/smartoffice.api.authen.request_customer_otp', {
      email: email.value
    })

    if (data.message.status === 'success') {
      showOTPInput.value = true
      referenceCode.value = data.message.reference_code
    } else {
      errorMessage.value = data.message.message || 'ไม่สามารถส่ง OTP ได้'
    }
  } catch (error) {
    errorMessage.value = handleAPIError(error)
  } finally {
    isLoading.value = false
  }
}

const verifyOTP = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    
    const { data } = await axios.post<VerifyOTPResponse>(
      '/api/method/smartoffice.api.authen.verify_customer_otp',
      {
        email: email.value,
        otp: otp.value,
        reference_code: referenceCode.value
      }
    )

    if (data.message.status === 'success') {
      localStorage.setItem('customerToken', data.message.token)
      router.push('/customer/services')
    } else {
      errorMessage.value = data.message.message || 'รหัส OTP ไม่ถูกต้อง'
    }
  } catch (error) {
    errorMessage.value = handleAPIError(error)
  } finally {
    isLoading.value = false
  }
}

const resendOTP = () => {
  requestOTP()
}
</script>
