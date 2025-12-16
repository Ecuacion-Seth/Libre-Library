from nicegui import ui, app
from pages import home, about, books, chatbot, study_planner, login, upload, profile, bookmark
import pages.book.book_details 
from pathlib import Path

# --- ADD THIS LINE ---
import pages.reader.reader 
# ---------------------

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / 'data' / 'assets'

app.add_static_files('/assets', ASSETS_DIR)



if __name__ in {'__main__', '__mp_main__'}:
    ui.run(title='Libre-Library', favicon='📚',storage_secret='super_secret_key_123')