<!-- src/pages/ReportPage.vue -->
<script setup lang="ts">
import { ref, onMounted, inject, computed } from 'vue'
import { useToast } from '@/composables/useToast'
import { utils, writeFile } from 'xlsx'
import UserLayout from '@/layouts/userLayout.vue'

// inject formatters
const formatDate = inject('formatDate') as (date: string) => string
const formatDuration = inject('formatDuration') as (minutes: number) => string

interface TaskReport {
  project_code: string
  customer_name: string 
  project_name: string
  task_type: string
  engineer: string
  task_count: number
  hours: string
  minutes: number
  percent_hour: number
  percent_task: number
}

const toast = useToast()
const selectedMonth = ref<string>(new Date().toISOString().slice(0,7))
const isLoading = ref(false)
const reportData = ref<TaskReport[]>([])
const ungroupTaskType = ref(false)
const ungroupEngineer = ref(false)

// แป้ไขการ format วันที่
const formattedMonth = computed(() => {
  if (!selectedMonth.value) return ''
  const date = new Date(selectedMonth.value + '-01')
  return date.toLocaleDateString('en-US', { 
    month: 'long',
    year: 'numeric'
  })
})

const fetchReport = async () => {
  isLoading.value = true
  try {
    const response = await fetch('/api/method/smartoffice.api.report.get_manhour_report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        month: selectedMonth.value,
        ungroup_task_type: ungroupTaskType.value ? 1 : 0,
        ungroup_engineer: ungroupEngineer.value ? 1 : 0
      })
    })
    const result = await response.json()
    
    if (result.message?.status === 'success') {
      reportData.value = result.message.data
    } else {
      toast.error(result.message?.message || 'เกิดข้อผิดพลาดในการดึงข้อมูล')
    }
  } catch (err) {
    console.error('API Error:', err)
    toast.error('เกิดข้อผิดพลาดในการดึงข้อมูล')
  } finally {
    isLoading.value = false
  }
}

// Format duration helper
const formatHourMinute = (minutes: number) => {
  return formatDuration(minutes)
}

// เพิ่ม computed properties สำหรับคำนวณ totals
const totals = computed(() => {
  if (!reportData.value.length) return null
  
  return {
    taskCount: reportData.value.reduce((sum, item) => sum + item.task_count, 0),
    minutes: reportData.value.reduce((sum, item) => sum + item.minutes, 0),
    percentHour: 100, // รวมต้องได้ 100%
    percentTask: 100  // รวมต้องได้ 100%
  }
})

const exportToExcel = () => {
  try {
    // สร้างข้อมูลสำหรับ Excel
    const excelData = reportData.value.map(item => ({
      'Project Code': item.project_code,
      'Customer': item.customer_name,
      'Project Name': item.project_name,
      'Task Type': item.task_type,
      'Engineer': item.engineer,
      'Tasks': item.task_count,
      'Hours': formatHourMinute(item.minutes),
      '% Hour': `${item.percent_hour.toFixed(2)}%`,
      '% Tasks': `${item.percent_task.toFixed(2)}%`
    }))

    // เพิ่มแถว Total
    if (totals.value) {
      excelData.push({
        'Project Code': '',
        'Customer': '',
        'Project Name': '',
        'Task Type': '',
        'Engineer': 'รวมทั้งหมด',
        'Tasks': totals.value.taskCount,
        'Hours': formatHourMinute(totals.value.minutes),
        '% Hour': `${totals.value.percentHour.toFixed(2)}%`,
        '% Tasks': `${totals.value.percentTask.toFixed(2)}%`
      })
    }

    // สร้าง workbook
    const ws = utils.json_to_sheet(excelData)
    const wb = utils.book_new()
    utils.book_append_sheet(wb, ws, 'Manhour Report')

    // กำหนดความกว้างคอลัมน์
    const colWidths = [
      { wch: 15 }, // Project Code
      { wch: 20 }, // Customer
      { wch: 30 }, // Project Name
      { wch: 15 }, // Task Type
      { wch: 25 }, // Engineer
      { wch: 10 }, // Tasks
      { wch: 10 }, // Hours
      { wch: 10 }, // % Hour
      { wch: 10 }  // % Tasks
    ]
    ws['!cols'] = colWidths

    // สร้างชื่อไฟล์
    const fileName = `manhour-report-${selectedMonth.value}.xlsx`

    // บันทึกไฟล์
    writeFile(wb, fileName)
    
    toast.success('ส่งออกข้อมูลสำเร็จ')
  } catch (err) {
    console.error('Export Error:', err)
    toast.error('เกิดข้อผิดพลาดในการส่งออกข้อมูล')
  }
}

onMounted(() => {
  fetchReport()
})
</script>

<template>
  <UserLayout>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Manhour Report</h1>
        <p class="text-gray-600">{{ formattedMonth }}</p>
      </div>
      
      <div class="flex gap-4 items-center">
        <!-- เลือกเดือน/ปี -->
        <input 
          type="month"
          v-model="selectedMonth"
          class="input input-bordered input-sm"
          @change="fetchReport"
        />

        <!-- Ungroup Options -->
        <div class="flex gap-2">
          <label class="label cursor-pointer gap-2">
            <input 
              type="checkbox" 
              v-model="ungroupTaskType"
              class="checkbox checkbox-sm"
              @change="fetchReport"
            />
            <span class="label-text text-sm">Ungroup Task Type</span>
          </label>

          <label class="label cursor-pointer gap-2">
            <input 
              type="checkbox" 
              v-model="ungroupEngineer"
              class="checkbox checkbox-sm"
              @change="fetchReport"
            />
            <span class="label-text text-sm">Ungroup Engineer</span>
          </label>
        </div>

        <!-- ปุ่ม Export -->
        <button 
          class="btn btn-ghost btn-sm"
          @click="exportToExcel"
          :disabled="isLoading || !reportData.length"
        >
          Export Excel
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="table table-zebra w-full table-xs">
        <thead>
          <tr>
            <th>Project Code</th>
            <th>Customer</th>
            <th>Project Name</th>
            <th>Task Type</th>
            <th>Engineer</th>
            <th class="text-right">Tasks</th>
            <th class="text-right">Hours</th>
            <th class="text-right">% Hour</th>
            <th class="text-right">% Tasks</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in reportData" :key="item.project_code">
            <td>{{ item.project_code }}</td>
            <td>{{ item.customer_name }}</td>
            <td>{{ item.project_name }}</td>
            <td>{{ item.task_type }}</td>
            <td>{{ item.engineer }}</td>
            <td class="text-right">{{ item.task_count }}</td>
            <td class="text-right">{{ formatHourMinute(item.minutes) }}</td>
            <td class="text-right">{{ (item.percent_hour).toFixed(2) }}%</td>
            <td class="text-right">{{ (item.percent_task).toFixed(2) }}%</td>
          </tr>
          
          <!-- Row Total -->
          <tr v-if="totals" class="font-bold bg-base-200">
            <td colspan="5" class="text-right">Total</td>
            <td class="text-right">{{ totals.taskCount }}</td>
            <td class="text-right">{{ formatHourMinute(totals.minutes) }}</td>
            <td class="text-right">{{ totals.percentHour.toFixed(2) }}%</td>
            <td class="text-right">{{ totals.percentTask.toFixed(2) }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  </UserLayout>
</template>

<style scoped>
/* เพิ่ม style สำหรับ row total ถ้าต้องการ */
.bg-base-200 {
  background-color: rgba(var(--b2) / var(--tw-bg-opacity));
  --tw-bg-opacity: 0.3;
}

/* ปรับ label ให้กระชับขึ้น */
.label {
  padding: 0.25rem;
  min-height: auto;
}
</style>