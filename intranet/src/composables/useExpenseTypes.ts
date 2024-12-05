import { ref } from 'vue'

export interface ExpenseType {
  name: string
  description: string
  for_expense: number
  account_code?: string
}

export const useExpenseTypes = () => {
  const expenseTypes = ref<ExpenseType[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const fetchExpenseTypes = async () => {
    loading.value = true
    try {
      const response = await fetch('/api/method/frappe.client.get_list', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          doctype: 'SMO Expense Type',
          fields: ['name', 'description', 'for_expense', 'account_code'],
          filters: [['for_expense', '=', 1]],
          order_by: 'description asc'
        })
      })

      const data = await response.json()
      expenseTypes.value = data.message || []
    } catch (err) {
      error.value = err as Error
      console.error('Error fetching expense types:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    expenseTypes,
    loading,
    error,
    fetchExpenseTypes
  }
}
