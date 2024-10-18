<template>
    <UserLayout>
       
        <div v-if="!isLoading" class="max-w-4xl mx-auto bg-white shadow-lg rounded-lg overflow-hidden">

            <div v-if="task.doc">
                <div class="bg-gray-100 p-4 flex justify-between items-center">
                    <div class="flex items-center space-x-4">
                        <h1 class="text-2xl font-bold text-gray-800">
                            {{ task.doc.task_name }}
                            <span v-if="todo?.doc?.status">
                                <span :class="getStatusBadgeClass(todo?.doc?.status)" class="ml-2">
                                    {{ todo.doc?.status || 'กำลังโหลด...' }}
                                </span>
                            </span>
                        </h1>
                    </div>
                    <div class="flex items-center space-x-4">
                        <button v-if="canCreateServiceReport" @click="createServiceReport"
                            class="btn btn-primary btn-sm">
                            <span>&#10133;</span> สร้าง Service Report
                        </button>
                        <button @click="goBack" class="btn btn-ghost btn-sm">
                            <span class="mr-2">←</span> ย้อนกลับ
                        </button>
                    </div>
                </div>

                <div class="p-6">
                    <div class="grid md:grid-cols-2 gap-6">
                        <div class="space-y-4">
                            <h2 class="text-xl font-semibold text-gray-700 mb-3">ข้อมูลงาน</h2>
                            <InfoItem label="ประเภทงาน" :value="task.doc.job_type" />
                            
                            <InfoItem label="สถานะ" :value="todo ? todo?.doc?.status : ''" />
                            <InfoItem label="ความสำคัญ" :value="task.doc.priority" />
                            <InfoItem label="ช่วงเวลา" :value="task.doc.period" />
                            <InfoItem label="วันที่เริ่ม" :value="formatDate(task.doc.start_date)" />
                            <InfoItem label="วันที่สิ้นสุด" :value="formatDate(task.doc.finish_date)" />
                        </div>

                        <div class="space-y-4">
                            <h2 class="text-xl font-semibold text-gray-700 mb-3">ข้อมูลโครงการ</h2>
                            <InfoItem label="โครงการ" :value="task.doc.project_name" />
                            <InfoItem label="ลูกค้า" :value="task.doc.customer_name" />
                            <InfoItem label="ผู้ติดต่อ" :value="task.doc.contact_name" />
                            <InfoItem label="เบอร์โทรผู้ติดต่อ" :value="task.doc.contact_mobile" />
                            <InfoItem label="อีเมลผู้ติดต่อ" :value="task.doc.contact_email" />
                            <InfoItem label="สถานที่" :value="task.doc.site" />
                        </div>
                    </div>

                    <div class="mt-8">
                        <h2 class="text-xl font-semibold text-gray-700 mb-3">รายละเอียด</h2>
                        <div v-if="task.doc.detail" class="text-gray-600">
                            {{ task.doc.detail }}
                        </div>

                    </div>

                    <div class="mt-8">
                        <h2 class="text-xl font-semibold text-gray-700 mb-3">ทีมงาน</h2>
                        <div v-if="task.doc.team && task.doc.team.length > 0" class="grid md:grid-cols-2 gap-4">
                            <div v-for="member in task.doc.team" :key="member.name"
                                class="flex items-center space-x-4 bg-gray-50 p-4 rounded-lg">
                                <UserAvatar :email="member.email" size="lg" />
                                <div>
                                    <div class="font-medium text-gray-800">{{ member.full_name }}</div>
                                    <div class="text-sm text-gray-500">{{ member.email }}</div>
                                    <div class="text-sm"
                                        :class="member.overlapping_job_on_date ? 'text-red-500' : 'text-green-500'">
                                        {{ member.overlapping_job_on_date ? 'มีงานซ้อน' : 'ไม่มีงานซ้อน' }}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <p v-else class="text-gray-600">ไม่มีข้อมูลทีมงาน</p>
                    </div>
                </div>
            </div>
            <div v-else class="flex flex-col justify-center items-center min-h-screen space-y-6">
                <div class="text-center">
                    <h2 class="text-2xl font-bold text-gray-800 mb-2">ไม่พบข้อมูล</h2>
                    <p class="text-gray-600">ขออภัย ไม่พบข้อมูลงานที่คุณกำลังค้นหา</p>
                </div>

                <button @click="goBack" class="btn btn-primary btn-sm">
                    <span class="mr-2">←</span> ย้อนกลับ
                </button>
            </div>

        </div>
        <div v-if="isLoading" class="text-center py-8">
            <span class="loading loading-spinner loading-lg"></span>
        </div>
    </UserLayout>

</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UserLayout from '@/layouts/userLayout.vue'
import { createDocumentResource } from 'frappe-ui'
import UserAvatar from '@/components/UserAvatar.vue'
import InfoItem from '@/components/InfoItem.vue'

const route = useRoute()
const router = useRouter()
const taskId = route.params.id as string
const todoId = route.query.todo as string

const task = createDocumentResource({
    doctype: 'SMO Task',
    name: taskId,
    auto: true,
})

const todo = createDocumentResource({
    doctype: 'ToDo',
    name: todoId,
    auto: true,
})

// ใช้ computed property เพื่อตรวจสอบสถานะการโหลด
const isLoading = computed(() => task.loading || (todoId && todo.loading))

const canCreateServiceReport = computed(() => {
    return todo.doc?.status === 'Open' && todoId && !todo.loading
})

const formatDate = (dateString: string): string => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('th-TH', { year: 'numeric', month: 'long', day: 'numeric' })
}

const goBack = () => {
    router.go(-1)
}

const createServiceReport = () => {
    if (task.doc.name && todoId) {
        location.href = `/app/smo-service-report/new?from_todo=${todoId}&from_page=${route.fullPath}&task=${task.doc.name}`
    }
}

const getStatusBadgeClass = (status: string | undefined) => {
    const baseClasses = 'badge text-xs font-semibold px-2 py-1'
    switch (status) {
        case 'Open':
            return `${baseClasses} badge-primary`
        case 'Closed':
            return `${baseClasses} badge-success`
        case 'Cancelled':
            return `${baseClasses} badge-error`
        default:
            return `${baseClasses} badge-ghost`
    }
}

onMounted(() => {
    // task.reload()
    // if (todoId) {
    //     todo.reload()
    // }
})
</script>
