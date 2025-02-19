import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export interface Employee {
  name: string
  custom_salutation_local?: string
  custom_first_name_local?: string
  custom_last_name_local?: string
  custom_nick_name?: string
  salutation: string
  first_name: string
  last_name: string
  department: string
  designation: string
  date_of_joining: string
  custom_address?: string
  custom_tambol?: string
  custom_amphoe?: string
  custom_province?: string
  custom_zip_code?: string
  company_email: string
  gender: string
  date_of_birth: string
}

interface FetchEmployeesParams {
  page?: number
  search?: string
  limit?: number
}

export const useEmployees = () => {
  const employees = ref<Employee[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const employeeFields = [
    'name',
    'employee_name',
    'department',
    'designation',
    'status',
    'image',
    'cell_number',
    'company_email',
    'date_of_joining',
    'custom_salution_local',
    'custom_first_name_local',
    'custom_last_name_local',
    'custom_nick_name',
    'custom_address',
    'custom_tambol',
    'custom_amphoe',
    'custom_province',
    'custom_zip_code',
    'salutation',
    'first_name',
    'last_name',
    'gender',
    'date_of_birth'
  ]

  const employeeResource = createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'Employee',
      fields: employeeFields
    }
  })

  const fetchEmployees = async (params: FetchEmployeesParams = {}) => {
    loading.value = true
    try {
      const limitStart = ((params.page || 1) - 1) * (params.limit || 15)
      
      const filters = [['status', '=', 'Active']]
      if (params.search) {
        filters.push([
          'employee_name',
          'like',
          `%${params.search}%`
        ])
      }

      const result = await employeeResource.submit({
        doctype: 'Employee',
        fields: employeeFields,
        filters,
        limit_start: limitStart,
        limit_page_length: params.limit || 15
      })
      
      if (params.page === 1) {
        employees.value = result
      } else {
        employees.value = [...employees.value, ...result]
      }
      
      return result
    } catch (err) {
      error.value = err as Error
      console.error('Error fetching employees:', err)
      return []
    } finally {
      loading.value = false
    }
  }

  const getEmployeeDetail = createResource({
    url: 'frappe.client.get',
    transform(data) {
      return data || null
    }
  })

  const fetchEmployeeDetail = async (employeeId: string) => {
    try {
      const result = await getEmployeeDetail.submit({
        doctype: 'Employee',
        name: employeeId
      })
      return result
    } catch (err) {
      error.value = err as Error
      console.error('Error fetching employee detail:', err)
      return null
    }
  }

  return {
    employees,
    loading,
    error,
    fetchEmployees,
    getEmployeeDetail
  }
} 