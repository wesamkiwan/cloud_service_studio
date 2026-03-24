import nbformat
import os

class NotebookBackend:
    def __init__(self):
        self.notebook = None
        self.current_filepath = None
        
    def new_notebook(self):
        self.notebook = nbformat.v4.new_notebook()
        self.current_filepath = None
        return self.notebook
        
    def load_notebook(self, filepath: str):
        if not os.path.exists(filepath):
            return False, f"File not found: {filepath}", None
            
        try:
            self.notebook = nbformat.read(filepath, as_version=4)
            self.current_filepath = filepath
            return True, "Loaded successfully", self.notebook
        except Exception as e:
            return False, f"Failed to load notebook: {str(e)}", None
            
    def save_notebook(self, filepath: str = None):
        if not self.notebook:
            return False, "No notebook open to save"
            
        save_path = filepath or self.current_filepath
        if not save_path:
            return False, "Save path required"
            
        try:
            nbformat.write(self.notebook, save_path)
            self.current_filepath = save_path
            return True, "Saved successfully"
        except Exception as e:
            return False, f"Failed to save notebook: {str(e)}"
