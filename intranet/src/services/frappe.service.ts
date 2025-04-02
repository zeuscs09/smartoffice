/**
 * บริการสำหรับเรียกใช้ Frappe API
 */
export class FrappeService {
  private baseUrl: string

  constructor() {
    this.baseUrl =  ''
  }

  /**
   * ดึงข้อมูลเอกสารด้วย ID
   */
  async getDocument<T>(doctype: string, name: string): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}/api/resource/${doctype}/${name}`, {
        method: 'GET',
        credentials: 'include'
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || `Failed to get ${doctype}`)
      }

      const result = await response.json()
      return result.data
    } catch (error) {
      console.error(`Error fetching ${doctype}:`, error)
      throw error
    }
  }

  /**
   * ดึงรายการเอกสาร
   */
  async getList<T>(doctype: string, params: {
    fields?: string[],
    filters?: any[],
    orderBy?: string,
    limit?: number,
    start?: number
  } = {}): Promise<T[]> {
    try {
      // สร้าง query params
      const queryParams = new URLSearchParams()
      
      if (params.fields) {
        queryParams.append('fields', JSON.stringify(params.fields))
      }
      
      if (params.filters) {
        queryParams.append('filters', JSON.stringify(params.filters))
      }
      
      if (params.orderBy) {
        queryParams.append('order_by', params.orderBy)
      }
      
      if (params.limit !== undefined) {
        queryParams.append('limit_page_length', params.limit.toString())
      }
      
      if (params.start !== undefined) {
        queryParams.append('limit_start', params.start.toString())
      }

      const endpoint = `${this.baseUrl}/api/resource/${doctype}?${queryParams}`
      
      const response = await fetch(endpoint, {
        method: 'GET',
        credentials: 'include'
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || `Failed to get ${doctype} list`)
      }

      const result = await response.json()
      return result.data
    } catch (error) {
      console.error(`Error fetching ${doctype} list:`, error)
      throw error
    }
  }

  /**
   * สร้างเอกสารใหม่
   */
  async createDocument<T>(doctype: string, data: any): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}/api/resource/${doctype}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
        credentials: 'include'
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || `Failed to create ${doctype}`)
      }

      const result = await response.json()
      return result.data
    } catch (error) {
      console.error(`Error creating ${doctype}:`, error)
      throw error
    }
  }

  /**
   * อัปเดตเอกสาร
   */
  async updateDocument<T>(doctype: string, name: string, data: any): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}/api/resource/${doctype}/${name}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
        credentials: 'include'
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || `Failed to update ${doctype}`)
      }

      const result = await response.json()
      return result.data
    } catch (error) {
      console.error(`Error updating ${doctype}:`, error)
      throw error
    }
  }

  /**
   * ลบเอกสาร
   */
  async deleteDocument(doctype: string, name: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/resource/${doctype}/${name}`, {
        method: 'DELETE',
        credentials: 'include'
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || `Failed to delete ${doctype}`)
      }
    } catch (error) {
      console.error(`Error deleting ${doctype}:`, error)
      throw error
    }
  }

  /**
   * Submit เอกสาร
   */
  async submitDocument<T>(doctype: string, name: string): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}/api/resource/${doctype}/${name}/submit`, {
        method: 'POST',
        credentials: 'include'
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || `Failed to submit ${doctype}`)
      }

      const result = await response.json()
      return result.data
    } catch (error) {
      console.error(`Error submitting ${doctype}:`, error)
      throw error
    }
  }

  /**
   * Cancel เอกสาร
   */
  async cancelDocument<T>(doctype: string, name: string): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}/api/resource/${doctype}/${name}/cancel`, {
        method: 'POST',
        credentials: 'include'
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || `Failed to cancel ${doctype}`)
      }

      const result = await response.json()
      return result.data
    } catch (error) {
      console.error(`Error cancelling ${doctype}:`, error)
      throw error
    }
  }

  /**
   * นับจำนวนเอกสาร
   */
  async getCount(doctype: string, filters?: any[], options?: {
    distinct?: boolean,
    limit?: number,
    fields?: string[]
  }): Promise<number> {
    try {
      const params = {
        doctype,
        filters: filters || [],
        fields: options?.fields || [],
        distinct: options?.distinct || false,
        limit: options?.limit || 1000
      }
      
      // เรียกใช้ method แทนที่จะเรียก resource endpoint โดยตรง
      const result = await this.callMethod<{ message: number }>(
        'frappe.desk.reportview.get_count',
        params,
        'GET'
      )
      
      return result;
    } catch (error) {
      console.error(`Error getting count for ${doctype}:`, error)
      throw error
    }
  }

  /**
   * เรียกใช้ Custom API Method ใน Frappe
   * 
   * @param method ชื่อเมธอด เช่น 'frappe.client.get_value' หรือ 'my_app.api.do_something'
   * @param params พารามิเตอร์ที่ส่งไปกับการเรียก API (optional)
   * @param httpMethod HTTP method (GET หรือ POST, default: POST)
   * @returns ข้อมูลที่ได้จากการเรียก API
   */
  async callMethod<T = any>(
    method: string, 
    params?: Record<string, any>,
    httpMethod: 'GET' | 'POST' = 'POST'
  ): Promise<T> {
    try {
      let url = `${this.baseUrl}/api/method/${method}`
      let options: RequestInit = {
        method: httpMethod,
        credentials: 'include'
      }

      // สำหรับ GET request จะเพิ่ม params เป็น query string
      if (httpMethod === 'GET' && params) {
        const queryParams = new URLSearchParams()
        Object.entries(params).forEach(([key, value]) => {
          queryParams.append(key, typeof value === 'object' ? 
            JSON.stringify(value) : String(value))
        })
        url += `?${queryParams.toString()}`
      } 
      // สำหรับ POST request จะส่ง params ใน body
      else if (httpMethod === 'POST' && params) {
        options.headers = {
          'Content-Type': 'application/json'
        }
        options.body = JSON.stringify(params)
      }

      const response = await fetch(url, options)

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || `Failed to call method: ${method}`)
      }

      const result = await response.json()
      return result.message || result  // Frappe custom methods return data in 'message' field
    } catch (error) {
      console.error(`Error calling method ${method}:`, error)
      throw error
    }
  }
}

// Export a singleton instance
export const frappeService = new FrappeService() 