import re
from nicegui import ui
from pages.book.book_details import load_book

# --- CONFIGURATION ---
CHUNK_SIZE = 3000

# --- HELPER: Fixes "hard wraps" so Justify works ---
def clean_text(text):
    """
    Replaces single newlines with spaces (unwrapping paragraphs)
    while preserving double newlines (paragraph breaks).
    """
    if not text: return ""
    # 1. Replace single newlines with space (fixes the "broken line" issue)
    #    Regex: Find newline NOT preceded by newline AND NOT followed by newline
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    
    # 2. Reduce multiple spaces to one (cleans up OCR artifacts)
    text = re.sub(r' +', ' ', text)
    return text

@ui.page('/read/{book_id}')
def reader_page(book_id: str):
    # 1. Load & Clean Data
    book = load_book(book_id)
    if not book:
        ui.label('Book not found').classes('text-xl text-red-500 p-8')
        return

    # Clean the text immediately so pagination is accurate
    raw_content = book.get('content', '')
    full_content = clean_text(raw_content)
    
    total_chars = len(full_content)
    # Avoid division by zero if book is empty
    total_pages = (total_chars + CHUNK_SIZE - 1) // CHUNK_SIZE if total_chars > 0 else 1
    
    # 2. State Variables
    state = {
        'page': 0,
        'font_size': 18,
        'theme': 'sepia',  # Options: 'light', 'dark', 'sepia'
    }

    # 3. Visual Themes (Background vs Paper Color)
    # tuple format: (window_background, paper_background, text_color)
    themes = {
        'light': ('bg-gray-100', 'bg-white', 'text-gray-900'),
        'dark':  ('bg-gray-900', 'bg-gray-800', 'text-gray-300'),
        'sepia': ('bg-stone-200', 'bg-[#f4ecd8]', 'text-gray-900'), # f4ecd8 is a nice cream color
    }

    # 4. Content Renderer
    @ui.refreshable
    def render_content():
        start = state['page'] * CHUNK_SIZE
        end = start + CHUNK_SIZE
        chunk = full_content[start:end]
        
        # Calculate Progress %
        progress = (state['page'] + 1) / total_pages

        # Get Theme Colors
        win_bg, paper_bg, text_col = themes[state['theme']]

        # --- OUTER CONTAINER (The Window) ---
        # Centered flex container with the window background color
        with ui.column().classes(f'w-full min-h-screen items-center py-8 px-4 transition-colors duration-300 {win_bg}'):
            
            # --- THE "SHEET OF PAPER" ---
            # Shadow-lg gives it depth. max-w-3xl restricts width for readability.
            with ui.column().classes(f'w-full max-w-3xl rounded-lg shadow-xl overflow-hidden transition-colors duration-300 {paper_bg}'):
                
                # --- Top Bar (Progress & Title) ---
                with ui.row().classes('w-full items-center justify-between p-4 border-b border-black/10'):
                    # Left: Exit Button
                    ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to(f'/book/{book_id}'))\
                        .props('flat round dense text-color=grey')
                    
                    # Center: Title (Truncated) & Progress Text
                    with ui.column().classes('items-center gap-0'):
                        title = book.get('title', 'Untitled')
                        if len(title) > 40: title = title[:40] + '...'
                        ui.label(title).classes(f'text-xs font-bold uppercase tracking-wider opacity-50 {text_col}')
                        ui.label(f'Page {state["page"] + 1} of {total_pages}').classes('text-[10px] opacity-40')

                    # Right: Settings
                    with ui.button(icon='settings').props('flat round dense text-color=grey'):
                        with ui.menu().classes('bg-white p-4 shadow-xl border border-gray-100 rounded-lg'):
                            ui.label('Appearance').classes('text-xs font-bold text-gray-400 mb-2 uppercase')
                            
                            # Theme Toggles
                            with ui.row().classes('gap-2 mb-4'):
                                def make_theme_btn(t, icon):
                                    # Highlight active theme
                                    is_active = state['theme'] == t
                                    color = 'orange' if is_active else 'grey'
                                    ui.button(icon=icon, on_click=lambda t=t: set_theme(t))\
                                        .props(f'round flat text-color={color}')
                                
                                make_theme_btn('light', 'light_mode')
                                make_theme_btn('dark', 'dark_mode')
                                make_theme_btn('sepia', 'menu_book')

                            ui.separator().classes('mb-4')
                            
                            # Font Size
                            ui.label('Text Size').classes('text-xs font-bold text-gray-400 mb-1 uppercase')
                            with ui.row().classes('items-center gap-2'):
                                ui.button('-', on_click=lambda: update_font(state['font_size'] - 2)).props('flat dense round size=sm')
                                ui.label(f"{state['font_size']}px").classes('min-w-[30px] text-center font-mono text-sm')
                                ui.button('+', on_click=lambda: update_font(state['font_size'] + 2)).props('flat dense round size=sm')

                # --- Visual Progress Bar ---
                ui.linear_progress(value=progress, size='4px', color='orange-400').props('instant-feedback')

                # --- TEXT CONTENT AREA ---
                # Added 'min-h-[60vh]' to keep the page size consistent even if text is short
                with ui.column().classes(f'w-full p-8 md:p-12 min-h-[70vh] {text_col}'):
                    # whitespace-normal + text-justify + clean_text = Perfect Book Layout
                    ui.markdown(chunk).classes(
                        'prose max-w-none font-serif leading-loose text-justify whitespace-normal'
                    ).style(f'font-size: {state["font_size"]}px')

                # --- Footer Navigation ---
                with ui.row().classes('w-full justify-between p-6 border-t border-black/5 bg-black/5'):
                    # Previous
                    if state['page'] > 0:
                        ui.button('Previous', on_click=prev_page, icon='arrow_back')\
                            .props('flat dense no-caps').classes('opacity-60 hover:opacity-100')
                    else:
                        ui.label('').classes('w-10') # Spacer
                        
                    # Next
                    if state['page'] < total_pages - 1:
                        ui.button('Next Page', on_click=next_page)\
                            .props('flat dense no-caps icon-right=arrow_forward').classes('opacity-60 hover:opacity-100')

    # 5. Event Handlers
    def next_page():
        if state['page'] < total_pages - 1:
            state['page'] += 1
            render_content.refresh()
            ui.run_javascript('window.scrollTo(0, 0)')

    def prev_page():
        if state['page'] > 0:
            state['page'] -= 1
            render_content.refresh()
            ui.run_javascript('window.scrollTo(0, 0)')

    def update_font(size):
        # Limit font size range
        state['font_size'] = max(12, min(32, size))
        render_content.refresh()

    def set_theme(theme_name):
        state['theme'] = theme_name
        render_content.refresh()

    # 6. Start
    render_content()