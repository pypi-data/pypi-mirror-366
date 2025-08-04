from abc import ABC, abstractmethod
from ftplib import FTP
import logging
from typing import Callable, Optional, Dict
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AbstractWriter(ABC):

    def __init__(self):
        self.location = None

    @abstractmethod
    def write(self, data: bytes):
        raise NotImplementedError
    
    def set_location(self, location: str):
        self.location = location


class WriterToFile(AbstractWriter):

    def __init__(self, output_dir: str = '.'):
        super().__init__()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def write(self, data: bytes):
        if self.location is None:
            raise ValueError("Set location before writing")
        with open(os.path.join(self.output_dir, self.location), 'wb') as fh:
            fh.write(data)


class WriterToMemory(AbstractWriter):

    def __init__(self):
        super().__init__()
        self.memory_buffer: Dict[str, bytearray] = {}
    
    def write(self, data: bytes):
        if self.location is None:
            raise ValueError("Set location before writing")
        self.memory_buffer[self.location] = bytearray(data)

    def __repr__(self) -> str:
        if not self.memory_buffer:
            return "WriterToMemory(empty)"
        
        # Calculate table formatting
        max_filename_len = max(len(filename) for filename in self.memory_buffer.keys())
        max_filename_len = max(max_filename_len, len("Filename"))
        
        # Create table header
        header = f"{'Filename':<{max_filename_len}} | {'Size (MB)':>10}"
        separator = "-" * (max_filename_len + 3 + 10)
        
        # Create table rows
        rows = []
        total_size_mb = 0
        for filename, data in self.memory_buffer.items():
            size_mb = len(data) / (1024 * 1024)
            total_size_mb += size_mb
            rows.append(f"{filename:<{max_filename_len}} | {size_mb:>10.2f}")
        
        # Add total row
        total_row = f"{'TOTAL':<{max_filename_len}} | {total_size_mb:>10.2f}"
        
        # Combine all parts
        result = f"WriterToMemory:\n{header}\n{separator}\n"
        result += "\n".join(rows)
        result += f"\n{separator}\n{total_row}"
        
        return result


class WriterToS3(AbstractWriter):

    def __init__(self, bucket: str, s3_client):
        super().__init__()
        self.bucket = bucket
        self.s3_client = s3_client

    def write(self, data: bytes):
        if self.location is None:
            raise ValueError("Set location before writing")
        self.s3_client.put_object(Bucket=self.bucket, Key=self.location, Body=data)


class ExtractNCBITaxonomy:

    NCBI_FTP_URL = 'ftp.ncbi.nlm.nih.gov'

    def __init__(self, fn_copy: AbstractWriter = None):
        self.files_to_copy = {
            'taxdmp.zip',
            'taxdmp.zip.md5',
            'taxdump_readme.txt',
            'taxcat.zip',
            'taxcat.zip.md5',
            'taxcat_readme.txt',
        }
        self.fn_copy = fn_copy
        if self.fn_copy is None:
            self.fn_copy = WriterToMemory()

    def file_writer(self, filename: str):
        def write(data: bytes):
            with open(filename, 'ab') as f:
                f.write(data)
        return write

    def memory_loader(self, filename: str):
        def load(data: bytes):
            if filename not in self.memory_buffer:
                self.memory_buffer[filename] = bytearray()
            self.memory_buffer[filename].extend(data)
        return load

    def extract(self):
        ftp = FTP(ExtractNCBITaxonomy.NCBI_FTP_URL)
        ftp.login()
        ftp.cwd('/pub/taxonomy/')
        with ftp:
            files = ftp.nlst()
            for f in files:
                if f in self.files_to_copy:
                    self.fn_copy.set_location(f)
                    ftp.retrbinary(f"RETR {f}", self.fn_copy.write)
        ftp.close()
