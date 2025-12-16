import re
import json
from pathlib import Path
from nicegui import ui, app
from pages.book.book_details import load_book

# --- CONFIGURATION ---
CHUNK_SIZE = 3000
BASE_DIR = Path(__file__).resolve().parent.parent.parent
USERS_DIR = BASE_DIR / 'data' / 'users'

# --- HELPER: TEXT CLEANING ---
def clean_text(text):
    if not text: return ""
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text

# --- HELPER: PROGRESS MANAGEMENT ---
def get_progress_file():
    if not app.storage.user.get('authenticated'):
        return None
        
    username = app.storage.user.get('username')
    safe_name = "".join([c for c in username if c.isalpha() or c.isdigit()])
    user_dir = USERS_DIR / safe_name
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir / 'reading_history.json'

def load_saved_page(book_id):
    p_file = get_progress_file()
    if not p_file or not p_file.exists():
        return 0
        
    try:
        with open(p_file, 'r') as f:
            history = json.load(f)
            return history.get(str(book_id), 0)
    except:
        return 0

def save_current_page(book_id, page_num):
    """Saves the current page number and moves book to end of list."""
    p_file = get_progress_file()
    if not p_file: return
    
    history = {}
    if p_file.exists():
        try:
            with open(p_file, 'r') as f:
                history = json.load(f)
        except:
            history = {}
            
    # --- THE FIX IS HERE ---
    # We delete the key if it exists, then re-add it.
    # This forces Python to move this book to the END of the dictionary.
    if str(book_id) in history:
        del history[str(book_id)]
        
    history[str(book_id)] = page_num
    
    with open(p_file, 'w') as f:
        json.dump(history, f)

# --- MAIN PAGE ---

@ui.page('/read/{book_id}')
def reader_page(book_id: str):
    # 1. Load Book
    book = load_book(book_id)
    if not book:
        ui.label('Book not found').classes('text-xl text-red-500 p-8')
        return

    raw_content = book.get('content', '')
    full_content = clean_text(raw_content)
    total_chars = len(full_content)
    total_pages = (total_chars + CHUNK_SIZE - 1) // CHUNK_SIZE if total_chars > 0 else 1
    
    # 2. Load History
    start_page = load_saved_page(book_id)
    
    # 3. State
    state = {
        'page': start_page,
        'font_size': 18,
        'theme': 'sepia', 
    }

    themes = {
        'light': ('bg-gray-100', 'bg-white', 'text-gray-900'),
        'dark':  ('bg-gray-900', 'bg-gray-800', 'text-gray-300'),
        'sepia': ('bg-stone-200', 'bg-[#f4ecd8]', 'text-gray-900'),
    }

    # 4. Render
    @ui.refreshable
    def render_content():
        if state['page'] >= total_pages: state['page'] = total_pages - 1
        
        start = state['page'] * CHUNK_SIZE
        end = start + CHUNK_SIZE
        chunk = full_content[start:end]
        progress = (state['page'] + 1) / total_pages
        win_bg, paper_bg, text_col = themes[state['theme']]

        with ui.column().classes(f'w-full min-h-screen items-center py-8 px-4 transition-colors duration-300 {win_bg}'):
            
            with ui.column().classes(f'w-full max-w-3xl rounded-lg shadow-xl overflow-hidden transition-colors duration-300 {paper_bg}'):
                
                # Header
                with ui.row().classes('w-full items-center justify-between p-4 border-b border-black/10'):
                    ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to(f'/book/{book_id}'))\
                        .props('flat round dense text-color=grey')
                    
                    with ui.column().classes('items-center gap-0'):
                        title = book.get('title', 'Untitled')
                        if len(title) > 40: title = title[:40] + '...'
                        ui.label(title).classes(f'text-xs font-bold uppercase tracking-wider opacity-50 {text_col}')
                        ui.label(f'Page {state["page"] + 1} of {total_pages}').classes('text-[10px] opacity-40')

                    with ui.button(icon='settings').props('flat round dense text-color=grey'):
                        with ui.menu().classes('bg-white p-4 shadow-xl border border-gray-100 rounded-lg'):
                            ui.label('Appearance').classes('text-xs font-bold text-gray-400 mb-2 uppercase')
                            with ui.row().classes('gap-2 mb-4'):
                                def make_theme_btn(t, icon):
                                    color = 'orange' if state['theme'] == t else 'grey'
                                    ui.button(icon=icon, on_click=lambda t=t: set_theme(t)).props(f'round flat text-color={color}')
                                make_theme_btn('light', 'light_mode')
                                make_theme_btn('dark', 'dark_mode')
                                make_theme_btn('sepia', 'menu_book')

                            ui.separator().classes('mb-4')
                            ui.label('Text Size').classes('text-xs font-bold text-gray-400 mb-1 uppercase')
                            with ui.row().classes('items-center gap-2'):
                                ui.button('-', on_click=lambda: update_font(state['font_size'] - 2)).props('flat dense round size=sm')
                                ui.label(f"{state['font_size']}px").classes('min-w-[30px] text-center font-mono text-sm')
                                ui.button('+', on_click=lambda: update_font(state['font_size'] + 2)).props('flat dense round size=sm')

                ui.linear_progress(value=progress, size='4px', color='orange-400').props('instant-feedback')

                with ui.column().classes(f'w-full p-8 md:p-12 min-h-[70vh] {text_col}'):
                    ui.markdown(chunk).classes('prose max-w-none font-serif leading-loose text-justify whitespace-normal')\
                        .style(f'font-size: {state["font_size"]}px')

                with ui.row().classes('w-full justify-between p-6 border-t border-black/5 bg-black/5'):
                    if state['page'] > 0:
                        ui.button('Previous', on_click=prev_page, icon='arrow_back').props('flat dense no-caps').classes('opacity-60 hover:opacity-100')
                    else:
                        ui.label('').classes('w-10')
                        
                    if state['page'] < total_pages - 1:
                        ui.button('Next Page', on_click=next_page).props('flat dense no-caps icon-right=arrow_forward').classes('opacity-60 hover:opacity-100')
                    else:
                        ui.button('Finish Book', on_click=lambda: ui.navigate.to(f'/book/{book_id}'))\
                            .props('flat dense no-caps text-color=green icon-right=check')

    # 5. Handlers
    def next_page():
        if state['page'] < total_pages - 1:
            state['page'] += 1
            save_current_page(book_id, state['page'])
            render_content.refresh()
            ui.run_javascript('window.scrollTo(0, 0)')

    def prev_page():
        if state['page'] > 0:
            state['page'] -= 1
            save_current_page(book_id, state['page'])
            render_content.refresh()
            ui.run_javascript('window.scrollTo(0, 0)')

    def update_font(size):
        state['font_size'] = max(12, min(32, size))
        render_content.refresh()

    def set_theme(theme_name):
        state['theme'] = theme_name
        render_content.refresh()

    render_content()