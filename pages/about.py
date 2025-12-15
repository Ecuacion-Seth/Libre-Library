from nicegui import ui
from components.header  import header
from components.sidebar import sidebar

@ui.page('/about')
def home_page():
    header()
    sidebar()
    with ui.column().classes('w-full'):
        with ui.column().classes('q-pa-lg'):
            ui.label('About Page').classes('text-h4')
            ui.button('Go to Home', on_click=lambda: ui.navigate.to('/'))