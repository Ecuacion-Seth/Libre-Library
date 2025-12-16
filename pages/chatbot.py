import json
import uuid
from pathlib import Path
from datetime import datetime
from nicegui import ui, app
from components.header import header
from components.sidebar import sidebar

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
USERS_DIR = BASE_DIR / 'data' / 'users'
BOOKS_DIR = BASE_DIR / 'data' / 'books'

# --- HELPER 1: GET PRIVATE CHAT FOLDER ---
def get_user_chat_folder():
    """Returns the path to the logged-in user's private chat folder."""
    if not app.storage.user.get('authenticated'):
        return None
        
    username = app.storage.user.get('username')
    safe_name = "".join([c for c in username if c.isalpha() or c.isdigit()])
    
    # Folder: data/users/Joseph/chats/
    chat_folder = USERS_DIR / safe_name / 'chats'
    chat_folder.mkdir(parents=True, exist_ok=True)
    return chat_folder

# --- HELPER 2: THE "BRAIN" (Book Search) ---
def search_library(query):
    """Searches the books folder for titles/authors matching the query."""
    results = []
    if not BOOKS_DIR.exists(): return []
    
    query = query.lower()
    for book_dir in BOOKS_DIR.iterdir():
        if not book_dir.is_dir(): continue
        try:
            with open(book_dir / 'metadata.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                title = data.get('title', '').lower()
                author = str(data.get('authors', '')).lower()
                
                if query in title or query in author:
                    results.append(data.get('title', 'Untitled'))
        except: continue
    return results

@ui.page('/chat')
def chat_page(chat_id: str = None):
    
    # Security: Redirect guests
    if not app.storage.user.get('authenticated'):
        return ui.navigate.to('/login')

    # NEW WAY (Connects them together)
    nav = sidebar()  # 1. Create Sidebar first
    header(nav)      # 2. Pass it to Header

    # --- 1. STATE ---
    state = {
        'current_chat_id': chat_id,
        'messages': []
    }
    
    chat_folder = get_user_chat_folder()

    # --- 2. DATA HANDLERS ---
    def load_current_chat():
        if not state['current_chat_id']:
            state['messages'] = []
            return

        file_path = chat_folder / f"{state['current_chat_id']}.json"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    state['messages'] = data.get('messages', [])
            except:
                state['messages'] = []
        else:
            state['messages'] = []

    def save_current_chat():
        if not state['current_chat_id']:
            state['current_chat_id'] = str(uuid.uuid4())
            # Title logic
            first_msg = state['messages'][0]['text'] if state['messages'] else "New Chat"
            title = first_msg[:30] + "..." if len(first_msg) > 30 else first_msg
        else:
            title = "Conversation"
            old_path = chat_folder / f"{state['current_chat_id']}.json"
            if old_path.exists():
                try:
                    with open(old_path, 'r') as f:
                        title = json.load(f).get('title', title)
                except: pass

        data = {
            'id': state['current_chat_id'],
            'title': title,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'messages': state['messages']
        }

        file_path = chat_folder / f"{state['current_chat_id']}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    # --- 3. UI COMPONENTS ---
    @ui.refreshable
    def chat_area():
        if not state['messages']:
            with ui.column().classes('w-full h-full items-center justify-center opacity-60'):
                ui.icon('auto_awesome', size='4em').classes('text-indigo-300 mb-4')
                ui.label('Libre AI Assistant').classes('text-2xl font-bold text-gray-600')
                ui.label('Ask me to find books or help with your studies.').classes('text-gray-400')
        else:
            for msg in state['messages']:
                is_user = msg['is_user']
                row_align = 'justify-end' if is_user else 'justify-start'
                bg_color = 'bg-indigo-50' if is_user else 'bg-white'
                
                with ui.row().classes(f'w-full {row_align} gap-3 mb-4'):
                    if not is_user:
                        ui.avatar(icon='auto_awesome').classes('bg-gradient-to-br from-indigo-500 to-purple-500 text-white shadow-sm')
                    
                    with ui.column().classes(f'max-w-xl {"items-end" if is_user else "items-start"}'):
                        with ui.element('div').classes(f'{bg_color} text-gray-800 rounded-2xl px-6 py-4 shadow-sm border border-gray-100'):
                            ui.markdown(msg['text']).classes('text-base leading-relaxed')

                    if is_user:
                        ui.avatar(icon='person').classes('bg-indigo-600 text-white shadow-sm')

    async def send_message():
        text = text_input.value.strip()
        if not text: return
        text_input.value = ''
        
        # 1. User Message
        state['messages'].append({
            'text': text, 
            'is_user': True, 
            'timestamp': datetime.now().strftime("%H:%M")
        })
        save_current_chat() 
        chat_area.refresh()
        
        # 2. AI Processing
        response = "I'm just a demo bot right now."
        
        # --- SIMPLE BRAIN LOGIC ---
        clean_text = text.lower()
        if "find" in clean_text or "search" in clean_text or "books about" in clean_text:
            # Extract search term (very basic)
            search_term = text.replace("find", "").replace("search", "").replace("books about", "").strip()
            
            if len(search_term) < 2:
                response = "What topic should I search for? (e.g., 'Find Python')"
            else:
                results = search_library(search_term)
                if results:
                    book_list = "\n".join([f"- **{t}**" for t in results[:5]])
                    response = f"I found these books matching '{search_term}':\n\n{book_list}"
                    if len(results) > 5: response += "\n\n(and more...)"
                else:
                    response = f"I couldn't find any books about '{search_term}' in the library."
        else:
            response = "I can help you find resources. Try saying 'Find books about Biology'."

        ui.timer(0.8, lambda: finalize_response(response), once=True)

    def finalize_response(response_text):
        state['messages'].append({
            'text': response_text, 
            'is_user': False, 
            'timestamp': datetime.now().strftime("%H:%M")
        })
        save_current_chat()
        chat_area.refresh()

    # --- 4. START ---
    load_current_chat()

    with ui.column().classes('w-full h-[calc(100vh-64px)] bg-gray-50 relative'):
        with ui.scroll_area().classes('w-full h-full pb-24 px-4 pt-8'):
            with ui.column().classes('w-full max-w-4xl mx-auto'):
                chat_area()

        with ui.row().classes('w-full absolute bottom-6 px-4 justify-center'):
            with ui.row().classes('w-full max-w-3xl bg-white rounded-full shadow-xl border border-gray-200 items-center px-2 py-2'):
                text_input = ui.input(placeholder='Ask me to find a book...') \
                    .props('borderless').classes('flex-1 px-4 text-lg') \
                    .on('keydown.enter', send_message)
                ui.button(icon='send', on_click=send_message).props('unelevated round color=indigo-600')

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(storage_secret='super_secret_key_123')