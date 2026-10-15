import os, sys, time, shutil, logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    filename=os.path.join(SCRIPT_DIR, "organizer_log.txt"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

EXTENSION_DICT = {"Documents": {".docx", ".pdf", ".html"},
                  "Presentations": {".ppt", ".pptx"},
                  "Spreadsheets": {".xlsx", ".xls", ".csv", ".tsv"},
                  "Images": {".jpg", ".jpeg", ".png", ".webp", ".gif"},
                  "Audio": {".mp3", ".ogg", ".flac", ".wav", ".opus"},
                  "Videos": {".mp4", ".webm", ".m4v", ".wmv", ".mov", ".mkv"},
                  "Code": {".py", ".ipynb", ".sql", ".java", ".tsx", ".js"},
                  "Archives": {".zip", ".rar", ".7z", ".tar"},
                  "Executables": {".exe", ".bin", ".bat", ".sh", ".msi"},
                  }
EXT_TO_CAT = {ext:cat for cat, exts in EXTENSION_DICT.items() for ext in exts}

def wait_for_size(item_path, timeout=300):
    previous_size = -1
    elapsed = 0
    
    while True:
        try:
            current_size = os.path.getsize(item_path)
        except OSError:
            return False
        
        if current_size == previous_size and current_size > 0:
            return True
        
        previous_size = current_size
        time.sleep(0.5)
        elapsed += 0.5
        
        if elapsed >= timeout:
            logging.warning("Timed out waiting for %s" % item_path)
            return False

def organize_existing(folder):
    for cat in EXTENSION_DICT.keys():
        os.makedirs(os.path.join(folder, cat), exist_ok=True)
        
    file_list = [item for item in os.listdir(folder)
                 if os.path.isfile(os.path.join(folder, item))]
        
    for item in file_list:
        file_path = os.path.join(folder, item)
        
        _, ext = os.path.splitext(item)
        cat = EXT_TO_CAT.get(ext.lower())

        if cat:
            shutil.move(file_path, os.path.join(folder, cat, item))
        else:
            logging.debug(f"Skipping uncategorized {item}")
    
def organize_folder(folder):
    folder_contents = [item for item in os.listdir(folder)
                       if os.path.isfile(os.path.join(folder, item))]
    
    for item in folder_contents:
        item_path = os.path.join(folder, item)
        _, ext = os.path.splitext(item)
        
        category = EXT_TO_CAT.get(ext.lower())
        
        if not category:
            logging.debug(f"{item} is uncategorized")
            continue
        
        if not wait_for_size(item_path):
            logging.debug(f"{item} timed out waiting — moving on")
            continue
            
        try:
            dest = os.path.join(folder, category, item)
            shutil.move(item_path, dest)
            logging.debug(f"{item} -> {category}")
        except PermissionError:
            logging.warning(f"Permission denied moving {item}—will retry on next event")
        except shutil.Error as e:
            logging.warning(f"Move failed for {item}: {e}")
            
class FileOrganizerHandler(FileSystemEventHandler):
    def __init__(self, target_folder):
        self.target_folder = target_folder
        organize_existing(self.target_folder)
    def on_created(self, event):
        if not event.is_directory:
            logging.debug(f"Created: {event.src_path}")
            organize_folder(self.target_folder)
    def on_modified(self, event):
        if not event.is_directory:
            logging.debug(f"Modified: {event.src_path}")
            organize_folder(self.target_folder)
    def on_moved(self, event):
        if not event.is_directory:
            logging.debug(f"Moved: {event.src_path}")
    def on_deleted(self, event):
        if not event.is_directory:
            logging.debug(f"Deleted: {event.src_path}")
            
if __name__ == "__main__":
    handler = FileOrganizerHandler(sys.argv[1] if len(sys.argv) > 1 else input("Folder:"))
    if not os.path.isdir(handler.target_folder):
        print(f'Error: {handler.target_folder} is not a valid directory')
        sys.exit(1)
    
    observer = Observer()
    observer.schedule(handler, path=handler.target_folder, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()