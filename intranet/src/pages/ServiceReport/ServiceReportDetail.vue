<template>
    <UserLayout>
        <div class="mx-auto px-4 py-6">
            <!-- Modal -->
            <input type="checkbox" id="reject-modal" class="modal-toggle" />
            <div class="modal">
                <div class="modal-box">
                    <h3 class="font-bold text-lg">Please enter rejection reason</h3>
                    <textarea v-model="rejectReason" class="textarea textarea-bordered textarea-sm w-full mt-4"
                        placeholder="Reason..."></textarea>
                    <div class="modal-action">
                        <label for="reject-modal" class="btn btn-sm" @click="confirmReject">Confirm</label>
                        <label for="reject-modal" class="btn btn-sm">Cancel</label>
                    </div>
                </div>
            </div>

            <!-- Workflow Transitions -->
            <div class="bg-white rounded-lg shadow p-4 mb-4">
                <div class="flex justify-between items-center">
                    <button @click="goBack"
                        class="btn btn-sm bg-gray-500 hover:bg-gray-700 text-white">
                        Back
                    </button>
                    <div class="flex gap-2">

                        <button
                            v-if="(serviceReportResource.doc.workflow_state === 'Draft' || serviceReportResource.doc.workflow_state === 'Customer Reject') && session.user === serviceReportResource.doc.owner"
                            @click="goEdit"
                            class="btn btn-sm bg-green-500 hover:bg-green-600 text-white">
                            Edit
                        </button>
                        <button v-for="transition in workflowResource.data" :key="transition.name"
                            @click="handleTransition(transition)" :disabled="applyWorkflowResource.loading" :class="{
                                'btn btn-sm': true,
                                'bg-blue-500 hover:bg-blue-600': transition.action === 'Request Approve',
                                'bg-green-500 hover:bg-green-600': transition.action === 'Approve',
                                'bg-red-500 hover:bg-red-600': transition.action === 'Reject',
                                'opacity-50 cursor-not-allowed': applyWorkflowResource.loading,
                                'text-white': true
                            }">
                            {{ transition.action }}
                        </button>
                    </div>
                </div>
            </div>

            <div v-if="serviceReportResource.doc" class="space-y-6">
                <!-- Header Card -->
                <div class="bg-white rounded-lg shadow p-4 sm:p-6">
                    <div class="flex flex-col sm:flex-row justify-between items-start gap-4">
                        <div>
                            <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                                <h1 class="text-lg sm:text-xl font-semibold text-gray-900">
                                    Service Report - {{ serviceReportResource.doc.name }}
                                </h1>
                                <!-- Document Status -->
                                <div :class="{
                                    'inline-flex border rounded-md px-2 py-1': true,
                                    'bg-gray-100 border-gray-200 text-gray-700': serviceReportResource.doc.workflow_state === 'Draft',
                                    'bg-yellow-100 border-yellow-200 text-yellow-700': serviceReportResource.doc.workflow_state === 'Customer Review',
                                    'bg-green-100 border-green-200 text-green-700': serviceReportResource.doc.workflow_state === 'Customer Approved',
                                    'bg-red-100 border-red-200 text-red-700': serviceReportResource.doc.workflow_state === 'Rejected'
                                }">
                                    <p class="text-xs sm:text-sm font-medium">{{
                                        serviceReportResource.doc.workflow_state }}</p>
                                </div>
                            </div>
                            <p class="mt-1 text-xs sm:text-sm text-gray-600">
                                {{ serviceReportResource.doc.task }} : {{ serviceReportResource.doc.task_name }}
                            </p>
                            <!-- Document Info -->
                            <div class="mt-2 space-y-2">
                                <div class="flex items-center gap-2">
                                    <UserAvatar :email="serviceReportResource.doc.owner" size="sm" />
                                    <div class="flex flex-col">
                                        <p class="text-xs sm:text-sm text-gray-600">
                                            Created by: {{ serviceReportResource.doc.owner }}
                                        </p>
                                        <p class="text-xs sm:text-sm text-gray-600">
                                            Created on: {{
                                                serviceReportResource.doc.creation?.split('.')[0]?.replace('T', ' ') }}
                                        </p>
                                    </div>
                                </div>
                            </div>
                            <p v-if="serviceReportResource.doc.workflow_state === 'Rejected' && serviceReportResource.doc.reject_reason"
                                class="mt-2 text-xs sm:text-sm text-red-600">
                                Reject Reason: {{ serviceReportResource.doc.reject_reason }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Info Cards Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Customer Info -->
                    <div class="bg-white rounded-lg shadow p-6">
                        <h2 class="text-lg font-medium text-gray-900 mb-4">
                            Customer Information
                        </h2>
                        <div class="grid grid-cols-2 gap-y-4">
                            <div>
                                <p class="text-sm text-gray-500">Customer</p>
                                <p class="font-medium">{{ serviceReportResource.doc.customer_name }}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500">Site</p>
                                <p class="font-medium">{{ serviceReportResource.doc.site_name }}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500">Project</p>
                                <p class="font-medium">{{ serviceReportResource.doc.project_name }}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500">Project Code</p>
                                <p class="font-medium">{{ serviceReportResource.doc.project_code }}</p>
                            </div>
                            <!-- เพิ่มส่วนข้อมูลติดต่อ -->
                            <template v-if="serviceReportResource.doc.contact_name">
                                <div>
                                    <p class="text-sm text-gray-500">Contact Person</p>
                                    <p class="font-medium">{{ serviceReportResource.doc.contact_name }}</p>
                                </div>
                            </template>
                            <template v-if="serviceReportResource.doc.contact_mobile">
                                <div>
                                    <p class="text-sm text-gray-500">Contact Mobile</p>
                                    <p class="font-medium">{{ serviceReportResource.doc.contact_mobile }}</p>
                                </div>
                            </template>
                            <template v-if="serviceReportResource.doc.contact_email">
                                <div>
                                    <p class="text-sm text-gray-500">Contact Email</p>
                                    <p class="font-medium">{{ serviceReportResource.doc.contact_email }}</p>
                                </div>
                            </template>
                        </div>
                    </div>

                    <!-- Service Info -->
                    <div class="bg-white rounded-lg shadow p-6">
                        <h2 class="text-lg font-medium text-gray-900 mb-4">
                            Service Details
                        </h2>
                        <div class="grid grid-cols-2 gap-y-4">
                            <div class="col-span-2 sm:col-span-1">
                                <p class="text-sm text-gray-500">Job Group</p>
                                <p class="font-medium truncate">{{ serviceReportResource.doc.job_group_name }}</p>
                            </div>
                            <div class="col-span-2 sm:col-span-1">
                                <p class="text-sm text-gray-500">Job Type</p>
                                <p class="font-medium break-words">{{ serviceReportResource.doc.job_type }}</p>
                            </div>
                            <div class="col-span-2 sm:col-span-1">
                                <p class="text-sm text-gray-500">Start Time</p>
                                <p class="font-medium">{{ serviceReportResource.doc.job_start_on }}</p>
                            </div>
                            <div class="col-span-2 sm:col-span-1">
                                <p class="text-sm text-gray-500">Finish Time</p>
                                <p class="font-medium">{{ serviceReportResource.doc.job_finish }}</p>
                            </div>
                            <div v-if="serviceReportResource.doc.is_holiday" class="col-span-2">
                                <p class="text-sm text-gray-500">Holiday</p>
                                <p class="font-medium">{{ serviceReportResource.doc.holiday_description }}</p>
                            </div>
                            <!-- Duration -->
                            <div class="col-span-2 sm:col-span-1">
                                <p class="text-sm text-gray-500">Duration (Hours)</p>
                                <p class="font-medium">{{ (serviceReportResource.doc.duration / 3600).toFixed(2) }}</p>
                            </div>
                            <!-- Overnight -->
                            <div v-if="serviceReportResource.doc.over_night" class="col-span-2 sm:col-span-1">
                                <p class="text-sm text-gray-500">Overnight</p>
                                <p class="font-medium text-yellow-600">Yes</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Team Members Card Grid -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-lg font-medium text-gray-900 mb-4">Team Members</h2>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div v-for="member in serviceReportResource.doc.team" :key="member.name"
                            class="flex items-center space-x-4 p-4 rounded-lg border border-gray-200 hover:bg-gray-50">
                            <UserAvatar :email="member.email" size="md" />
                            <div>
                                <p class="font-medium text-gray-900">{{ member.full_name }}</p>
                                <p class="text-sm text-gray-500">{{ member.employee }}</p>
                                <p class="text-sm text-gray-500">{{ member.email }}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Part Usage Table -->
                <div v-if="serviceReportResource.doc.part_usage.length > 0"
                    class="bg-white rounded-lg shadow overflow-hidden">
                    <div class="p-6 border-b border-gray-200">
                        <h2 class="text-lg font-medium text-gray-900">Part Usage</h2>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item
                                        Code</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item
                                        Name</th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity
                                    </th>
                                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Serial
                                        No</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200">
                                <tr v-for="part in serviceReportResource.doc.part_usage" :key="part.name">
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ part.item_code }}
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ part.item_name }}
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ part.qty }}</td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ part.serial_no }}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Solutions -->
                <div v-if="serviceReportResource.doc.solutions" class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-lg font-medium text-gray-900 mb-4">Solutions</h2>
                    <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ serviceReportResource.doc.solutions }}</p>
                </div>
            </div>
        </div>
    </UserLayout>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createDocumentResource, createResource } from 'frappe-ui'
import UserLayout from '@/layouts/userLayout.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { session } from '@/data/session'
import { useToast } from '@/composables/useToast'



const route = useRoute()
const router = useRouter()
const docName = route.params.id

const workflowResource = createResource({
    url: 'frappe.model.workflow.get_transitions',
    auto: false,
})

const serviceReportResource = createDocumentResource({
    doctype: 'SMO Service Report',
    name: route.params.id,
    auto: true,
})

const applyWorkflowResource = createResource({
    url: 'frappe.model.workflow.apply_workflow',
    auto: false,
    onSuccess: () => {
        // รีโหลดข้อมูลเกสารหลังจาก apply workflow สำเร็จ
        serviceReportResource.reload()
    },
})

const rejectReason = ref('')

const toast = useToast()

const applyTransition = async (transition) => {
    try {
        if (transition.action === 'Reject') {
            serviceReportResource.doc.reject_reason = rejectReason.value
            await serviceReportResource.setValue.submit(serviceReportResource.doc)
        }

        await applyWorkflowResource.submit({
            doc: serviceReportResource.doc,
            action: transition.action,
        })
        
        // แสดง success message
        toast.success('บันทึกข้อมูลสำเร็จ')
        
    } catch (error) {
        let errorMessage = 'เกิดข้อผิดพลาดในการดำเนินการ'
        console.log("debug", applyWorkflowResource.error.messages)
        if (applyWorkflowResource.error.messages) {
            errorMessage = applyWorkflowResource.error.messages.join(', ')
        }
        
        toast.error(errorMessage)
    }
}

const handleTransition = (transition) => {
    if (transition.action === 'Reject') {
        document.getElementById('reject-modal').checked = true
    } else {
        applyTransition(transition)
    }
}

const confirmReject = async () => {
    if (!rejectReason.value) {
        alert('กรุณาใส่เหตุผลในการ Reject')
        return
    }
    serviceReportResource.doc.reject_reason = rejectReason.value
    await applyTransition({ action: 'Reject' })
}

const goBack = () => router.go(-1)
const goEdit = () => window.open(`/app/smo-service-report/${serviceReportResource.doc.name}`, '_blank')

window.refresh_table = () => {
    serviceReportResource.reload()
}

watch(() => serviceReportResource.doc, (newDoc) => {
    if (newDoc) {
        workflowResource.fetch({
            doc: newDoc
        })
    }
}, { immediate: true })
</script>