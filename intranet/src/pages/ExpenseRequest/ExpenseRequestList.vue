<template>
    <UserLayout>
        <div class="mx-auto p-4">
            <div class="flex justify-between items-center mb-4">
                <div class="breadcrumbs text-sm">
                    <ul>
                        <li><a @click="router.push('/')">Home</a></li>
                        <li>Expense Request</li>
                    </ul>
                </div>
                <div class="flex gap-2">
                    <!-- ปุ่ม + -->
                    <button class="btn btn-ghost btn-sm tooltip tooltip-bottom" data-tip="Create Expense Request" @click="createExpenseRequest">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                        
                    </button>

                    <!-- ปุ่ม Filter -->
                    <button class="btn btn-sm" :class="{ 'btn-ghost': !showFilter }" @click="toggleFilter">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                        </svg>
                        <!-- {{ showFilter ? 'ซ่อนตัวกรอง' : 'ตัวกรอง' }} -->
                    </button>
                </div>
            </div>

            <!-- ส่วนค้นหาและกรอง -->
            <div v-if="showFilter" class="flex flex-wrap gap-4 mb-4">
                <input type="text" placeholder="Search..."
                    class="input input-bordered flex-grow" v-model="searchQuery" @input="handleSearch" />
                <select class="select select-bordered w-full max-w-xs" v-model="statusFilter"
                    @change="handleFilter">
                    <option value="">All</option>
                    <option value="Draft">Draft</option>
                    <option value="Pending Approval">Pending Approval</option>
                    <option value="Approved">Approved</option>
                    <option value="Rejected">Rejected</option>
                </select>
                <input type="date" class="input input-bordered " v-model="startDate" @change="handleFilter" />
                <input type="date" class="input input-bordered " v-model="endDate" @change="handleFilter" />
            </div>

            <!-- ตารางแสดงข้อมูล -->
            <div class="overflow-x-auto mt-4">
                <ExpenseRequestTable
                    :data="expenseRequestStore.data"
                    :loading="expenseRequestStore.documentsResource.loading"
                    :error="expenseRequestStore.documentsResource.error"
                    :sort-field="expenseRequestStore.sortField"
                    :sort-order="expenseRequestStore.sortOrder"
                    :sortable="true"
                    @sort="handleSort"
                    @view="viewDocument"
                />
            </div>

            <!-- Pagination -->
            <Pagination 
                v-if="expenseRequestStore.data.length > 0" 
                :current-page="expenseRequestStore.currentPage"
                :is-first-page="expenseRequestStore.isFirstPage" 
                :is-last-page="expenseRequestStore.isLastPage"
                :page-size="pageSize" 
                :displayed-items-count="displayedItemsCount" 
                :total-items="totalItems"
                @previous="expenseRequestStore.previousPage()" 
                @next="expenseRequestStore.nextPage()"
                @update:page-size="handlePageSizeChange" 
            />

         

        </div>


    </UserLayout>


</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import UserLayout from '@/layouts/userLayout.vue'
import { useExpenseRequestStore } from '@/stores/expenseRequestStore'
import ExpenseRequestTable from '@/components/ExpenseRequestTable.vue'
import Pagination from '@/components/Pagination.vue'

const router = useRouter()
const expenseRequestStore = useExpenseRequestStore()
expenseRequestStore.pageSize = 10

// กำหนดคีย์สำหรับเก็บข้อมูลใน localStorage
const STORAGE_KEY = 'expense-request-criteria'

const searchQuery = ref('')
const statusFilter = ref('')
const startDate = ref('')
const endDate = ref('')
const pageSize = ref(10)
const showFilter = ref(false)
const timelineModal = ref<HTMLDialogElement | null>(null)
const timelineEvents = ref([])

const displayedItemsCount = computed(() => expenseRequestStore.data.length)
const totalItems = computed(() => expenseRequestStore.documentsResource.data?.total || 0)

// เพิ่มฟังก์ชันสำหรับบันทึกและโหลด criteria
const saveCriteria = () => {
  const criteria = {
    searchQuery: searchQuery.value,
    statusFilter: statusFilter.value,
    startDate: startDate.value,
    endDate: endDate.value,
    pageSize: pageSize.value,
    showFilter: showFilter.value,
    currentPage: expenseRequestStore.currentPage,
    sortField: expenseRequestStore.sortField,
    sortOrder: expenseRequestStore.sortOrder
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(criteria))
}

const loadCriteria = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const criteria = JSON.parse(saved)
      
      // กำหนดค่าให้กับตัวแปรต่างๆ
      searchQuery.value = criteria.searchQuery || ''
      statusFilter.value = criteria.statusFilter || ''
      startDate.value = criteria.startDate || ''
      endDate.value = criteria.endDate || ''
      pageSize.value = criteria.pageSize || 10
      showFilter.value = criteria.showFilter || false
      
      // กำหนดค่าให้ store
      expenseRequestStore.searchQuery = searchQuery.value
      expenseRequestStore.statusFilter = statusFilter.value
      expenseRequestStore.startDate = startDate.value
      expenseRequestStore.endDate = endDate.value
      expenseRequestStore.pageSize = pageSize.value
      expenseRequestStore.sortField = criteria.sortField || 'creation'
      expenseRequestStore.sortOrder = criteria.sortOrder || 'desc'
      
      // ดึงข้อมูลโดยใช้หน้าที่บันทึกไว้
      expenseRequestStore.fetchAll(criteria.currentPage || 1)
    } else {
      // กรณีไม่มีข้อมูลที่บันทึกไว้ ใช้ค่าเริ่มต้น
      expenseRequestStore.pageSize = pageSize.value
      expenseRequestStore.fetchAll(1)
    }
  } catch (err) {
    console.error('Error loading criteria:', err)
    // หากโหลดไม่สำเร็จให้ใช้ค่าเริ่มต้น
    expenseRequestStore.pageSize = pageSize.value
    expenseRequestStore.fetchAll(1)
  }
}

onMounted(() => {
  // เรียกใช้ loadCriteria แทนการเรียก fetchAll โดยตรง
  loadCriteria()
})

const toggleFilter = () => {
  showFilter.value = !showFilter.value
  saveCriteria() // บันทึกการแสดง/ซ่อนตัวกรอง
}

const handleSearch = () => {
  expenseRequestStore.searchQuery = searchQuery.value
  expenseRequestStore.fetchAll(1)
  saveCriteria() // บันทึกเกณฑ์การค้นหา
}

const handleFilter = () => {
  expenseRequestStore.statusFilter = statusFilter.value
  expenseRequestStore.startDate = startDate.value
  expenseRequestStore.endDate = endDate.value
  expenseRequestStore.fetchAll(1)
  saveCriteria() // บันทึกเกณฑ์การกรอง
}

const sortField = ref('')
const sortOrder = ref('asc')

const handleSort = (field: string) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
  expenseRequestStore.sortField = sortField.value
  expenseRequestStore.sortOrder = sortOrder.value
  expenseRequestStore.fetchAll(1)
  saveCriteria() // บันทึกการจัดเรียง
}

const handlePageSizeChange = (newSize: number) => {
  pageSize.value = newSize
  expenseRequestStore.pageSize = newSize
  expenseRequestStore.fetchAll(1)
  saveCriteria() // บันทึกขนาดหน้า
}

// เพิ่มฟังก์ชัน viewDocument
const viewDocument = (docName: string) => {
  // บันทึก criteria ก่อนไปหน้ารายละเอียด
  saveCriteria()
  location.href = `/app/smo-expense-request/${docName}?from=frontend`
}

const createExpenseRequest = () => {
  // บันทึก criteria ก่อนไปหน้าสร้างใหม่
  saveCriteria()
  window.open('/app/smo-expense-request/new?from_page=/intranet', '_blank')
}

// แก้ไขให้ window.refresh_table บันทึก criteria ด้วย
window.refresh_table = () => {
  expenseRequestStore.fetchAll(expenseRequestStore.currentPage)
  saveCriteria()
}

// ให้บันทึก criteria เมื่อ store ได้รับข้อมูลใหม่
watch(() => expenseRequestStore.currentPage, () => {
  saveCriteria()
})

// บันทึก criteria เมื่อ pageSize เปลี่ยน
watch(pageSize, (newSize) => {
  console.log('Page size changed to:', newSize)
  saveCriteria()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>

