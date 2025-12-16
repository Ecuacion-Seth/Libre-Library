import uuid
import json
from pathlib import Path
from nicegui import ui, app, events
from components.header import header
from components.sidebar import sidebar

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
BOOKS_DIR = BASE_DIR / 'data' / 'books'
BOOKS_DIR.mkdir(parents=True, exist_ok=True)

@ui.page('/upload')
def upload_page():
    # Security: Require Login
    if not app.storage.user.get('authenticated'):
        return ui.navigate.to('/login')

    nav = sidebar()
    header(nav)

    # --- STATE ---
    state = {
        'title': '',
        'author': '',
        'category': 'Uncategorized',
        'description': '',
        # We store the raw bytes and filename strings immediately
        'cover_data': None,   
        'cover_name': None,
        'content_data': None, 
        'content_name': None,
        'uploading': False
    }

    # --- HELPERS ---
    def handle_cover_upload(e: events.UploadEventArguments):
        # 1. Capture data immediately
        state['cover_data'] = e.content.read()
        # 2. Capture name safely
        state['cover_name'] = e.name 
        ui.notify(f'Cover ready: {e.name}', color='positive')
        
    def handle_content_upload(e: events.UploadEventArguments):
            # DEBUG: Print to terminal to prove this function ran
            print(f"DEBUG: Handler started for {e.name}") 
            
            state['content_data'] = e.content.read()
            state['content_name'] = e.name
            
            print(f"DEBUG: Data saved. Size: {len(state['content_data'])} bytes")
            ui.notify(f'File ready: {e.name}', color='positive')

    def save_resource():
        # Validation
        if not state['title'] or not state['author']:
            ui.notify('Title and Author are required', color='warning')
            return
        
        if not state['content_data']:
            ui.notify('Please upload a document file', color='warning')
            return

        state['uploading'] = True
        loading_dialog.open()

        try:
            # 1. Generate Unique ID & Folder
            book_id = str(uuid.uuid4())
            book_dir = BOOKS_DIR / book_id
            book_dir.mkdir(parents=True, exist_ok=True)

            # 2. Save Content File (Using the string we saved earlier)
            content_filename = state['content_name'] 
            content_path = book_dir / content_filename
            
            with open(content_path, 'wb') as f:
                f.write(state['content_data'])

            # 3. Save Cover Image (If exists)
            cover_filename = None
            if state['cover_data']:
                ext = Path(state['cover_name']).suffix
                cover_filename = f"cover{ext}"
                with open(book_dir / cover_filename, 'wb') as f:
                    f.write(state['cover_data'])

            # 4. Generate Metadata
            metadata = {
                "id": book_id,
                "title": state['title'],
                "authors": [{"name": state['author']}],
                "subjects": [state['category']],
                "summaries": [state['description'] if state['description'] else "No description provided."],
                "languages": ["en"],
                "download_count": 0,
                "formats": {
                    "application/octet-stream": content_filename, 
                }
            }
            
            if cover_filename:
                metadata["formats"]["image/jpeg"] = f"/covers/{book_id}/{cover_filename}"

            # 5. Write Metadata File
            with open(book_dir / 'metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)

            loading_dialog.close()
            ui.notify('Upload successful!', color='green')
            ui.navigate.to(f'/book/{book_id}')

        except Exception as e:
            loading_dialog.close()
            # This will now give a cleaner error if something else goes wrong
            ui.notify(f'Error saving file: {str(e)}', color='negative')
            state['uploading'] = False

    # --- UI LAYOUT ---
    with ui.column().classes('w-full min-h-screen bg-gray-50 p-4 md:p-8 items-center'):
        
        with ui.card().classes('w-full max-w-3xl p-8 shadow-lg'):
            ui.label('Upload Resource').classes('text-2xl font-bold text-gray-800 mb-6')

            with ui.column().classes('w-full gap-4'):
                
                # Metadata Inputs
                ui.input('Resource Title').bind_value(state, 'title').classes('w-full')
                ui.input('Author Name').bind_value(state, 'author').classes('w-full')
                
                categories = ['Uncategorized', 'Computer Science', 'Mathematics', 'Science', 'History', 'Literature', 'Other']
                ui.select(categories, label='Category', value='Uncategorized').bind_value(state, 'category').classes('w-full')
                
                ui.textarea('Description').bind_value(state, 'description').classes('w-full').props('rows=3')

                ui.separator().classes('my-4')

                # File Uploaders
                with ui.row().classes('w-full gap-8 wrap'):
                    
                    # 1. Main Document Upload
                    with ui.column().classes('flex-1 min-w-[250px]'):
                        ui.label('Document File (PDF, DOCX, EPUB)').classes('font-bold text-gray-600')
                        # auto_upload=True ensures we catch the file immediately
                        ui.upload(on_upload=handle_content_upload, auto_upload=True, max_files=1) \
                            .props('accept=".pdf,.epub,.docx,.ppt,.pptx,.txt" flat bordered') \
                            .classes('w-full')
                        ui.label('Required').classes('text-xs text-red-400')

                    # 2. Cover Image Upload
                    with ui.column().classes('flex-1 min-w-[250px]'):
                        ui.label('Cover Image').classes('font-bold text-gray-600')
                        ui.upload(on_upload=handle_cover_upload, auto_upload=True, max_files=1) \
                            .props('accept="image/*" flat bordered') \
                            .classes('w-full')
                        ui.label('Optional').classes('text-xs text-gray-400')

                # Submit Button
                ui.separator().classes('my-4')
                ui.button('Save to Library', on_click=save_resource) \
                    .classes('w-full py-3 text-lg font-bold') \
                    .props('color=indigo-600')

    # Loading Dialog
    with ui.dialog() as loading_dialog, ui.card().classes('items-center p-8'):
        ui.spinner(size='lg')
        ui.label('Processing upload...').classes('mt-4 text-gray-600')