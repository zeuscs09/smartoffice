frappe.ready(function() {
    const todoList = new TodoList(frappe.boot.todos);

    // อัพเดท todos ทุก 5 นาที
    setInterval(() => {
        frappe.call({
            method: 'smartoffice.www.employee.index.get_employee_todos',
            callback: function(r) {
                todoList.updateTodos(r.message);
            }
        });
    }, 5 * 60 * 1000);
});

class TodoList {
    constructor(initialTodos) {
        this.todos = initialTodos;
        this.render();
    }

    updateTodos(newTodos) {
        this.todos = newTodos;
        this.render();
    }

    render() {
        const todoListElement = document.getElementById('todo-list');
        todoListElement.innerHTML = this.todos.map(todo => `
            <div class="flex items-center justify-between py-2 border-b">
                <div>
                    <p class="font-medium">${todo.description}</p>
                    <p class="text-sm text-gray-500">${todo.date}</p>
                </div>
                <span class="px-2 py-1 text-xs font-semibold rounded-full 
                             ${this.getPriorityClass(todo.priority)}">
                    ${todo.priority}
                </span>
            </div>
        `).join('');
    }

    getPriorityClass(priority) {
        switch(priority) {
            case 'High': return 'bg-red-100 text-red-800';
            case 'Medium': return 'bg-yellow-100 text-yellow-800';
            default: return 'bg-green-100 text-green-800';
        }
    }
}
