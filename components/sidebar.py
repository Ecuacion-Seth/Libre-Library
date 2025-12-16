import json
from pathlib import Path
from nicegui import ui, app 

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
USERS_DIR = BASE_DIR / 'data' / 'users'

def sidebar():
    user = app.storage.user
    is_logged_in = user.get('authenticated', False)
    username = user.get('username', 'Guest')
    
    # --- 1. NAME LOGIC ---
    first_name = user.get('first_name', '')
    last_name = user.get('last_name', '')
    full_name = f"{first_name} {last_name}".strip()
    if not full_name:
        full_name = username

    # --- 2. SUBTITLE / POSITION LOGIC ---
    role = user.get('role', 'Student')
    details = user.get('details', {})
    
    if role == 'Student':
        dept = details.get('department', '')
        position_text = f"{dept} Student" if dept else "Student"
    elif role == 'Teacher':
        position_text = details.get('rank', 'Teacher')
    else:
        position_text = role

    # --- HELPER: GET PRIVATE HISTORY ---
    def get_user_chats():
        if not is_logged_in: return []
        
        safe_name = "".join([c for c in username if c.isalpha() or c.isdigit()])
        chat_folder = USERS_DIR / safe_name / 'chats'
        
        if not chat_folder.exists(): return []

        chats = []
        for file_path in chat_folder.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chats.append({
                        'id': data.get('id'),
                        'title': data.get('title', 'Untitled Chat'),
                        'timestamp': data.get('timestamp', '')
                    })
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

        # --- 1. MAIN SECTION ---
        with ui.column().classes('w-full px-4 gap-1 mb-6'):
            ui.label('MAIN').classes('px-2 text-xs font-bold text-gray-400 tracking-wider mb-2')
            nav_item('Dashboard', 'dashboard', '/')
            nav_item('Library', 'library_books', '/books')
            
        # --- 2. TOOLS SECTION ---
        with ui.column().classes('w-full px-4 gap-1 mb-6'):
            ui.label('TOOLS').classes('px-2 text-xs font-bold text-gray-400 tracking-wider mb-2')
            
            # Chatbot Dropdown
            with ui.expansion('Chatbot', icon='chat').classes('w-full text-gray-600 group'):
                with ui.row().classes('w-full items-center gap-3 px-4 py-2 cursor-pointer hover:text-indigo-600 transition-colors').on('click', lambda: ui.navigate.to('/chat')):
                    ui.icon('add_circle_outline').classes('text-lg')
                    ui.label('New Chat').classes('text-xs font-bold')
                
                if is_logged_in:
                    recent = get_user_chats()
                    if not recent:
                         ui.label('No history yet.').classes('px-4 py-1 text-xs text-gray-400 italic')
                    else:
                        for chat in recent[:5]: 
                            with ui.row().classes('w-full px-4 py-2 cursor-pointer hover:bg-gray-50 truncate').on('click', lambda c=chat['id']: ui.navigate.to(f'/chat?chat_id={c}')):
                                ui.label(chat['title']).classes('text-xs text-gray-500 truncate w-full')
                else:
                    ui.label('Login to save chats').classes('px-4 py-2 text-xs text-indigo-400 italic cursor-pointer').on('click', lambda: ui.navigate.to('/login'))
            
            nav_item('Study Planner', 'event_note', '/planner')

        # --- 3. CONTRIBUTE SECTION (NEW - MISSING FEATURE) ---
        if is_logged_in:
            with ui.column().classes('w-full px-4 gap-1 mb-6'):
                ui.label('CONTRIBUTE').classes('px-2 text-xs font-bold text-gray-400 tracking-wider mb-2')
                # Needs 'upload.py'
                nav_item('Upload Resource', 'cloud_upload', '/upload') 

            # --- 4. PERSONAL SECTION (UPDATED - MISSING PAGES) ---
            with ui.column().classes('w-full px-4 gap-1 mb-6'):
                ui.label('PERSONAL').classes('px-2 text-xs font-bold text-gray-400 tracking-wider mb-2')
                # Needs 'profile.py'
                nav_item('My Profile', 'badge', '/profile')
                # Needs 'bookmarks.py'
                nav_item('Reading List', 'bookmark_border', '/bookmarks')
                # Needs 'notes.py'
                nav_item('My Notes', 'edit_note', '/notes')

        # --- FOOTER ---
        with ui.column().classes('absolute bottom-0 left-0 w-full border-t border-gray-100 bg-gray-50/50 p-4'):
            with ui.row().classes('items-center gap-3 w-full'):
                
                if is_logged_in:
                    role_color = 'indigo' if role == 'Teacher' else 'green'
                    initial = full_name[0].upper() if full_name else '?'
                    
                    with ui.element('div').classes(f'w-10 h-10 rounded-full bg-{role_color}-100 flex items-center justify-center text-{role_color}-700 font-bold'):
                        ui.label(initial) 
                    
                    with ui.column().classes('gap-0 flex-1 overflow-hidden'):
                        ui.label(full_name).classes('text-sm font-bold text-gray-800 truncate')
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