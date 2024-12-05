import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'

export const useWorkFlowStore = defineStore('workflow', {
  state: () => ({
   
    transitions: [],
    documentsResource: createResource({
      url: 'frappe.model.workflow.get_transitions',
      auto: false,
    }),
   
  }),
  actions: {
    getTransitions(doc: any) {
    
      this.documentsResource.fetch({
        doc: this.doc,
      })

      console.log('this.documentsResource', this.documentsResource)
      this.transitions = this.documentsResource.data
      return this.documentsResource
    },
    applyTransition(transition: any) {},
  },
})
