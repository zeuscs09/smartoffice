<script setup>
import { ref, onMounted, watch, computed, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createDocumentResource, createResource } from 'frappe-ui'
import UserLayout from '@/layouts/userLayout.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { session } from '@/data/session'
import { useToast } from '@/composables/useToast'
import ExpenseChart from '@/components/ExpenseChart.vue'
import { useExpenseTypes } from '@/composables/useExpenseTypes'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const workflowResource = createResource({
  url: 'frappe.model.workflow.get_transitions',
  auto: false,
})

const expenseResource = createDocumentResource({
  doctype: 'SMO Expense Request',
  name: route.params.id,
  auto: true,
})

const applyWorkflowResource = createResource({
  url: 'frappe.model.workflow.apply_workflow',
  auto: false,
  onSuccess: () => {
    expenseResource.reload()
  },
})

const rejectReason = ref('')

const applyTransition = async (transition) => {
  try {
    if (transition.action === 'Reject') {
      expenseResource.doc.reject_reason = rejectReason.value
      await expenseResource.setValue.submit(expenseResource.doc)
    }

    await applyWorkflowResource.submit({
      doc: expenseResource.doc,
      action: transition.action,
    })
    
    toast.success('Saved successfully')
    
  } catch (error) {
    let errorMessage = 'An error occurred during the operation'
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
    alert('Please enter a reason for rejection')
    return
  }
  await applyTransition({ action: 'Reject' })
}

const goBack = () => {
  router.go(-1)
}

const goEdit = () => { 
  window.open(`/app/smo-expense-request/${route.params.id}?from_page=/intranet`, '_blank') 
}

watch(() => expenseResource.doc, (newDoc) => {
  if (newDoc) {
    workflowResource.fetch({
      doc: newDoc
    })
  }
}, { immediate: true })

const groupedByProject = computed(() => {
  if (!expenseResource.doc?.expense_request_item) return {}
  
  return expenseResource.doc.expense_request_item.reduce((acc, item) => {
    const objectData = JSON.parse(item.object_data || '{}')
    const projectName = objectData.project_name || 'Uncategorized'
    
    if (!acc[projectName]) {
      acc[projectName] = []
    }
    acc[projectName].push({
      ...item,
      parsedData: objectData
    })
    
    return acc
  }, {})
})

const getProjectTotal = (items) => {
  return items.reduce((sum, item) => {
    const objectData = item.parsedData
    return sum + (objectData.total_cost || 0)
  }, 0)
}

const groupedByExpenseType = computed(() => {
  if (!expenseResource.doc?.expense_request_item) return {}
  
  return expenseResource.doc.expense_request_item.reduce((acc, item) => {
    const objectData = JSON.parse(item.object_data || '{}')
    const expenseType = objectData.expense_type_desc || 'Uncategorized'
    
    if (!acc[expenseType]) {
      acc[expenseType] = []
    }
    acc[expenseType].push({
      ...item,
      parsedData: objectData
    })
    
    return acc
  }, {})
})

const getExpenseTypeTotal = (items) => {
  return items.reduce((sum, item) => {
    const objectData = item.parsedData
    return sum + (objectData.total_cost || 0)
  }, 0)
}

const groupedExpenseItems = computed(() => {
  if (!expenseResource.doc?.expense_request_item) return []
  
  const expenseMap = new Map()
  
  expenseResource.doc.expense_request_item.forEach(item => {
    const objectData = JSON.parse(item.object_data || '{}')
    const key = `${objectData.service_date}-${objectData.customer_name}-${objectData.project_name}-${objectData.receipt_date}`
    
    if (!expenseMap.has(key)) {
      expenseMap.set(key, {
        key,
        service_date: objectData.service_date,
        customer_name: objectData.customer_name,
        project_name: objectData.project_name,
        receipt_date: objectData.receipt_date,
        total: 0,
        ...Object.fromEntries(expenseTypes.value.map(type => [type.name, 0]))
      })
    }
    
    const record = expenseMap.get(key)
    record[objectData.expense_type] = (record[objectData.expense_type] || 0) + objectData.total_cost
    record.total += objectData.total_cost
  })
  
  return Array.from(expenseMap.values()).sort((a, b) => {
    return `${a.service_date}${a.customer_name}${a.project_name}${a.receipt_date}`
      .localeCompare(`${b.service_date}${b.customer_name}${b.project_name}${b.receipt_date}`)
  })
})

const totals = computed(() => {
  if (!groupedExpenseItems.value.length) return {}
  
  return groupedExpenseItems.value.reduce((acc, item) => {
    expenseTypes.value.forEach(type => {
      acc[type.name] = (acc[type.name] || 0) + (item[type.name] || 0)
    })
    acc.total = (acc.total || 0) + item.total
    return acc
  }, {})
})

// inject formatters
const formatDate = inject('formatDate')
const formatCurrency = inject('formatCurrency')

const { expenseTypes, loading: loadingExpenseTypes, fetchExpenseTypes } = useExpenseTypes()

onMounted(() => {
  fetchExpenseTypes()
})
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
              v-if="expenseResource.doc?.workflow_state === 'Draft' && session.user === expenseResource.doc?.owner"
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
                'bg-blue-500 hover:bg-blue-600': transition.action === 'Request Approve',
                'bg-green-500 hover:bg-green-600': transition.action === 'Approve',
                'bg-red-500 hover:bg-red-600': transition.action === 'Reject',
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
                  Expense Request - {{ expenseResource.doc.name }}
                </h1>
                <!-- Document Status -->
                <div :class="{
                  'inline-flex border rounded-md px-2 py-1': true,
                  'bg-gray-100 border-gray-200 text-gray-700': expenseResource.doc.workflow_state === 'Draft',
                  'bg-yellow-100 border-yellow-200 text-yellow-700': expenseResource.doc.workflow_state === 'Approval Review',
                  'bg-green-100 border-green-200 text-green-700': expenseResource.doc.workflow_state === 'Approved',
                  'bg-red-100 border-red-200 text-red-700': expenseResource.doc.workflow_state === 'Rejected'
                }">
                  <p class="text-xs sm:text-sm font-medium">{{ expenseResource.doc.workflow_state }}</p>
                </div>
              </div>

              <!-- Request Information -->
              <div class="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div>
                  <p class="text-sm text-gray-500">Year</p>
                  <p class="font-medium">{{ expenseResource.doc.year }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Month</p>
                  <p class="font-medium">{{ expenseResource.doc.month }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Period</p>
                  <p class="font-medium">{{ expenseResource.doc.period }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Department</p>
                  <p class="font-medium">{{ expenseResource.doc.department }}</p>
                </div>
              </div>

              <!-- Document Info -->
              <div class="mt-4 space-y-2">
                <div class="flex items-center gap-2">
                  <UserAvatar 
                    :email="expenseResource.doc.request_by" 
                    size="sm"
                  />
                  <div class="flex flex-col">
                    <p class="text-xs sm:text-sm text-gray-600">
                      Request by: {{ expenseResource.doc.request_by }}
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
                {{ formatCurrency(expenseResource.doc.total) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Info Cards Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Summary by Expense Type -->
          <div class="bg-white rounded-lg shadow overflow-hidden">
            <div class="p-6 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">Summary by Expense Type</h2>
            </div>
            <!-- Chart -->
            <div class="h-64 px-6">
              <ExpenseChart 
                :data="groupedByExpenseType" 
                type="Expense Type"
                chartType="pie"
              />
            </div>
            <!-- Table -->
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Expense Type
                    </th>
                    <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Items
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(items, expenseType) in groupedByExpenseType" :key="expenseType">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {{ expenseType }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                      {{ formatCurrency(getExpenseTypeTotal(items)) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">
                      {{ items.length }} items
                    </td>
                  </tr>
                </tbody>
                <tfoot class="bg-gray-50">
                  <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Grand Total</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-blue-600">
                      {{ formatCurrency(expenseResource.doc?.total || 0) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">
                      {{ expenseResource.doc?.expense_request_item?.length || 0 }} items
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- Summary by Project -->
          <div class="bg-white rounded-lg shadow overflow-hidden">
            <div class="p-6 border-b border-gray-200">
              <h2 class="text-lg font-medium text-gray-900">Summary by Project</h2>
            </div>
            <!-- Chart -->
            <div class="h-64 px-6">
              <ExpenseChart 
                :data="groupedByProject" 
                type="Project"
                chartType="bar"
              />
            </div>
            <!-- Table -->
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Project
                    </th>
                    <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Items
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(items, projectName) in groupedByProject" :key="projectName">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {{ projectName }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                      {{ formatCurrency(getProjectTotal(items)) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">
                      {{ items.length }} items
                    </td>
                  </tr>
                </tbody>
                <tfoot class="bg-gray-50">
                  <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Grand Total</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-blue-600">
                      {{ formatCurrency(expenseResource.doc?.total || 0) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">
                      {{ expenseResource.doc?.expense_request_item?.length || 0 }} items
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>

       

        <!-- Expense Items Table -->
        <div class="bg-white rounded-lg shadow">
          <div class="p-6 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">Expense Items</h2>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">
                    Service Date
                  </th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">
                    Customer
                  </th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">
                    Project
                  </th>
                  <th scope="col" class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">
                    Receipt Date
                  </th>
                  <th 
                    v-for="type in expenseTypes" 
                    :key="type.name"
                    class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase whitespace-nowrap"
                  >
                    {{ type.description }}
                  </th>
                  <th scope="col" class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase whitespace-nowrap">
                    Total
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="item in groupedExpenseItems" :key="item.key">
                  <td class="px-3 py-4 text-sm text-gray-900 whitespace-nowrap">{{ formatDate(item.service_date) }}</td>
                  <td class="px-3 py-4 text-sm text-gray-900 whitespace-nowrap">{{ item.customer_name }}</td>
                  <td class="px-3 py-4 text-sm text-gray-900 whitespace-nowrap">{{ item.project_name }}</td>
                  <td class="px-3 py-4 text-sm text-gray-900 whitespace-nowrap">{{ formatDate(item.receipt_date) }}</td>
                  <td 
                    v-for="type in expenseTypes" 
                    :key="type.name"
                    class="px-3 py-4 text-sm text-right text-gray-900 whitespace-nowrap"
                  >
                    {{ formatCurrency(item[type.name]) }}
                  </td>
                  <td class="px-3 py-4 text-sm text-right font-medium text-blue-600 whitespace-nowrap">
                    {{ formatCurrency(item.total) }}
                  </td>
                </tr>
              </tbody>
              <tfoot class="bg-gray-50">
                <tr>
                  <td>&nbsp;</td>
                  <td>&nbsp;</td>
                  <td>&nbsp;</td>
                  
                  <td class="px-3 py-4 text-sm font-medium text-gray-900 whitespace-nowrap sticky left-0 bg-gray-50">
                    Grand Total
                  </td>
                  <td 
                    v-for="type in expenseTypes" 
                    :key="type.name"
                    class="px-3 py-4 text-sm text-right font-medium text-gray-900 whitespace-nowrap"
                  >
                    {{ formatCurrency(totals[type.name]) }}
                  </td>
                  <td class="px-3 py-4 text-sm text-right font-medium text-blue-600 whitespace-nowrap">
                    {{ formatCurrency(totals.total) }}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

         <!-- Approvers Card Grid -->
         <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Approvers</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="approver in expenseResource.doc.approvers" :key="approver.name"
              class="flex items-center space-x-4 p-4 rounded-lg border border-gray-200"
              :class="{
                'bg-green-50 border-green-200': approver.status === 'Approved',
                'bg-red-50 border-red-200': approver.status === 'Rejected',
                'bg-gray-50 border-gray-200 opacity-50': approver.status === 'Pending',
              }">
              <UserAvatar :email="approver.user_id" size="md" />
              <div>
                <p class="font-medium text-gray-900">{{ approver.user_id }}</p>
                <p class="text-sm text-gray-500">{{ approver.approver_role }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <span :class="{
                    'px-2 py-0.5 text-xs font-medium rounded-full': true,
                    'bg-green-100 text-green-800': approver.status === 'Approved',
                    'bg-red-100 text-red-800': approver.status === 'Rejected',
                    'bg-gray-100 text-gray-800': approver.status === 'Pending'
                  }">
                    {{ approver.status }}
                  </span>
                  <span v-if="approver.action_date" class="text-xs text-gray-500">
                    {{ approver.action_date?.split('.')[0]?.replace('T', ' ') }}
                  </span>
                </div>
                <p v-if="approver.comment" class="text-sm text-gray-600 mt-1">
                  Comment: {{ approver.comment }}
                </p>
                <p v-if="approver.duration" class="text-xs text-gray-500 mt-1">
                  Duration: {{ Math.round(approver.duration) }} seconds
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </UserLayout>
</template>

<style scoped>

</style>
