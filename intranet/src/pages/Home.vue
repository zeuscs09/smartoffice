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
            <CalendarHeatmap v-else :values="heatmapData" :end-date="endDateHeatmap" :tooltip-unit="'น'"
              :range-color="['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']" :max="5" :round="0"
              class="w-full" />
          </div>
        </transition>
      </div>

      <!-- Dashboard and Tasks Section -->
      <div class="grid grid-cols-1" :class="{ 'lg:grid-cols-3': todos.length > 0 }">
        <!-- Dashboard Section -->
        <div :class="{ 'lg:col-span-2': todos.length > 0, 'lg:col-span-3': todos.length === 0 }" class="space-y-6">
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
                <DashboardCard 
                  v-for="(card, index) in dashboardCards" 
                  :key="index" 
                  :title="card.title"
                  :icon="card.icon" 
                  :color="card.color" 
                  :value="dashboardData[card.dataKey]?.current ?? 0"
                  :previous="dashboardData[card.dataKey]?.previous ?? 0"
                  :change="dashboardData[card.dataKey]?.change ?? 0"
                  :desc="formatChangeDescription(dashboardData[card.dataKey]?.change)"
                />
              </div>
            </div>
          </div>

          <div class="bg-base-100 p-6 rounded-lg shadow" >
            <div role="tablist" class="tabs tabs-bordered mb-4">
              <a v-for="tab in tabs" :key="tab.value" role="tab" class="tab"
                :class="{ 'tab-active': activeTab === tab.value }" @click="activeTab = tab.value">
                {{ tab.label }}
              </a>
            </div>

            <div v-if="activeTab == 'service_report'">
              <ServiceReportTable
                :data="serviceReportStore.data"
                :loading="serviceReportStore.loading"
                :error="documentsResource.error"
               
                @viewDocument="viewDocument"
                @viewAllDocuments="viewAllDocuments"
              />
            </div>

            <div v-if="activeTab == 'expense_entry'">

            </div>
          </div>
        </div>

        <!-- Tasks List -->
        <div class="lg:col-span-1" v-if="todos.length > 0">
          <div class="bg-base-100 p-6 rounded-lg shadow">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-bold">Task</h2>
              <button class="btn btn-circle btn-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>
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
// 1. การ import
import UserLayout from '@/layouts/userLayout.vue'
import { createResource } from 'frappe-ui'
import { computed, ref, onMounted, watch, inject } from 'vue'
import DashboardCard from '@/components/DashboardCard.vue'
import TaskCard from '@/components/TaskCard.vue'
import { Chart, registerables } from 'chart.js'
import { CalendarHeatmap } from 'vue3-calendar-heatmap'
import { useServiceReportStore } from "@/stores/serviceReportStore"
import { useExpenseEntryStore } from "@/stores/expenseEntryStore"
import { storeToRefs } from 'pinia'
import ServiceReportTable from '@/components/ServiceReportTable.vue'

// 2. การตั้งค่า
Chart.register(...registerables)

// 3. การประกาศตัวแปรและ stores
const serviceReportStore = useServiceReportStore()
const expenseEntryStore = useExpenseEntryStore()
const { data: serviceReportData, loading: serviceReportLoading } = storeToRefs(serviceReportStore)
const formatDate = inject('formatDate') as (date: string) => string
const formatCurrency = inject('formatCurrency') as (amount: number) => string

// 4. ประกาศ interfaces
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

interface DashboardData {
  total_tasks: { value: number; previous: number; change: number }
  urgent_tasks: { value: number; previous: number; change: number }
  completed_tasks: { value: number; previous: number; change: number }
  period: { current: { start: string; end: string } }
  daily_tasks: { [date: string]: number }
}

// 5. ประกาศฟังก์ชัน (ย้ายมาก่อน)
const getLastDayOfMonth = (date: Date): Date => {
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  return new Date(year, month, 0);
}

// 6. ประกาศ refs และ computed properties
const endDateHeatmap = ref(getLastDayOfMonth(new Date()))
const selectedTimeRange = ref('week')
const activeTab = ref('service_report')
const documents = ref([])
const isHeatmapExpanded = ref(false)
const heatmapData = ref([])
const active_tab_data = ref([])
const dashboardData = ref<DashboardData>({
  total_tasks: { value: 0, previous: 0, change: 0 },
  urgent_tasks: { value: 0, previous: 0, change: 0 },
  completed_tasks: { value: 0, previous: 0, change: 0 },
  period: { current: { start: '', end: '' } },
  daily_tasks: {}
})

// 7. ประกาศ resources
const todosResource = createResource({
  url: 'smartoffice.api.task.get_todos_with_smo_tasks',
  auto: true,
})

const heatmapResource = createResource({
  url: 'smartoffice.api.dashboard.get_heatmap_data',
  auto: true,
})

const dashboardResource = createResource({
  url: 'smartoffice.api.dashboard.get_dashboard_home',
  method: 'POST',
  auto: false,
})

const documentsResource = createResource({
  url: 'smartoffice.api.dashboard.get_recent_documents',
  auto: false,
})

// 8. ประกาศ computed properties
const todos = computed<Todo[]>(() => todosResource.data || [])

// 9. ประกาศค่าคงที่
const dashboardCards = [
  { title: "งานทั้งหมด", icon: "📊", color: "primary", dataKey: "total_tasks" },
  { title: "งานด่วน", icon: "🚨", color: "warning", dataKey: "urgent_tasks" },
  { title: "งานเสร็จสิ้น", icon: "✅", color: "success", dataKey: "completed_tasks" }
]

const tabs = [
  { value: 'service_report', label: 'Service Report' },
  { value: 'expense_entry', label: 'Expense Entry' },
  { value: 'expense_request', label: 'Expense Request' },
  { value: 'advance_request', label: 'Advance Request' }
]

// 10. ประกาศฟังก์ชันอื่นๆ
const formatHeatmapData = (data) => {
  return Object.entries(data).map(([date, count]) => ({
    date,
    count
  }))
}

const fetchHeatmapData = () => {
  heatmapResource.submit()
    .then((response) => {
      heatmapData.value = formatHeatmapData(response)
    })
    .catch((error) => {
      console.error('เกิดข้อผิดพลาดในกาดึงข้อมูล Heatmap:', error)
    })
}

const fetchDashboardData = () => {
  console.log('Fetching dashboard data for:', selectedTimeRange.value)
  dashboardResource.submit({
    time_range: selectedTimeRange.value
  })
    .then((response) => {
      console.log('Dashboard data received:', response)
      dashboardData.value = response
    })
    .catch((error) => {
      console.error('เกิดข้อผิดพลาดในการดึงข้อมูล Dashboard:', error)
    })
}

const fetchDocuments = () => {
  
  load_service_report()

}

const load_service_report = async () => {
  console.log('Loading service report...')
  serviceReportStore.pageSize = 10;
  serviceReportStore.fetchAll(1)


}

const load_expense_entry = async () => {
  expenseEntryStore.pageSize = 5;
  await expenseEntryStore.fetchAll(1)

  active_tab_data.value = expenseEntryStore.data.map(item => ({
    name: item.name,
    creation: item.service_date,
    status: item.workflow_state,
    description: item.total_amount
  }))
}

const formatChangeDescription = (change: number | undefined) => {
  if (change === undefined || change === null) return ''
  const absChange = Math.abs(change)
  const direction = change >= 0 ? 'มากกว่า' : 'น้อยกว่า'
  return `${absChange.toFixed(0)}% ${direction}${selectedTimeRange.value === 'week' ? 'สัปดาห์' : selectedTimeRange.value === 'month' ? 'เดือน' : 'ปี'}ที่แล้ว`
}

const toggleHeatmap = () => {
  isHeatmapExpanded.value = !isHeatmapExpanded.value
  localStorage.setItem('heatmapExpanded', isHeatmapExpanded.value.toString())
}



// const viewDocument = (docName: string) => {
//   window.location.href = `/app/${activeTab.value}/${docName}`
// }

// const viewAllDocuments = () => {
//   window.location.href = `/app/${activeTab.value}`
// }

// 11. ประกาศ watchers
watch(selectedTimeRange, (newValue) => {
  console.log('Time range changed to:', newValue)
  fetchDashboardData()
})

// watch(activeTab, () => {
//   fetchDocuments()
// })

// 12. ประกาศ lifecycle hooks
onMounted(async () => {
  console.log('Component mounted')
  fetchDashboardData()
  fetchHeatmapData()

  fetchDocuments()
  console.log('fetchAll completed')

  console.log('Service Report Store:', serviceReportStore)
  console.log('Service Report Data:', serviceReportData.value)
  const savedState = localStorage.getItem('heatmapExpanded')
  if (savedState !== null) {
    isHeatmapExpanded.value = savedState === 'true'
  }
})

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
