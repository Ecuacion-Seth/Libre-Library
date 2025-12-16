import json
from pathlib import Path
from nicegui import ui, app
from components.header import header
from components.sidebar import sidebar

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
USERS_DIR = BASE_DIR / 'data' / 'users'
BOOKS_DIR = BASE_DIR / 'data' / 'books'

# --- BACKEND LOGIC (Helpers) ---

def get_bookmark_file():
    """Returns the path to the current user's bookmarks.json"""
    if not app.storage.user.get('authenticated'): return None
    username = app.storage.user.get('username')
    safe_name = "".join([c for c in username if c.isalpha() or c.isdigit()])
    return USERS_DIR / safe_name / 'bookmarks.json'

def load_bookmarks():
    """Returns a list of book IDs that are bookmarked."""
    f = get_bookmark_file()
    if not f or not f.exists(): return []
    try:
        with open(f, 'r') as file:
            return json.load(file)
    except: return []

def toggle_bookmark(book_id):
    """Adds or removes a book ID from the user's list."""
    f = get_bookmark_file()
    if not f: return False
    
    bookmarks = load_bookmarks()
    
    if book_id in bookmarks:
        bookmarks.remove(book_id)
        is_bookmarked = False
    else:
        bookmarks.append(book_id)
        is_bookmarked = True
        
    with open(f, 'w') as file:
        json.dump(bookmarks, file)
        
    return is_bookmarked

def is_bookmarked(book_id):
    return book_id in load_bookmarks()

# --- FRONTEND UI (The Page) ---

@ui.page('/bookmarks')
def bookmarks_page():
    if not app.storage.user.get('authenticated'): return ui.navigate.to('/login')

    nav = sidebar()
    header(nav)
    
    # 1. Load Data
    bookmark_ids = load_bookmarks()
    books = []

    # Load metadata for each bookmarked ID
    if bookmark_ids and BOOKS_DIR.exists():
        for b_id in bookmark_ids:
            # FIX: Convert b_id to string here
            meta_path = BOOKS_DIR / str(b_id) / 'metadata.json'
            
            if meta_path.exists():
                try:
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'id' not in data: data['id'] = b_id
                        books.append(data)
                except: continue

    # 2. Render Page
    with ui.column().classes('w-full min-h-screen bg-gray-50 p-4 md:p-8'):
        
        ui.label('Your Reading List').classes('text-3xl font-black text-gray-900 mb-2')
        ui.label(f'{len(books)} books saved for later.').classes('text-gray-500 mb-8')

        if not books:
            with ui.column().classes('w-full items-center justify-center py-12 opacity-50'):
                ui.icon('bookmark_border', size='4em').classes('text-gray-300 mb-4')
                ui.label('No bookmarks yet.').classes('text-xl font-bold text-gray-400')
                ui.button('Browse Library', on_click=lambda: ui.navigate.to('/books')).props('outline')
        else:
            # Reusing the grid layout style
            with ui.grid().classes('w-full gap-6 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5'):
                for book in books:
                    # Simple Card Logic
                    with ui.card().classes('w-full h-auto p-0 group cursor-pointer hover:shadow-xl transition-all') \
                            .on('click', lambda b=book: ui.navigate.to(f'/book/{b["id"]}')):
                        
                        # Image
                        cover = book.get('formats', {}).get('image/jpeg')
                        if cover:
                            ui.image(cover).classes('w-full aspect-[2/3] object-cover')
                        else:
                            with ui.element('div').classes('w-full aspect-[2/3] bg-gray-200 flex items-center justify-center'):
                                ui.icon('auto_stories', color='grey')
                        
                        # Text
                        with ui.column().classes('p-4'):
                            ui.label(book['title']).classes('font-bold leading-tight line-clamp-2 text-sm')
                            
                            # Remove Button
                            with ui.button(icon='delete', color='red').props('flat dense size=sm') \
                                    .classes('self-end mt-2 opacity-0 group-hover:opacity-100 transition-opacity') \
                                    .on('click.stop', lambda b=book: [toggle_bookmark(b['id']), ui.navigate.reload()]):
                                ui.tooltip('Remove from list')