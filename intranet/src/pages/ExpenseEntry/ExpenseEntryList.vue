<template>
    <UserLayout>
        <div class="mx-auto p-4">
            <div class="flex justify-between items-center mb-4">
                <div class="breadcrumbs text-sm">
                    <ul>
                        <li><a @click="router.push('/')">Home</a></li>
                        <li>Expense Entry</li>
                    </ul>
                </div>
                <div class="flex gap-2">
                    <!-- ปุ่ม + -->
                    <button class="btn btn-ghost btn-sm" @click="newExpenseEntry">
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
                <input type="text" placeholder="Search..." class="input input-bordered  flex-grow" v-model="searchQuery"
                    @input="handleSearch" />
                <select class="select select-bordered w-full max-w-xs" v-model="statusFilter" @change="handleFilter">
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
            <ExpenseEntryTable 
                :data="expenseEntryStore.data" 
                :loading="expenseEntryStore.documentsResource.loading"
                :error="expenseEntryStore.documentsResource.error" 
                :sortField="expenseEntryStore.sortField"
                :sortOrder="expenseEntryStore.sortOrder" 
                @sort="sortBy" 
                @view="viewDocument"
            />

            <!-- Pagination -->
            <Pagination 
                v-if="expenseEntryStore.data.length > 0" 
                :current-page="expenseEntryStore.currentPage"
                :is-first-page="expenseEntryStore.isFirstPage" 
                :is-last-page="expenseEntryStore.isLastPage"
                :page-size="pageSize" 
                :displayed-items-count="displayedItemsCount" 
                :total-items="totalItems"
                @previous="expenseEntryStore.previousPage()" 
                @next="expenseEntryStore.nextPage()"
                @update:page-size="handlePageSizeChange" 
            />

            <!-- แสดงจำนวนรายการ -->
           


        </div>


    </UserLayout>

    <!-- Modal for timeline -->
    <dialog id="timeline_modal" class="modal" ref="timelineModal">
        <div class="modal-box w-11/12 max-w-5xl">
            <h3 class="font-bold text-lg mb-4">ประวัติการอนุมัติ</h3>

            <Timeline :events="timelineEvents" />

            <div class="modal-action">
                <form method="dialog">
                    <button class="btn">ปิด</button>
                </form>
            </div>
        </div>
    </dialog>

</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import UserLayout from '@/layouts/userLayout.vue'
import { useExpenseEntryStore } from '@/stores/expenseEntryStore'
import Pagination from '@/components/Pagination.vue'
import Timeline from '@/components/TimeLine.vue'
import ExpenseEntryTable from '@/components/ExpenseEntryTable.vue'
import { createDocumentResource } from 'frappe-ui'

const router = useRouter()
const expenseEntryStore = useExpenseEntryStore()
expenseEntryStore.pageSize = 10

// กำหนดคีย์สำหรับเก็บข้อมูลใน localStorage
const STORAGE_KEY = 'expense-entry-criteria'

const searchQuery = ref('')
const statusFilter = ref('')
const startDate = ref('')
const endDate = ref('')
const pageSize = ref(10)
const showFilter = ref(false)
const timelineModal = ref<HTMLDialogElement | null>(null)
const timelineEvents = ref([])

const displayedItemsCount = computed(() => expenseEntryStore.data.length)
const totalItems = computed(() => expenseEntryStore.documentsResource.data?.total || 0)

// เพิ่มฟังก์ชันสำหรับบันทึกและโหลด criteria
const saveCriteria = () => {
  const criteria = {
    searchQuery: searchQuery.value,
    statusFilter: statusFilter.value,
    startDate: startDate.value,
    endDate: endDate.value,
    pageSize: pageSize.value,
    showFilter: showFilter.value,
    currentPage: expenseEntryStore.currentPage,
    sortField: expenseEntryStore.sortField,
    sortOrder: expenseEntryStore.sortOrder
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
      expenseEntryStore.searchQuery = searchQuery.value
      expenseEntryStore.statusFilter = statusFilter.value
      expenseEntryStore.startDate = startDate.value
      expenseEntryStore.endDate = endDate.value
      expenseEntryStore.pageSize = pageSize.value
      expenseEntryStore.sortField = criteria.sortField || 'creation'
      expenseEntryStore.sortOrder = criteria.sortOrder || 'desc'
      
      // ดึงข้อมูลโดยใช้หน้าที่บันทึกไว้
      expenseEntryStore.fetchAll(criteria.currentPage || 1)
    } else {
      // กรณีไม่มีข้อมูลที่บันทึกไว้ ใช้ค่าเริ่มต้น
      expenseEntryStore.pageSize = pageSize.value
      expenseEntryStore.fetchAll(1)
    }
  } catch (err) {
    console.error('Error loading criteria:', err)
    // หากโหลดไม่สำเร็จให้ใช้ค่าเริ่มต้น
    expenseEntryStore.pageSize = pageSize.value
    expenseEntryStore.fetchAll(1)
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
  expenseEntryStore.searchQuery = searchQuery.value
  expenseEntryStore.fetchAll(1)
  saveCriteria() // บันทึกเกณฑ์การค้นหา
}

const handleFilter = () => {
  expenseEntryStore.statusFilter = statusFilter.value
  expenseEntryStore.startDate = startDate.value
  expenseEntryStore.endDate = endDate.value
  expenseEntryStore.fetchAll(1)
  saveCriteria() // บันทึกเกณฑ์การกรอง
}

const sortBy = (field: string) => {
  if (expenseEntryStore.sortField === field) {
    expenseEntryStore.sortOrder = expenseEntryStore.sortOrder === 'asc' ? 'desc' : 'asc'
  } else {
    expenseEntryStore.sortField = field
    expenseEntryStore.sortOrder = 'asc'
  }
  expenseEntryStore.fetchAll(1)
  saveCriteria() // บันทึกลำดับการเรียง
}

const handlePageSizeChange = (newSize: number) => {
  pageSize.value = newSize
  expenseEntryStore.pageSize = newSize
  expenseEntryStore.fetchAll(1)
  saveCriteria() // บันทึกขนาดหน้า
}

const refreshData = () => {
  expenseEntryStore.fetchAll(expenseEntryStore.currentPage)
}

// แก้ไขให้ window.refresh_table บันทึก criteria ด้วย
window.refresh_table = () => {
  expenseEntryStore.fetchAll(expenseEntryStore.currentPage)
  saveCriteria()
}

const applyFiltersAndRefresh = () => {
  // รวมตรรกะการค้นหาและกรอง
  handleSearch()
  handleFilter()
  // รีเฟรชข้อมูล
  expenseEntryStore.fetchAll(expenseEntryStore.currentPage)
  saveCriteria() // บันทึกทุกเกณฑ์
}

const viewDocument = (docName: string) => {
  // บันทึก criteria ก่อนไปหน้ารายละเอียด
  saveCriteria()
  location.href = `/app/smo-expense-entry/${docName}?from=frontend`
}

const showTimeline = async (docName: string) => {
  console.log(docName)
  const expenseRequest = createDocumentResource({
    doctype: 'SMO Expense Entry',
    name: docName,
    auto: false,
  })
  timelineEvents.value = []

  await expenseRequest.reload();
  console.log(expenseRequest.doc);

  // เพิ่มเหตุการณ์ "สร้างคำขอ" ที่ด้านบนสุดของ timeline
  timelineEvents.value.push({
    date: expenseRequest.doc.creation,
    action: 'Submit Request',
    status: 'Approved',
    approve_role: 'Requestor',
    by: expenseRequest.doc.owner
  });

  timelineEvents.value.push({
    date: expenseRequest.doc.creation,
    action: expenseRequest.doc.workflow_state,
    status: expenseRequest.doc.workflow_state,
    approve_role: 'Vice President',
    by: expenseRequest.doc.approver
  });

  timelineModal.value?.showModal();
}

const newExpenseEntry = () => {
  // บันทึก criteria ก่อนไปหน้าสร้างใหม่
  saveCriteria()
  window.open('/app/smo-expense-entry/new?from_page=/intranet', '_blank')
}

// ให้บันทึก criteria เมื่อ store ได้รับข้อมูลใหม่
watch(() => expenseEntryStore.currentPage, () => {
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
