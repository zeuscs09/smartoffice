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

// เพิ่ม interface สำหรับ criteria
interface ReportCriteria {
  month: string
  jobTypes: SelectOption[]
  departments: SelectOption[]
  grades: SelectOption[]
  ungroupTaskType: boolean
  ungroupEngineer: boolean
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
    ungroupEngineer: ungroupEngineer.value
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
    saveCriteria() // บันทึก criteria ก่อนดึงข้อมูล
    
    const response = await fetch('/api/method/smartoffice.api.report.get_manhour_report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        month: selectedMonth.value,
        job_types: selectedJobTypeNames.value,
        departments: selectedDepartmentNames.value,
        grades: selectedGradeNames.value,
        ungroup_task_type: ungroupTaskType.value,
        ungroup_engineer: ungroupEngineer.value
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
        filters: [['is_group', '=', 0]],
        order_by: 'name asc'
      })
    })
    const deptsResult = await deptsResponse.json() as ApiResponse
    console.log('Departments:', deptsResult)
    
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

// เพิ่มฟังก์ชันสำหรับลบรายการที่เลือก (ไม่มี fetchReport)
const removeJobType = (item: SelectOption) => {
  selectedJobTypeValues.value = selectedJobTypeValues.value.filter(i => i !== item)
}

const removeDepartment = (item: SelectOption) => {
  selectedDepartmentValues.value = selectedDepartmentValues.value.filter(i => i !== item)
}

const removeGrade = (item: SelectOption) => {
  selectedGradeValues.value = selectedGradeValues.value.filter(i => i !== item)
}

onMounted(async () => {
  await fetchFilterOptions()
  loadCriteria() // โหลด criteria จาก localStorage
  fetchReport() // ดึงข้อมูลด้วย criteria ที่โหลดมา
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
        />

        <!-- Ungroup Options -->
        <div class="flex gap-2">
          <label class="label cursor-pointer gap-2">
            <input 
              type="checkbox" 
              v-model="ungroupTaskType"
              class="checkbox checkbox-sm"
            />
            <span class="label-text text-sm">Ungroup Task Type</span>
          </label>

          <label class="label cursor-pointer gap-2">
            <input 
              type="checkbox" 
              v-model="ungroupEngineer"
              class="checkbox checkbox-sm"
            />
            <span class="label-text text-sm">Ungroup Engineer</span>
          </label>
        </div>

        <!-- ปุ่ม Refresh และ Export -->
        <div class="flex gap-2">
          <button 
            class="btn btn-primary btn-sm"
            @click="fetchReport"
            :disabled="isLoading"
          >
            Refresh
          </button>
          <button 
            class="btn btn-ghost btn-sm"
            @click="exportToExcel"
            :disabled="isLoading || !reportData.length"
          >
            Export Excel
          </button>
        </div>
      </div>
    </div>

    <!-- แก้ไข Filters Section -->
    <div class="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Job Types Filter -->
      <div class="form-control w-full">
        <label class="label">
          <span class="label-text">Job Types</span>
        </label>
        <Multiselect
          v-model="selectedJobTypeValues"
          :options="jobTypeOptions"
          mode="multiple"
          :groups="true"
          placeholder="Select job types..."
          label="label"
          track-by="value"
          group-label="label"
          group-values="options"
          :searchable="true"
          :clear-on-select="false"
          :close-on-select="false"
        />
        <div class="mt-2 flex flex-wrap gap-2">
          <div v-for="item in selectedJobTypeValues" :key="item" 
            class="badge badge-lg badge-primary gap-2 px-3">
            <span class="text-sm">{{ item }}</span>
            <button class="hover:bg-base-200 rounded-full p-1" 
              @click="removeJobType(item)">
              ×
            </button>
          </div>
          <div v-if="!selectedJobTypeValues.length" class="text-sm text-gray-500">
            No job types selected
          </div>
        </div>
      </div>

      <!-- Departments Filter -->
      <div class="form-control w-full">
        <label class="label">
          <span class="label-text">Departments</span>
        </label>
        <Multiselect
          v-model="selectedDepartmentValues"
          :options="departmentOptions"
          mode="multiple"
          placeholder="Select departments..."
          label="label"
          track-by="value"
          :searchable="true"
          :clear-on-select="false"
          :close-on-select="false"
        />
        <div class="mt-2 flex flex-wrap gap-2">
          <div v-for="item in selectedDepartmentValues" :key="item" 
            class="badge badge-lg badge-primary gap-2 px-3">
            <span class="text-sm">{{ item }}</span>
            <button class="hover:bg-base-200 rounded-full p-1" 
              @click="removeDepartment(item)">
              ×
            </button>
          </div>
          <div v-if="!selectedDepartmentValues.length" class="text-sm text-gray-500">
            No departments selected
          </div>
        </div>
      </div>

      <!-- Grades Filter -->
      <div class="form-control w-full">
        <label class="label">
          <span class="label-text">Grades</span>
        </label>
        <Multiselect
          v-model="selectedGradeValues"
          :options="gradeOptions"
          mode="multiple"
          placeholder="Select grades..."
          label="label"
          track-by="value"
          :searchable="true"
          :clear-on-select="false"
          :close-on-select="false"
        />
        <div class="mt-2 flex flex-wrap gap-2">
          <div v-for="item in selectedGradeValues" :key="item" 
            class="badge badge-lg badge-primary gap-2 px-3">
            <span class="text-sm">{{ item }}</span>
            <button class="hover:bg-base-200 rounded-full p-1" 
              @click="removeGrade(item)">
              ×
            </button>
          </div>
          <div v-if="!selectedGradeValues.length" class="text-sm text-gray-500">
            No grades selected
          </div>
        </div>
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
          
          <!-- Row Total -->
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

/* ปรับแต่ง style สำหรับ multiple select ของ DaisyUI */
.select[multiple] {
  height: auto;
  min-height: 8rem;
  padding: 0.5rem;
}

.select[multiple] option {
  padding: 0.25rem 0.5rem;
  margin: 0.25rem 0;
  border-radius: 0.25rem;
}

.select[multiple] option:checked {
  background-color: hsl(var(--p) / 0.1);
  color: hsl(var(--p));
}

.select[multiple] optgroup {
  font-weight: bold;
  margin-top: 0.5rem;
  padding: 0.25rem 0;
  color: hsl(var(--bc) / 0.6);
}

.select[multiple] optgroup option {
  padding-left: 1rem;
}

/* เพิ่ม smooth scrolling */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: hsl(var(--bc) / 0.2) transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: hsl(var(--bc) / 0.2);
  border-radius: 3px;
}

/* เพิ่ม style สำหรับ dropdown */
.dropdown-content {
  max-height: 300px;
  overflow-y: auto;
}

/* ปรับแต่ง style ของ multiselect ให้เข้ากับ theme */
.multiselect {
  --ms-font-size: 0.875rem;
  --ms-border-color: hsl(var(--bc) / 0.2);
  --ms-border-width: 1px;
  --ms-border-radius: 0.5rem;
  --ms-bg: hsl(var(--b1));
  --ms-option-bg-selected: hsl(var(--p) / 0.1);
  --ms-option-color-selected: hsl(var(--p));
  --ms-tag-bg: hsl(var(--p));
  --ms-tag-color: hsl(var(--pc));
  --ms-ring-width: 0;
}

.multiselect-option.is-selected {
  background: var(--ms-option-bg-selected);
  color: var(--ms-option-color-selected);
}

.multiselect-option.is-pointed {
  background: hsl(var(--bc) / 0.1);
  color: hsl(var(--bc));
}

.multiselect-tag {
  background: var(--ms-tag-bg);
  color: var(--ms-tag-color);
  padding: 4px 8px;
  border-radius: 4px;
  margin: 2px;
}

.multiselect-tag i {
  margin-left: 4px;
}

/* ปรับแต่ง style ของ badges */
.badge {
  @apply py-2;
  min-height: 2rem;
}

.badge button {
  @apply opacity-70 hover:opacity-100 transition-opacity;
}

.badge button:hover {
  @apply bg-base-200/20;
}
</style>