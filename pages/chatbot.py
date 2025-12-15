import json
import uuid
from pathlib import Path
from datetime import datetime
from nicegui import ui
from components.header import header
from components.sidebar import sidebar

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
HISTORY_DIR = BASE_DIR / 'data' / 'chat_history'
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

# Note: We define the page to accept a parameter 'chat_id'
# If the URL is /chat?chat_id=123, this variable will be populated.
@ui.page('/chat')
def chat_page(chat_id: str = None):
    
    # Load Global Layout
    header()
    sidebar() # This now contains the history list!

    # --- 1. STATE MANAGEMENT ---
    state = {
        'current_chat_id': chat_id, # Set from URL parameter
        'messages': []
    }

    # --- 2. DATA HANDLERS ---
    
    def load_current_chat():
        """Loads the chat specified in state['current_chat_id']."""
        if not state['current_chat_id']:
            state['messages'] = []
            return

        file_path = HISTORY_DIR / f"{state['current_chat_id']}.json"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    state['messages'] = data.get('messages', [])
            except:
                state['messages'] = []
        else:
            # If ID is invalid, just start fresh
            state['messages'] = []

    def save_current_chat():
        """Saves current messages to JSON."""
        # Generate ID if this is a new chat
        if not state['current_chat_id']:
            state['current_chat_id'] = str(uuid.uuid4())
            # Title logic
            first_msg = state['messages'][0]['text'] if state['messages'] else "New Chat"
            title = first_msg[:30] + "..." if len(first_msg) > 30 else first_msg
            
            # OPTIONAL: If we just created a new chat, we might want to update the URL
            # so a refresh doesn't lose it. But for now, we just save it.
        else:
            # Try to keep existing title
            title = "Conversation"
            old_path = HISTORY_DIR / f"{state['current_chat_id']}.json"
            if old_path.exists():
                with open(old_path, 'r') as f:
                    title = json.load(f).get('title', title)

        data = {
            'id': state['current_chat_id'],
            'title': title,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'messages': state['messages']
        }

        file_path = HISTORY_DIR / f"{state['current_chat_id']}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    # --- 3. UI COMPONENTS ---

    @ui.refreshable
    def chat_area():
        if not state['messages']:
            # WELCOME SCREEN
            with ui.column().classes('w-full h-full items-center justify-center opacity-60'):
                ui.icon('auto_awesome', size='4em').classes('text-indigo-300 mb-4')
                ui.label('Start a new conversation').classes('text-2xl font-bold text-gray-600')
                ui.label('Select "New Chat" or pick a history item from the sidebar.').classes('text-gray-400')
        else:
            # MESSAGES
            for msg in state['messages']:
                is_user = msg['is_user']
                row_align = 'justify-end' if is_user else 'justify-start'
                bg_color = 'bg-indigo-50' if is_user else 'bg-white'
                round_class = 'rounded-2xl rounded-tr-sm' if is_user else 'rounded-2xl rounded-tl-sm'
                
                with ui.row().classes(f'w-full {row_align} gap-3 mb-4'):
                    if not is_user:
                        ui.avatar(icon='auto_awesome').classes('bg-gradient-to-br from-indigo-500 to-purple-500 text-white shadow-sm')
                    
                    with ui.column().classes(f'max-w-xl {"items-end" if is_user else "items-start"}'):
                        with ui.element('div').classes(f'{bg_color} text-gray-800 {round_class} px-6 py-4 shadow-sm border border-gray-100'):
                            ui.markdown(msg['text']).classes('text-base leading-relaxed')

                    if is_user:
                        ui.avatar(icon='person').classes('bg-indigo-600 text-white shadow-sm')

    async def send_message():
        text = text_input.value
        if not text: return
        
        text_input.value = ''
        
        # 1. Update State (User)
        state['messages'].append({
            'text': text, 
            'is_user': True, 
            'timestamp': datetime.now().strftime("%H:%M")
        })
        save_current_chat() 
        chat_area.refresh()
        
        # 2. Simulate AI Response
        response = "I am the Library AI. This conversation is being saved!"
        ui.timer(1.0, lambda: finalize_response(response), once=True)

    def finalize_response(response_text):
        state['messages'].append({
            'text': response_text, 
            'is_user': False, 
            'timestamp': datetime.now().strftime("%H:%M")
        })
        save_current_chat()
        chat_area.refresh()

    # --- 4. INITIALIZATION ---
    # Load the data before rendering
    load_current_chat()

    # --- 5. LAYOUT ---
    
    # Only the chat area (Sidebar handles the left panel now)
    with ui.column().classes('w-full h-[calc(100vh-64px)] bg-gray-50 relative'):
        
        # Scrollable Messages
        with ui.scroll_area().classes('w-full h-full pb-24 px-4 pt-8'):
            with ui.column().classes('w-full max-w-4xl mx-auto'):
                chat_area()

        # Input Area
        with ui.row().classes('w-full absolute bottom-6 px-4 justify-center'):
            with ui.row().classes('w-full max-w-3xl bg-white rounded-full shadow-xl border border-gray-200 items-center px-2 py-2'):
                ui.button(icon='add_circle').props('flat round color=grey-6').classes('ml-2')
                text_input = ui.input(placeholder='Type your message...') \
                    .props('borderless').classes('flex-1 text-lg px-2') \
                    .on('keydown.enter', send_message)
                ui.button(icon='send', on_click=send_message) \
                    .props('unelevated round color=indigo-600').classes('mr-1')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret='super_secret_key_123')