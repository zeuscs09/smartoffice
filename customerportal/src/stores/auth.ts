import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('customer_token'))
  const user = ref(null)
  const isLoading = ref(false)
  const error = ref('')

  watch(token, (newToken) => {
    console.log('Token changed:', newToken)
    if (newToken) {
      localStorage.setItem('customer_token', newToken)
    }
  })

  const isLoggedIn = computed(() => {
    const storedToken = localStorage.getItem('customer_token')
    console.log('Checking login status, stored token:', storedToken)
    if (!storedToken) {
      token.value = null
      return false
    }
    if (storedToken !== token.value) {
      token.value = storedToken
    }
    return true
  })

  const requestOTP = createResource({
    url: 'smartoffice.api.authen.request_customer_otp',
    onSuccess(response) {
      if (response.status === 'success') {
        error.value = ''
        return response
      }
      error.value = response.message
    },
    onError(err) {
      error.value = err.message || 'เกิดข้อผิดพลาด กรุณาลองใหม่'
    }
  })

  const verifyOTP = createResource({
    url: 'smartoffice.api.authen.verify_customer_otp',
    onSuccess(response) {
      if (response.status === 'success' && response.token) {
        token.value = response.token
        localStorage.setItem('customer_token', response.token)
        router.push('/service-report')
      } else {
        error.value = response.message || 'ไม่สามารถยืนยัน OTP ได้'
      }
    },
    onError(err) {
      error.value = err.message || 'เกิดข้อผิดพลาด กรุณาลองใหม่'
    }
  })

  function logout() {
    console.log('Logging out')
    token.value = null
    user.value = null
    localStorage.removeItem('customer_token')
    router.push('/login')
  }

  return {
    token,
    user,
    isLoading,
    error,
    isLoggedIn,
    requestOTP,
    verifyOTP,
    logout
  }
})
