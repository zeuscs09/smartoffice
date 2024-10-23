<template>
    <UserLayout>
        <div class="container mx-auto p-4">
            <div class="flex justify-between items-center mb-4">
                <div class="breadcrumbs text-sm">
                    <ul>
                        <li><a @click="router.push('/')">Home</a></li>
                        <li>Mailbox</li>
                    </ul>
                </div>
                <div class="flex gap-2">


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
            <!-- update git -->
            <!-- ส่วนค้นหาและกรอง -->
            <div v-if="showFilter" class="flex flex-wrap gap-4 mb-4">
                <input type="text" placeholder="Search..."
                    class="input input-bordered flex-grow" v-model="searchQuery" @input="handleSearch" />
                <select class="select select-bordered w-full max-w-xs" v-model="statusFilter"
                    @change="handleFilter">
                    <option value="">All</option>
                    <option value="read">Read</option>
                    <option value="unread">Unread</option>
                </select>
                <input type="date" class="input input-bordered " v-model="startDate" @change="handleFilter" />
                <input type="date" class="input input-bordered " v-model="endDate" @change="handleFilter" />
            </div>


            <!-- ตารางแสดงข้อมูล -->
            <div class="overflow-x-auto mt-4">
                <MailboxTable 
                    :data="serviceReportStore.data" 
                    :loading="serviceReportStore.documentsResource.loading"
                    :error="serviceReportStore.documentsResource.error" 
                    :sortField="serviceReportStore.sortField"
                    :sortOrder="serviceReportStore.sortOrder" 
                    :sortable="true" 
                    @sort="sortMailbox" 
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


</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import UserLayout from '@/layouts/userLayout.vue'
import { useMailBoxStore } from '@/stores/mailBoxStore'
import MailboxTable from '@/components/MailboxTable.vue'
import Pagination from '@/components/Pagination.vue' // นำเข้า Pagination component

const router = useRouter()
const serviceReportStore = useMailBoxStore()
serviceReportStore.pageSize = 10

const searchQuery = ref('')
const statusFilter = ref('')
const startDate = ref('')
const endDate = ref('')
const pageSize = ref(10)
const showFilter = ref(false)

const displayedItemsCount = computed(() => serviceReportStore.data.length)
const totalItems = computed(() => serviceReportStore.documentsResource.data?.total || 0)

// เพิ่มฟังก์ชันสำหรับบันทึก state ทั้งหมด
const saveMailboxState = () => {
    const state = {
        searchQuery: searchQuery.value,
        statusFilter: statusFilter.value,
        startDate: startDate.value,
        endDate: endDate.value,
        pageSize: pageSize.value,
        showFilter: showFilter.value,
        currentPage: serviceReportStore.currentPage
    }
    localStorage.setItem('mailboxState', JSON.stringify(state))
}

// เพิ่มฟังก์ชันสำหรับโหลด state
const loadMailboxState = () => {
    const savedState = localStorage.getItem('mailboxState')
    if (savedState) {
        const state = JSON.parse(savedState)
        searchQuery.value = state.searchQuery
        statusFilter.value = state.statusFilter
        startDate.value = state.startDate
        endDate.value = state.endDate
        pageSize.value = state.pageSize
        showFilter.value = state.showFilter
        updateStoreFromState(state)
    }
}

// เพิ่มฟังก์ชันใหม่สำหรับอัปเดต store
const updateStoreFromState = (state) => {
    serviceReportStore.searchQuery = state.searchQuery
    serviceReportStore.statusFilter = state.statusFilter
    serviceReportStore.startDate = state.startDate
    serviceReportStore.endDate = state.endDate
    serviceReportStore.pageSize = state.pageSize
    serviceReportStore.currentPage = state.currentPage
}

onMounted(() => {
    loadMailboxState()
    serviceReportStore.fetchAll(1)
})

// บันทึก state ก่อนออกจากคอมโพเนนต์
onBeforeUnmount(() => {
    saveMailboxState()
})

const toggleFilter = () => {
    showFilter.value = !showFilter.value
}

const handleSearch = () => {
    serviceReportStore.searchQuery = searchQuery.value
    serviceReportStore.fetchAll(1)
    saveMailboxState()
}

const handleFilter = () => {
    serviceReportStore.statusFilter = statusFilter.value
    serviceReportStore.startDate = startDate.value
    serviceReportStore.endDate = endDate.value
    serviceReportStore.fetchAll(1)
    saveMailboxState()
}

const sortMailbox = (field: string) => {
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

// เพิ่ม watch เพื่อติดตามการเปลี่ยนแปลงของ pageSize
watch(pageSize, (newSize) => {
    console.log('Page size changed to:', newSize)
})

// เพิ่มการบันทึก state เมื่อมีการเปลี่ยนหน้า
const handlePageChange = (newPage: number) => {
    serviceReportStore.fetchAll(newPage)
    saveMailboxState()
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
