from nicegui import ui
from pages import home, about, books, chatbot, study_planner
import pages.book.book_details 


# --- ADD THIS LINE ---
import pages.reader.reader 
# ---------------------

if __name__ in {'__main__', '__mp_main__'}:
    ui.run()