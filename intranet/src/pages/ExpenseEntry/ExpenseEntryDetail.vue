<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { createDocumentResource, createResource } from 'frappe-ui'
import { formatCurrency } from '@/utils/formatters'
import UserLayout from '@/layouts/userLayout.vue'
import { useRouter } from 'vue-router'
import UserAvatar from '@/components/UserAvatar.vue'
import { session } from '@/data/session'
import { useToast } from '@/composables/useToast'
import ApproversGrid from '@/components/ApproversGrid.vue'

const router = useRouter()

// import { useWorkFlowStore } from '@/stores/workFlowStore'

const route = useRoute()
// const workflowStore = useWorkFlowStore()

const workflowResource = createResource({
  url: 'frappe.model.workflow.get_transitions',
  auto: false,
  transform: (data) => {
    const uniqueTransitions = data.reduce((acc, transition) => {
      const key = `${transition.state}-${transition.action}-${transition.next_state}`
      if (!acc[key]) {
        acc[key] = transition
      }
      return acc
    }, {})

    return Object.values(uniqueTransitions)
  }
})
const expenseResource = createDocumentResource({
  doctype: 'SMO Expense Entry',
  name: route.params.id,
  auto: true,
})

const formatWorkingHours = (seconds) => {
  if (!seconds) return '-'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (minutes === 0) {
    return `${hours} ชั่วโมง`
  }

  return `${hours} ชั่วโมง ${minutes} นาที`
}

const applyWorkflowResource = createResource({
  url: 'frappe.model.workflow.apply_workflow',
  auto: false,
  onSuccess: () => {
    // รีโหลดข้อมูลเอกสารหลังจาก apply workflow สำเร็จ
    expenseResource.reload()
  },
  onError: (error) => {
    console.log("error in resource",error.messages)
  }
})

const rejectReason = ref('')

const toast = useToast()


const applyTransition = async (transition) => {
  try {
    if (transition.action === 'Reject') {
      // เพิ่มการจัดการ error สำหรับ API call
      const response = await fetch(`/api/method/smartoffice.api.expense.update_reject_reason`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          doctype: 'SMO Expense Entry',
          docname: route.params.id,
          reject_reason: rejectReason.value
        })
      })

      // ตรวจสอบ response status
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'ไม่สามารถบันทึกเหตุผลการ Reject ได้')
      }

      // ถ้าบันทึกเหตุผลสำเร็จ จึงดำเนินการ workflow ต่อ

    }
    await applyWorkflowResource.submit({
      doc: expenseResource.doc,
      action: transition.action,
    })


    toast.success('บันทึกสำเร็จ')

  } catch (error) {
    console.error('Error:', error)
    const errorMessage = error.messages.join(' ') || 'เกิดข้อผิดพลาดในการดำเนินการ'
    toast.error(errorMessage)
    return // ยกเลิกการทำงานถ้าเกิด error
  }
}

const goBack = () => {
  router.go(-1)
}
watch(() => expenseResource.doc, (newDoc) => {
  if (newDoc) {

    workflowResource.fetch({
      doc: newDoc
    })
  }
}, { immediate: true })

const handleTransition = (transition) => {
  if (transition.action === 'Reject') {
    // เปิด modal
    document.getElementById('reject-modal').checked = true
  } else {
    applyTransition(transition)
  }
}

const confirmReject = async () => {
  if (!rejectReason.value) {
    alert('กรุณาใ���่เหตุผลในการ Reject')
    return
  }
  expenseResource.doc.reject_reason = rejectReason.value
  await applyTransition({ action: 'Reject' })
}

const goEdit = () => {
  window.open(`/app/smo-expense-entry/${route.params.id}?from_page=/intranet`, '_blank')
}

// ฟังก์ชันสำหรับแปลงวันที่ให้อยู่ในรูปแบบที่ถูกต้อง


</script>

<template>
  <UserLayout>


    <div class="mx-auto px-4 py-6">
      <!-- Modal -->
      <input type="checkbox" id="reject-modal" class="modal-toggle" />
      <div class="modal">
        <div class="modal-box">
          <h3 class="font-bold text-lg">กรุณาใส่เหตุผลในการ Reject</h3>
          <textarea v-model="rejectReason" class="textarea textarea-bordered w-full mt-4"
            placeholder="เหตุผล..."></textarea>
          <div class="modal-action">
            <label for="reject-modal" class="btn" @click="confirmReject">ยืนยัน</label>
            <label for="reject-modal" class="btn">ยกเลิก</label>
          </div>
        </div>
      </div>

      <!-- Workflow Transitions -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="flex justify-between items-center">
          <button @click="goBack" class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
            Back
          </button>
          <div class="flex gap-4">
            <button v-if="expenseResource.doc.workflow_state === 'Draft' && session.user === expenseResource.doc.owner"
              @click="goEdit" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
              Edit
            </button>
            <button v-for="transition in workflowResource.data" :key="transition.name"
              @click="handleTransition(transition)" :disabled="applyWorkflowResource.loading" :class="{
                'bg-blue-500 hover:bg-blue-600': transition.action === 'Request Approve' || transition.action === 'Submit',
                'bg-green-500 hover:bg-green-600': transition.action === 'Approve' || transition.action === 'Final Approve',
                'bg-red-500 hover:bg-red-600': transition.action === 'Reject',
                'bg-gray-500 hover:bg-gray-600': !['Request Approve', 'Approve', 'Reject', 'Submit'].includes(transition.action),
                'opacity-50 cursor-not-allowed': applyWorkflowResource.loading,
                'text-white font-medium px-4 py-2 rounded-md transition-colors': true
              }">
              {{ transition.action }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="expenseResource.doc" class="space-y-6">

        <!-- Header Card -->
        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row justify-between items-start gap-4">
            <div>
              <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                <h1 class="text-lg sm:text-xl font-semibold text-gray-900">
                  Expense Entry - {{ expenseResource.doc.name }}
                </h1>
                <!-- Document Status -->
                <div :class="{
                  'inline-flex border rounded-md px-2 py-1': true,
                  'bg-gray-100 border-gray-200 text-gray-700': expenseResource.doc.workflow_state === 'Draft',
                  'bg-yellow-100 border-yellow-200 text-yellow-700': expenseResource.doc.workflow_state === 'Approval Review' || expenseResource.doc.workflow_state === 'Admin Review',
                  'bg-green-100 border-green-200 text-green-700': expenseResource.doc.workflow_state === 'Approved',
                  'bg-red-100 border-red-200 text-red-700': expenseResource.doc.workflow_state === 'Rejected'
                }">
                  <p class="text-xs sm:text-sm font-medium">{{ expenseResource.doc.workflow_state }}</p>
                </div>
              </div>
              <p class="mt-1 text-xs sm:text-sm text-gray-600">
                Service Report: {{ expenseResource.doc.service_report }}
              </p>
              <!-- Document Info -->
              <div class="mt-2 space-y-2">
                <div class="flex items-center gap-2">
                  <UserAvatar :email="expenseResource.doc.owner" size="sm" />
                  <div class="flex flex-col">
                    <p class="text-xs sm:text-sm text-gray-600">
                      Created by: {{ expenseResource.doc.owner }}
                    </p>
                    <p class="text-xs sm:text-sm text-gray-600">
                      Created on: {{ expenseResource.doc.creation?.split('.')[0]?.replace('T', ' ') }}
                    </p>
                  </div>
                </div>
              </div>
              <p v-if="expenseResource.doc.workflow_state === 'Rejected' && expenseResource.doc.reject_reason"
                class="mt-2 text-xs sm:text-sm text-red-600">
                Reject Reason: {{ expenseResource.doc.reject_reason }}
              </p>
            </div>
            <div class="bg-blue-50 p-3 rounded-lg self-start">
              <p class="text-xs sm:text-sm text-gray-600">Total Amount</p>
              <p class="text-lg sm:text-xl font-bold text-blue-600">
                {{ formatCurrency(expenseResource.doc.total_amount) }}
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
                <p class="font-medium">{{ expenseResource.doc.customer_name }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Site</p>
                <p class="font-medium">{{ expenseResource.doc.site_name }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Project</p>
                <p class="font-medium">{{ expenseResource.doc.project_name }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Project Code</p>
                <p class="font-medium">{{ expenseResource.doc.project_code }}</p>
              </div>
            </div>
          </div>

          <!-- Service Info -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">
              Service Details
            </h2>
            <div class="grid grid-cols-2 gap-y-4">
              <div>
                <p class="text-sm text-gray-500">Service Report No.</p>
                <p class="font-medium">{{ expenseResource.doc.service_report }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Service Date</p>
                <p class="font-medium">{{ expenseResource.doc.service_date }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Working Hours</p>
                <p class="font-medium">{{ formatWorkingHours(expenseResource.doc.working_hour) }}</p>
              </div>
              <div v-if="expenseResource.doc.is_holiday">
                <p class="text-sm text-gray-500">Holiday</p>
                <p class="font-medium">{{ expenseResource.doc.holiday_description }}</p>
              </div>
              <div v-if="expenseResource.doc.over_night">
                <p class="text-sm text-gray-500">Finish Date</p>
                <p class="font-medium">{{ expenseResource.doc.finish_date }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Expense Items Table -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div class="p-6 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">Expense Items</h2>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col"
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Expense Type
                  </th>
                  <th scope="col"
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th scope="col"
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Receipt Date
                  </th>
                  <th scope="col"
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Paid By
                  </th>
                  <th scope="col"
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th scope="col"
                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ไฟล์แนบ
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="item in expenseResource.doc.expense_item" :key="item.name">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ item.expense_type_name }}
                    <template v-if="item.system_reminder || item.reminder">
                      <br><small class="text-red-500">{{ item.reminder || item.system_reminder }}</small>
                    </template>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-500">
                    {{ item.description || '' }}
                    <template v-if="item.fuel_detail">
                      <br><small>รายละเอียดน้ำมัน: {{ item.fuel_detail }}</small>
                    </template>
                    <template v-if="item.fuel_liter">
                      <br><small>จำนวนลิตร: {{ item.fuel_liter }}</small>
                    </template>
                    <template v-if="item.hotel_name && item.total_day">
                      <br><small>โรงแรม: {{ item.hotel_name }} {{ item.total_day }} วัน</small>
                    </template>
                    <template v-if="item.from_date && item.to_date">
                      <br><small>จากวันที่: {{ item.from_date }} ถึงวันที่: {{ item.to_date }}</small>
                    </template>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ item.receipt_date }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ item.paid_by }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                    {{ formatCurrency(item.total_cost) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <a v-if="item.attachment"
                      :href="`${item.attachment}`"
                      target="_blank" class="inline-flex items-center text-blue-600 hover:text-blue-800">
                      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      เปิดดู
                    </a>
                  </td>
                </tr>
              </tbody>
              <tfoot class="bg-gray-50">
                <tr>
                  <td colspan="4" class="px-6 py-4 text-right font-medium">Total</td>
                  <td class="px-6 py-4 whitespace-nowrap text-gray-900 font-bold">
                    {{ formatCurrency(expenseResource.doc.total_amount) }}
                  </td>
                  <td colspan="2"></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <!-- Approvers Card Grid -->
        <ApproversGrid :approvers="expenseResource.doc.approvers" />
      </div>
    </div>
  </UserLayout>
</template>