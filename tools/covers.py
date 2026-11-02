"""Host-only cover discovery. Never modifies books or reads Amazon databases."""
from io import BytesIO
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, BadZipFile
import xml.etree.ElementTree as ET
from PIL import Image, UnidentifiedImageError

MAX_BYTES = 4 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 12_000_000

def image_bytes(data):
    if len(data) > MAX_BYTES:
        return None
    try:
        with Image.open(BytesIO(data)) as im:
            im.load()
            return im.convert('L')
    except (OSError, ValueError, Image.DecompressionBombError):
        return None

def member(z, name):
    info = z.getinfo(name)
    if info.file_size > MAX_BYTES:
        raise ValueError('Oversized EPUB member')
    return z.read(info)

def epub_cover(path):
    # ZIP members are read in memory; no extraction or traversal to disk.
    try:
        with ZipFile(path) as z:
            container = ET.fromstring(member(z, 'META-INF/container.xml'))
            opf = next(e.attrib['full-path'] for e in container.iter() if e.tag.endswith('}rootfile'))
            package = ET.fromstring(member(z, opf))
            items = [e for e in package.iter() if e.tag.endswith('}item')]
            legacy_id = next((e.get('content') for e in package.iter()
                              if e.tag.endswith('}meta') and e.get('name') == 'cover'), None)
            cover = next((e for e in items if 'cover-image' in e.get('properties', '').split()
                          or (legacy_id is not None and e.get('id') == legacy_id)), None)
            if cover is None:
                return None
            import posixpath
            name = posixpath.normpath(str(PurePosixPath(opf).parent / cover.attrib['href']))
            return image_bytes(member(z, name))
    except (OSError, BadZipFile, KeyError, ValueError, ET.ParseError, StopIteration):
        return None

def safe_file(path, root):
    p = Path(path)
    try:
        resolved = p.resolve(strict=True)
        if resolved.is_relative_to(root.resolve()) and resolved.is_file() and not p.is_symlink():
            return resolved
    except (OSError, ValueError):
        pass
    return None

def discover(book, usb):
    # Explicit remapping of /mnt/us to a mounted USB root. No arbitrary host paths.
    def mapped(s):
        if not s.startswith('/mnt/us/'):
            return None
        return safe_file(usb / s[len('/mnt/us/'):], usb)
    if book.cover:
        p = mapped(book.cover)
        if p and p.stat().st_size <= MAX_BYTES:
            image = image_bytes(p.read_bytes())
            if image is not None:
                return image
    p = mapped(book.path)
    if p and book.format.lower() == 'epub':
        return epub_cover(p)
    # MOBI/AZW embedded extraction not implemented: sidecars or placeholders only.
    return None
