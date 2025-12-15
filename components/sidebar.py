import json
from pathlib import Path
from nicegui import ui, app 

BASE_DIR = Path(__file__).parent.parent
HISTORY_DIR = BASE_DIR / 'data' / 'chat_history'

def sidebar():
    user = app.storage.user
    is_logged_in = user.get('authenticated', False)
    
    # --- 1. NAME LOGIC ---
    # Try to combine first and last name. Fallback to username.
    first_name = user.get('first_name', '')
    last_name = user.get('last_name', '')
    full_name = f"{first_name} {last_name}".strip()
    if not full_name:
        full_name = user.get('username', 'Guest')

    # --- 2. SUBTITLE / POSITION LOGIC ---
    role = user.get('role', 'Student')
    details = user.get('details', {})
    
    if role == 'Student':
        dept = details.get('department', '')
        position_text = f"{dept} Student" if dept else "Student"
    elif role == 'Teacher':
        # Display Rank (e.g. "Instructor II")
        position_text = details.get('rank', 'Teacher')
    else:
        position_text = role

    # --- HELPER: HISTORY ---
    def get_recent_chats():
        if not is_logged_in: return []
        chats = []
        if not HISTORY_DIR.exists(): return [] 
        for file_path in HISTORY_DIR.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chats.append({'id': data.get('id'), 'title': data.get('title'), 'timestamp': data.get('timestamp')})
            except: continue
        chats.sort(key=lambda x: x['timestamp'], reverse=True)
        return chats

    with ui.left_drawer(value=True).classes('bg-white border-r border-gray-200 w-64') as drawer:
        # Header
        with ui.row().classes('w-full items-center gap-3 px-6 py-8'):
            with ui.element('div').classes('bg-indigo-600 p-2 rounded-lg shadow-sm'):
                ui.icon('auto_stories', color='white', size='20px')
            ui.label('Libre Library').classes('text-lg font-bold text-gray-800 tracking-tight')

        # Nav Helper
        def nav_item(label: str, icon: str, target: str):
            with ui.row().classes('w-full items-center gap-3 px-4 py-2 rounded-md transition-all duration-200 cursor-pointer group text-gray-600 hover:bg-gray-50 hover:text-gray-900') \
                    .on('click', lambda: ui.navigate.to(target)):
                ui.icon(icon).classes('text-xl opacity-80 group-hover:opacity-100')
                ui.label(label).classes('text-sm font-medium flex-1')

        # Menu Items
        with ui.column().classes('w-full px-4 gap-1 mb-6'):
            ui.label('MAIN').classes('px-2 text-xs font-bold text-gray-400 tracking-wider mb-2')
            nav_item('Dashboard', 'dashboard', '/')
            nav_item('Library', 'library_books', '/books')
            
        with ui.column().classes('w-full px-4 gap-1 mb-6'):
            ui.label('TOOLS').classes('px-2 text-xs font-bold text-gray-400 tracking-wider mb-2')
            with ui.expansion('Chatbot', icon='chat').classes('w-full text-gray-600 group'):
                with ui.row().classes('w-full items-center gap-3 px-4 py-2 cursor-pointer hover:text-indigo-600 transition-colors').on('click', lambda: ui.navigate.to('/chat')):
                    ui.icon('add_circle_outline').classes('text-lg')
                    ui.label('New Chat').classes('text-xs font-bold')
                if is_logged_in:
                    for chat in get_recent_chats()[:5]:
                        with ui.row().classes('w-full px-4 py-2 cursor-pointer hover:bg-gray-50 truncate').on('click', lambda c=chat['id']: ui.navigate.to(f'/chat?chat_id={c}')):
                            ui.label(chat['title']).classes('text-xs text-gray-500 truncate w-full')
                else:
                    ui.label('Login to save chats').classes('px-4 py-2 text-xs text-indigo-400 italic cursor-pointer').on('click', lambda: ui.navigate.to('/login'))
            nav_item('Study Planner', 'auto_stories', '/planner')

        if is_logged_in:
            with ui.column().classes('w-full px-4 gap-1 mb-6'):
                ui.label('PERSONAL').classes('px-2 text-xs font-bold text-gray-400 tracking-wider mb-2')
                nav_item('Reading List', 'bookmark_border', '#')
                nav_item('Notes', 'edit_note', '#')

        # --- FOOTER (UPDATED) ---
        with ui.column().classes('absolute bottom-0 left-0 w-full border-t border-gray-100 bg-gray-50/50 p-4'):
            with ui.row().classes('items-center gap-3 w-full'):
                
                if is_logged_in:
                    # Color based on Role
                    role_color = 'indigo' if role == 'Teacher' else 'green'
                    initial = full_name[0].upper() if full_name else '?'
                    
                    with ui.element('div').classes(f'w-10 h-10 rounded-full bg-{role_color}-100 flex items-center justify-center text-{role_color}-700 font-bold'):
                        ui.label(initial) 
                    
                    with ui.column().classes('gap-0 flex-1 overflow-hidden'):
                        # SHOW FULL NAME
                        ui.label(full_name).classes('text-sm font-bold text-gray-800 truncate')
                        # SHOW POSITION (e.g. CBM Student)
                        ui.label(position_text).classes(f'text-xs text-{role_color}-600 font-bold uppercase tracking-wider truncate')
                    
                    def logout():
                        app.storage.user.clear()
                        ui.navigate.to('/login')
                    ui.button(icon='logout', on_click=logout).props('flat dense round size=sm color=grey')
                
                else:
                    with ui.element('div').classes('w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500'):
                        ui.icon('person_outline')
                    with ui.column().classes('gap-0 flex-1 overflow-hidden'):
                        ui.label('Guest').classes('text-sm font-bold text-gray-800 truncate')
                        ui.link('Sign In', '/login').classes('text-xs text-indigo-600 font-bold')

    return drawer