"""Read stage-1 TSV without executing paths. Host-only module."""
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass(frozen=True)
class Book:
    title: str
    author: str
    format: str
    path: str
    cover: str
    source: str

def unescape(text):
    return re.sub(r'\\([\\trn])', lambda m: {'\\': '\\', 't': '\t', 'r': '\r', 'n': '\n'}[m[1]], text)

def load_catalog(path):
    with Path(path).open(encoding='utf-8') as f:
        header = f.readline().rstrip('\r\n').split('\t')
        if header != ['title', 'author', 'format', 'path', 'cover_candidate', 'metadata_source']:
            raise ValueError('Not a stage-1 catalog')
        books = []
        for line in f:
            fields = line.rstrip('\n').split('\t')
            if len(fields) != 6:
                raise ValueError('Malformed TSV')
            books.append(Book(*(unescape(x) for x in fields)))
        if len(books) > 600:
            raise ValueError('At most 600 books per prepared library')
        return books
