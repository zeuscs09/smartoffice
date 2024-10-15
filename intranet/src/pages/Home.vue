<template>
  <UserLayout>

    <div class="space-y-6">
      <!-- Heatmap Section -->
      <div class="bg-base-100 p-4 rounded-lg shadow w-full">
        <div class="flex justify-between items-center mb-2 cursor-pointer" @click="toggleHeatmap">
          <h2 class="text-xl font-bold">สถิติงานรายเดือน</h2>
          <span class="text-2xl">{{ isHeatmapExpanded ? '▲' : '▼' }}</span>
        </div>
        <transition name="collapse">
          <div v-show="isHeatmapExpanded" class="overflow-hidden">
            <div v-if="heatmapResource.loading" class="flex justify-center items-center h-40">
              <span class="loading loading-spinner loading-lg"></span>
            </div>
            <div v-else-if="heatmapResource.error" class="text-center py-8">
              <p class="text-error">เกิดข้อผิดพลาดในการโหลดข้อมูล Heatmap</p>
            </div>
            <CalendarHeatmap v-else :values="heatmapData" :end-date="endDateHeatmap" :tooltip-unit="'งาน'"
              :range-color="['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']" :max="5" :round="0"
              class="w-full" />
          </div>
        </transition>
      </div>

      <!-- Dashboard and Tasks Section -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Dashboard Section -->
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-base-100 p-6 rounded-lg shadow">
            <h2 class="text-2xl font-bold mb-4">แดชบอร์ด</h2>
            <!-- Display Current Period -->
            <div class="text-sm text-gray-500 mb-4" v-if="dashboardData.period">
              ช่วงเวลาปัจจุบัน: {{ formatDate(dashboardData.period.current.start) }} - {{
                formatDate(dashboardData.period.current.end) }}
            </div>
            <!-- Time Range Selector -->
            <div class="flex justify-end mb-4">
              <select v-model="selectedTimeRange" class="select select-bordered w-full max-w-xs">
                <option value="week">สัปดาห์นี้</option>
                <option value="month">เดือนนี้</option>
                <option value="year">ปีนี้</option>
              </select>
            </div>
            <div v-if="dashboardResource.loading" class="flex justify-center items-center h-40">
              <span class="loading loading-spinner loading-lg"></span>
            </div>
            <div v-else-if="dashboardResource.error" class="text-center py-8">
              <p class="text-error">เกิดข้อผิดพลาดในการโหลดข้อมูล</p>
            </div>
            <div v-else>
              <!-- Summary Cards -->
              <div class="stats shadow w-full">
                <DashboardCard title="งานทั้งหมด" :value="dashboardData.total_tasks.value"
                  :previous="dashboardData.total_tasks.previous" icon="📊" color="primary"
                  :desc="formatChangeDescription(dashboardData.total_tasks.change)" />
                <DashboardCard title="งานด่วน" :value="dashboardData.urgent_tasks.value"
                  :previous="dashboardData.urgent_tasks.previous" icon="🚨" color="warning"
                  :desc="formatChangeDescription(dashboardData.urgent_tasks.change)" />
                <DashboardCard title="งานเสร็จสิ้น" :value="dashboardData.completed_tasks.value"
                  :previous="dashboardData.completed_tasks.previous" icon="✅" color="success"
                  :desc="formatChangeDescription(dashboardData.completed_tasks.change)" />
              </div>
            </div>
          </div>

          <div class="bg-base-100 p-6 rounded-lg shadow">
            <div role="tablist" class="tabs tabs-bordered mb-4">
              <a role="tab" class="tab" :class="{ 'tab-active': activeTab === 'service_report' }" @click="activeTab = 'service_report'">Service Report</a>
              <a role="tab" class="tab" :class="{ 'tab-active': activeTab === 'expense_entry' }" @click="activeTab = 'expense_entry'">Expense Entry</a>
              <a role="tab" class="tab" :class="{ 'tab-active': activeTab === 'expense_request' }" @click="activeTab = 'expense_request'">Expense Request</a>
              <a role="tab" class="tab" :class="{ 'tab-active': activeTab === 'advance_request' }" @click="activeTab = 'advance_request'">Advance Request</a>
            </div>

            <div v-if="documentsResource.loading" class="flex justify-center items-center h-40">
              <span class="loading loading-spinner loading-lg"></span>
            </div>
            <div v-else-if="documentsResource.error" class="text-center py-8">
              <p class="text-error">เกิดข้อผิดพลาดในการโหลดข้อมูล</p>
            </div>
            <div v-else>
              <table class="table table-zebra w-full">
                <thead>
                  <tr>
                    <th>เลขที่เอกสาร</th>
                    <th>วันที่</th>
                    <th>สถานะ</th>
                    <th>การดำเนินการ</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="doc in documents" :key="doc.name">
                    <td>{{ doc.name }}</td>
                    <td>{{ formatDate(doc.creation) }}</td>
                    <td>
                      <span :class="getStatusClass(doc.status)">{{ doc.status }}</span>
                    </td>
                    <td>
                      <button class="btn btn-sm btn-primary" @click="viewDocument(doc.name)">ดู</button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div class="text-right mt-4">
                <button class="btn btn-link" @click="viewAllDocuments">ดูทั้งหมด</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Tasks List -->
        <div class="lg:col-span-1">
          <div class="bg-base-100 p-6 rounded-lg shadow">
            <h2 class="text-xl font-bold mb-4">งานคงค้าง</h2>
            <div v-if="todosResource.loading" class="flex justify-center items-center h-40">
              <span class="loading loading-spinner loading-lg"></span>
            </div>
            <div v-else-if="todosResource.error" class="text-center py-8">
              <p class="text-error">เกิดข้อผิดพลาดในการโหลดข้อมูล</p>
            </div>
            <div v-else-if="todos.length === 0" class="text-center py-8">
              <p class="text-gray-500">ไม่พบงานในขณะนี้</p>
            </div>
            <div v-else class="space-y-4">
              <TaskCard v-for="todo in todos" :key="todo.name" :todo="todo" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </UserLayout>
</template>

<script setup lang="ts">
import UserLayout from '@/layouts/userLayout.vue'
import { createResource } from 'frappe-ui'
import { computed, ref, onMounted, watch } from 'vue'
import DashboardCard from '@/components/DashboardCard.vue'
import TaskCard from '@/components/TaskCard.vue'
import { Chart, registerables } from 'chart.js'
import { CalendarHeatmap } from 'vue3-calendar-heatmap'

Chart.register(...registerables)

// เพิ่มฟังก์ชัน getLastDayOfMonth
const getLastDayOfMonth = (date: Date): Date => {
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  console.log(new Date(year, month, 0))
  return new Date(year, month, 0);
}

interface Todo {
  name: string
  description: string
  status: string
  allocated_to: string
  reference_name: string
  project: string
  site_name: string
  contact_person: string
  contact_phone: string
  contact_email: string
  start_date: string
  finish_date: string
  job_type: string
  priority: string
  due_date: string
}

const todosResource = createResource({
  url: 'smartoffice.api.task.get_todos_with_smo_tasks',
  auto: true,
})

const todos = computed<Todo[]>(() => todosResource.data || [])

const endDateHeatmap = ref(getLastDayOfMonth(new Date()))
const selectedTimeRange = ref('week')

// เพิ่ม watch เพื่อติดตามการเปลี่ยนแปลงของ selectedTimeRange
watch(selectedTimeRange, (newValue) => {
  console.log('Time range changed to:', newValue)
  fetchDashboardData()
})

const dashboardResource = createResource({
  url: 'smartoffice.api.dashboard.get_dashboard_home',
  method: 'POST',
  auto: false,
})

// สร้าง resource สำหรับ Heatmap
const heatmapResource = createResource({
  url: 'smartoffice.api.dashboard.get_heatmap_data',
  auto: true,
})

// สร้าง ref สำหรับเก็บข้อมูล heatmap
const heatmapData = ref([])

// ฟังก์ชันสำหรับแปลงข้อมูลจาก API เป็นรูปแบบที่ Heatmap ต้องการ
const formatHeatmapData = (data) => {
  return Object.entries(data).map(([date, count]) => ({
    date,
    count
  }))
}

// โหลดข้อมูล Heatmap
const fetchHeatmapData = () => {
  heatmapResource.submit()
    .then((response) => {
      heatmapData.value = formatHeatmapData(response)
    })
    .catch((error) => {
      console.error('เกิดข้อผิดพลาดในการดึงข้อมูล Heatmap:', error)
    })
}

onMounted(() => {
  console.log('Component mounted')
  fetchDashboardData()
  fetchHeatmapData()

  const savedState = localStorage.getItem('heatmapExpanded')
  if (savedState !== null) {
    isHeatmapExpanded.value = savedState === 'true'
  }
})

const fetchDashboardData = () => {
  console.log('Fetching dashboard data for:', selectedTimeRange.value)
  dashboardResource.submit({
    time_range: selectedTimeRange.value
  })
    .then((response) => {
      console.log('Dashboard data received:', response)
      dashboardData.value = {
        total_tasks: {
          value: response.total_tasks.current,
          previous: response.total_tasks.previous,
          change: response.total_tasks.change
        },
        urgent_tasks: {
          value: response.urgent_tasks.current,
          previous: response.urgent_tasks.previous,
          change: response.urgent_tasks.change
        },
        completed_tasks: {
          value: response.completed_tasks.current,
          previous: response.completed_tasks.previous,
          change: response.completed_tasks.change
        },
        period: response.period
      }
    })
    .catch((error) => {
      console.error('เกิดข้อผิดพลาดในการดึงข้อมูล Dashboard:', error)
    })
}

interface DashboardData {
  total_tasks: { value: number; previous: number; change: number }
  urgent_tasks: { value: number; previous: number; change: number }
  completed_tasks: { value: number; previous: number; change: number }
  period: { current: { start: string; end: string } }
  daily_tasks: { [date: string]: number }
}

const dashboardData = ref<DashboardData>({
  total_tasks: { value: 0, previous: 0, change: 0 },
  urgent_tasks: { value: 0, previous: 0, change: 0 },
  completed_tasks: { value: 0, previous: 0, change: 0 },
  period: { current: { start: '', end: '' } },
  daily_tasks: {}
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const year = date.getFullYear().toString().slice(-2)
  return `${day}/${month}/${year}`
}

const viewTask = (todo: Todo) => {
  window.location.href = `/app/smo-task/${todo.reference_name}`
}

const createServiceReport = (todo: Todo) => {
  window.location.href = `/app/smo-service-report/new?from_todo=${todo.name}&from_page=intranet&task=${todo.reference_name}`
}

const formatChangeDescription = (change: number) => {
  const absChange = Math.abs(change)
  const direction = change >= 0 ? 'มากกว่า' : 'น้อยกว่า'
  return `${absChange.toFixed(0)}% ${direction}${selectedTimeRange.value === 'week' ? 'สัปดาห์' : selectedTimeRange.value === 'month' ? 'เดือน' : 'ปี'}ที่แล้ว`
}

// ใช้ ref เพื่อเก็บสถานะ Heatmap
const isHeatmapExpanded = ref(false)

// ฟังก์ชันสำหรับ toggle Heatmap
const toggleHeatmap = () => {
  isHeatmapExpanded.value = !isHeatmapExpanded.value
  // บันทึกสถานะลง localStorage
  localStorage.setItem('heatmapExpanded', isHeatmapExpanded.value.toString())
}

const activeTab = ref('service_report')
const documents = ref([])

const documentsResource = createResource({
  url: 'smartoffice.api.dashboard.get_recent_documents',
  auto: false,
})

watch(activeTab, () => {
  fetchDocuments()
})

const fetchDocuments = () => {
  documentsResource.submit({
    doctype: activeTab.value,
    limit: 5
  })
    .then((response) => {
      documents.value = response.documents
    })
    .catch((error) => {
      console.error('เกิดข้อผิดพลาดในการดึงข้อมูลเอกสาร:', error)
    })
}

const getStatusClass = (status: string) => {
  switch (status.toLowerCase()) {
    case 'draft': return 'badge badge-warning'
    case 'submitted': return 'badge badge-success'
    case 'cancelled': return 'badge badge-error'
    default: return 'badge'
  }
}

const viewDocument = (docName: string) => {
  window.location.href = `/app/${activeTab.value}/${docName}`
}

const viewAllDocuments = () => {
  window.location.href = `/app/${activeTab.value}`
}
</script>

<style scoped>
.btn-ghost {
  @apply hover:-translate-y-0.5 transition-all duration-200 ease-in-out;
}

canvas {
  width: 100% !important;
  height: 300px !important;
}

/* ปรับขนาดและสไตล์ของ Heatmap */
:deep(.vch__wrapper) {
  max-width: 100%;
  font-size: 7px;
  /* ลดขนาดฟอนต์ลงอีก */
}

:deep(.vch__months__labels) {
  font-size: 9px;
}

:deep(.vch__days__labels) {
  font-size: 9px;
}

:deep(.vch__legend__wrapper) {
  font-size: 9px;
}

/* ปรับนาดของช่อง square ใน heatmap */
:deep(.vch__day__square) {
  width: 8px !important;
  height: 8px !important;
}

/* ปรับระยะห่างระหว่างแถว */
:deep(.vch__days__row) {
  margin-bottom: 1px;
}

/* Animation for collapse/expand */
.collapse-enter-active,
.collapse-leave-active {
  transition: max-height 0.3s ease-out, opacity 0.3s ease-out;
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  opacity: 0;
}

.collapse-enter-to,
.collapse-leave-from {
  max-height: 300px;
  /* ปรับตามความสูงจริงของ Heatmap */
  opacity: 1;
}

.badge {
  @apply px-2 py-1 rounded-full text-xs font-semibold;
}
</style>