<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useEmployees } from '@/composables/useEmployees'
import { usePermissions } from '@/composables/usePermissions'
import UserLayout from '@/layouts/userLayout.vue'
import { useInfiniteScroll, useDebounceFn } from '@vueuse/core'
import Avatar from '@/components/ui/Avatar.vue'

const router = useRouter()
const { employees, loading, fetchEmployees } = useEmployees()
const { menuPermissions } = usePermissions()

// เพิ่ม state สำหรับการค้นหาและ pagination
const searchQuery = ref('')
const page = ref(1)
const hasMore = ref(true)
const target = ref<HTMLElement | null>(null)

// ฟังก์ชันสำหรับโหลดข้อมูลเพิ่มเติม
const loadMore = async () => {
  if (loading.value || !hasMore.value) return
  
  const result = await fetchEmployees({
    page: page.value,
    search: searchQuery.value,
    limit: 15
  })
  
  if (result.length < 15) {
    hasMore.value = false
  } else {
    page.value++
  }
}

// ใช้ useInfiniteScroll สำหรับ lazy loading
useInfiniteScroll(target, loadMore)

// debounce การค้นหาเพื่อป้องกันการ request ถี่เกินไป
const handleSearch = useDebounceFn(async () => {
  page.value = 1
  hasMore.value = true
  employees.value = []
  await loadMore()
}, 300)

onMounted(async () => {
  if (!menuPermissions.value.employeeList) {
    router.push('/')
    return
  }
  await loadMore()
})

const navigateToDetail = (employeeId: string) => {
  if (menuPermissions.value.employeeDetail) {
    router.push(`/employees/${employeeId}`)
  }
}
</script>

<template>
  <UserLayout>
    <div class="container mx-auto px-4 py-8">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">รายชื่อพนักงาน</h1>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="ค้นหาพนักงาน..."
          class="input input-bordered w-full max-w-xs"
          @input="handleSearch"
        />
      </div>

      <div v-if="employees.length === 0 && !loading" class="text-center py-8">
        <p class="text-gray-500">ไม่พบข้อมูลพนักงาน</p>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="employee in employees"
          :key="employee.name"
          class="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer"
          @click="navigateToDetail(employee.name)"
        >
          <figure class="px-10 pt-10">
            <img
              v-if="employee.image"
              :src="employee.image"
              :alt="employee.employee_name"
              class="rounded-xl w-32 h-32 object-cover"
            />
            <Avatar
              v-else
              :name="employee.employee_name"
              size="lg"
              class="rounded-xl"
            />
          </figure>
          <div class="card-body items-center text-center">
            <h2 class="card-title">{{ employee.employee_name }}</h2>
            <p class="text-sm text-gray-600">{{ employee.designation }}</p>
            <p class="text-sm text-gray-500">{{ employee.department }}</p>
            <div class="flex gap-2 mt-2">
              <span v-if="employee.cell_number" class="badge badge-primary">
                {{ employee.cell_number }}
              </span>
              <span v-if="employee.company_email" class="badge badge-secondary">
                {{ employee.company_email }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Infinite scroll target -->
      <div ref="target" class="h-4 mt-4">
        <div v-if="loading" class="flex justify-center">
          <span class="loading loading-spinner loading-lg"></span>
        </div>
        <div v-if="!hasMore && employees.length > 0" class="text-center text-gray-500">
          ไม่มีข้อมูลเพิ่มเติม
        </div>
      </div>
    </div>
  </UserLayout>
</template>
