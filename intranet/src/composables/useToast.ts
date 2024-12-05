import { ref } from 'vue'

export function useToast() {
  const showToast = (msg: string, type: string) => {
    // สร้าง toast element
    const toast = document.createElement('div')
    
    // กำหนด style และ class ตาม type
    let bgColor = type === 'error' ? 'bg-red-500' : 
                 type === 'success' ? 'bg-green-500' : 
                 'bg-blue-500'
    
    toast.className = `fixed bottom-4 right-4 z-[9999] px-4 py-2 rounded-lg shadow-lg ${bgColor} text-white`
    toast.style.minWidth = '200px'
    toast.style.transition = 'all 0.3s ease-in-out'
    toast.textContent = msg
    
    // ปรับ animation ให้เลื่อนขึ้นจากล่าง
    toast.style.opacity = '0'
    toast.style.transform = 'translateY(20px)'
    
    document.body.appendChild(toast)
    
    setTimeout(() => {
      toast.style.opacity = '1'
      toast.style.transform = 'translateY(0)'
    }, 10)
    
    setTimeout(() => {
      toast.style.opacity = '0'
      toast.style.transform = 'translateY(20px)'
      
      setTimeout(() => {
        document.body.removeChild(toast)
      }, 300)
    }, 3000)
  }

  return {
    error: (msg: string) => showToast(msg, 'error'),
    success: (msg: string) => showToast(msg, 'success'),
    info: (msg: string) => showToast(msg, 'info')
  }
} 