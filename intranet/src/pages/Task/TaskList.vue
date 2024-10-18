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
                    <button class="btn btn-primary btn-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                        เพิ่ม
                    </button>
                    <!-- ปุ่ม Filter -->
                    <button 
                      class="btn btn-sm" 
                      :class="{ 'btn-ghost': !showFilter }" 
                      @click="toggleFilter"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                      </svg>
                      {{ showFilter ? 'ซ่อนตัวกรอง' : 'ตัวกรอง' }}
                    </button>
                </div>
            </div>

            <!-- ส่วนค้นหาและกรอง -->
            <div v-if="showFilter" class="flex flex-wrap gap-4 mb-4">
                <input type="text" placeholder="No.,Task,Customer,Responsible"
                    class="input input-bordered input-sm flex-grow" v-model="searchQuery" @input="handleSearch" />
                <select class="select select-bordered select-sm w-full max-w-xs" v-model="statusFilter"
                    @change="handleFilter">
                    <option value="">ทุกสถานะ</option>
                    <option value="Open">เปิด</option>
                    <option value="Closed">ปิด</option>
                    <option value="Cancelled">ยกเลิก</option>
                </select>
                <input type="date" class="input input-bordered input-sm" v-model="startDate" @change="handleFilter" />
                <input type="date" class="input input-bordered input-sm" v-model="endDate" @change="handleFilter" />
            </div>


            <!-- ตารางแสดงข้อมูล -->
            <div class="overflow-x-auto mt-4">
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
                    <tbody>
                        <tr v-for="report in serviceReportStore.data" :key="report.name">
                            <td>
                                <span class="cursor-pointer" @click="router.push({ name: 'TaskDetail', params: { id: report.reference_name } })">
                                    {{ report.reference_name }}
                                </span>
                            </td>
                            <td>
                                <!-- router.push({ name: 'TaskDetail', params: { id: todo.reference_name }, query: { todo: todo.name } }) -->
                                <span class="cursor-pointer"
                                    @click="router.push({ name: 'TaskDetail', params: { id: report.reference_name } })"
                                >
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
                </table>
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
    location.href = `/app/smo-service-report/${docName}?from_page=service_report`
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
</style>
