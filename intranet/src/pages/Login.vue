<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="card w-full max-w-sm shadow-lg bg-white">
      <div class="card-body">
        <h2 class="card-title text-center">Login to Smart Office</h2>
        
        <!-- เพิ่มตัวเลือกโหมด login -->
        <div class="form-control">
          <label class="label cursor-pointer">
            <span class="label-text">LDAP Login</span>
            <input 
              type="checkbox" 
              class="toggle toggle-primary" 
              v-model="isLDAPMode"
            />
          </label>
        </div>

        <form class="space-y-4" @submit.prevent="submit">
          <div class="form-control">
            <label class="label">
              <span class="label-text">{{ isLDAPMode ? 'Username' : 'Email' }}</span>
            </label>
            <!-- ปรับสัดส่วน input username ให้ยาวขึ้น -->
            <div v-if="isLDAPMode" class="join w-full">
              <input
                v-model="username"
                type="text"
                placeholder="username"
                class="input input-bordered join-item w-2/5"
                required
              />
              <input
                type="text"
                value="@thepractical.co.th"
                class="input input-bordered join-item w-3/5"
                disabled
              />
            </div>
            <input
              v-else
              type="email"
              name="email"
              placeholder="email@example.com"
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
              :disabled="isLDAPMode ? ldapLoading : session.login.loading"
            >
              <span v-if="isLDAPMode ? ldapLoading : session.login.loading" 
                class="loading loading-spinner loading-sm">
              </span>
              Login
            </button>
          </div>
        </form>

        <!-- แสดง error message ด้วย alert component -->
        <div v-if="errorMessage" class="alert alert-error shadow-lg mt-4">
          <div>
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ errorMessage }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import { session } from '../data/session'
import { usePermissions } from '../composables/usePermissions'

const errorMessage = ref('')
const ldapLoading = ref(false)
const isLDAPMode = ref(true)
const username = ref('')

const { fetchPermissions } = usePermissions()

// ฟังก์ชันสำหรับสร้าง email จาก username
const getEmail = computed(() => {
  return isLDAPMode.value === 'ldap' ? `${username.value}@thepractical.co.th` : ''
})

// ฟังก์ชันสำหรับจัดการ error message
function handleLoginError(error: any) {
  console.error('Login error:', error)
  
  // ตรวจสอบ error จาก server
  if (error.exc_type === 'ValidationError') {
    if (error.exception?.includes('LDAP is not enabled')) {
      return 'ระบบ LDAP ยังไม่ได้เปิดใช้งาน กรุณาติดต่อผู้ดูแลระบบ'
    }
    if (error.exception?.includes('Invalid login credentials')) {
      return 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง'
    }
    if (error.exception?.includes('User disabled')) {
      return 'บัญชีผู้ใช้ถูกระงับการใช้งาน กรุณาติดต่อผู้ดูแลระบบ'
    }
  }

  // ตรวจสอบ error จาก network
  if (error.message === 'Network Error') {
    return 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ต'
  }

  // error กรณีอื่นๆ
  return 'เกิดข้อผิดพลาดในการเข้าสู่ระบบ กรุณาลองใหม่ภายหลัง'
}

async function loginWithLDAP({ username, password }) {
  ldapLoading.value = true
  errorMessage.value = ''
  
  try {
    await session.ldapLogin.submit({
      username,
      password
    })
    
  } catch (error: any) {
    errorMessage.value = handleLoginError(error)
  } finally {
    ldapLoading.value = false
  }
}

async function submit(e: Event) {
  e.preventDefault()
  const formData = new FormData(e.target as HTMLFormElement)
  errorMessage.value = ''
  
  try {
    if (isLDAPMode.value) {
      await loginWithLDAP({
        username: username.value,
        password: formData.get('password') as string
      })
    } else {
      await session.login.submit({
        email: formData.get('email') as string,
        password: formData.get('password') as string,
      })
    }
    await fetchPermissions()  
  } catch (error: any) {
    errorMessage.value = handleLoginError(error)
  }
}
</script>

<style scoped>
.join {
  min-width: 100%;
}

.join-item:first-child {
  min-width: 45%;
}

.join-item:last-child {
  min-width: 55%;
}

/* ปรับ style ของ input disabled */
.join-item[disabled] {
  text-align: left;
  padding-left: 0.5rem;
  color: #666;
  background-color: #f5f5f5;
  font-size: 0.95rem;
}

/* เพิ่ม animation สำหรับ error message */
.alert-error {
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* ปรับ style ของ loading spinner */
.loading-spinner {
  margin-right: 0.5rem;
}
</style>
