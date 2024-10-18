import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    data: [],
    unreadCount: 0,
  }),
  actions: {
    fetchAll() {
      const notificationResource = createResource({
        url: 'smartoffice.api.notification.get_notifications',
        onSuccess: (data) => {
          this.data = data.notifications
          this.unreadCount = data.unread_count
        },
      })
      return notificationResource
    },
    get(id) {
      return this.data.find(notification => notification.id === id)
    },
    markAsRead(id) {
      // ตรงนี้คุณสามารถเพิ่มลอจิกสำหรับการทำเครื่องหมายการแจ้งเตือนว่าอ่านแล้ว
    },
  },
})
