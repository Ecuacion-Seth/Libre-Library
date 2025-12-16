import json
import hashlib
from pathlib import Path
from nicegui import ui, app
from components.header import header
from components.sidebar import sidebar

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
USERS_DIR = BASE_DIR / 'data' / 'users'

# --- HELPERS ---
def get_user_file(username):
    safe_name = "".join([c for c in username if c.isalpha() or c.isdigit()])
    return USERS_DIR / f"{safe_name}.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@ui.page('/profile')
def profile_page():
    if not app.storage.user.get('authenticated'): return ui.navigate.to('/login')

    nav = sidebar()
    header(nav)
    
    # 1. Load Current User Data from Disk (to get freshest data)
    username = app.storage.user.get('username')
    user_file = get_user_file(username)
    
    current_data = {}
    if user_file.exists():
        with open(user_file, 'r') as f:
            current_data = json.load(f)
            
    # State for Inputs
    state = {
        'first_name': current_data.get('first_name', ''),
        'last_name': current_data.get('last_name', ''),
        'password': '', # Empty by default
        'bio': current_data.get('details', {}).get('bio', '')
    }

    def save_changes():
        # Update Data Object
        current_data['first_name'] = state['first_name']
        current_data['last_name'] = state['last_name']
        
        # Only update details if they exist, carefully preserving role info
        if 'details' not in current_data: current_data['details'] = {}
        current_data['details']['bio'] = state['bio']
        
        # Only update password if typed
        if state['password']:
            current_data['password'] = hash_password(state['password'])
            
        # Save to Disk
        try:
            with open(user_file, 'w') as f:
                json.dump(current_data, f, indent=2)
            
            # Update Session
            app.storage.user['first_name'] = state['first_name']
            app.storage.user['last_name'] = state['last_name']
            
            ui.notify('Profile updated successfully!', color='green')
        except Exception as e:
            ui.notify(f'Error saving: {e}', color='negative')

    # --- UI ---
    with ui.column().classes('w-full min-h-screen bg-gray-50 p-4 md:p-8 items-center'):
        
        with ui.card().classes('w-full max-w-2xl p-8 shadow-sm'):
            
            # Header Profile
            with ui.row().classes('w-full items-center gap-6 mb-8'):
                with ui.element('div').classes('w-20 h-20 bg-indigo-600 rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-lg'):
                    ui.label(state['first_name'][0].upper() if state['first_name'] else '?')
                
                with ui.column().classes('gap-1'):
                    ui.label(username).classes('text-2xl font-bold text-gray-900')
                    ui.label(current_data.get('role', 'User')).classes('text-sm font-bold text-indigo-500 uppercase tracking-widest')

            # --- SETTINGS FORM ---
            with ui.column().classes('w-full gap-4'):
                ui.label('Personal Information').classes('text-sm font-bold text-gray-400 uppercase mt-4')
                
                with ui.row().classes('w-full gap-4'):
                    ui.input('First Name').bind_value(state, 'first_name').classes('flex-1')
                    ui.input('Last Name').bind_value(state, 'last_name').classes('flex-1')
                
                ui.textarea('Bio / About Me').bind_value(state, 'bio').classes('w-full').props('rows=3')
                
                ui.label('Security').classes('text-sm font-bold text-gray-400 uppercase mt-4')
                ui.input('New Password', password=True, password_toggle_button=True).bind_value(state, 'password') \
                    .classes('w-full').props('placeholder="Leave blank to keep current"')

                ui.separator().classes('my-4')
                
                ui.button('Save Changes', on_click=save_changes) \
                    .classes('w-full py-3 text-lg font-bold').props('color=indigo-600 unelevated')

        # --- SHORTCUT TO BOOKMARKS ---
        with ui.card().classes('w-full max-w-2xl mt-6 p-6 flex-row items-center justify-between cursor-pointer hover:bg-gray-50') \
                .on('click', lambda: ui.navigate.to('/bookmarks')):
            with ui.row().classes('items-center gap-4'):
                ui.icon('bookmark', color='pink-500', size='md')
                with ui.column().classes('gap-0'):
                    ui.label('My Reading List').classes('font-bold text-gray-800')
                    ui.label('Manage your saved books').classes('text-xs text-gray-500')
            ui.icon('chevron_right', color='grey')