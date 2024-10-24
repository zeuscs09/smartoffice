<template>
    <UserLayout>
        <div class="container mx-auto p-4">
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
                    :data="serviceReportStore.data"
                    :loading="serviceReportStore.documentsResource.loading"
                    :error="serviceReportStore.documentsResource.error"
                    :sort-field="serviceReportStore.sortField"
                    :sort-order="serviceReportStore.sortOrder"
                    :sortable="true"
                    @sort="handleSort"
                />
            </div>

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
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import UserLayout from '@/layouts/userLayout.vue'
import { useExpenseRequestStore } from '@/stores/expenseRequestStore'
import ExpenseRequestTable from '@/components/ExpenseRequestTable.vue'
import Pagination from '@/components/Pagination.vue' // นำเข้า Pagination component
const router = useRouter()
const serviceReportStore = useExpenseRequestStore()
serviceReportStore.pageSize = 10



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

const sortField = ref('')
const sortOrder = ref('asc')

const handleSort = (field: string) => {
    if (sortField.value === field) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
        sortField.value = field
        sortOrder.value = 'asc'
    }
    serviceReportStore.sortField = sortField.value
    serviceReportStore.sortOrder = sortOrder.value
    serviceReportStore.fetchAll(1)
}

const handlePageSizeChange = (newSize: number) => {
    pageSize.value = newSize
    serviceReportStore.pageSize = newSize
    serviceReportStore.fetchAll(1)
}
const createExpenseRequest = () => {
    location.href='/app/smo-expense-request/new?from_page=intranet'
}

const timelineModal = ref<HTMLDialogElement | null>(null)

const timelineEvents = ref([
   
])

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

