from nicegui import ui
from components.header import header
from components.sidebar import sidebar
from datetime import datetime, timedelta
import json
from pathlib import Path

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent

# Store inside a dedicated 'study_task' folder in 'data'
TASKS_DIR = BASE_DIR / 'data' / 'study_task'
TASKS_FILE = TASKS_DIR / 'tasks.json'

# Ensure the directory exists
TASKS_DIR.mkdir(parents=True, exist_ok=True)

@ui.page('/planner')
def planner_page():
    header()
    sidebar()
    
    # --- 1. STATE ---
    tasks = []
    
    # --- 2. DEFINE UI CONTAINERS EARLY ---
    with ui.column().classes('w-full h-screen p-4 bg-gray-50'):
        ui.label('Study Planner').classes('text-2xl font-bold mb-4 text-gray-800')
        
        with ui.row().classes('w-full h-[calc(100vh-120px)] gap-4'):
            
            # LEFT: Chat Interface
            with ui.column().classes('flex-1 h-full bg-white rounded-xl shadow-sm border border-gray-200'):
                with ui.row().classes('w-full p-4 border-b border-gray-200 items-center'):
                    ui.icon('chat').classes('text-blue-500')
                    ui.label('Study Assistant').classes('text-lg font-semibold text-gray-700')
                
                chat_scroll = ui.scroll_area().classes('flex-1 p-4')
                with chat_scroll:
                    chat_container = ui.column().classes('w-full space-y-3')

                with ui.row().classes('w-full p-4 border-t border-gray-200 items-center gap-2'):
                    message_input = ui.input(placeholder='Type a message...').classes('flex-1')
                    send_btn = ui.button(icon='send').props('flat color=primary').classes('self-end')

            # RIGHT: Tasks Interface
            with ui.column().classes('w-1/2 h-full bg-white rounded-xl shadow-sm border border-gray-200'):
                with ui.row().classes('w-full p-4 border-b border-gray-200 items-center justify-between'):
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('task_alt').classes('text-green-500')
                        ui.label('My Tasks').classes('text-lg font-semibold text-gray-700')
                    add_task_btn = ui.button('Add Task').props('flat dense color=primary')
                
                tasks_column = ui.column().classes('flex-1 p-4 space-y-2 overflow-y-auto')

    # --- 3. HELPER FUNCTIONS ---

    def save_tasks():
        try:
            with open(TASKS_FILE, 'w') as f:
                json.dump(tasks, f)
        except Exception as e:
            ui.notify(f"Error saving tasks: {str(e)}", color='negative')

    def update_tasks_display():
        tasks_column.clear()
        with tasks_column:
            if not tasks:
                ui.label("No tasks yet. Add one using the chat!").classes('text-gray-500 text-center p-4')
                return
                
            for task in tasks:
                with ui.card().classes('w-full mb-2'):
                    with ui.row().classes('w-full items-center'):
                        ui.checkbox(value=task['completed'], 
                                  on_change=lambda e, t=task: toggle_task_complete(t, e.value)).props('dense')
                        
                        with ui.column().classes('flex-1'):
                            ui.label(task['task']).classes('text-sm ' + ('line-through text-gray-400' if task['completed'] else ''))
                            ui.label(f"Due: {task['due_date']}").classes('text-xs text-gray-500')
                        
                        ui.button(icon='delete', on_click=lambda t=task: delete_task(t))\
                            .props('flat dense color=red').classes('opacity-50 hover:opacity-100')

    def toggle_task_complete(task, is_completed):
        task['completed'] = is_completed
        save_tasks()
        update_tasks_display()

    def delete_task(task):
        if task in tasks:
            tasks.remove(task)
            save_tasks()
            update_tasks_display()

    def add_message(text, is_user=False):
        with chat_container:
            with ui.row().classes('w-full'):
                align_class = 'ml-auto bg-blue-100' if is_user else 'bg-gray-100'
                text_align = 'text-right' if is_user else ''
                
                with ui.column().classes(f'max-w-[80%] rounded-lg p-3 {align_class}'):
                    ui.label(text).classes(f'text-sm {text_align}')
                    ui.label(datetime.now().strftime('%I:%M %p')).classes(f'text-xs text-gray-500 {text_align}')
        chat_scroll.scroll_to(percent=100)

    def handle_message():
        text = message_input.value.strip()
        if not text: return
        add_message(text, is_user=True)
        message_input.value = ""
        process_command(text)

    def process_command(text):
        text = text.lower()
        if text in ['hi', 'hello', 'hey']:
            add_message("Hello! How can I help you with your studies today?")
        elif 'add task' in text:
            task_name = text.replace('add task', '').strip()
            if task_name:
                add_new_task(task_name)
                add_message(f"I've added '{task_name}' to your list.")
            else:
                add_message("Please specify a task name. E.g., 'add task Read Chapter 1'")
        elif 'show tasks' in text:
            if tasks:
                count = len([t for t in tasks if not t['completed']])
                add_message(f"You have {count} pending tasks. Check the list on the right!")
            else:
                add_message("You have no tasks pending.")
        else:
            add_message("I didn't quite catch that. Try 'add task [name]' or 'show tasks'.")

    def add_new_task(text, due=None):
        if due is None:
            due = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        new_task = {
            'id': len(tasks) + 1,
            'task': text,
            'due_date': due,
            'completed': False
        }
        tasks.append(new_task)
        save_tasks()
        update_tasks_display()

    # --- 4. INITIALIZATION ---
    
    # Load tasks from file
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE, 'r') as f:
                tasks = json.load(f)
        except:
            tasks = []
    
    # Connect handlers
    message_input.on('keydown.enter', handle_message)
    send_btn.on('click', handle_message)
    
    # Dialog Setup
    with ui.dialog() as add_dialog, ui.card():
        with ui.column().classes('w-96 p-4 gap-4'):
            ui.label('Add New Task').classes('text-lg font-bold')
            d_input = ui.input('Task Name').classes('w-full')
            d_date = ui.date(value=datetime.now().strftime('%Y-%m-%d')).classes('w-full')
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=add_dialog.close).props('flat')
                ui.button('Add', on_click=lambda: [
                    add_new_task(d_input.value, d_date.value), 
                    add_dialog.close()
                ])
    
    add_task_btn.on('click', add_dialog.open)

    # Initial Render
    update_tasks_display()
    add_message("Welcome! I'm your AI Study Planner. Try saying 'add task Finish Essay'")