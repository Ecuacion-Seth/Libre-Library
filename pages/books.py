import json
from pathlib import Path
from typing import Dict, List
from nicegui import app, ui
from components.header import header
from components.sidebar import sidebar

# Ensure detail routes are registered if needed
import pages.book.book_details

# --- CONSTANTS ---
BASE_DIR = Path(__file__).parent.parent
if not (BASE_DIR / 'data').exists():
    BASE_DIR = BASE_DIR.parent
BOOKS_DIR = BASE_DIR / 'data' / 'books'

# --- CONFIGURATION ---
# This tells NiceGUI: "When the browser asks for /covers/..., look inside the books folder"
app.add_static_files('/covers', BOOKS_DIR)

# --- DATA LOADING ---
def load_books() -> List[Dict]:
    """Load all books with robust error handling."""
    books = []
    if not BOOKS_DIR.exists():
        return books
        
    for book_dir in BOOKS_DIR.iterdir():
        if not book_dir.is_dir(): continue
        
        metadata_path = book_dir / 'metadata.json'
        if not metadata_path.exists(): continue
            
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'id' not in data: data['id'] = book_dir.name
                if 'subjects' not in data: data['subjects'] = ['Uncategorized']
                books.append(data)
        except:
            continue
    return books

# --- UI COMPONENTS ---

def render_book_card(book: Dict):
    """A beautiful, modern card component for a single book."""
    book_id = str(book.get('id'))
    title = book.get('title', 'Untitled')
    authors = book.get('authors', [{'name': 'Unknown'}])
    if isinstance(authors, list) and len(authors) > 0:
        author_name = authors[0].get('name', 'Unknown')
    else:
        author_name = 'Unknown'
    
    # --- IMAGE LOGIC START ---
    # 1. Check if we have a local cover cached
    local_cover_path = BOOKS_DIR / book_id / 'cover.jpg'
    
    if local_cover_path.exists():
        # Use the local static route
        cover_url = f'/covers/{book_id}/cover.jpg'
    else:
        # Fallback to remote URL (or placeholder)
        cover_url = book.get('formats', {}).get('image/jpeg')
    # --- IMAGE LOGIC END ---
    
    with ui.card().classes('w-full h-[360px] p-0 gap-0 group hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden bg-white border-none') \
            .on('click', lambda: ui.navigate.to(f'/book/{book_id}')):
            
        # 1. Cover Image Area
        with ui.element('div').classes('w-full h-[220px] relative overflow-hidden bg-gray-100'):
            if cover_url:
                ui.image(cover_url).classes('w-full h-full object-cover group-hover:scale-105 transition-transform duration-500')
            else:
                with ui.column().classes('w-full h-full justify-center items-center bg-gradient-to-br from-indigo-50 to-purple-100 p-4'):
                    ui.icon('auto_stories', size='3em').classes('text-indigo-300 mb-2')
                    ui.label(title[:2]).classes('text-4xl font-serif font-bold text-indigo-200 uppercase')

            with ui.column().classes('absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 items-center justify-center'):
                ui.button('Read Now', icon='menu_book').props('rounded color=white text-color=black')

        # 2. Details Area
        with ui.column().classes('w-full h-[140px] p-4 justify-between bg-white'):
            with ui.column().classes('gap-1'):
                ui.label(title).classes('text-base font-bold leading-tight text-gray-900 line-clamp-2')
                ui.label(author_name).classes('text-xs text-gray-500 font-medium uppercase tracking-wide truncate w-full')
            
            with ui.row().classes('w-full justify-between items-center border-t border-gray-50 pt-3'):
                with ui.row().classes('items-center gap-1'):
                    ui.icon('language', size='xs').classes('text-gray-400')
                    lang = book.get('languages', ['en'])[0].upper()
                    ui.label(lang).classes('text-xs text-gray-400')
                
                if 'download_count' in book:
                    with ui.row().classes('items-center gap-1'):
                        ui.icon('download', size='xs').classes('text-gray-400')
                        ui.label(str(book['download_count'])).classes('text-xs text-gray-400')

# --- MAIN PAGE ---

@ui.page('/books')
def books_page():
    # 1. Load Data
    all_books = load_books()
    
    categories = {}
    for b in all_books:
        cat = b.get('subjects', ['Uncategorized'])[0] if b.get('subjects') else 'Uncategorized'
        simple_cat = cat.split(' -- ')[0] 
        if simple_cat not in categories: categories[simple_cat] = []
        categories[simple_cat].append(b)
    
    sorted_cats = sorted(categories.keys(), key=lambda k: len(categories[k]), reverse=True)

    # 2. Page Setup
    header()
    sidebar()

    # 3. State Management
    state = {
        'search_term': '',
        'current_tab': 'All Books'
    }

    # 4. The Unified Grid Function
    @ui.refreshable
    def books_grid():
        query = state['search_term'].lower()
        active_cat = state['current_tab']

        # A. Filter by Category
        if active_cat == "All Books":
            books_pool = all_books
        else:
            books_pool = categories.get(active_cat, [])

        # B. Filter by Search Term
        filtered_books = [
            b for b in books_pool 
            if query in b.get('title', '').lower() 
            or query in str(b.get('authors', '')).lower()
        ]

        # C. Render Logic
        if not filtered_books:
            with ui.column().classes('w-full py-20 items-center justify-center text-center opacity-60'):
                ui.icon('search_off', size='4em').classes('text-gray-300 mb-4')
                ui.label('No books match your search').classes('text-xl font-bold text-gray-400')
        else:
            with ui.grid().classes('w-full gap-6 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5'):
                for book in filtered_books:
                    render_book_card(book)

    # 5. EVENT HANDLERS
    def handle_search(e):
        state['search_term'] = e.value
        books_grid.refresh()

    def handle_tab_change(e):
        state['current_tab'] = e.value
        books_grid.refresh()

    # 6. Main Layout
    with ui.column().classes('w-full min-h-screen bg-gray-50/50'):
        
        # --- HERO SECTION ---
        with ui.column().classes('w-full bg-white border-b border-gray-200 px-8 py-10 mb-8'):
            with ui.row().classes('w-full max-w-7xl mx-auto items-end justify-between gap-6'):
                with ui.column().classes('gap-2'):
                    ui.label('Library').classes('text-4xl font-black text-gray-900 tracking-tight')
                    ui.label(f'{len(all_books)} books available for reading').classes('text-gray-500 font-medium')
                
                # --- SEARCH INPUT ---
                ui.input(placeholder='Search title or author...', 
                        value=state['search_term'],
                        on_change=handle_search) \
                    .props('outlined rounded dense icon=search') \
                    .classes('w-full md:w-80 bg-gray-50')

        # --- CONTENT SECTION ---
        with ui.column().classes('w-full max-w-7xl mx-auto px-8 pb-20'):
            
            # --- TABS ---
            with ui.tabs(value=state['current_tab'], on_change=handle_tab_change) \
                .classes('w-full text-gray-600 border-b border-gray-200 mb-8 bg-transparent'):
                
                ui.tab('All Books')
                for cat in sorted_cats[:6]: 
                    ui.tab(cat)
            
            # --- THE GRID ---
            books_grid()

ui.run()