<template>
    <userLayout>
        <div class="mx-auto p-4">
            <div class="flex justify-between items-center mb-4">
                <div class="breadcrumbs text-sm">
                    <ul>
                        <li><a @click="router.push('/')">Home</a></li>
                        <li>Team Workload</li>
                    </ul>
                </div>
                <div class="flex gap-2">
                    <!-- Filter Button -->
                    <button class="btn btn-sm" :class="{ 'btn-ghost': !showFilter }" @click="toggleFilter">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Search and Filter Section -->
            <div v-if="showFilter" class="flex flex-wrap gap-4 mb-4">
                <div class="form-control">
                    <label class="label">
                        <span class="label-text">Month</span>
                    </label>
                    <select @change="loadData" v-model="selectedMonth" class="select select-bordered w-full max-w-xs">
                        <option v-for="month in months" :key="month.value" :value="month.value">
                            {{ month.label }}
                        </option>
                    </select>
                </div>
                <div class="form-control">
                    <label class="label">
                        <span class="label-text">Year</span>
                    </label>
                    <select @change="loadData" v-model="selectedYear" class="select select-bordered w-full max-w-xs">
                        <option v-for="year in years" :key="year" :value="year">
                            {{ year }}
                        </option>
                    </select>
                </div>
            </div>

            <!-- Work Status Table -->
            <div class="overflow-x-auto relative shadow-md rounded-lg mb-4">
                <table class="w-full">
                    <thead>
                        <tr class="bg-gray-100">
                            <th class="sticky left-0 z-10 bg-gray-100 p-2 text-center min-w-[200px]">Name</th>
                            <th v-for="day in daysInMonth" :key="day" class="p-2 text-center min-w-[60px]">
                                {{ day }}<br>
                                <span class="text-xs">{{ getDayName(day) }}</span>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="engineer in engineers" :key="engineer.id">
                            <td class="sticky left-0 z-10 bg-white p-2 min-w-[200px]">
                                <div class="flex items-center space-x-2">
                                    <UserAvatar :email="engineer.user_id" class="w-8 h-8" />
                                    <span class="font-medium">{{ engineer.name }}</span>
                                </div>
                            </td>
                            <td v-for="day in daysInMonth" :key="`${engineer.id}-${day}`"
                                :class="getStatusClass(engineer.status[day]?.status)"
                                class="min-w-[60px] relative"
                                @click="showTaskDetails(engineer.status[day]?.task_details)"
                                >
                                <div v-if="engineer.status[day]?.count_job > 0" 
                                     class="flex flex-wrap gap-1 justify-center items-center p-1 cursor-pointer"
                                   
                                     >
                                    <div v-for="n in engineer.status[day]?.count_job" 
                                         :key="n" 
                                         class="job-dot">
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Color Legend -->
            <div class="flex flex-wrap gap-4 justify-center">
                <div v-for="(color, status) in statusColors" :key="status" class="flex items-center">
                    <div :class="['w-6 h-6 rounded mr-2', color]"></div>
                    <span>{{ getStatusText(status) }}</span>
                </div>
            </div>
        </div>
    </userLayout>

    <!-- เพิ่ม Drawer component ไว้ด้านล่างสุดของ template -->
    <div class="drawer-container" :class="{ 'active': isDrawerOpen }">
        <div class="drawer-overlay" @click="closeDrawer"></div>
        <div class="drawer-content">
            <div class="drawer-header">
                <h3 class="text-lg font-semibold">Task Details</h3>
                <button class="btn btn-ghost btn-sm" @click="closeDrawer">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div class="drawer-body">
                <div v-if="selectedTasks?.length" class="space-y-4">
                    <div v-for="(task, index) in selectedTasks" :key="index" class="card bg-base-100 shadow-sm">
                        <div class="card-body p-4">
                            <h4 class="card-title text-base">{{ task }}</h4>
                            
                        </div>
                    </div>
                </div>
                <div v-else class="text-center text-gray-500 py-8">
                    ไม่มีงานในวันที่เลือก
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import userLayout from '@/layouts/userLayout.vue'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import UserAvatar from '@/components/UserAvatar.vue'
const router = useRouter()
const showFilter = ref(false)

const toggleFilter = () => {
    showFilter.value = !showFilter.value
}

const selectedMonth = ref(new Date().getMonth() + 1)
const selectedYear = ref(new Date().getFullYear())
const workloadResource = createResource({
    url: 'smartoffice.api.planing.get_team_workload',
    auto: false,
})
const months = [
    { value: 1, label: 'January' },
    { value: 2, label: 'February' },
    { value: 3, label: 'March' },
    { value: 4, label: 'April' },
    { value: 5, label: 'May' },
    { value: 6, label: 'June' },
    { value: 7, label: 'July' },
    { value: 8, label: 'August' },
    { value: 9, label: 'September' },
    { value: 10, label: 'October' },
    { value: 11, label: 'November' },
    { value: 12, label: 'December' },
]

const currentYear = new Date().getFullYear()
const years = computed(() => {
    const yearList = []
    for (let i = currentYear - 5; i <= currentYear + 5; i++) {
        yearList.push(i)
    }
    return yearList
})

const daysInMonth = computed(() => {
    return new Date(selectedYear.value, selectedMonth.value, 0).getDate();
});

const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const getDayName = (day: number) => {
    const date = new Date(selectedYear.value, selectedMonth.value - 1, day);
    return dayNames[date.getDay()];
};

const engineers = computed(() => workloadResource.data)

const statusColors = {
    available: 'bg-green-500',
    unavailable: 'bg-red-500',
    holiday: 'bg-gray-500',
    work_on_holiday: 'bg-red-900',
    default: 'bg-white'
};

const getStatusClass = (status: string) => {
    const baseClasses = 'p-2 transition-colors duration-200';
    const colorClass = statusColors[status as keyof typeof statusColors] || statusColors.default;
    const hoverClass = `hover:${colorClass.replace('bg-', 'bg-opacity-75 ')}`;
    return `${baseClasses} ${colorClass} ${hoverClass}`;
};

const getStatusText = (status: string) => {
    switch (status) {
        case 'available':
            return 'Available';
        case 'unavailable':
            return 'Unavailable';
        case 'holiday':
            return 'Holiday';
        case 'work_on_holiday':
            return 'Working on Holiday';
        default:
            return 'Unspecified';
    }
};

const loadData = () => {
    workloadResource.fetch({
        year: selectedYear.value,
        month: selectedMonth.value,
    })

}
onMounted(()=>{
    loadData()
})

const isDrawerOpen = ref(false)
const selectedTasks = ref<any[]>([])

const showTaskDetails = (details: any) => {
    if (details?.length) {
        selectedTasks.value = details.split('{|}')
        isDrawerOpen.value = true
    }
}

const closeDrawer = () => {
    isDrawerOpen.value = false
    selectedTasks.value = []
}
</script>

<style scoped>
.overflow-x-auto {
    overflow-x: auto;
    overflow-y: visible;
}

table {
    border-collapse: separate;
    border-spacing: 1px;
}

th, td {
    transition: all 0.2s ease-in-out;
}

th:hover, td:hover {
    transform: scale(1.05);
    z-index: 20;
}

/* ปรับแต่งสไตล์สำหรับคอลัมน์แรกที่ติดอยู่ */
th:first-child, td:first-child {
    position: sticky;
    left: 0;
    z-index: 10;
    background-color: white;
}

/* ปรับแต่งสไตล์สำหรับแถวหัวตาราง */
thead th {
    background-color: #f3f4f6;
    font-weight: bold;
}

thead th:first-child {
    z-index: 11; /* ให้อยู่เหนือเซลล์อื่นๆ */
}

.bg-yellow-200 {
    background-color: #fef08a;
}

/* เพิ่มสไตล์เพื่อให้เซลล์มีความสูงพอดีกับเนื้อหา */
td {
    height: auto;
    min-height: 60px;
    padding: 4px;
}

/* ปรับขนาดตัวอักษรของวันที่และชื่อวัน */
th {
    font-size: 0.9rem;
}

th span {
    font-size: 0.75rem;
}

.job-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.8);
}

.drawer-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 100%;
    z-index: 50;
    visibility: hidden;
    transition: visibility 0.3s;
}

.drawer-container.active {
    visibility: visible;
}

.drawer-overlay {
    position: absolute;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5);
    opacity: 0;
    transition: opacity 0.3s ease-in-out;
    pointer-events: none;
}

.drawer-container.active .drawer-overlay {
    opacity: 1;
    pointer-events: auto;
}

.drawer-content {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: white;
    border-top-left-radius: 1rem;
    border-top-right-radius: 1rem;
    padding: 1rem;
    transform: translateY(100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    height: 50vh;
    overflow-y: auto;
}

.drawer-container.active .drawer-content {
    transform: translateY(0);
}

.drawer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 1rem;
}

.drawer-body {
    max-height: calc(50vh - 4rem);
    overflow-y: auto;
}
</style>
