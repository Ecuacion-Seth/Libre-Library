import json
from pathlib import Path
from typing import Dict, Optional
from nicegui import ui
from components.header import header
from components.sidebar import sidebar

# --- PATH CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent.parent
if not (BASE_DIR / 'data').exists():
    BASE_DIR = BASE_DIR.parent
BOOKS_DIR = BASE_DIR / 'data' / 'books'

def load_book(book_id: str) -> Optional[Dict]:
    """Load a book's metadata and content by ID."""
    book_dir = BOOKS_DIR / str(book_id)
    metadata_path = book_dir / 'metadata.json'
    content_path = book_dir / 'content.txt'
    
    if not metadata_path.exists():
        return None
        
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
            if 'id' not in book_data: book_data['id'] = book_id
            
        if content_path.exists():
            with open(content_path, 'r', encoding='utf-8') as f:
                book_data['content'] = f.read()
        else:
            book_data['content'] = "Content not available."
            
        return book_data
    except Exception as e:
        print(f"Error loading book {book_id}: {e}")
        return None

@ui.page('/book/{book_id}')
def book_detail_page(book_id: str):
    """Page for displaying detailed information about a specific book."""
    
    # 1. Load Data
    book = load_book(book_id)
    
    # 2. Setup Layout
    sidebar() # Load sidebar first so it sits on the left
    
    # Check if book exists
    if not book:
        header()
        with ui.column().classes('w-full h-screen items-center justify-center bg-gray-50'):
            ui.icon('sentiment_dissatisfied', size='4em').classes('text-gray-300 mb-4')
            ui.label('Book not found').classes('text-xl font-bold text-gray-500')
            ui.button('Return to Library', on_click=lambda: ui.navigate.to('/books')) \
                .props('outline')
        return

    # Extract info for easier usage
    title = book.get('title', 'Untitled')
    authors = book.get('authors', [{'name': 'Unknown Author'}])
    author_name = authors[0].get('name', 'Unknown Author') if authors else 'Unknown'
    description = book.get('summaries', ['No description available.'])[0]
    subjects = book.get('subjects', [])
    languages = book.get('languages', ['en'])
    download_count = book.get('download_count', 0)

    # --- IMAGE LOGIC (Matches your books.py) ---
    local_cover_path = BOOKS_DIR / str(book_id) / 'cover.jpg'
    if local_cover_path.exists():
        cover_url = f'/covers/{book_id}/cover.jpg'
    else:
        cover_url = book.get('formats', {}).get('image/jpeg', 'https://via.placeholder.com/300x450?text=No+Cover')

    # 3. Main Content Wrapper
    # We remove the standard header call inside the layout because we might want a transparent one,
    # but for consistency, we'll stick to the white one.
    header()

    with ui.column().classes('w-full min-h-screen bg-gray-50 pb-20'):
        
        # --- BREADCRUMBS & NAV ---
        with ui.row().classes('w-full max-w-7xl mx-auto px-6 py-4 items-center gap-2 text-sm text-gray-500'):
            ui.link('Library', '/books').classes('hover:text-indigo-600 transition-colors')
            ui.label('/')
            ui.label(title).classes('text-gray-900 font-medium truncate max-w-[200px]')

        # --- HERO SECTION ---
        with ui.row().classes('w-full max-w-7xl mx-auto px-6 py-8 gap-12 items-start wrap'):
            
            # LEFT COLUMN: Cover Image & Actions
            with ui.column().classes('w-full md:w-1/3 lg:w-1/4 gap-6'):
                # Cover with fancy shadow
                with ui.element('div').classes('w-full rounded-lg shadow-2xl overflow-hidden bg-white p-2 transform transition-transform hover:scale-[1.01]'):
                    ui.image(cover_url).classes('w-full object-cover rounded aspect-[2/3]')
                
                # Primary Actions
                with ui.column().classes('w-full gap-3'):
                    ui.button('Read Now', icon='menu_book', on_click=lambda: ui.navigate.to(f'/read/{book_id}')) \
                        .classes('w-full py-3 text-lg font-bold shadow-lg shadow-indigo-200') \
                        .props('color=indigo-600 unelevated')
                    
                    ui.button('Download ePub', icon='download') \
                        .classes('w-full py-2') \
                        .props('outline color=grey-8')

            # RIGHT COLUMN: Details & Metadata
            with ui.column().classes('flex-1 gap-6 min-w-[300px]'):
                
                # Title Block
                with ui.column().classes('gap-2'):
                    ui.label(title).classes('text-4xl md:text-5xl font-black text-gray-900 leading-tight font-serif')
                    ui.label(f'by {author_name}').classes('text-xl text-indigo-600 font-medium')

                # Stats Row (Icons + Data)
                with ui.row().classes('w-full gap-8 py-6 border-y border-gray-200'):
                    
                    # Language
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('translate').classes('text-gray-400')
                        with ui.column().classes('gap-0'):
                            ui.label('Language').classes('text-xs text-gray-400 uppercase tracking-wide')
                            ui.label(languages[0].upper()).classes('font-bold text-gray-700')
                    
                    # Downloads
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('cloud_download').classes('text-gray-400')
                        with ui.column().classes('gap-0'):
                            ui.label('Downloads').classes('text-xs text-gray-400 uppercase tracking-wide')
                            ui.label(f"{download_count:,}").classes('font-bold text-gray-700')
                    
                    # File Type (Static for now)
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('description').classes('text-gray-400')
                        with ui.column().classes('gap-0'):
                            ui.label('Format').classes('text-xs text-gray-400 uppercase tracking-wide')
                            ui.label('Digital Text').classes('font-bold text-gray-700')

                # Tags / Subjects
                if subjects:
                    with ui.column().classes('gap-2'):
                        ui.label('TOPICS').classes('text-xs font-bold text-gray-400 tracking-wider')
                        with ui.row().classes('gap-2 wrap'):
                            for subject in subjects[:6]: # Limit to top 6 tags to keep it clean
                                clean_sub = subject.split('--')[0].strip()
                                ui.chip(clean_sub).props('dense outline square color=grey-6').classes('font-medium')

                # Description
                with ui.column().classes('gap-3 mt-4'):
                    ui.label('About this Book').classes('text-2xl font-bold text-gray-800')
                    # We use markdown for nice text rendering
                    ui.markdown(description).classes('text-gray-600 leading-relaxed text-lg max-w-prose')

        # --- PREVIEW SECTION ---
        # Only show if there is content
        if book.get('content') and len(book['content']) > 100:
            with ui.column().classes('w-full max-w-7xl mx-auto px-6 mt-12'):
                ui.label('First Chapter Preview').classes('text-2xl font-bold text-gray-800 mb-6')
                
                with ui.card().classes('w-full bg-orange-50/30 border-none p-8 shadow-inner'):
                    # Show first 1500 characters
                    preview_text = book['content'][:1500] + "..."
                    ui.markdown(preview_text).classes('font-serif text-gray-700 leading-loose text-lg whitespace-pre-line')
                    
                    # Fade out effect overlay
                    with ui.element('div').classes('w-full h-32 bg-gradient-to-t from-orange-50 to-transparent -mt-32 relative'):
                        pass
                    
                    with ui.row().classes('w-full justify-center mt-4'):
                         ui.button('Continue Reading', icon='auto_stories', on_click=lambda: ui.navigate.to(f'/read/{book_id}')) \
                            .props('unelevated color=indigo-600')