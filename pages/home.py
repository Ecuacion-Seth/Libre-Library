import json
import random
from pathlib import Path
from nicegui import ui, app
from components.header import header
from components.sidebar import sidebar

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
BOOKS_DIR = BASE_DIR / 'data' / 'books'
USERS_DIR = BASE_DIR / 'data' / 'users'

# --- DATA HELPERS ---
def load_books():
    books = []
    if not BOOKS_DIR.exists(): return books
    for book_dir in BOOKS_DIR.iterdir():
        if not book_dir.is_dir(): continue
        try:
            with open(book_dir / 'metadata.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'id' not in data: data['id'] = book_dir.name
                books.append(data)
        except: continue
    return books

def get_last_read_book(all_books):
    """Finds the last book the logged-in user interacted with."""
    if not app.storage.user.get('authenticated'): return None
    
    username = app.storage.user.get('username')
    safe_name = "".join([c for c in username if c.isalpha() or c.isdigit()])
    history_file = USERS_DIR / safe_name / 'reading_history.json'
    
    if not history_file.exists(): return None
    
    try:
        with open(history_file, 'r') as f:
            history = json.load(f)
            if not history: return None
            last_book_id = list(history.keys())[-1]
            last_page = history[last_book_id]
            
            for b in all_books:
                if str(b['id']) == last_book_id:
                    b['last_page'] = last_page
                    return b
    except: return None
    return None

@ui.page('/')
def home_page():
    all_books = load_books()
    user = app.storage.user
    is_logged_in = user.get('authenticated', False)
    first_name = user.get('first_name', 'Guest')
    
    last_read = get_last_read_book(all_books)

    nav = sidebar()
    header(nav)

    with ui.column().classes('w-full min-h-screen bg-gray-50/50 p-4 md:p-8'):
        
        # --- WELCOME ---
        with ui.column().classes('mb-8'):
            greeting = f"Welcome back, {first_name}." if is_logged_in else "Welcome to Libre Library."
            subtitle = "Ready to continue your studies?" if is_logged_in else "Log in to access your personal dashboard."
            
            ui.label(greeting).classes('text-3xl md:text-4xl font-black text-gray-900 tracking-tight')
            ui.label(subtitle).classes('text-lg text-gray-500')

        # --- DASHBOARD GRID ---
        with ui.grid().classes('w-full gap-6 grid-cols-1 lg:grid-cols-3 mb-8'):
            
            # 1. CONTINUE READING
            with ui.card().classes('lg:col-span-2 p-0 overflow-hidden bg-white shadow-sm border border-gray-100 flex flex-col h-full'):
                ui.label('JUMP BACK IN').classes('px-6 pt-6 text-xs font-bold text-gray-400 tracking-widest')
                
                if last_read:
                    cover = last_read.get('formats', {}).get('image/jpeg')
                    title = last_read.get('title', 'Untitled')
                    page = last_read.get('last_page', 0) + 1
                    
                    with ui.row().classes('w-full p-6 gap-6 items-center flex-nowrap'):
                        if cover: 
                            ui.image(cover).classes('w-24 md:w-32 rounded shadow-lg shrink-0')
                        else:
                            with ui.element('div').classes('w-24 md:w-32 aspect-[2/3] bg-gray-100 rounded flex items-center justify-center shrink-0'):
                                ui.icon('auto_stories', color='grey')
                        
                        with ui.column().classes('flex-1 gap-2'):
                            ui.label(title).classes('text-xl md:text-2xl font-bold leading-tight line-clamp-2')
                            ui.label(f'You left off on Page {page}').classes('text-indigo-500 font-medium')
                            ui.button('Resume Reading', icon='arrow_forward', on_click=lambda: ui.navigate.to(f'/read/{last_read["id"]}')) \
                                .props('unelevated rounded color=indigo-600').classes('mt-2')
                
                elif all_books:
                    feat = random.choice(all_books)
                    with ui.row().classes('w-full p-6 gap-6 items-center'):
                        ui.icon('menu_book', size='4em').classes('text-gray-200')
                        with ui.column().classes('flex-1 gap-1'):
                            ui.label("You haven't started a book yet.").classes('text-lg font-bold text-gray-700')
                            ui.label(f"Why not try '{feat['title']}'?").classes('text-gray-500')
                            ui.button('Start Reading', on_click=lambda: ui.navigate.to(f'/read/{feat["id"]}')).props('outline color=indigo')
                else:
                    ui.label('Library is empty.').classes('p-6 text-gray-400')

            # 2. QUICK ACTIONS
            with ui.grid().classes('grid-cols-2 gap-4 h-full'):
                def action_card(title, icon, color, link):
                    with ui.card().classes(f'p-4 items-center justify-center gap-2 cursor-pointer hover:shadow-md transition-all bg-{color}-50 border border-{color}-100') \
                            .on('click', lambda: ui.navigate.to(link)):
                        with ui.element('div').classes(f'p-3 rounded-full bg-{color}-100 text-{color}-600'):
                            ui.icon(icon, size='md')
                        ui.label(title).classes(f'text-sm font-bold text-{color}-800')

                action_card('Library', 'library_books', 'indigo', '/books')
                action_card('AI Chat', 'chat', 'purple', '/chat')
                action_card('Planner', 'event_note', 'orange', '/planner')
                action_card('Upload', 'cloud_upload', 'emerald', '/upload')

        # --- DISCOVER SECTION ---
        ui.label('FRESH PICKS').classes('text-xs font-bold text-gray-400 tracking-widest mb-4')
        
        if all_books:
            with ui.scroll_area().classes('w-full whitespace-nowrap pb-4'):
                with ui.row().classes('flex-nowrap gap-4'):
                    display_books = random.sample(all_books, min(len(all_books), 8))
                    
                    for book in display_books:
                        cover = book.get('formats', {}).get('image/jpeg')
                        
                        # --- SIZE UPDATE HERE ---
                        # Changed w-40 h-64 -> w-32 h-48 (Smaller cards)
                        with ui.card().classes('w-32 h-48 p-0 shrink-0 group relative overflow-hidden cursor-pointer') \
                                .on('click', lambda b=book: ui.navigate.to(f'/book/{b["id"]}')):
                            
                            if cover:
                                ui.image(cover).classes('w-full h-full object-cover transition-transform group-hover:scale-110 duration-500')
                            else:
                                with ui.column().classes('w-full h-full bg-gray-100 items-center justify-center p-2'):
                                    ui.label(book['title']).classes('text-xs text-center font-bold line-clamp-3')

                            with ui.column().classes('absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity items-center justify-center'):
                                ui.icon('visibility', color='white', size='md')
        else:
            ui.label('No books available to discover.').classes('text-gray-400 italic')