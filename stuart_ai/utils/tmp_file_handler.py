import os

class TempFileHandler:
    def __init__(self, temp_file_path):
        self.temp_file_path = temp_file_path

    def create_temp_file(self):
        dir_name = os.path.dirname(self.temp_file_path)
        if dir_name and not os.path.exists(dir_name):
            # mode=0o700: only the owner can read/write/traverse this directory.
            # Other users on the same system cannot access captured audio files.
            os.makedirs(dir_name, mode=0o700)
        # Restrict the file itself to owner-only read/write (no world-readable audio)
        fd = os.open(self.temp_file_path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
        os.close(fd)
        return self.temp_file_path

    def cleanup_temp_file(self):
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)

    def __enter__(self):
        self.create_temp_file()
        return self.temp_file_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_temp_file()
