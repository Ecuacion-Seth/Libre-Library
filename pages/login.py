import json
import hashlib
import os
from pathlib import Path
from nicegui import ui, app

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
USERS_DIR = BASE_DIR / 'data' / 'users'
ASSETS_DIR = BASE_DIR / 'data' / 'assets'
USERS_DIR.mkdir(parents=True, exist_ok=True)

# --- AUTH LOGIC (Unchanged) ---
def get_user_file(username: str) -> Path:
    safe_name = "".join([c for c in username if c.isalpha() or c.isdigit()])
    return USERS_DIR / f"{safe_name}.json"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    file_path = get_user_file(username)
    if not file_path.exists():
        return None
    try:
        with open(file_path, 'r') as f:
            user_data = json.load(f)
            if user_data.get('password') == hash_password(password):
                return user_data 
            return None
    except:
        return None

def create_user(username, password, first_name, last_name, role, extra_data):
    file_path = get_user_file(username)
    if file_path.exists():
        return False 
    
    user_data = {
        'username': username,
        'password': hash_password(password),
        'first_name': first_name,
        'last_name': last_name,
        'role': role,
        'details': extra_data,
        'created_at': str(os.path.getctime(USERS_DIR)) if USERS_DIR.exists() else ""
    }
    
    with open(file_path, 'w') as f:
        json.dump(user_data, f, indent=2)
    return True

# --- RESPONSIVE UI PAGE ---
@ui.page('/login')
def login_page():
    ui.add_head_html('''
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { margin: 0 !important; padding: 0 !important; overflow: hidden; }
            .nicegui-content { padding: 0 !important; margin: 0 !important; width: 100%; height: 100vh; }
        </style>
    ''')

    # Main Layout Container
    with ui.element('div').classes('w-full h-screen flex flex-col md:flex-row gap-0 overflow-hidden'):
        
        # --- BRANDING PANEL (Header on Mobile / Sidebar on Desktop) ---
        # Mobile: w-full, h-auto, flex-row (Logo left, Text right), p-4
        # Desktop: md:w-1/2, md:h-full, md:flex-col (Logo top, Text bottom), md:p-12
        with ui.column().classes(
            'w-full h-auto md:w-1/2 md:h-full '
            'bg-gradient-to-br from-indigo-600 to-violet-700 '
            'text-white shrink-0 '
            'flex-row md:flex-col '         # Row on Mobile, Col on Desktop
            'items-center '
            'justify-start md:justify-center ' # Left align Mobile, Center Desktop
            'gap-4 md:gap-6 '
            'p-4 md:p-12 shadow-md md:shadow-none z-10'
        ):
            
            # LOGO IMAGE
            # Mobile: Small (w-10), Desktop: Large (w-64)
            ui.image('/assets/login-page.png').classes('w-10 md:w-64 drop-shadow-md')

            # TEXT CONTAINER
            # Mobile: No extra spacing, Desktop: Pulse animation
            with ui.column().classes('items-start md:items-center gap-0 md:gap-6'):
                
                # Title
                # Mobile: Text-lg (Header size), Desktop: Text-5xl (Hero size)
                ui.label('Libre Library').classes('text-xl md:text-5xl font-black tracking-tight drop-shadow-md')
                
                # Subtitles (HIDDEN ON MOBILE, Visible on Desktop)
                ui.label('Empowering Students & Teachers').classes('hidden md:block text-xl font-light opacity-90 text-center')
                ui.element('div').classes('hidden md:block w-24 h-1 bg-white/30 rounded-full')
                ui.label('Access knowledge, share resources, and study smarter.').classes('hidden md:block text-lg opacity-80 text-center max-w-md leading-relaxed')

        # --- FORM PANEL ---
        # Mobile: flex-1 (Takes remaining height)
        # Desktop: md:w-1/2 md:h-full
        with ui.column().classes('w-full flex-1 md:w-1/2 md:h-full bg-white items-center justify-center p-4 md:p-8 overflow-y-auto'):
            
            with ui.column().classes('w-full max-w-md gap-4'):
                
                # Note: We removed the extra mobile logo here since we now have a header!

                # Headers
                title_label = ui.label('Welcome Back').classes('text-3xl font-bold text-gray-900 tracking-tight')
                subtitle_label = ui.label('Please enter your details to sign in.').classes('text-gray-500 mb-6')

                is_registering = False
                
                # --- INPUT FIELDS ---
                username_input = ui.input('Username') \
                    .props('outlined rounded prepend-inner-icon=account_circle') \
                    .classes('w-full text-lg')
                
                password_input = ui.input('Password', password=True, password_toggle_button=True) \
                    .props('outlined rounded prepend-inner-icon=lock') \
                    .classes('w-full text-lg')

                # Registration Fields
                with ui.column().classes('w-full gap-3 hidden transition-all duration-300') as reg_container:
                    
                    ui.separator().classes('my-2')
                    ui.label('Personal Details').classes('text-xs font-bold text-gray-400 uppercase tracking-wider')

                    with ui.row().classes('w-full gap-3'):
                        first_name_input = ui.input('First Name').props('outlined dense').classes('flex-1')
                        last_name_input = ui.input('Last Name').props('outlined dense').classes('flex-1')

                    ui.label('I am a:').classes('text-xs font-bold text-gray-400 mt-2')
                    role_select = ui.toggle(['Student', 'Teacher', 'Contributor'], value='Student') \
                        .props('spread no-caps toggle-color=indigo-600 color=grey-3 text-color=grey-8') \
                        .classes('w-full border border-gray-200 rounded shadow-sm')

                    # Dynamic Fields
                    student_fields = ui.column().classes('w-full gap-3 bg-gray-50 p-4 rounded-lg border border-gray-200')
                    with student_fields:
                        ui.label('Academic Info').classes('text-xs font-bold text-indigo-500')
                        dept_select = ui.select(['CAS', 'CBM', 'CET', 'CTE', 'CITE'], label='Department') \
                            .props('outlined dense bg-white').classes('w-full')
                        year_select = ui.select(['1st Year', '2nd Year', '3rd Year', '4th Year', '5th Year'], label='Year Level') \
                            .props('outlined dense bg-white').classes('w-full')

                    teacher_fields = ui.column().classes('w-full gap-3 bg-gray-50 p-4 rounded-lg border border-gray-200 hidden')
                    with teacher_fields:
                        ui.label('Faculty Profile').classes('text-xs font-bold text-indigo-500')
                        rank_select = ui.select(
                            ['Teacher I', 'Teacher II', 'Teacher III', 'Master Teacher I', 
                             'Instructor I', 'Instructor II', 'Assistant Professor', 'Professor'], 
                            label='Current Rank'
                        ).props('outlined dense bg-white').classes('w-full')

                # --- LOGIC ---
                def update_role_visibility():
                    role = role_select.value
                    student_fields.set_visibility(role == 'Student')
                    teacher_fields.set_visibility(role == 'Teacher')

                role_select.on_value_change(update_role_visibility)

                def toggle_mode():
                    nonlocal is_registering
                    is_registering = not is_registering
                    
                    title_label.text = 'Create Account' if is_registering else 'Welcome Back'
                    subtitle_label.text = 'Join the community today.' if is_registering else 'Please enter your details to sign in.'
                    action_btn.text = 'Sign Up' if is_registering else 'Sign In'
                    toggle_text.text = 'Already have an account?' if is_registering else "Don't have an account?"
                    toggle_link.text = 'Log In' if is_registering else 'Sign Up'
                    
                    if is_registering: reg_container.classes(remove='hidden')
                    else: reg_container.classes(add='hidden')

                def handle_submit():
                    username = username_input.value.strip()
                    password = password_input.value.strip()
                    
                    if not username or not password:
                        ui.notify('Please fill in username and password', color='warning', icon='warning'); return

                    if is_registering:
                        fname = first_name_input.value.strip()
                        lname = last_name_input.value.strip()
                        role = role_select.value
                        
                        extra_data = {}
                        if role == 'Student': 
                            if not dept_select.value or not year_select.value:
                                ui.notify('Missing student details', color='warning'); return
                            extra_data = {'department': dept_select.value, 'year': year_select.value}
                        elif role == 'Teacher': 
                            if not rank_select.value:
                                ui.notify('Missing rank details', color='warning'); return
                            extra_data = {'rank': rank_select.value}
                        
                        if create_user(username, password, fname, lname, role, extra_data):
                            ui.notify(f'Account created! Welcome, {fname}.', color='positive', icon='check')
                            toggle_mode()
                        else:
                            ui.notify('Username already taken', color='negative', icon='error')
                    else:
                        user = verify_user(username, password)
                        if user:
                            # Save to session
                            app.storage.user['username'] = user['username']
                            app.storage.user['first_name'] = user.get('first_name', '')
                            app.storage.user['last_name'] = user.get('last_name', '')
                            app.storage.user['role'] = user.get('role', 'Student')
                            app.storage.user['details'] = user.get('details', {})
                            app.storage.user['authenticated'] = True
                            
                            ui.notify(f'Welcome back, {user.get("first_name", "")}!', color='positive', icon='waving_hand')
                            ui.navigate.to('/')
                        else:
                            ui.notify('Incorrect username or password', color='negative', icon='lock')

                # --- BUTTONS ---
                action_btn = ui.button('Sign In', on_click=handle_submit) \
                    .classes('w-full py-3 text-lg font-bold shadow-xl shadow-indigo-100 mt-2 hover:scale-[1.02] transition-transform') \
                    .props('unelevated rounded color=indigo-600')

                with ui.row().classes('w-full justify-center gap-2 mt-4'):
                    toggle_text = ui.label("Don't have an account?").classes('text-gray-500')
                    toggle_link = ui.label('Sign Up').classes('text-indigo-600 font-bold cursor-pointer hover:underline') \
                        .on('click', toggle_mode)

                password_input.on('keydown.enter', handle_submit)