<script setup>
import { ref, onMounted, watch, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createDocumentResource, createResource } from 'frappe-ui'
import UserLayout from '@/layouts/userLayout.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { session } from '@/data/session'
import { useToast } from '@/composables/useToast'
import ApproversGrid from '@/components/ApproversGrid.vue'

const formatDate = inject('formatDate')
const formatCurrency = inject('formatCurrency')

const router = useRouter()
const route = useRoute()
const toast = useToast()

const workflowResource = createResource({
  url: 'frappe.model.workflow.get_transitions',
  auto: false,
})

const advanceResource = createDocumentResource({
  doctype: 'SMO Advance Entry',
  name: route.params.id,
  auto: true,
  onError: (error) => {
    toast.error(error.messages.join(', '))
  }
})

const applyWorkflowResource = createResource({
  url: 'frappe.model.workflow.apply_workflow',
  auto: false,
  onSuccess: () => {
    advanceResource.reload()
  },
})

const rejectReason = ref('')

const applyTransition = async (transition) => {
  try {
    if (transition.action === 'Reject') {
      try {
        const response = await fetch(`/api/method/smartoffice.api.expense.update_reject_reason`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            doctype: 'SMO Advance Entry',
            docname: route.params.id,
            reject_reason: rejectReason.value
          })
        })

        const data = await response.json()
        
        if (!response.ok) {
          // ตรวจสอบข้อความ error จาก server
          const errorMessage = data._server_messages 
            ? JSON.parse(JSON.parse(data._server_messages)[0]).message 
            : 'ไม่สามารถบันทึกเหตุผลการ Reject ได้'
          
          toast.error(errorMessage)
          return
        }
      } catch (error) {
        toast.error('เกิดข้อผิดพลาดในการบันทึกเหตุผลการ Reject')
        return
      }
    }

    await applyWorkflowResource.submit({
      doc: advanceResource.doc,
      action: transition.action,
    })
    
    toast.success('บันทึกข้อมูลสำเร็จ')
    
  } catch (error) {
    console.log(error)
    let errorMessage = 'เกิดข้อผิดพลาดในการดำเนินการ'
    if (applyWorkflowResource.error?.messages) {
      errorMessage = applyWorkflowResource.error.messages.join(', ')
    }
    toast.error(errorMessage)
  }
}

const goBack = () => {
  router.go(-1)
}

watch(() => advanceResource.doc, (newDoc) => {
  if (newDoc) {
    workflowResource.fetch({
      doc: newDoc
    })
  }
}, { immediate: true })

const handleTransition = (transition) => {
  if (transition.action === 'Reject') {
    document.getElementById('reject-modal').checked = true
  } else {
    applyTransition(transition)
  }
}

const confirmReject = async () => {
  if (!rejectReason.value) {
    alert('Please enter a reason for rejection')
    return
  }
  advanceResource.doc.reject_reason = rejectReason.value
  await applyTransition({ action: 'Reject' })
}

const goEdit = () => {
  window.open(`/app/smo-advance-entry/${route.params.id}?from_page=/intranet`, '_blank')
}

window.refresh_table = () => {
  advanceResource.reload()
}
</script>

<template>
  <UserLayout>
    <div class="mx-auto px-4 py-6">
      <!-- Modal -->
      <input type="checkbox" id="reject-modal" class="modal-toggle" />
      <div class="modal">
        <div class="modal-box">
          <h3 class="font-bold text-lg">Please provide a reason for rejection</h3>
          <textarea v-model="rejectReason" class="textarea textarea-bordered w-full mt-4" placeholder="Reason..."></textarea>
          <div class="modal-action">
            <label for="reject-modal" class="btn" @click="confirmReject">Confirm</label>
            <label for="reject-modal" class="btn">Cancel</label>
          </div>
        </div>
      </div>

      <!-- Workflow Transitions -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="flex justify-between items-center">
          <button 
            @click="goBack"
            class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
            Back
          </button>
          <div class="flex gap-4">
            <button 
              v-if="advanceResource.doc.workflow_state === 'Draft' && session.user === advanceResource.doc.owner"
              @click="goEdit"
              class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
              Edit
            </button>
            <button 
              v-for="transition in workflowResource.data" 
              :key="transition.name"
              @click="handleTransition(transition)"
              :disabled="applyWorkflowResource.loading"
              :class="{
                'bg-blue-500 hover:bg-blue-600': transition.action === 'Request Approve' || transition.action === 'Submit',
                'bg-green-500 hover:bg-green-600': transition.action === 'Approve' || transition.action === 'Final Approve',
                'bg-red-500 hover:bg-red-600': transition.action === 'Reject',
                'opacity-50 cursor-not-allowed': applyWorkflowResource.loading,
                'text-white font-medium px-4 py-2 rounded-md transition-colors': true
              }">
              {{ transition.action }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="advanceResource.doc" class="space-y-6">
        <!-- Header Card -->
        <div class="bg-white rounded-lg shadow p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row justify-between items-start gap-4">
            <div>
              <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                <h1 class="text-lg sm:text-xl font-semibold text-gray-900">
                  Advance Entry - {{ advanceResource.doc.name }}
                </h1>
                <!-- Document Status -->
                <div :class="{
                  'inline-flex border rounded-md px-2 py-1': true,
                  'bg-gray-100 border-gray-200 text-gray-700': advanceResource.doc.workflow_state === 'Draft',
                  'bg-yellow-100 border-yellow-200 text-yellow-700': advanceResource.doc.workflow_state === 'Approval Review' || advanceResource.doc.workflow_state === 'Pending Approval',
                  'bg-green-100 border-green-200 text-green-700': advanceResource.doc.workflow_state === 'Approved',
                  'bg-red-100 border-red-200 text-red-700': advanceResource.doc.workflow_state === 'Rejected'
                }">
                  <p class="text-xs sm:text-sm font-medium">{{ advanceResource.doc.workflow_state }}</p>
                </div>
              </div>
              <p class="mt-1 text-xs sm:text-sm text-gray-600">
                Reference Code: {{ advanceResource.doc.reference_code }}
              </p>
              <!-- Document Info -->
              <div class="mt-2 space-y-2">
                <div class="flex items-center gap-2">
                  <UserAvatar 
                    :email="advanceResource.doc.owner" 
                    size="sm"
                  />
                  <div class="flex flex-col">
                    <p class="text-xs sm:text-sm text-gray-600">
                      Created by: {{ advanceResource.doc.owner }}
                    </p>
                    <p class="text-xs sm:text-sm text-gray-600">
                      Created on: {{ advanceResource.doc.creation?.split('.')[0]?.replace('T', ' ') }}
                    </p>
                  </div>
                </div>
              </div>
              <p v-if="advanceResource.doc.workflow_state === 'Rejected' && advanceResource.doc.reject_reason" 
                 class="mt-2 text-xs sm:text-sm text-red-600">
                Reject Reason: {{ advanceResource.doc.reject_reason }}
              </p>
            </div>
            <div class="bg-blue-50 p-3 rounded-lg self-start">
              <p class="text-xs sm:text-sm text-gray-600">Total Amount</p>
              <p class="text-lg sm:text-xl font-bold text-blue-600">
                {{ formatCurrency(advanceResource.doc.total_amount) }}
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
                <p class="font-medium">{{ advanceResource.doc.customer_name }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Site</p>
                <p class="font-medium">{{ advanceResource.doc.site_name }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Project</p>
                <p class="font-medium">{{ advanceResource.doc.project_name }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Project Code</p>
                <p class="font-medium">{{ advanceResource.doc.project_code }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Service Date</p>
                <p class="font-medium">{{ advanceResource.doc.service_date }}</p>
              </div>
            </div>
          </div>

          <!-- Service Info -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-4">
              Advance Details
            </h2>
            <div class="grid grid-cols-2 gap-y-4">
              <div>
                <p class="text-sm text-gray-500">Reference Code Finance</p>
                <p class="font-medium">{{ advanceResource.doc.reference_code_finance }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Reference Code Accounting</p>
                <p class="font-medium">{{ advanceResource.doc.reference_code_accounting }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Advance Amount</p>
                <p class="font-medium">{{ formatCurrency(advanceResource.doc.advance_amount) }}</p>
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
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Item
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Receipt Date
                  </th>
                  <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Attachment
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="item in advanceResource.doc.expense_item" :key="item.name">
                  <td class="px-6 py-4">
                    <div class="text-sm text-gray-900">{{ item.expense_type_name }}</div>
                    <div v-if="item.description" class="text-sm text-gray-500">
                      {{ item.description }}
                    </div>
                    <!-- Fuel Details -->
                    <div v-if="item.fuel_detail" class="text-sm text-gray-500">
                      Fuel Details: {{ item.fuel_detail }}
                    </div>
                    <div v-if="item.fuel_liter" class="text-sm text-gray-500">
                      Liters: {{ item.fuel_liter }}
                    </div>
                    <!-- Hotel Details -->
                    <div v-if="item.hotel_name && item.total_day" class="text-sm text-gray-500">
                      Hotel: {{ item.hotel_name }} {{ item.total_day }} days
                    </div>
                    <!-- Taxi Details -->
                    <div v-if="item.taxi_depart_distance" class="text-sm text-gray-500">
                      Departure Distance: {{ item.taxi_depart_distance }} km
                    </div>
                    <div v-if="item.taxi_return_distance" class="text-sm text-gray-500">
                      Return Distance: {{ item.taxi_return_distance }} km
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(item.receipt_date) }}
                  </td>
                  <td class="px-6 py-4 text-right whitespace-nowrap text-sm text-gray-900 font-medium">
                    {{ formatCurrency(item.total_cost) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <a 
                      v-if="item.attachment"
                      :href="`${item.attachment}`"
                      target="_blank"
                      class="inline-flex items-center text-blue-600 hover:text-blue-800"
                    >
                      <svg 
                        class="w-4 h-4 mr-1" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path 
                          stroke-linecap="round" 
                          stroke-linejoin="round" 
                          stroke-width="2" 
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                        <path 
                          stroke-linecap="round" 
                          stroke-linejoin="round" 
                          stroke-width="2"
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                        />
                      </svg>
                      View
                    </a>
                  </td>
                </tr>
              </tbody>
              <tfoot class="bg-gray-50 divide-y divide-gray-200">
                <tr>
                  <td colspan="2" class="px-6 py-4 text-right font-medium">Total Expenses</td>
                  <td class="px-6 py-4 text-right whitespace-nowrap text-gray-900 font-bold">
                    {{ formatCurrency(advanceResource.doc.total_amount) }}
                  </td>
                  <td></td>
                </tr>
                <tr>
                  <td colspan="2" class="px-6 py-4 text-right font-medium">Advance Amount</td>
                  <td class="px-6 py-4 text-right whitespace-nowrap text-gray-900 font-bold">
                    {{ formatCurrency(advanceResource.doc.advance_amount) }}
                  </td>
                  <td></td>
                </tr>
                <tr>
                  <td colspan="2" class="px-6 py-4 text-right font-medium">
                    {{ advanceResource.doc.advance_amount > advanceResource.doc.total_amount ? 'Advance Remaining (Refund)' : 'Advance Shortfall (Pay More)' }}
                  </td>
                  <td class="px-6 py-4 text-right whitespace-nowrap font-bold" 
                      :class="{
                        'text-green-600': advanceResource.doc.advance_amount > advanceResource.doc.total_amount,
                        'text-red-600': advanceResource.doc.advance_amount < advanceResource.doc.total_amount
                      }">
                    {{ formatCurrency(Math.abs(advanceResource.doc.advance_amount - advanceResource.doc.total_amount)) }}
                  </td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

          <!-- Approvers Card Grid -->
         <ApproversGrid 
          :approvers="advanceResource.doc.approvers"
        />
      </div>
    </div>
  </UserLayout>
</template>
