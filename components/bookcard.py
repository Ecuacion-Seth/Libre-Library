from nicegui import ui
from typing import Optional, Dict, Any
import os


def book_card(book_data: Dict[str, Any], on_click=None):
    """
    Render a book card using Project Gutenberg metadata format.
    
    Args:
        book_data: Dictionary containing book metadata
        on_click: Callback function when card is clicked
    """
    # Extract book information with fallbacks
    title = book_data.get('title', 'Untitled')
    authors = book_data.get('authors', [{'name': 'Unknown'}])
    author_names = ', '.join(author.get('name', 'Unknown') for author in authors)
    
    # Get cover image URL from formats, or use a placeholder
    formats = book_data.get('formats', {})
    cover_url = formats.get('image/jpeg', 'https://via.placeholder.com/150x200?text=No+Cover')
    
    # Get description from summaries or use a default
    description = book_data.get('summaries', ['No description available.'])[0]
    if len(description) > 100:  # Truncate long descriptions
        description = description[:97] + '...'
    
    # Get language and format info
    languages = ', '.join(book_data.get('languages', ['en']))
    
    with ui.card().props('outlined').classes('w-64 h-96 m-2 overflow-hidden flex flex-col cursor-pointer hover:shadow-lg transition-shadow') as card:
        if on_click:
            card.on('click', on_click)
            
        # Cover image with fallback
        ui.image(cover_url).classes('w-full h-48 object-cover')
        
        # Book info
        with ui.column().classes('p-2 flex-1'):
            ui.label(title).classes('font-bold text-lg line-clamp-2')
            ui.label(f'by {author_names}').classes('text-sm text-gray-600')
            
            # Additional metadata
            with ui.column().classes('mt-2 text-xs text-gray-500'):
                ui.label(f'Language: {languages}')
                if 'subjects' in book_data:
                    subjects = ', '.join(book_data['subjects'][:2])
                    ui.label(f'Subjects: {subjects}...').classes('line-clamp-1')
            
            # Description
            ui.separator().classes('my-1')
            ui.label(description).classes('text-xs text-gray-700 line-clamp-3')
            
        # Footer with action buttons
        with ui.row().classes('p-2 bg-gray-50 w-full justify-end'):
            ui.button(icon='menu_book', on_click=on_click).props('flat dense')