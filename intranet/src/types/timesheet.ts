/**
 * Type definitions for SMO Timesheet
 */

export interface SMOTimesheet {
  name: string
  employee: string
  employee_name?: string
  department?: string
  company: string
  posting_date: string
  total_hours: number
  status: 'Draft' | 'Submitted' | 'Cancelled'
  note?: string
  timesheet_details: SMOTimesheetDetail[]
  docstatus: number
  // Other common fields
  owner?: string
  creation?: string
  modified?: string
  modified_by?: string
  idx?: number
}

export interface SMOTimesheetDetail {
  name: string
  idx: number
  activity_type: string
  from_time: string
  to_time: string
  hours: number
  description?: string
  project?: string
  task?: string
  billing_hours?: number
  billing_rate?: number
  billing_amount?: number
}

export interface TimesheetFilters {
  employee?: string
  from_date?: string
  to_date?: string
  status?: 'Draft' | 'Submitted' | 'Cancelled'
} 