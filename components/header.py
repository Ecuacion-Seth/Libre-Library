from nicegui import ui

def header():
    """
    A modern, minimal header.
    It replaces the old navigation links (now in the Sidebar) with
    utility icons like Search, Dark Mode, and Notifications.
    """
    # 'elevated=False' removes the heavy shadow for a flatter look
    # 'border-b border-gray-200' adds a subtle separator line
    # 'bg-white' keeps it clean to match the sidebar
    with ui.header().classes('bg-white border-b border-gray-200 items-center px-6 h-16') \
            .props('elevated=False'):
        
        # --- 1. BRANDING / BREADCRUMBS ---
        # Since we have the main logo in the Sidebar, we can use this space
        # to show the current section or just a clean title.
        with ui.row().classes('items-center gap-2'):
            ui.icon('local_library').classes('text-indigo-600 text-2xl')
            ui.label('Libre Library').classes('text-lg font-bold text-gray-800 tracking-tight')

        ui.space()

        # --- 2. GLOBAL UTILITIES (Right Side) ---
        with ui.row().classes('items-center gap-2'):
            
            # A. Global Search (Visual only for now)
            # This is different from the "Book Search". This would be for finding
            # settings, users, or help articles in a real app.
            with ui.row().classes('hidden md:flex bg-gray-100 rounded-full px-4 py-1 items-center mr-4'):
                ui.icon('search', color='grey-5').classes('text-sm')
                ui.input(placeholder='Search...').props('borderless dense input-class="text-sm"').classes('w-32')

            # B. Dark Mode Toggle
            # NiceGUI handles the logic for you!
            dark = ui.dark_mode()
            ui.button(icon='dark_mode', on_click=dark.toggle) \
                .props('flat round text-color=grey-7 dense') \
                .tooltip('Toggle Dark Theme')

            # C. Notifications
            with ui.button(icon='notifications_none').props('flat round text-color=grey-7 dense'):
                # A red badge to show "3 new alerts"
                ui.badge('3', color='red-500').props('floating rounded size=xs')

            # D. Profile / Settings (Quick Access)
            ui.button(icon='more_vert').props('flat round text-color=grey-7 dense')