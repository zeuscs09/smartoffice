<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useToast } from '@/composables/useToast'
import { utils, writeFile } from 'xlsx'
import UserLayout from '@/layouts/userLayout.vue'
interface ExpenseReport {
  QCCORP: string
  QCBRANCH: string
  QCACCBOOK: string
  DATE: string
  CODE: string
  REMARKH1: string
  REMARKH2: string
  REMARKH3: string
  REMARKH4: string
  REMARKH5: string
  QCACCHART: string
  AMT: number
  DETAIL: string
  QCSECTI: string
  year: number
  month: string
  period: string
}

const toast = useToast()
const selectedMonth = ref<string>(new Date().toISOString().slice(0,7))
const isLoading = ref(false)
const reportData = ref<ExpenseReport[]>([])

// Format month display
const formattedMonth = computed(() => {
  if (!selectedMonth.value) return ''
  const date = new Date(selectedMonth.value + '-01')
  return date.toLocaleDateString('en-US', { 
    month: 'long',
    year: 'numeric'
  })
})

const getMonthName = (monthStr: string): string => {
  const date = new Date(`${monthStr}-01`)
  return date.toLocaleString('en-US', { month: 'long' })
}

const fetchReport = async () => {
  isLoading.value = true
  try {
    const [year, monthNumber] = selectedMonth.value.split('-')
    const monthName = getMonthName(`${year}-${monthNumber}`)
    
    const response = await fetch('/api/method/smartoffice.api.report.get_expense_report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        year: year,
        month: monthName
      })
    })
    const result = await response.json()
    
    if (result.message?.status === 'success') {
      reportData.value = result.message.data
    } else {
      toast.error(result.message?.message || 'Error fetching data')
    }
  } catch (err) {
    console.error('API Error:', err)
    toast.error('Error fetching data')
  } finally {
    isLoading.value = false
  }
}

// Calculate totals
const totals = computed(() => {
  if (!reportData.value.length) return null
  
  return {
    amount: reportData.value.reduce((sum, item) => sum + (item.AMT || 0), 0)
  }
})

const exportToExcel = () => {
  try {
    const excelData = reportData.value.map(item => ({
      'QCCORP': item.QCCORP,
      'QCBRANCH': item.QCBRANCH,
      'QCACCBOOK': item.QCACCBOOK,
      'DATE': item.DATE,
      'CODE': item.CODE,
      'REMARKH1': item.REMARKH1,
      'REMARKH2': item.REMARKH2,
      'REMARKH3': item.REMARKH3,
      'REMARKH4': item.REMARKH4,
      'REMARKH5': item.REMARKH5,
      'QCACCHART': item.QCACCHART,
      'AMT': item.AMT,
      'DETAIL': item.DETAIL,
      'QCSECTI': item.QCSECTI
    }))

    if (totals.value) {
      excelData.push({
        'QCCORP': 'Total',
        'QCBRANCH': '',
        'QCACCBOOK': '',
        'DATE': '',
        'CODE': '',
        'REMARKH1': '',
        'REMARKH2': '',
        'REMARKH3': '',
        'REMARKH4': '',
        'REMARKH5': '',
        'QCACCHART': '',
        'AMT': totals.value.amount,
        'DETAIL': '',
        'QCSECTI': ''
      })
    }

    const ws = utils.json_to_sheet(excelData)
    const wb = utils.book_new()
    utils.book_append_sheet(wb, ws, 'Expense Report')

    // กำหนดความกว้างคอลัมน์
    const colWidths = [
      { wch: 10 },  // QCCORP
      { wch: 10 },  // QCBRANCH
      { wch: 12 },  // QCACCBOOK
      { wch: 12 },  // DATE
      { wch: 12 },  // CODE
      { wch: 50 },  // REMARKH1
      { wch: 15 },  // REMARKH2
      { wch: 15 },  // REMARKH3
      { wch: 15 },  // REMARKH4
      { wch: 15 },  // REMARKH5
      { wch: 12 },  // QCACCHART
      { wch: 15 },  // AMT
      { wch: 30 },  // DETAIL
      { wch: 12 }   // QCSECTI
    ]
    ws['!cols'] = colWidths

    const fileName = `expense-report-${selectedMonth.value}.xlsx`
    writeFile(wb, fileName)
    
    toast.success('Export successful')
  } catch (err) {
    console.error('Export Error:', err)
    toast.error('Error exporting data')
  }
}

onMounted(() => {
  fetchReport()
})
</script>

<template>
  <UserLayout>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold">Expense Report</h1>
        <p class="text-gray-600">{{ formattedMonth }}</p>
      </div>
      
      <div class="flex gap-4 items-center">
        <input 
          type="month"
          v-model="selectedMonth"
          class="input input-bordered input-sm"
          @change="fetchReport"
        />

        <button 
          class="btn btn-ghost btn-sm"
          @click="exportToExcel"
          :disabled="isLoading || !reportData.length"
        >
          Export Excel
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="table table-zebra w-full table-xs">
        <thead>
          <tr>
            <th>QCCORP</th>
            <th>QCBRANCH</th>
            <th>QCACCBOOK</th>
            <th>DATE</th>
            <th>CODE</th>
            <th>REMARKH1</th>
            <th>REMARKH2</th>
            <th>REMARKH3</th>
            <th>REMARKH4</th>
            <th>REMARKH5</th>
            <th>QCACCHART</th>
            <th class="text-right">AMT</th>
            <th>DETAIL</th>
            <th>QCSECTI</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in reportData" :key="index">
            <td>{{ item.QCCORP }}</td>
            <td>{{ item.QCBRANCH }}</td>
            <td>{{ item.QCACCBOOK }}</td>
            <td>{{ item.DATE }}</td>
            <td>{{ item.CODE }}</td>
            <td>{{ item.REMARKH1 }}</td>
            <td>{{ item.REMARKH2 }}</td>
            <td>{{ item.REMARKH3 }}</td>
            <td>{{ item.REMARKH4 }}</td>
            <td>{{ item.REMARKH5 }}</td>
            <td>{{ item.QCACCHART }}</td>
            <td class="text-right">{{ item.AMT?.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</td>
            <td>{{ item.DETAIL }}</td>
            <td>{{ item.QCSECTI }}</td>
          </tr>
          
          <!-- Row Total -->
          <tr v-if="totals" class="font-bold bg-base-200">
            <td colspan="11" class="text-right">Total</td>
            <td class="text-right">{{ totals.amount.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}</td>
            <td colspan="2"></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  </UserLayout>
</template>

<style scoped>
.bg-base-200 {
  background-color: rgba(var(--b2) / var(--tw-bg-opacity));
  --tw-bg-opacity: 0.3;
}
</style>
