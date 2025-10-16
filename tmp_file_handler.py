import os
class TempFileHandler:
    def __init__(self, temp_file_path):
        self.temp_file_path = temp_file_path
        self.create_temp_file()

    def create_temp_file(self):
        if not os.path.exists(os.path.dirname(self.temp_file_path)):
            os.makedirs(os.path.dirname(self.temp_file_path))  # Create directory if it doesn't exist
        return self.temp_file_path

    def cleanup_temp_file(self):
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)  # Clean up temporary file
    
    def file_exists(self):
        return os.path.exists(self.temp_file_path)
    
    def get_temp_file_path(self):
        return self.temp_file_path