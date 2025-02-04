<script setup lang="ts">
import { ref, onMounted, watch, computed, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createDocumentResource, createResource } from 'frappe-ui'
import UserLayout from '@/layouts/userLayout.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { session } from '@/data/session'
import { useToast } from '@/composables/useToast'
import ExpenseChart from '@/components/ExpenseChart.vue'
import { useExpenseTypes } from '@/composables/useExpenseTypes'
import ApproversGrid from '@/components/ApproversGrid.vue'
import * as XLSX from 'xlsx'

const router = useRouter()
const route = useRoute()
const toast = useToast()

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
      try {
        const response = await fetch(`/api/method/smartoffice.api.expense.update_reject_reason`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            doctype: 'SMO Expense Request',
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
      doc: expenseResource.doc,
      action: transition.action,
    })
    
    toast.success('บันทึกข้อมูลสำเร็จ')
    
  } catch (error) {
    let errorMessage = 'เกิดข้อผิดพลาดในการดำเนินการ'
    if (applyWorkflowResource.error?.messages) {
      errorMessage = applyWorkflowResource.error.messages.join(', ')
    }
    toast.error(errorMessage)
  }
}

const cancelDocumentResource = createResource({
  url: 'frappe.desk.form.save.cancel',
  auto: false,
  onSuccess: () => {
    expenseResource.reload()
    toast.success('เอกสารถูกยกเลิกเรียบร้อยแล้ว')
  },
  onError: (error) => {
    toast.error(error.messages?.join(', ') || 'ไม่สามารถยกเลิกเอกสารได้')
  }
})

const goCancel = async () => {
  try {
    await cancelDocumentResource.submit({
      doctype: 'SMO Expense Request',
      name: route.params.id,
      workflow_state_fieldname: 'workflow_state',
      workflow_state: 'Rejected'
    })
  } catch (error) {
    console.error('Error cancelling document:', error)
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
        project: objectData.project,
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

const groupedAttachments = computed(() => {
  if (!expenseResource.doc?.expense_request_item) return []
  
  const attachmentMap = new Map()
  
  expenseResource.doc.expense_request_item.forEach(item => {
    const objectData = JSON.parse(item.object_data || '{}')
    if (!objectData.attachment) return // ข้ามรายการที่ไม่มีเอกสารแนบ
    
    const key = `${objectData.service_date}-${objectData.customer_name}-${objectData.project_name}`
    
    if (!attachmentMap.has(key)) {
      attachmentMap.set(key, {
        service_date: objectData.service_date,
        customer_name: objectData.customer_name,
        project_name: objectData.project_name,
        attachments: []
      })
    }
    
    const record = attachmentMap.get(key)
    record.attachments.push({
      file_url: objectData.attachment,
      expense_type: objectData.expense_type_desc,
      receipt_date: objectData.receipt_date,
      total_cost: objectData.total_cost
    })
  })
  
  return Array.from(attachmentMap.values()).sort((a, b) => 
    `${a.service_date}${a.customer_name}${a.project_name}`
      .localeCompare(`${b.service_date}${b.customer_name}${b.project_name}`)
  )
})

// inject formatters
const formatDate = inject('formatDate')
const formatCurrency = inject('formatCurrency')

const { expenseTypes, loading: loadingExpenseTypes, fetchExpenseTypes } = useExpenseTypes()

onMounted(() => {
  fetchExpenseTypes()
})

// เพิ่มฟังก์ชันสำหรับการพิมพ์ข้อมูลทั้งหมด
const printExpenseDetails = () => {
  const printWindow = window.open('', '_blank')
  if (!printWindow) return

  const expenseItemRows = groupedExpenseItems.value.map(item => `
    <tr>
      <td>${formatDate(item.service_date)}</td>
      <td>${item.project || ''}</td>
      <td>${item.customer_name}</td>
      <td>${item.project_name}</td>
      <td>${formatDate(item.receipt_date)}</td>
      ${expenseTypes.value.map(type => `
        <td class="text-right">${formatCurrency(item[type.name] || 0)}</td>
      `).join('')}
      <td class="text-right">${formatCurrency(item.total)}</td>
    </tr>
  `).join('')

  const expenseTypeHeaders = expenseTypes.value.map(type => 
    `<th class="text-right">${type.description}</th>`
  ).join('')

  const expenseTypeTotals = expenseTypes.value.map(type => 
    `<td class="text-right">${formatCurrency(totals.value[type.name] || 0)}</td>`
  ).join('')

  printWindow.document.write(`
    <html>
      <head>
        <title>Expense Details - ${expenseResource.doc?.name}</title>
        <style>
          @page {
            size: landscape;
            margin: 10mm;
          }
          body { 
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 15px;
            font-size: 12px;
          }
          .header {
            margin-bottom: 20px;
          }
          .header-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 15px;
          }
          .header-item {
            display: flex;
            gap: 10px;
          }
          .header-label {
            color: #666;
            min-width: 80px;
          }
          .header-value {
            font-weight: 500;
          }
          .doc-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
          }
          .total-amount {
            text-align: right;
            font-weight: bold;
            color: #1d4ed8;
            margin: 10px 0;
          }
          table { 
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1rem;
            font-size: 11px;
          }
          th, td { 
            border: 1px solid #000;
            padding: 6px;
            text-align: left;
          }
          th {
            background-color: #f8f9fa !important;
            -webkit-print-color-adjust: exact;
          }
          .text-right {
            text-align: right;
          }
          tfoot td {
            font-weight: bold;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div class="doc-title">
            Expense Request - ${expenseResource.doc?.name}
          </div>
          <div class="header-grid">
            <div class="header-item">
              <span class="header-label">Year:</span>
              <span class="header-value">${expenseResource.doc?.year}</span>
            </div>
            <div class="header-item">
              <span class="header-label">Month:</span>
              <span class="header-value">${expenseResource.doc?.month}</span>
            </div>
            <div class="header-item">
              <span class="header-label">Period:</span>
              <span class="header-value">${expenseResource.doc?.period}</span>
            </div>
            <div class="header-item">
              <span class="header-label">Request by:</span>
              <span class="header-value">${expenseResource.doc?.request_by}</span>
            </div>
            <div class="header-item">
              <span class="header-label">Created on:</span>
              <span class="header-value">${expenseResource.doc?.creation?.split('.')[0]?.replace('T', ' ')}</span>
            </div>
            <div class="header-item">
              <span class="header-label">Status:</span>
              <span class="header-value">${expenseResource.doc?.workflow_state}</span>
            </div>
          </div>
          <div class="total-amount">
            Total Amount: ${formatCurrency(expenseResource.doc?.total || 0)}
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Service Date</th>
              <th>Project Code</th>
              <th>Customer</th>
              <th>Project</th>
              <th>Receipt Date</th>
              ${expenseTypeHeaders}
              <th class="text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            ${expenseItemRows}
          </tbody>
          <tfoot>
            <tr>
              <td colspan="5">Grand Total</td>
              ${expenseTypeTotals}
              <td class="text-right">${formatCurrency(totals.value.total || 0)}</td>
            </tr>
          </tfoot>
        </table>
      </body>
    </html>
  `)
  
  printWindow.document.close()
  printWindow.print()
}

// เพิ่มฟังก์ชันสำหรับการพิมพ์
const printAttachments = () => {
  const printWindow = window.open('', '_blank')
  if (!printWindow) return
  
  const tableRows = attachmentsList.value.map(item => `
    <tr>
      <td>${formatDate(item.service_date)}</td>
      <td>${item.customer_name}</td>
      <td>${item.project_name}</td>
      <td>${item.expense_type_desc}</td>
      <td>${formatDate(item.receipt_date)}</td>
      <td class="text-right">${formatCurrency(item.total_cost)}</td>
    </tr>
  `).join('')

  printWindow.document.write(`
    <html>
      <head>
        <title>Expense Attachments - ${expenseResource.doc?.name}</title>
        <style>
          body { 
            font-family: Arial, sans-serif;
            margin: 20px;
            font-size: 12px;
          }
          h2 { 
            margin-bottom: 20px;
            font-size: 14px;
          }
          table { 
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1rem;
          }
          th, td { 
            border: 1px solid #000;
            padding: 8px;
            text-align: left;
          }
          th {
            background-color: #f8f9fa !important;
            -webkit-print-color-adjust: exact;
          }
          .text-right {
            text-align: right;
          }
          tfoot td {
            font-weight: bold;
          }
        </style>
      </head>
      <body>
        <h2>Expense Attachments - ${expenseResource.doc?.name}</h2>
        <table>
          <thead>
            <tr>
              <th>Service Date</th>
              <th>Customer</th>
              <th>Project</th>
              <th>Expense Type</th>
              <th>Receipt Date</th>
              <th class="text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            ${tableRows}
          </tbody>
          <tfoot>
            <tr>
              <td colspan="5">Total</td>
              <td class="text-right">${formatCurrency(totalAmount.value)}</td>
            </tr>
          </tfoot>
        </table>
      </body>
    </html>
  `)
  
  printWindow.document.close()
  printWindow.print()
}

// ปรับ computed property สำหรับแสดงในตาราง
const attachmentsList = computed(() => {
  if (!expenseResource.doc?.expense_request_item) return []
  
  return expenseResource.doc.expense_request_item
    .filter(item => {
      const objectData = JSON.parse(item.object_data || '{}')
      return objectData.attachment // กรองเฉพาะรายการที่มีเอกสารแนบ
    })
    .map(item => {
      const objectData = JSON.parse(item.object_data || '{}')
      return {
        service_date: objectData.service_date,
        customer_name: objectData.customer_name,
        project_name: objectData.project_name,
        expense_type_desc: objectData.expense_type_desc,
        receipt_date: objectData.receipt_date,
        total_cost: objectData.total_cost,
        file_url: objectData.attachment
      }
    })
    .sort((a, b) => 
      `${a.service_date}${a.customer_name}${a.project_name}`
        .localeCompare(`${b.service_date}${b.customer_name}${b.project_name}`)
    )
})

const totalAmount = computed(() => {
  return attachmentsList.value.reduce((sum, item) => sum + (item.total_cost || 0), 0)
})

// เพิ่มฟังก์ชันสำหรับ Export Excel
const exportToExcel = () => {
  // สร้าง styles ที่ใช้บ่อย
  const styles = {
    header: {
      font: { bold: true, color: { rgb: "FFFFFF" } },
      fill: { patternType: 'solid', fgColor: { rgb: "1F4E78" } },  // น้ำเงินเข้ม
      alignment: { horizontal: 'left', vertical: 'center' },
      border: {
        top: { style: 'thin', color: { rgb: "000000" } },
        bottom: { style: 'thin', color: { rgb: "000000" } },
        left: { style: 'thin', color: { rgb: "000000" } },
        right: { style: 'thin', color: { rgb: "000000" } }
      }
    },
    headerValue: {
      font: { bold: true, size: 11 },
      fill: { patternType: 'solid', fgColor: { rgb: "F2F2F2" } },  // สีเทาอ่อน
      alignment: { horizontal: 'left', vertical: 'center' },
      border: {
        top: { style: 'thin', color: { rgb: "000000" } },
        bottom: { style: 'thin', color: { rgb: "000000" } },
        left: { style: 'thin', color: { rgb: "000000" } },
        right: { style: 'thin', color: { rgb: "000000" } }
      }
    },
    tableHeader: {
      font: { bold: true, color: { rgb: "FFFFFF" } },
      fill: { patternType: 'solid', fgColor: { rgb: "366092" } },  // น้ำเงินกลาง
      alignment: { horizontal: 'center', vertical: 'center', wrapText: true },
      border: {
        top: { style: 'thin', color: { rgb: "000000" } },
        bottom: { style: 'thin', color: { rgb: "000000" } },
        left: { style: 'thin', color: { rgb: "000000" } },
        right: { style: 'thin', color: { rgb: "000000" } }
      }
    },
    cell: {
      alignment: { vertical: 'center' },
      fill: { patternType: 'solid', fgColor: { rgb: "FFFFFF" } },
      border: {
        top: { style: 'thin', color: { rgb: "000000" } },
        bottom: { style: 'thin', color: { rgb: "000000" } },
        left: { style: 'thin', color: { rgb: "000000" } },
        right: { style: 'thin', color: { rgb: "000000" } }
      }
    },
    numericCell: {
      alignment: { horizontal: 'right', vertical: 'center' },
      fill: { patternType: 'solid', fgColor: { rgb: "FFFFFF" } },
      numFmt: '#,##0.00',
      border: {
        top: { style: 'thin', color: { rgb: "000000" } },
        bottom: { style: 'thin', color: { rgb: "000000" } },
        left: { style: 'thin', color: { rgb: "000000" } },
        right: { style: 'thin', color: { rgb: "000000" } }
      }
    },
    footer: {
      font: { bold: true },
      fill: { patternType: 'solid', fgColor: { rgb: "DCE6F1" } },  // สีฟ้าอ่อน
      alignment: { horizontal: 'left', vertical: 'center' },
      border: {
        top: { style: 'thin', color: { rgb: "000000" } },
        bottom: { style: 'double', color: { rgb: "000000" } },
        left: { style: 'thin', color: { rgb: "000000" } },
        right: { style: 'thin', color: { rgb: "000000" } }
      }
    },
    footerNumeric: {
      font: { bold: true },
      fill: { patternType: 'solid', fgColor: { rgb: "DCE6F1" } },  // สีฟ้าอ่อน
      alignment: { horizontal: 'right', vertical: 'center' },
      numFmt: '#,##0.00',
      border: {
        top: { style: 'thin', color: { rgb: "000000" } },
        bottom: { style: 'double', color: { rgb: "000000" } },
        left: { style: 'thin', color: { rgb: "000000" } },
        right: { style: 'thin', color: { rgb: "000000" } }
      }
    }
  }

  // สร้าง title และ header information
  const headerInfo = [
    ['EXPENSE REQUEST DETAILS', expenseResource.doc?.name],
    [''],  // blank row
    ['Year', expenseResource.doc?.year],
    ['Month', expenseResource.doc?.month],
    ['Period', expenseResource.doc?.period],
    ['Request by', expenseResource.doc?.request_by],
    ['Created on', expenseResource.doc?.creation?.split('.')[0]?.replace('T', ' ')],
    ['Status', expenseResource.doc?.workflow_state],
    ['Total Amount', formatCurrency(expenseResource.doc?.total || 0)],
    ['']  // blank row
  ]

  // สร้าง table headers
  const tableHeaders = [
    ['Service Date', 'Project Code', 'Customer', 'Project', 'Receipt Date',
     ...expenseTypes.value.map(type => type.description),
     'Total'
    ]
  ]

  // สร้าง data rows
  const dataRows = groupedExpenseItems.value.map(item => [
    formatDate(item.service_date),
    item.project || '',
    item.customer_name,
    item.project_name,
    formatDate(item.receipt_date),
    ...expenseTypes.value.map(type => item[type.name] || 0),
    item.total
  ])

  // สร้าง footer row
  const footerRow = [
    ['Grand Total', '', '', '', '',
     ...expenseTypes.value.map(type => totals.value[type.name] || 0),
     totals.value.total || 0
    ]
  ]

  // รวมทุก rows เข้าด้วยกัน
  const allRows = [...headerInfo, ...tableHeaders, ...dataRows, ...footerRow]

  // สร้าง workbook และ worksheet
  const wb = XLSX.utils.book_new()
  const ws = XLSX.utils.aoa_to_sheet(allRows)

  // กำหนดความกว้างคอลัมน์
  ws['!cols'] = [
    { wch: 12 },  // Service Date
    { wch: 15 },  // Project Code
    { wch: 30 },  // Customer
    { wch: 30 },  // Project
    { wch: 12 },  // Receipt Date
    ...expenseTypes.value.map(() => ({ wch: 15 })),  // Expense columns
    { wch: 15 }   // Total
  ]

  // กำหนด row height
  ws['!rows'] = Array(allRows.length).fill({ hpt: 25 })  // 25 points height

  // Apply styles for title and header info
  for (let R = 0; R < headerInfo.length; R++) {
    for (let C = 0; C < 2; C++) {
      const cellRef = XLSX.utils.encode_cell({ r: R, c: C })
      if (!ws[cellRef]) continue
      
      if (R === 0) {  // Title row
        ws[cellRef].s = {
          ...styles.header,
          font: { ...styles.header.font, size: 14 }
        }
      } else if (R > 1) {  // Header info (skip blank row)
        ws[cellRef].s = C === 0 ? styles.header : styles.headerValue
      }
    }
  }

  // Apply styles for table headers
  const tableHeaderRowIndex = headerInfo.length
  for (let C = 0; C < tableHeaders[0].length; C++) {
    const cellRef = XLSX.utils.encode_cell({ r: tableHeaderRowIndex, c: C })
    if (!ws[cellRef]) continue
    ws[cellRef].s = styles.tableHeader
  }

  // Apply styles for data rows
  for (let R = 0; R < dataRows.length; R++) {
    const rowIndex = tableHeaderRowIndex + 1 + R
    for (let C = 0; C < dataRows[R].length; C++) {
      const cellRef = XLSX.utils.encode_cell({ r: rowIndex, c: C })
      if (!ws[cellRef]) continue
      ws[cellRef].s = C >= 5 ? styles.numericCell : styles.cell
    }
  }

  // Apply styles for footer row
  const footerRowIndex = tableHeaderRowIndex + 1 + dataRows.length
  for (let C = 0; C < footerRow[0].length; C++) {
    const cellRef = XLSX.utils.encode_cell({ r: footerRowIndex, c: C })
    if (!ws[cellRef]) continue
    ws[cellRef].s = C >= 5 ? styles.footerNumeric : styles.footer
  }

  // Merge cells for title
  ws['!merges'] = [
    { s: { r: 0, c: 0 }, e: { r: 0, c: tableHeaders[0].length - 1 } }
  ]

  XLSX.utils.book_append_sheet(wb, ws, 'Expense Details')
  XLSX.writeFile(wb, `expense-${expenseResource.doc?.name}.xlsx`)
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
              v-if="(expenseResource.doc?.workflow_state === 'Draft' || expenseResource.doc?.workflow_state === 'Rejected') && session.user === expenseResource.doc?.owner"
              @click="goEdit"
              class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded">
              Edit
            </button>
            <!-- <button 
              v-if="(expenseResource.doc?.workflow_state === 'Rejected' && expenseResource.doc?.docstatus !==2 )&& session.user === expenseResource.doc?.owner"
              @click="goCancel"
              :disabled="cancelDocumentResource.loading"
              class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded disabled:opacity-50">
              {{ cancelDocumentResource.loading ? 'กำลังยกเลิก...' : 'Cancel Document' }}
            </button> -->
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
                  'bg-yellow-100 border-yellow-200 text-yellow-700': expenseResource.doc.workflow_state === 'Approval Review' || expenseResource.doc.workflow_state === 'Pending Approval',
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
            <div class="flex gap-2">
              <button 
                @click="printExpenseDetails"
                class="no-print inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                Print Details
              </button>
              <button 
                @click="exportToExcel"
                class="no-print inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export Excel
              </button>
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
                    Project Code
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
                  <td class="px-3 py-4 text-sm text-gray-900 whitespace-nowrap">{{ item.project }}</td>
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

        <!-- แทนที่ส่วนแสดงผลเดิมในส่วนของ Attachments tab ด้วยโค้ดนี้ -->
        <div class="bg-white rounded-lg shadow mt-6">
          <div class="border-b border-gray-200">
            <div class="flex justify-between items-center px-6 py-4">
              <h2 class="text-lg font-medium text-gray-900">Attachments</h2>
              <button 
                @click="printAttachments"
                class="no-print inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                Print
              </button>
            </div>
          </div>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200" id="attachments-table">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Service Date
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Project
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Expense Type
                  </th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Receipt Date
                  </th>
                  <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider no-print">
                    Attachment
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(item, index) in attachmentsList" :key="index">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(item.service_date) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ item.customer_name }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ item.project_name }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ item.expense_type_desc }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatDate(item.receipt_date) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                    {{ formatCurrency(item.total_cost) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-center no-print">
                    <a 
                      :href="item.file_url" 
                      target="_blank"
                      class="text-blue-600 hover:text-blue-900"
                    >
                      View
                    </a>
                  </td>
                </tr>
              </tbody>
              <tfoot class="bg-gray-50">
                <tr>
                  <td colspan="5" class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    Total
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-right text-blue-600">
                    {{ formatCurrency(totalAmount) }}
                  </td>
                  <td class="no-print"></td>
                </tr>
              </tfoot>
            </table>

            <!-- แสดงข้อความเมื่อไม่มีเอกสารแนบ -->
            <div v-if="attachmentsList.length === 0" class="text-center py-8">
              <p class="text-gray-500">ไม่พบเอกสารแนบ</p>
            </div>
          </div>
        </div>

         <!-- Approvers Card Grid -->
         <ApproversGrid 
          :approvers="expenseResource.doc.approvers"
        />
      </div>
    </div>
  </UserLayout>
</template>

<style scoped>
@media print {
  .no-print {
    display: none !important;
  }
  
  .print-only {
    display: block !important;
  }
  
  table { 
    border-collapse: collapse;
    width: 100%;
  }
  
  th, td { 
    border: 1px solid #000;
    padding: 8px;
    text-align: left;
  }
  
  th {
    background-color: #f8f9fa !important;
    -webkit-print-color-adjust: exact;
  }
}
</style>
