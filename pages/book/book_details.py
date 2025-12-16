import json
import os
from pathlib import Path
from typing import Dict, Optional
from nicegui import ui, app
from components.header import header
from components.sidebar import sidebar

# Import the bookmark backend logic
from pages.bookmark import toggle_bookmark, is_bookmarked 

# --- PATH CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BOOKS_DIR = BASE_DIR / 'data' / 'books'

# --- HELPER: FILE TYPE DETECTION ---
def get_file_info(book_data: Dict):
    """
    Analyzes the book metadata to find the main file and determine its type.
    Returns: (file_url, file_type, is_readable_text)
    """
    formats = book_data.get('formats', {})
    
    # 1. Check for the main file uploaded via upload.py
    filename = formats.get('application/octet-stream')
    
    # Fallback for old manual books that might just have content.txt
    if not filename:
        if book_data.get('content'):
            return (None, 'text', True)
        return (None, 'unknown', False)

    # 2. Determine Type based on extension
    ext = os.path.splitext(filename)[1].lower()
    
    # URL structure: /covers/{book_id}/{filename}
    file_url = f"/covers/{book_data['id']}/{filename}"
    
    if ext == '.pdf':
        return (file_url, 'pdf', False) # Browser handles PDF
    elif ext in ['.txt', '.md']:
        return (file_url, 'text', True) # Our reader handles Text
    elif ext == '.epub':
        return (file_url, 'epub', False) # EPUBs usually need download
    else:
        return (file_url, 'download', False) # DOCX, PPT, etc.

def load_book(book_id: str) -> Optional[Dict]:
    """Load a book's metadata."""
    book_dir = BOOKS_DIR / str(book_id)
    metadata_path = book_dir / 'metadata.json'
    
    if not metadata_path.exists():
        return None
        
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
            if 'id' not in book_data: book_data['id'] = book_id
            
        # Try to load raw text content if it exists (legacy support)
        content_path = book_dir / 'content.txt'
        if content_path.exists():
            with open(content_path, 'r', encoding='utf-8') as f:
                book_data['content'] = f.read()
            
        return book_data
    except Exception as e:
        return None

@ui.page('/book/{book_id}')
def book_detail_page(book_id: str):
    
    # 1. Load Data
    book = load_book(book_id)
    nav = sidebar()
    header(nav)
    
    # Check if book exists
    if not book:
        with ui.column().classes('w-full h-screen items-center justify-center bg-gray-50'):
            ui.icon('sentiment_dissatisfied', size='4em').classes('text-gray-300 mb-4')
            ui.label('Book not found').classes('text-xl font-bold text-gray-500')
            ui.button('Return to Library', on_click=lambda: ui.navigate.to('/books')).props('outline')
        return

    # Extract info
    title = book.get('title', 'Untitled')
    authors = book.get('authors', [{'name': 'Unknown Author'}])
    author_name = authors[0].get('name', 'Unknown Author') if authors else 'Unknown'
    description = book.get('summaries', ['No description available.'])[0]
    subjects = book.get('subjects', [])
    
    # Image Logic
    local_cover = BOOKS_DIR / str(book_id) / 'cover.jpg'
    if not local_cover.exists():
        local_cover = BOOKS_DIR / str(book_id) / 'cover.png'
        
    if local_cover.exists():
        cover_url = f'/covers/{book_id}/{local_cover.name}'
    else:
        cover_url = book.get('formats', {}).get('image/jpeg', None)

    # File Type Logic
    file_url, file_type, is_readable = get_file_info(book)

    # Check Bookmark Status (Backend)
    saved_state = is_bookmarked(book_id)

    # 3. Main Content
    with ui.column().classes('w-full min-h-screen bg-gray-50 pb-20'):
        
        # Breadcrumbs
        with ui.row().classes('w-full max-w-7xl mx-auto px-6 py-4 items-center gap-2 text-sm text-gray-500'):
            ui.link('Library', '/books').classes('hover:text-indigo-600')
            ui.label('/')
            ui.label(title).classes('text-gray-900 font-medium truncate max-w-[200px]')

        # --- HERO SECTION ---
        with ui.row().classes('w-full max-w-7xl mx-auto px-6 py-8 gap-12 items-start wrap'):
            
            # LEFT: Cover Image & Actions
            with ui.column().classes('w-full md:w-1/3 lg:w-1/4 gap-6'):
                if cover_url:
                    ui.image(cover_url).classes('w-full rounded-lg shadow-2xl')
                else:
                    with ui.element('div').classes('w-full aspect-[2/3] bg-gray-200 rounded flex items-center justify-center'):
                        ui.icon('auto_stories', size='4em').classes('text-gray-400')

                # --- ACTION BUTTON STACK ---
                with ui.column().classes('w-full gap-3'):
                    
                    # 1. PRIMARY ACTION 
                    # Logic Updated: If it's a PDF, show PDF view.
                    # For everything else (Text, EPUB, etc), show "Read Now".
                    
                    if file_type == 'pdf':
                        ui.button('View PDF', icon='visibility', on_click=lambda: ui.open(file_url, new_tab=True)) \
                            .classes('w-full py-3 text-lg font-bold shadow-lg shadow-red-200') \
                            .props('color=red-600 unelevated')
                    
                    elif is_readable or file_url:
                        # Merged 'is_readable' and the old 'file_url' (Download) logic here
                        ui.button('Read Now', icon='menu_book', on_click=lambda: ui.navigate.to(f'/read/{book_id}')) \
                            .classes('w-full py-3 text-lg font-bold shadow-lg shadow-indigo-200') \
                            .props('color=indigo-600 unelevated')
                    
                    else:
                        ui.button('Unavailable', icon='block').classes('w-full').props('disabled outline')

                    # 2. SECONDARY ACTION (Bookmark)
                    def handle_bookmark_click(btn):
                        new_state = toggle_bookmark(book_id)
                        if new_state:
                            btn.props('icon=bookmark color=pink-100 text-color=pink-600')
                            btn.text = 'Saved to List'
                            ui.notify('Book saved to your list!', color='pink')
                        else:
                            btn.props('icon=bookmark_border color=white text-color=grey-8')
                            btn.text = 'Save to List'
                            ui.notify('Book removed from list.')

                    # Initial Button State
                    b_icon = 'bookmark' if saved_state else 'bookmark_border'
                    b_color = 'pink-100' if saved_state else 'white'
                    b_text_color = 'pink-600' if saved_state else 'grey-8'
                    b_text = 'Saved to List' if saved_state else 'Save to List'

                    ui.button(b_text, icon=b_icon, on_click=lambda e: handle_bookmark_click(e.sender)) \
                        .classes('w-full py-2 font-bold border border-gray-200') \
                        .props(f'unelevated color={b_color} text-color={b_text_color}')

            # RIGHT: Details
            with ui.column().classes('flex-1 gap-6 min-w-[300px]'):
                
                # Title & Author
                with ui.column().classes('gap-2'):
                    ui.label(title).classes('text-4xl md:text-5xl font-black text-gray-900 leading-tight font-serif')
                    ui.label(f'by {author_name}').classes('text-xl text-indigo-600 font-medium')

                # Tags
                if subjects:
                    with ui.row().classes('gap-2 wrap'):
                        for subject in subjects[:4]:
                            ui.chip(subject).props('dense square outline color=grey-6').classes('font-bold text-xs uppercase tracking-wider')

                # Description
                ui.separator().classes('my-2')
                ui.label('Description').classes('text-sm font-bold text-gray-400 uppercase tracking-wider')
                ui.markdown(description).classes('text-gray-700 leading-relaxed text-lg max-w-prose')

        # --- PREVIEW SECTION (Only for Readable Text) ---
        if book.get('content') and len(book['content']) > 100:
            with ui.column().classes('w-full max-w-7xl mx-auto px-6 mt-12'):
                ui.label('Preview').classes('text-2xl font-bold text-gray-800 mb-4')
                with ui.card().classes('w-full bg-orange-50/30 border-none p-8 shadow-inner'):
                    preview_text = book['content'][:1000] + "..."
                    ui.markdown(preview_text).classes('font-serif text-gray-700 leading-loose text-lg whitespace-pre-line')
                    with ui.button('Continue Reading', icon='arrow_forward', on_click=lambda: ui.navigate.to(f'/read/{book_id}')) \
                        .classes('mt-4').props('flat color=indigo'):
                        pass