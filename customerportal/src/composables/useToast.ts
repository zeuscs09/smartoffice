import { ref } from 'vue'

export const useToast = () => {
  const showToast = (message: string, type: 'success' | 'error' | 'warning' | 'info') => {
    // สร้าง toast element
    const toast = document.createElement('div')
    toast.className = `toast toast-top toast-end`
    
    // สร้าง alert element
    const alert = document.createElement('div')
    alert.className = `alert alert-${type}`
    alert.innerHTML = message
    
    // เพิ่ม alert เข้าไปใน toast
    toast.appendChild(alert)
    
    // เพิ่ม toast เข้าไปใน body
    document.body.appendChild(toast)
    
    // ลบ toast หลังจาก 3 วินาที
    setTimeout(() => {
      document.body.removeChild(toast)
    }, 3000)
  }

  return {
    success: (message: string) => showToast(message, 'success'),
    error: (message: string) => showToast(message, 'error'),
    warning: (message: string) => showToast(message, 'warning'),
    info: (message: string) => showToast(message, 'info')
  }
}
