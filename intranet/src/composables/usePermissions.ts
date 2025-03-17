import { ref } from 'vue'
import { createResource } from 'frappe-ui'

export interface MenuPermissions {
  serviceReport: boolean
  expenseEntry: boolean
  expenseRequest: boolean
  advanceRequest: boolean
  manhourReport: boolean
  expenseReport: boolean
  employeeList: boolean
  employeeDetail: boolean
  timesheet: boolean
}

const defaultPermissions: MenuPermissions = {
  serviceReport: false,
  expenseEntry: false,
  expenseRequest: false,
  advanceRequest: false,
  manhourReport: false,
  expenseReport: false,
  employeeList: false,
  employeeDetail: false,
  timesheet: false
}

export function usePermissions() {
  const menuPermissions = ref<MenuPermissions>(
    JSON.parse(localStorage.getItem('menuPermissions') || JSON.stringify(defaultPermissions))
  )

  const permissionResource = createResource({
    url: 'smartoffice.api.auth.get_user_permissions',
    auto: false,
  })

  const fetchPermissions = async () => {
    try {
      await permissionResource.submit()
      if (permissionResource.data) {
        menuPermissions.value = permissionResource.data
        localStorage.setItem('menuPermissions', JSON.stringify(permissionResource.data))
      }
    } catch (error) {
      console.error('Error fetching permissions:', error)
    }
  }

  const clearPermissions = () => {
    menuPermissions.value = { ...defaultPermissions }
    localStorage.removeItem('menuPermissions')
  }

  return {
    menuPermissions,
    fetchPermissions,
    clearPermissions
  }
} 