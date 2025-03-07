<!-- src/pages/ReportPage.vue -->
<script setup lang="ts">
import { ref, onMounted, inject, computed, watch } from 'vue'
import { useToast } from '@/composables/useToast'
import { utils, writeFile } from 'xlsx'
import UserLayout from '@/layouts/userLayout.vue'
import Multiselect from '@vueform/multiselect'
import '@vueform/multiselect/themes/default.css'

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

interface JobType {
  name: string
  description: string
  group: string
}

interface Department {
  name: string
  description: string
}

interface Grade {
  name: string
  description: string
}

const toast = useToast()
const selectedMonth = ref<string>(new Date().toISOString().slice(0,7))
const isLoading = ref(false)
const reportData = ref<TaskReport[]>([])
const ungroupTaskType = ref(false)
const ungroupEngineer = ref(false)
const selectedJobTypes = ref<string[]>([])
const selectedDepartments = ref<string[]>([])
const selectedGrades = ref<string[]>([])

const jobTypes = ref<JobType[]>([])
const departments = ref<Department[]>([])
const grades = ref<Grade[]>([])

// เพิ่ม ref สำหรับเก็บค่าประเภทรายงาน
const reportType = ref<'task' | 'service_report'>('task')

// แป้ไขการ format วันที่
const formattedMonth = computed(() => {
  if (!selectedMonth.value) return ''
  const date = new Date(selectedMonth.value + '-01')
  return date.toLocaleDateString('en-US', { 
    month: 'long',
    year: 'numeric'
  })
})

// เพิ่ม computed property สำหรับจัดกลุ่ม Job Types
const groupedJobTypes = computed(() => {
  const groups: { [key: string]: JobType[] } = {}
  
  jobTypes.value.forEach(type => {
    const group = type.group || 'Other'
    if (!groups[group]) {
      groups[group] = []
    }
    groups[group].push(type)
  })

  return Object.entries(groups).map(([name, items]) => ({
    name,
    items
  }))
})

// เพิ่ม refs สำหรับควบคุม dropdown
const jobTypeDropdownOpen = ref(false)
const departmentDropdownOpen = ref(false)
const gradeDropdownOpen = ref(false)

// เพิ่ม refs สำหรับการค้นหา
const jobTypeSearch = ref('')
const departmentSearch = ref('')
const gradeSearch = ref('')

// computed สำหรับแสดงรายการที่เลือก
const selectedJobTypeLabels = computed(() => {
  return selectedJobTypes.value.map(name => {
    const item = jobTypes.value.find(j => j.name === name)
    return item?.description || name
  })
})

const selectedDepartmentLabels = computed(() => {
  return selectedDepartments.value.map(name => {
    const item = departments.value.find(d => d.name === name)
    return item?.description || name
  })
})

const selectedGradeLabels = computed(() => {
  return selectedGrades.value.map(name => {
    const item = grades.value.find(g => g.name === name)
    return item?.description || name
  })
})

// เพิ่ม computed properties สำหรับกรองรายการตามคำค้นหา
const filteredJobTypes = computed(() => {
  const search = jobTypeSearch.value.toLowerCase()
  return groupedJobTypes.value.map(group => ({
    name: group.name,
    items: group.items.filter(item => 
      item.name.toLowerCase().includes(search) || 
      (item.description?.toLowerCase().includes(search))
    )
  })).filter(group => group.items.length > 0)
})

const filteredDepartments = computed(() => {
  const search = departmentSearch.value.toLowerCase()
  return departments.value.filter(dept =>
    dept.name.toLowerCase().includes(search) ||
    (dept.description?.toLowerCase().includes(search))
  )
})

const filteredGrades = computed(() => {
  const search = gradeSearch.value.toLowerCase()
  return grades.value.filter(grade =>
    grade.name.toLowerCase().includes(search) ||
    (grade.description?.toLowerCase().includes(search))
  )
})

// แก้ไข interface สำหรับ options
interface SelectOption {
  value: string
  label: string
}

interface GroupedOption {
  label: string
  options: SelectOption[]
}

// เพิ่ม refs สำหรับเก็บค่าที่เลือก (เก็บเป็น object แทน string)
const selectedJobTypeValues = ref<SelectOption[]>([])
const selectedDepartmentValues = ref<SelectOption[]>([])
const selectedGradeValues = ref<SelectOption[]>([])

// แก้ไข computed properties สำหรับ options และการแปลงค่า
const jobTypeOptions = computed((): GroupedOption[] => {
  // จัดกลุ่มตาม group
  const groups = jobTypes.value.reduce((acc, type) => {
    const group = type.group || 'Other'
    if (!acc[group]) {
      acc[group] = []
    }
    acc[group].push({
      value: type.name,
      label: type.name // ใช้ name แทน description ที่เป็น null
    })
    return acc
  }, {} as Record<string, SelectOption[]>)

  // แปลงเป็น array ของ groups
  return Object.entries(groups).map(([groupName, options]) => ({
    label: groupName,
    options: options
  }))
})

const departmentOptions = computed((): SelectOption[] => {
  return departments.value.map(dept => ({
    value: dept.name,
    label: dept.name.replace(/\s*-\s*TPS$/, '') // ลบ "- TPS" ออกจากชื่อ
  }))
})

const gradeOptions = computed((): SelectOption[] => {
  return grades.value.map(grade => ({
    value: grade.name,
    label: grade.name // ใช้ name เป็น label
  }))
})

// computed สำหรับแปลงค่าที่เลือกเป็น array ของ values สำหรับส่งไป API
const selectedJobTypeNames = computed(() => selectedJobTypeValues.value.map(opt => opt))
const selectedDepartmentNames = computed(() => selectedDepartmentValues.value.map(opt => opt))
const selectedGradeNames = computed(() => selectedGradeValues.value.map(opt => opt))

// แก้ไข interface สำหรับ criteria
interface ReportCriteria {
  month: string
  jobTypes: SelectOption[]
  departments: SelectOption[]
  grades: SelectOption[]
  ungroupTaskType: boolean
  ungroupEngineer: boolean
  reportType: 'task' | 'service_report'
}

// เพิ่ม key สำหรับ localStorage
const STORAGE_KEY = 'manhour-report-criteria'

// เพิ่มฟังก์ชันสำหรับจัดการ criteria
const saveCriteria = () => {
  const criteria: ReportCriteria = {
    month: selectedMonth.value,
    jobTypes: selectedJobTypeValues.value,
    departments: selectedDepartmentValues.value,
    grades: selectedGradeValues.value,
    ungroupTaskType: ungroupTaskType.value,
    ungroupEngineer: ungroupEngineer.value,
    reportType: reportType.value
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(criteria))
}

const loadCriteria = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const criteria: ReportCriteria = JSON.parse(saved)
      selectedMonth.value = criteria.month
      selectedJobTypeValues.value = criteria.jobTypes
      selectedDepartmentValues.value = criteria.departments
      selectedGradeValues.value = criteria.grades
      ungroupTaskType.value = criteria.ungroupTaskType
      ungroupEngineer.value = criteria.ungroupEngineer
      reportType.value = criteria.reportType || 'task'
    }
  } catch (err) {
    console.error('Error loading criteria:', err)
    // ถ้าโหลดไม่สำเร็จให้ใช้ค่าเริ่มต้น (ที่กำหนดไว้แล้วใน ref)
  }
}

// แก้ไขฟังก์ชัน fetchReport ให้บันทึก criteria
const fetchReport = async () => {
  try {
    isLoading.value = true
    saveCriteria()
    
    // เลือก endpoint ตามประเภทรายงาน
    const endpoint = reportType.value === 'task' 
      ? '/api/method/smartoffice.api.report.get_manhour_report_by_task'
      : '/api/method/smartoffice.api.report.get_manhour_report'
    
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        month: selectedMonth.value,
        job_types: selectedJobTypeValues.value,
        departments: selectedDepartmentValues.value,
        grades: selectedGradeValues.value,
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

// ปรับฟังก์ชัน formatHourMinute ใหม่
const formatHourMinute = (minutes: number) => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  const hourText = hours > 0 ? `${hours} hour${hours > 1 ? 's' : ''}` : ''
  const minText = mins > 0 ? `${mins} min${mins > 1 ? 's' : ''}` : ''
  
  if (hours > 0 && mins > 0) {
    return `${hourText} ${minText}`
  }
  return hourText || minText || '0 mins'
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
    const excelData = reportData.value.map(item => ({
      'Project Code': item.project_code,
      'Customer': item.customer_name,
      'Project Name': item.project_name,
      'Task Type': item.task_type,
      'Engineer': item.engineer,
      'Tasks': item.task_count,
      'Total Min': item.minutes,
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
        'Total Min': totals.value.minutes,
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
      { wch: 10 }, // Total Min
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

// แก้ไขฟังก์ชัน fetchFilterOptions
const fetchFilterOptions = async () => {
  try {
    // ดึงข้อมูล Job Types
    const jobTypesResponse = await fetch('/api/method/frappe.client.get_list', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doctype: 'SMO Job Type',
        fields: ['name', 'description', 'group'],
        order_by: 'name asc'
      })
    })
    const jobTypesResult = await jobTypesResponse.json()
    console.log('Job Types:', jobTypesResult)
    jobTypes.value = jobTypesResult.message

    // ดึงข้อมูล Departments
    const deptsResponse = await fetch('/api/method/frappe.desk.reportview.get', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doctype: 'Department',
        fields: ['name', 'department_name'],
        filters: [
          ['disabled', '=', 0],
          ['department_name', '!=', 'All Departments']
        ],
        order_by: 'department_name asc'
      })
    })
    const deptsResult = await deptsResponse.json() as ApiResponse
   
    // แก้ไขการ map ข้อมูล departments
    departments.value = deptsResult.message.values.map(([name]) => ({
      name,
      description: name.replace(/\s*-\s*TPS$/, '')
    }))

    // แก้ไขการดึงข้อมูล Employee Grade
    const gradesResponse = await fetch('/api/method/frappe.desk.reportview.get', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        doctype: 'Employee Grade',
        fields: ['name'],
        order_by: 'name asc'
      })
    })
    const gradesResult = await gradesResponse.json() as ApiResponse
    console.log('Grades:', gradesResult)
    
    // แก้ไขการ map ข้อมูล grades
    grades.value = gradesResult.message.values.map(([name]) => ({
      name,
      description: name
    }))

    // Log ข้อมูลหลังจาก map
    console.log('Mapped Departments:', departments.value)
    console.log('Mapped Grades:', grades.value)
  } catch (err) {
    console.error('Error fetching filter options:', err)
    toast.error('เกิดข้อผิดพลาดในการดึงข้อมูลตัวกรอง')
  }
}

// เพิ่ม watch เพื่อดู การเปลี่ยนแปลงของค่าที่เลือก
watch([selectedJobTypeValues, selectedDepartmentValues, selectedGradeValues], 
  ([jobs, depts, grades]) => {
    console.log('Selected Job Types:', jobs)
    console.log('Selected Departments:', depts)
    console.log('Selected Grades:', grades)
  },
  { deep: true }
)

// เพิ่ม computed property สำหรับตรวจสอบการเลือก
const hasAnySelection = computed(() => {
  return selectedJobTypeValues.value.length > 0 ||
         selectedDepartmentValues.value.length > 0 ||
         selectedGradeValues.value.length > 0
})

// เพิ่มฟังก์ชันสำหรับลบรายการที่เลือก
const removeJobType = (item: SelectOption) => {
  selectedJobTypeValues.value = selectedJobTypeValues.value.filter(i => i !== item)
  fetchReport()
}

const removeDepartment = (item: SelectOption) => {
  selectedDepartmentValues.value = selectedDepartmentValues.value.filter(i => i !== item)
  fetchReport()
}

const removeGrade = (item: SelectOption) => {
  selectedGradeValues.value = selectedGradeValues.value.filter(i => i !== item)
  fetchReport()
}

// เพิ่ม watch สำหรับ ungroup options
watch([ungroupTaskType, ungroupEngineer], () => {
  fetchReport() // ดึงข้อมูลใหม่เมื่อมีการเปลี่ยนแปลง ungroup options
})

// เพิ่ม watch สำหรับ reportType
watch(reportType, () => {
  fetchReport()
})

onMounted(async () => {
  await fetchFilterOptions()
  loadCriteria() // โหลด criteria จาก localStorage
  fetchReport() // ดึงข้อมูลด้วย criteria ที่โหลดมา
})
</script>

<template>
  <UserLayout>
    <div class="p-6">
      <!-- Header Section -->
      <div class="flex flex-col gap-6">
        <!-- Title -->
        <div>
          <h1 class="text-2xl font-bold">Manhour Report</h1>
          <p class="text-gray-600">{{ formattedMonth }}</p>
        </div>

        <!-- Main Controls -->
        <div class="flex flex-col gap-4 p-4 bg-base-100 rounded-lg border border-base-200">
          <!-- Report Type and Date -->
          <div class="flex items-center gap-8">
            <!-- Report Type Selection -->
            <div class="flex items-center gap-6 min-w-[400px]">
              <label class="label-radio">
                <input 
                  type="radio" 
                  name="report-type"
                  value="task"
                  v-model="reportType"
                  class="radio radio-sm radio-primary"
                />
                <span class="label-text font-medium">Report from Task</span>
              </label>

              <label class="label-radio">
                <input 
                  type="radio" 
                  name="report-type"
                  value="service_report"
                  v-model="reportType"
                  class="radio radio-sm radio-primary"
                />
                <span class="label-text font-medium">Report from Service Report</span>
              </label>
            </div>

            <!-- Month Selection -->
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium">Period:</span>
              <input 
                type="month"
                v-model="selectedMonth"
                class="input input-bordered input-sm w-40"
              />
            </div>

            <!-- Action Buttons -->
            <div class="flex items-center gap-2 ml-auto">
              <button 
                class="btn btn-primary btn-sm gap-2"
                @click="fetchReport"
                :disabled="isLoading"
              >
                <i class="fas fa-sync-alt text-sm"></i>
                Refresh
              </button>
              <button 
                class="btn btn-outline btn-sm gap-2"
                @click="exportToExcel"
                :disabled="isLoading || !reportData.length"
              >
                <i class="fas fa-file-excel text-sm"></i>
                Export Excel
              </button>
            </div>
          </div>

          <!-- Selected Criteria Badges -->
          <div class="flex flex-wrap gap-2 mt-4">
            <!-- Job Type Badges -->
            <div v-for="item in selectedJobTypeValues" :key="item" 
              class="badge badge-primary gap-1 py-3 px-3"
            >
              <span>{{ item }}</span>
              <button 
                class="btn btn-ghost btn-xs px-1 min-h-0 h-auto hover:bg-transparent"
                @click="removeJobType(item)"
              >
                ×
              </button>
            </div>

            <!-- Department Badges -->
            <div v-for="item in selectedDepartmentValues" :key="item"
              class="badge badge-primary gap-1 py-3 px-3"
            >
              <span>{{ item }}</span>
              <button 
                class="btn btn-ghost btn-xs px-1 min-h-0 h-auto hover:bg-transparent"
                @click="removeDepartment(item)"
              >
                ×
              </button>
            </div>

            <!-- Grade Badges -->
            <div v-for="item in selectedGradeValues" :key="item"
              class="badge badge-primary gap-1 py-3 px-3"
            >
              <span>{{ item }}</span>
              <button 
                class="btn btn-ghost btn-xs px-1 min-h-0 h-auto hover:bg-transparent"
                @click="removeGrade(item)"
              >
                ×
              </button>
            </div>

            <!-- Show placeholder if no selections -->
            <div v-if="!hasAnySelection" class="text-gray-500 text-sm">
              No filters selected
            </div>
          </div>

          <!-- Filters -->
          <div class="grid grid-cols-3 gap-6">
            <!-- Job Types Filter -->
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Job Types</span>
              </label>
              <Multiselect
                v-model="selectedJobTypeValues"
                :options="jobTypeOptions"
                mode="multiple"
                :searchable="true"
                :groups="true"
                placeholder="Select job types..."
                class="multiselect-primary"
                label="label"
                track-by="value"
                group-label="label"
                group-values="options"
              />
            </div>

            <!-- Departments Filter -->
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Departments</span>
              </label>
              <Multiselect
                v-model="selectedDepartmentValues"
                :options="departmentOptions"
                mode="multiple"
                :searchable="true"
                placeholder="Select departments..."
                class="multiselect-primary"
                label="label"
                track-by="value"
              />
            </div>

            <!-- Grades Filter -->
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Grades</span>
              </label>
              <Multiselect
                v-model="selectedGradeValues"
                :options="gradeOptions"
                mode="multiple"
                :searchable="true"
                placeholder="Select grades..."
                class="multiselect-primary"
                label="label"
                track-by="value"
              />
            </div>
          </div>

          <!-- Additional Options -->
          <div class="flex items-center gap-6 pt-2 border-t border-base-200">
            <label class="label-checkbox">
              <input 
                type="checkbox" 
                v-model="ungroupTaskType"
                class="checkbox checkbox-sm checkbox-primary"
              />
              <span class="label-text text-sm">Ungroup Task Type</span>
            </label>

            <label class="label-checkbox">
              <input 
                type="checkbox" 
                v-model="ungroupEngineer"
                class="checkbox checkbox-sm checkbox-primary"
              />
              <span class="label-text text-sm">Ungroup Engineer</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Table Section -->
      <div class="mt-6">
        <div v-if="isLoading" class="flex justify-center py-8">
          <span class="loading loading-spinner loading-lg"></span>
        </div>

        <div v-else class="overflow-x-auto bg-white rounded-lg shadow">
          <table class="table table-zebra w-full table-sm">
            <thead>
              <tr class="bg-base-200">
                <th>Project Code</th>
                <th>Customer</th>
                <th>Project Name</th>
                <th>Task Type</th>
                <th>Engineer</th>
                <th class="text-right">Tasks</th>
                <th class="text-right">Total Min</th>
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
                <td class="text-right">{{ item.minutes }}</td>
                <td class="text-right">{{ formatHourMinute(item.minutes) }}</td>
                <td class="text-right">{{ (item.percent_hour).toFixed(2) }}%</td>
                <td class="text-right">{{ (item.percent_task).toFixed(2) }}%</td>
              </tr>
              
              <tr v-if="totals" class="font-bold bg-base-200">
                <td colspan="5" class="text-right">Total</td>
                <td class="text-right">{{ totals.taskCount }}</td>
                <td class="text-right">{{ totals.minutes }}</td>
                <td class="text-right">{{ formatHourMinute(totals.minutes) }}</td>
                <td class="text-right">{{ totals.percentHour.toFixed(2) }}%</td>
                <td class="text-right">{{ totals.percentTask.toFixed(2) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </UserLayout>
</template>

<style scoped>
.label-radio,
.label-checkbox {
  @apply flex items-center cursor-pointer hover:bg-base-200/50 px-3 py-1.5 rounded-md transition-colors;
}

.label-radio .label-text,
.label-checkbox .label-text {
  @apply ml-2;
}

.multiselect-primary {
  --ms-tag-bg: hsl(var(--p));
  --ms-tag-color: hsl(var(--pc));
  --ms-ring-color: hsl(var(--p) / 0.2);
  --ms-option-bg-selected: hsl(var(--p) / 0.1);
  --ms-option-color-selected: hsl(var(--p));
}

.table th {
  @apply text-base-content/70 font-medium;
}

.table td {
  @apply text-sm;
}

.table tr.bg-base-200 {
  background-color: hsl(var(--b2) / 0.3);
}

.badge {
  @apply font-normal text-sm flex items-center;
}

.badge button {
  @apply ml-1 text-current opacity-60 hover:opacity-100 flex items-center justify-center text-lg font-medium leading-none;
}

/* ปรับแต่ง badge เมื่อ hover */
.badge:hover {
  @apply shadow-sm;
}

/* ปรับแต่ง close button เมื่อ hover */
.badge button:hover {
  @apply bg-transparent;
}
</style>