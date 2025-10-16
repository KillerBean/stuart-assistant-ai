import os
class TempFileHandler:
    def __init__(self, temp_file_path):
        self.temp_file_path = temp_file_path

    def create_temp_file(self):
        dir_name = os.path.dirname(self.temp_file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)  # Create directory if it doesn't exist
        return self.temp_file_path

    def cleanup_temp_file(self):
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)  # Clean up temporary file
    
    def __enter__(self):
        self.create_temp_file()
        return self.temp_file_path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_temp_file()