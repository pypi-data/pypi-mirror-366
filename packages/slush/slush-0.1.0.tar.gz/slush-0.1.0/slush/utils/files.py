from cgi import FieldStorage, MiniFieldStorage
from typing import Optional, BinaryIO

class UploadedFile:
    def __init__(self, field: FieldStorage):
        self.filename: str = field.filename
        self.content_type: str = field.type
        self.file: BinaryIO = field.file
        self.size: int = self._get_file_size()

    def _get_file_size(self) -> int:
        current_pos = self.file.tell()
        self.file.seek(0, 2)  # Seek to end
        size = self.file.tell()
        self.file.seek(current_pos)  # Return to original position
        return size

    def read(self) -> bytes:
        self.file.seek(0)
        return self.file.read()

    def save(self, path: str):
        with open(path, "wb") as f:
            f.write(self.read())