import json
from pathlib import Path
from nicegui import ui

# --- CONFIGURATION ---
# We define the path here so the sidebar can find the files
BASE_DIR = Path(__file__).parent.parent
HISTORY_DIR = BASE_DIR / 'data' / 'chat_history'

def sidebar():
    """
    A modern sidebar that includes a dynamic Chat History section.
    """
    
    # --- HELPER: GET HISTORY ---
    def get_recent_chats():
        chats = []
        if not HISTORY_DIR.exists():
            return []
            
        for file_path in HISTORY_DIR.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chats.append({
                        'id': data.get('id'),
                        'title': data.get('title', 'Untitled Chat'),
                        'timestamp': data.get('timestamp', '')
                    })
            except:
                continue
        # Sort by newest first
        chats.sort(key=lambda x: x['timestamp'], reverse=True)
        return chats

    # drawer settings
    with ui.left_drawer(value=True).classes('bg-white border-r border-gray-200 w-64') as drawer:
        
        # --- 1. BRAND HEADER ---
        with ui.row().classes('w-full items-center gap-3 px-6 py-8'):
            with ui.element('div').classes('bg-indigo-600 p-2 rounded-lg shadow-sm'):
                ui.icon('auto_stories', color='white', size='20px')
            ui.label('Libre Library').classes('text-lg font-bold text-gray-800 tracking-tight')

        # --- 2. NAVIGATION HELPER ---
        def nav_item(label: str, icon: str, target: str):
            with ui.row().classes('w-full items-center gap-3 px-4 py-2 rounded-md transition-all duration-200 cursor-pointer group text-gray-600 hover:bg-gray-50 hover:text-gray-900') \
                    .on('click', lambda: ui.navigate.to(target)):
                ui.icon(icon).classes('text-xl opacity-80 group-hover:opacity-100')
                ui.label(label).classes('text-sm font-medium flex-1')

        # --- 3. MENU GROUPS ---
        
        # Group: Main
        with ui.column().classes('w-full px-4 gap-1 mb-6'):
            ui.label('MAIN').classes('px-2 text-xs font-bold text-gray-400 tracking-wider mb-2')
            nav_item('Dashboard', 'dashboard', '/')
            nav_item('Library', 'library_books', '/books')
            
        # Group: Tools (Modified)
        with ui.column().classes('w-full px-4 gap-1 mb-6'):
            ui.label('TOOLS').classes('px-2 text-xs font-bold text-gray-400 tracking-wider mb-2')
            
            # --- CHATBOT EXPANSION ---
            with ui.expansion('Chatbot', icon='chat').classes('w-full text-gray-600 group'):
                
                # A. "New Chat" Button
                with ui.row().classes('w-full items-center gap-3 px-4 py-2 cursor-pointer hover:text-indigo-600 transition-colors') \
                        .on('click', lambda: ui.navigate.to('/chat')):
                    ui.icon('add_circle_outline').classes('text-lg')
                    ui.label('New Chat').classes('text-xs font-bold')

                # B. History List
                recent_chats = get_recent_chats()
                if not recent_chats:
                    ui.label('No history yet').classes('px-4 py-2 text-xs text-gray-400 italic')
                
                for chat in recent_chats[:5]: # Show top 5
                    # Link to /chat?chat_id=...
                    with ui.row().classes('w-full px-4 py-2 cursor-pointer hover:bg-gray-50 truncate') \
                            .on('click', lambda c=chat['id']: ui.navigate.to(f'/chat?chat_id={c}')):
                        ui.label(chat['title']).classes('text-xs text-gray-500 truncate w-full')

            # Planner
            nav_item('Study Planner', 'auto_stories', '/planner')

        # Group: Personal
        with ui.column().classes('w-full px-4 gap-1 mb-6'):
            ui.label('PERSONAL').classes('px-2 text-xs font-bold text-gray-400 tracking-wider mb-2')
            nav_item('Reading List', 'bookmark_border', '#')
            nav_item('Notes', 'edit_note', '#')

        # --- 4. FOOTER ---
        with ui.column().classes('absolute bottom-0 left-0 w-full border-t border-gray-100 bg-gray-50/50 p-4'):
            with ui.row().classes('items-center gap-3 w-full'):
                with ui.element('div').classes('w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold'):
                    ui.label('S')
                with ui.column().classes('gap-0 flex-1 overflow-hidden'):
                    ui.label('Student User').classes('text-sm font-bold text-gray-800 truncate')
                    ui.label('student@univ.edu').classes('text-xs text-gray-500 truncate')
                ui.button(icon='logout').props('flat dense round size=sm color=grey')

    return drawer