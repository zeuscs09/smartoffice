<script setup lang="ts">
import { onMounted, ref, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEmployees } from '@/composables/useEmployees'
import { usePermissions } from '@/composables/usePermissions'
import UserLayout from '@/layouts/userLayout.vue'
import Avatar from '@/components/ui/Avatar.vue'
import type { Employee } from '@/composables/useEmployees'

const route = useRoute()
const router = useRouter()
const { getEmployeeDetail } = useEmployees()
const { menuPermissions } = usePermissions()
const employee = ref<Employee | null>(null)
const loading = ref(true)

const formatDate = inject('formatDate') as (date: string) => string

onMounted(async () => {
  if (!menuPermissions.value.employeeDetail) {
    router.push('/')
    return
  }

  try {
    const response = await getEmployeeDetail.submit({
      doctype: 'Employee',
      name: route.params.id
    })
    employee.value = response
  } catch (error) {
    console.error('Error fetching employee details:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <UserLayout>
    <div class="container mx-auto px-4 py-8">
      <button class="btn btn-ghost mb-4" @click="router.push('/employees/list')">
        <span class="i-lucide-arrow-left mr-2"></span>
        กลับ
      </button>

      <div v-if="loading" class="flex justify-center">
        <span class="loading loading-spinner loading-lg"></span>
      </div>

      <div v-else-if="employee" class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <div class="flex flex-col md:flex-row gap-8 mb-8">
            <div class="flex-none">
              <Avatar
                v-if="!employee.image"
                :name="`${employee.custom_first_name_local} ${employee.custom_last_name_local}`"
                size="lg"
                class="w-48 h-48"
              />
              <img
                v-else
                :src="employee.image"
                :alt="employee.employee_name"
                class="rounded-xl w-48 h-48 object-cover"
              />
            </div>
            <div class="flex-grow">
              <h2 class="text-2xl font-bold mb-4">ข้อมูลพนักงาน</h2>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-sm text-gray-500">รหัสพนักงาน</p>
                  <p class="font-medium">{{ employee.name }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">แผนก</p>
                  <p class="font-medium">{{ employee.department }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">ตำแหน่ง</p>
                  <p class="font-medium">{{ employee.designation }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">วันที่เริ่มงาน</p>
                  <p class="font-medium">{{ formatDate(employee.date_of_joining) }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="divider">ข้อมูลส่วนตัว</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <h3 class="font-semibold">ข้อมูลภาษาไทย</h3>
              <div class="grid grid-cols-1 gap-4">
                <div>
                  <p class="text-sm text-gray-500">คำนำหน้า</p>
                  <p class="font-medium">{{ employee.custom_salutation_local || '-' }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">ชื่อ</p>
                  <p class="font-medium">{{ employee.custom_first_name_local || '-' }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">นามสกุล</p>
                  <p class="font-medium">{{ employee.custom_last_name_local || '-' }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">ชื่อเล่น</p>
                  <p class="font-medium">{{ employee.custom_nick_name || '-' }}</p>
                </div>
              </div>
            </div>

            <div class="space-y-4">
              <h3 class="font-semibold">ข้อมูลภาษาอังกฤษ</h3>
              <div class="grid grid-cols-1 gap-4">
                <div>
                  <p class="text-sm text-gray-500">Title</p>
                  <p class="font-medium">{{ employee.salutation || '-' }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">First Name</p>
                  <p class="font-medium">{{ employee.first_name || '-' }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Last Name</p>
                  <p class="font-medium">{{ employee.last_name || '-' }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="divider">ข้อมูลการติดต่อ</div>
          <div class="grid grid-cols-1 gap-6">
            <div>
              <p class="text-sm text-gray-500">ที่อยู่</p>
              <p class="font-medium">{{ employee.custom_address || '-' }}</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-gray-500">ตำบล</p>
                <p class="font-medium">{{ employee.custom_tambol || '-' }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">อำเภอ</p>
                <p class="font-medium">{{ employee.custom_amphoe || '-' }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">จังหวัด</p>
                <p class="font-medium">{{ employee.custom_province || '-' }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">รหัสไปรษณีย์</p>
                <p class="font-medium">{{ employee.custom_zip_code || '-' }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">อีเมล</p>
                <p class="font-medium">{{ employee.company_email || '-' }}</p>
              </div>
            </div>
          </div>

          <div class="divider">ข้อมูลอื่นๆ</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-500">เพศ</p>
              <p class="font-medium">{{ employee.gender || '-' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">วันเกิด</p>
              <p class="font-medium">{{ employee.date_of_birth ? formatDate(employee.date_of_birth) : '-' }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="alert alert-error">
        ไม่พบข้อมูลพนักงาน
      </div>
    </div>
  </UserLayout>
</template>
