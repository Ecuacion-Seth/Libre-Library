from nicegui import ui

def header(nav_drawer=None):
    """
    A modern header with a mobile toggle button.
    
    Args:
        nav_drawer: The sidebar drawer object. If provided, adds a menu toggle button.
    """
    # 'elevated=False' removes shadow for a flat look
    # 'lg:hidden' on the menu button makes it disappear on large screens (desktop)
    with ui.header().classes('bg-white border-b border-gray-200 items-center px-4 h-16') \
            .props('elevated=False'):
        
        # --- 1. MOBILE MENU BUTTON ---
        # Only shows if a drawer was passed AND we are on a smaller screen
        if nav_drawer:
            ui.button(icon='menu', on_click=nav_drawer.toggle) \
                .classes('lg:hidden text-gray-600 mr-2') \
                .props('flat round dense icon-size=md')

        # --- 2. BRANDING ---
        with ui.row().classes('items-center gap-2'):
            # On mobile, we might want to hide the text if it gets too crowded, 
            # but usually, it's fine to keep it.
            ui.icon('local_library').classes('text-indigo-600 text-2xl')
            ui.label('Libre Library').classes('text-lg font-bold text-gray-800 tracking-tight')

        ui.space()

        # --- 3. GLOBAL UTILITIES (Right Side) ---
        with ui.row().classes('items-center gap-1 md:gap-2'):
            
            # Dark Mode (Visible on all screens)
            dark = ui.dark_mode()
            ui.button(icon='dark_mode', on_click=dark.toggle) \
                .props('flat round text-color=grey-7 dense') \
                .tooltip('Toggle Dark Theme')

            # Notifications (Hidden on very small phones if needed, or keep it)
            with ui.button(icon='notifications_none').props('flat round text-color=grey-7 dense'):
                ui.badge('3', color='red-500').props('floating rounded size=xs')

            # Profile / Settings (The "Quick Access" you mentioned)
            ui.button(icon='more_vert').props('flat round text-color=grey-7 dense')