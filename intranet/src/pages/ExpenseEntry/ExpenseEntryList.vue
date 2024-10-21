<template>
    <UserLayout>
        <div class="container mx-auto p-4">
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
                    <option value="Approval Review">Approval Review</option>
                    <option value="Approved">Approve</option>
                    <option value="Rejected">Reject</option>
                </select>
                <input type="date" class="input input-bordered " v-model="startDate" @change="handleFilter" />
                <input type="date" class="input input-bordered " v-model="endDate" @change="handleFilter" />
            </div <!-- ตารางแสดงข้อมูล -->
            <ExpenseEntryTable 
                :data="serviceReportStore.data" 
                :loading="serviceReportStore.documentsResource.loading"
                :error="serviceReportStore.documentsResource.error" 
                :sortField="serviceReportStore.sortField"
                :sortOrder="serviceReportStore.sortOrder" 
                @sort="sortBy" 
            />

            <!-- Pagination -->
            <Pagination 
                v-if="serviceReportStore.data.length > 0" 
                :current-page="serviceReportStore.currentPage"
                :is-first-page="serviceReportStore.isFirstPage" 
                :is-last-page="serviceReportStore.isLastPage"
                :page-size="pageSize" 
                :displayed-items-count="displayedItemsCount" 
                :total-items="totalItems"
                @previous="serviceReportStore.previousPage()" 
                @next="serviceReportStore.nextPage()"
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

import Timeline from '@/components/Timeline.vue'
import ExpenseEntryTable from '@/components/ExpenseEntryTable.vue'
const router = useRouter()
const serviceReportStore = useExpenseEntryStore()
serviceReportStore.pageSize = 10


import { createDocumentResource } from 'frappe-ui'



const searchQuery = ref('')
const statusFilter = ref('')
const startDate = ref('')
const endDate = ref('')
const pageSize = ref(10)
const showFilter = ref(false)

const displayedItemsCount = computed(() => serviceReportStore.data.length)
const totalItems = computed(() => serviceReportStore.documentsResource.data?.total || 0)

onMounted(() => {
    serviceReportStore.fetchAll(1)
})

const toggleFilter = () => {
    showFilter.value = !showFilter.value
}

const handleSearch = () => {
    serviceReportStore.searchQuery = searchQuery.value
    serviceReportStore.fetchAll(1)
}

const handleFilter = () => {
    serviceReportStore.statusFilter = statusFilter.value
    serviceReportStore.startDate = startDate.value
    serviceReportStore.endDate = endDate.value
    serviceReportStore.fetchAll(1)
}

const sortBy = (field: string) => {
    if (serviceReportStore.sortField === field) {
        serviceReportStore.sortOrder = serviceReportStore.sortOrder === 'asc' ? 'desc' : 'asc'
    } else {
        serviceReportStore.sortField = field
        serviceReportStore.sortOrder = 'asc'
    }
    serviceReportStore.fetchAll(1)
}

const handlePageSizeChange = (newSize: number) => {
    pageSize.value = newSize
    serviceReportStore.pageSize = newSize
    serviceReportStore.fetchAll(1)
}

const refreshData = () => {
    serviceReportStore.fetchAll(serviceReportStore.currentPage)
}

const applyFiltersAndRefresh = () => {
    // รวมตรรกะการค้นหาและกรอง
    handleSearch()
    handleFilter()
    // รีเฟรชข้อมูล
    serviceReportStore.fetchAll(serviceReportStore.currentPage)
}

const viewDocument = (docName: string) => {

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
    // ในที่นี้เราจะใช้ข้อมูลจำลอง แต่ในการใช้งานจริงคุณอาจต้องโหลดข้อมูลจาก API

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
    location.href = '/app/smo-expense-entry/new?from=frontend'
}

const timelineModal = ref<HTMLDialogElement | null>(null)

const timelineEvents = ref([

])

// เพิ่ม watch เพื่อติดตามการเปลี่ยนแปลงของ pageSize
watch(pageSize, (newSize) => {
    console.log('Page size changed to:', newSize)
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
