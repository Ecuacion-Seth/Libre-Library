import random
from nicegui import ui
from components.header import header
from components.sidebar import sidebar

# Import your existing logic to get real data
# Make sure books.py is in the same directory or adjust import
try:
    from books import load_books
except ImportError:
    # Fallback if import fails (just for safety)
    def load_books(): return []

@ui.page('/')
def home_page():
    # 1. Load Data
    all_books = load_books()
    total_books = len(all_books)
    
    # Calculate some stats dynamically
    authors = set()
    languages = set()
    for b in all_books:
        if 'authors' in b and b['authors']:
            authors.add(b['authors'][0].get('name', 'Unknown'))
        if 'languages' in b:
            languages.update(b['languages'])
            
    # Pick a random "Featured Book"
    featured_book = random.choice(all_books) if all_books else None

    # 2. Page Setup
    sidebar()
    header()

    with ui.column().classes('w-full min-h-screen bg-gray-50/50 p-8'):
        
        # --- WELCOME SECTION ---
        with ui.column().classes('mb-8'):
            ui.label('Welcome back, Student!').classes('text-4xl font-black text-gray-900 tracking-tight')
            ui.label('Here is what is happening in your library today.').classes('text-lg text-gray-500')

        # --- STATS CARDS ROW ---
        with ui.row().classes('w-full gap-6 mb-8'):
            # Card 1: Total Books
            with ui.card().classes('w-full md:w-1/4 p-4 items-center flex-row gap-4 border-l-4 border-indigo-500'):
                ui.icon('library_books', size='3em').classes('text-indigo-100 bg-indigo-500 rounded-full p-2')
                with ui.column().classes('gap-0'):
                    ui.label(str(total_books)).classes('text-3xl font-bold text-gray-800')
                    ui.label('Total Books').classes('text-sm text-gray-400 font-medium uppercase')

            # Card 2: Authors
            with ui.card().classes('w-full md:w-1/4 p-4 items-center flex-row gap-4 border-l-4 border-purple-500'):
                ui.icon('person', size='3em').classes('text-purple-100 bg-purple-500 rounded-full p-2')
                with ui.column().classes('gap-0'):
                    ui.label(str(len(authors))).classes('text-3xl font-bold text-gray-800')
                    ui.label('Unique Authors').classes('text-sm text-gray-400 font-medium uppercase')

            # Card 3: Reading Streak (Mock Data for now)
            with ui.card().classes('w-full md:w-1/4 p-4 items-center flex-row gap-4 border-l-4 border-orange-500'):
                ui.icon('local_fire_department', size='3em').classes('text-orange-100 bg-orange-500 rounded-full p-2')
                with ui.column().classes('gap-0'):
                    ui.label('3 Days').classes('text-3xl font-bold text-gray-800')
                    ui.label('Reading Streak').classes('text-sm text-gray-400 font-medium uppercase')

        # --- MAIN CONTENT GRID ---
        with ui.grid().classes('w-full gap-8 grid-cols-1 lg:grid-cols-3'):
            
            # LEFT COLUMN (2/3 width): Featured & Quick Actions
            with ui.column().classes('lg:col-span-2 gap-8'):
                
                # A. Hero / Featured Book
                if featured_book:
                    with ui.card().classes('w-full p-0 overflow-hidden bg-gradient-to-r from-indigo-600 to-purple-600 text-white'):
                        with ui.row().classes('w-full items-center p-8 gap-8'):
                            # Cover Image
                            cover = featured_book.get('formats', {}).get('image/jpeg')
                            if cover:
                                ui.image(cover).classes('w-32 rounded shadow-2xl')
                            
                            # Text
                            with ui.column().classes('flex-1'):
                                ui.label('RECOMMENDED READ').classes('text-xs font-bold opacity-75 tracking-widest mb-1')
                                ui.label(featured_book.get('title')).classes('text-3xl font-bold leading-tight')
                                author = featured_book.get('authors', [{}])[0].get('name', 'Unknown')
                                ui.label(f'by {author}').classes('text-lg opacity-90 mb-4')
                                
                                with ui.row().classes('gap-2'):
                                    ui.button('Read Now', icon='menu_book', 
                                              on_click=lambda: ui.navigate.to(f'/book/{featured_book["id"]}')) \
                                              .props('unelevated text-color=indigo-700 color=white')
                                    ui.button('Details', icon='info', 
                                              on_click=lambda: ui.navigate.to(f'/book/{featured_book["id"]}')) \
                                              .props('outline text-color=white')

                # B. Quick Actions
                with ui.card().classes('w-full p-6'):
                    ui.label('Quick Actions').classes('text-xl font-bold text-gray-800 mb-4')
                    with ui.row().classes('w-full gap-4'):
                        ui.button('Browse Library', icon='search', on_click=lambda: ui.navigate.to('/books')) \
                            .classes('flex-1 py-4').props('outline color=grey-8')
                        ui.button('Upload Book', icon='upload', on_click=lambda: ui.notify('Coming soon!')) \
                            .classes('flex-1 py-4').props('outline color=grey-8')
                        ui.button('My Favorites', icon='favorite', on_click=lambda: ui.notify('Coming soon!')) \
                            .classes('flex-1 py-4').props('outline color=grey-8')

            # RIGHT COLUMN (1/3 width): Recent Activity / System Status
            with ui.column().classes('gap-6'):
                
                # Recent Activity List
                with ui.card().classes('w-full p-6 h-full'):
                    ui.label('Recent Activity').classes('text-xl font-bold text-gray-800 mb-4')
                    
                    # Mock activity items
                    activities = [
                        ('Opened "Moby Dick"', '10 mins ago', 'menu_book'),
                        ('Searched for "Horror"', '2 hours ago', 'search'),
                        ('Added "Frankenstein"', 'Yesterday', 'add_circle'),
                    ]
                    
                    with ui.column().classes('w-full gap-4'):
                        for text, time, icon in activities:
                            with ui.row().classes('w-full items-center gap-3 pb-3 border-b border-gray-100 last:border-0'):
                                ui.icon(icon).classes('text-gray-400')
                                with ui.column().classes('gap-0 flex-1'):
                                    ui.label(text).classes('text-sm font-medium text-gray-700')
                                    ui.label(time).classes('text-xs text-gray-400')