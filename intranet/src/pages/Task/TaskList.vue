<template>
    <UserLayout>
        <div class="container mx-auto p-4">
            <div class="flex justify-between items-center mb-4">
                <div class="breadcrumbs text-sm">
                    <ul>
                        <li><a @click="router.push('/')">Home</a></li>
                        <li>My Task</li>
                    </ul>
                </div>
                <div class="flex gap-2">
                    <!-- ปุ่ม + -->
                    <button @click="newTask" class="btn btn-ghost btn-sm">
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
                    <option value="">ทุกสถานะ</option>
                    <option value="Open">เปิด</option>
                    <option value="Closed">ปิด</option>
                    <option value="Cancelled">ยกเลิก</option>
                </select>
                <input type="date" class="input input-bordered " v-model="startDate" @change="handleFilter" />
                <input type="date" class="input input-bordered " v-model="endDate" @change="handleFilter" />
            </div>


            <!-- ตารางสำหรับหน้าจอขนาดกลางขึ้นไป -->
            <div class="hidden md:block overflow-x-auto mt-4">
                <table class="table table-zebra w-full">
                    <thead>
                        <tr>
                            <th class="cursor-pointer" @click="sortBy('reference_name')">
                                No.
                                <span class="ml-1">
                                    <span
                                        :class="{ 'text-primary': serviceReportStore.sortField === 'reference_name' }">
                                        {{ serviceReportStore.sortField === 'reference_name' &&
                                            serviceReportStore.sortOrder ===
                                            'asc' ? '▲' : '△' }}
                                    </span>
                                    <span
                                        :class="{ 'text-primary': serviceReportStore.sortField === 'reference_name' }">
                                        {{ serviceReportStore.sortField === 'reference_name' &&
                                            serviceReportStore.sortOrder ===
                                            'desc' ? '▼' : '▽' }}
                                    </span>
                                </span>
                            </th>
                            <th class="cursor-pointer" @click="sortBy('status')">
                                Task
                                <span class="ml-1">
                                    <span :class="{ 'text-primary': serviceReportStore.sortField === 'status' }">
                                        {{ serviceReportStore.sortField === 'status' &&
                                            serviceReportStore.sortOrder === 'asc' ? '▲' : '△' }}
                                    </span>
                                    <span :class="{ 'text-primary': serviceReportStore.sortField === 'status' }">
                                        {{ serviceReportStore.sortField === 'status' &&
                                            serviceReportStore.sortOrder === 'desc' ? '▼' : '▽' }}
                                    </span>
                                </span>
                            </th>
                            <th class="cursor-pointer" @click="sortBy('due_date')">
                                Job Date
                                <span class="ml-1">
                                    <span :class="{ 'text-primary': serviceReportStore.sortField === 'due_date' }">
                                        {{ serviceReportStore.sortField === 'due_date' &&
                                            serviceReportStore.sortOrder === 'asc' ? '▲' : '△' }}
                                    </span>
                                    <span :class="{ 'text-primary': serviceReportStore.sortField === 'due_date' }">
                                        {{ serviceReportStore.sortField === 'due_date' &&
                                            serviceReportStore.sortOrder === 'desc' ? '▼' : '▽' }}
                                    </span>
                                </span>
                            </th>

                            <th>Customer</th>
                            <th>Responsible</th>
                        </tr>
                    </thead>
                    <tbody v-if ="serviceReportStore.documentsResource.loading">
                        <tr >
                            <td colspan="5" >
                                <SkeletonTable />
                            </td>
                        </tr>
                    </tbody>
                    <tbody v-if="serviceReportStore.data.length > 0">
                        <tr v-for="report in serviceReportStore.data" :key="report.name">
                            <td>
                                <span class="cursor-pointer"
                                    @click="router.push({ name: 'TaskDetail', params: { id: report.reference_name }, query: { todo: report.name } })">
                                    {{ report.reference_name }}
                                </span>
                            </td>
                            <td>
                                <!-- router.push({ name: 'TaskDetail', params: { id: todo.reference_name }, query: { todo: todo.name } }) -->
                                <span class="cursor-pointer"
                                    @click="router.push({ name: 'TaskDetail', params: { id: report.reference_name } })">
                                    {{ report.description }}
                                </span>
                                <br />

                                <span class="badge badge-sm" :class="{
                                    'badge-primary': report.status === 'Open',
                                    'badge-success': report.status === 'Closed',
                                    'badge-error': report.status === 'Cancelled'
                                }">{{ report.status }}</span>
                            </td>
                            <td>{{ formatDate(report.due_date) }}</td>

                            <td> {{ report.contact_person }} - {{ report.contact_email }} <br />
                                <span class="badge badge-sm badge-ghost">{{ report.project }}</span>

                            </td>
                            <td>
                                <UserAvatar :email="report.assign_to" />


                            </td>
                        </tr>
                    </tbody>
                    <tbody v-else>
                        <tr >
                            <td colspan="5" >
                               <NoDataFoundTable />
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- การ์ดสำหรับหน้าจอขนาดเล็ก -->
            <div class="md:hidden space-y-4 mt-4">
                <div v-if="serviceReportStore.documentsResource.loading">
                    <div class="card bg-base-100 shadow-xl animate-pulse">
                        <div class="card-body">
                            <div class="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
                            <div class="h-4 bg-gray-300 rounded w-1/2 mb-2"></div>
                            <div class="h-4 bg-gray-300 rounded w-1/4"></div>
                        </div>
                    </div>
                </div>
                <div v-else-if="serviceReportStore.data.length > 0">
                    <div v-for="report in serviceReportStore.data" :key="report.name" class="card bg-base-100 shadow-xl mb-4">
                        <div class="card-body p-4">
                            <div class="flex justify-between items-start mb-2">
                                <h2 class="card-title text-base cursor-pointer" @click="router.push({ name: 'TaskDetail', params: { id: report.reference_name }, query: { todo: report.name } })">
                                    {{ report.reference_name }}
                                </h2>
                                <span class="badge badge-sm" :class="{
                                    'badge-primary': report.status === 'Open',
                                    'badge-success': report.status === 'Closed',
                                    'badge-error': report.status === 'Cancelled'
                                }">{{ report.status }}</span>
                            </div>
                            <p class="text-sm text-gray-600 mb-2">{{ report.description }}</p>
                            <div class="text-sm">
                                <p><span class="font-semibold">Job Date:</span> {{ formatDate(report.due_date) }}</p>
                                <p><span class="font-semibold">Customer:</span> {{ report.contact_person }}</p>
                                <p class="text-xs text-gray-500">{{ report.contact_email }}</p>
                                <p class="mt-1"><span class="badge badge-sm badge-ghost">{{ report.project }}</span></p>
                            </div>
                            <div class="flex justify-end mt-2">
                                <div>
                                    <p class="text-xs text-gray-500 mb-1">Responsible:</p>
                                    <UserAvatar :email="report.assign_to" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-else>
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center">No Data Found</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pagination -->
            <div class="flex justify-between items-center mt-4">
                <div class="join">
                    <button class="join-item btn" @click="serviceReportStore.previousPage()"
                        :disabled="serviceReportStore.isFirstPage">
                        «
                    </button>
                    <button class="join-item btn">
                        หน้า {{ serviceReportStore.currentPage }}
                    </button>
                    <button class="join-item btn" @click="serviceReportStore.nextPage()"
                        :disabled="serviceReportStore.isLastPage">
                        »
                    </button>
                </div>
                <select v-model="pageSize" @change="handlePageSizeChange" class="select select-bordered">
                    <option :value="10">10 รายการ/หน้า</option>
                    <option :value="20">20 รายการ/หน้า</option>
                    <option :value="50">50 รายการ/หน้า</option>
                </select>
            </div>

            <!-- แสดงจำนวนรายการ -->
            <div class="text-sm text-gray-600 mt-2">
                แสดง {{ displayedItemsCount }} จาก {{ totalItems }} รายการ
            </div>


        </div>


    </UserLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import UserLayout from '@/layouts/userLayout.vue'
import { useSmoTaskStore } from '@/stores/taskStore'
import UserAvatar from '../../components/UserAvatar.vue'
import SkeletonTable from '@/components/SkeletonTable.vue'
import NoDataFoundTable from '@/components/NoDataFoundTable.vue'
const router = useRouter()
const serviceReportStore = useSmoTaskStore()

const formatDate = inject('formatDate') as (date: string) => string

const searchQuery = ref('')
const statusFilter = ref('')
const startDate = ref('')
const endDate = ref('')
const pageSize = ref(10)
const showFilter = ref(false)

const displayedItemsCount = computed(() => serviceReportStore.data.length)
const totalItems = computed(() => serviceReportStore.documentsResource.data?.total || 0)

onMounted(() => {
    serviceReportStore.pageSize = 10
    handleFilter()
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

const handlePageSizeChange = () => {
    serviceReportStore.pageSize = pageSize.value
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
    location.href = `/app/smo-service-report/${docName}?from_page=service_report&from=front_end`
}
const newTask = () => {
    window.location.href = '/app/smo-task/new?from=front_end'
}
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

.badge {
  @apply px-2 py-1 rounded-full text-xs font-semibold;
}

.card {
  @apply w-full;
}

.card-body {
  @apply p-4;
}

.card-title {
  @apply text-base mb-1;
}
</style>
