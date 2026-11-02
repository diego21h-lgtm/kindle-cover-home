import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from library_model import Book, load_catalog, unescape
from render_library import render, prepare
from covers import discover, epub_cover
EXT = ROOT/'extensions/kindlecoverhome'

class StageTwo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.usb = Path(self.tmp.name)/'USB'
        (self.usb/'documents').mkdir(parents=True)
        self.env = dict(os.environ, KCH_USB_ROOT=str(self.usb))

    def shell(self, name, *args):
        return subprocess.run(['sh',str(EXT/'bin'/name),*args],env=self.env,capture_output=True,text=True)

    def test_tsv_escaping(self):
        self.assertEqual(unescape(r'path\tline\nend\\'), 'path\tline\nend\\')

    def test_diagnostics_and_stage1_wrapper(self):
        for action in ['diagnose','demo','scan']:
            r=self.shell('launch.sh',action)
            self.assertEqual(r.returncode,0,r.stderr)
            log=(self.usb/'coverhome/logs/session.log').read_text()
            self.assertIn('mode='+action,log)
            self.assertIn('completed mode='+action,log)
        self.assertTrue((self.usb/'kindle-cover-home-data/catalog.tsv').exists())
        self.assertTrue((self.usb/'kindle-cover-home-data/demo.tsv').exists())

    def test_navigation_reducer(self):
        def nav(n,s,a):
            r=subprocess.run(['awk','-v',f'count={n}','-v',f'selected={s}','-v',f'action={a}',
                              '-f',str(EXT/'bin/navigation.awk')],capture_output=True,text=True,check=True)
            return int(r.stdout)
        for n in [0,1,5,6,7,12,13]:
            for s in range(max(1,n)):
                for a in ['left','right','up','down','next','previous']:
                    self.assertTrue(0 <= nav(n,s,a) < max(1,n))
        self.assertEqual(nav(7,5,'next'),6)
        self.assertEqual(nav(7,6,'previous'),0)
        self.assertEqual(nav(6,1,'down'),3)
        self.assertEqual(nav(6,2,'left'),2)

    def test_renderer_demo_empty_pagination(self):
        books=load_catalog(EXT/'demo.tsv')
        self.assertEqual(len(books),6)
        im=render(books,0,0,demo=True)
        self.assertEqual((im.size,im.mode),((600,800),'L'))
        self.assertNotEqual(im.tobytes(),render(books,0,1,demo=True).tobytes())
        empty=render([],0,0)
        self.assertLess(min(empty.tobytes()),255)
        catalog=Path(self.tmp.name)/'catalog.tsv'
        header=(EXT/'demo.tsv').read_text().splitlines()[0]
        data=(EXT/'demo.tsv').read_text().splitlines()[1:]
        catalog.write_text(header+'\n'+'\n'.join(data+data[:1])+'\n')
        out=prepare(catalog,Path(self.tmp.name)/'pages')
        self.assertEqual(len(list(out.glob('*.png'))),7)
        self.assertTrue((out/'page-2-select-0.png').exists())
        with self.assertRaises(FileExistsError): prepare(catalog,out)

    def test_display_is_disabled_and_no_input_capture(self):
        r=self.shell('library.sh','demo')
        self.assertEqual(r.returncode,3)
        self.assertIn('BLOCKED', (self.usb/'coverhome/logs/session.log').read_text())
        self.assertEqual(self.shell('library.sh','right').returncode,3)
        self.assertEqual((self.usb/'coverhome/ui-state').read_text(),'demo 1\n')
        self.assertEqual(self.shell('library.sh','select').returncode,0)
        self.assertIn('opening intentionally unavailable',(self.usb/'coverhome/logs/session.log').read_text())
        self.assertEqual(self.shell('library.sh','back').returncode,0)
        self.assertFalse((self.usb/'coverhome/ui-state').exists())
        self.assertFalse((self.usb/'coverhome/.ui-lock').exists())

    def test_cover_sidecar_epub_and_traversal(self):
        raw=io.BytesIO();Image.new('RGB',(20,30),'gray').save(raw,format='PNG')
        (self.usb/'documents/book.png').write_bytes(raw.getvalue())
        b=Book('Title','Author','mobi','/mnt/us/documents/book.mobi',
               '/mnt/us/documents/book.png','filename')
        self.assertEqual(discover(b,self.usb).mode,'L')
        b=Book('t','a','mobi','demo://x','/mnt/us/../../etc/passwd','filename')
        self.assertIsNone(discover(b,self.usb))
        epub=self.usb/'documents/book.epub'
        with zipfile.ZipFile(epub,'w') as z:
            z.writestr('META-INF/container.xml','<container xmlns="c"><rootfile full-path="OPS/book.opf"/></container>')
            z.writestr('OPS/book.opf','<package xmlns="o"><manifest><item id="cover" href="cover.png" properties="cover-image"/></manifest></package>')
            z.writestr('OPS/cover.png',raw.getvalue())
        self.assertEqual(epub_cover(epub).size,(20,30))
        epub.write_bytes(b'invalid zip')
        self.assertIsNone(epub_cover(epub))

    def test_logs_symlink_and_invalid_state(self):
        (self.usb/'coverhome').mkdir()
        (self.usb/'coverhome/logs').symlink_to(self.usb,target_is_directory=True)
        self.assertNotEqual(self.shell('launch.sh','diagnose').returncode,0)
        (self.usb/'coverhome/logs').unlink()
        (self.usb/'coverhome/ui-state').write_text('demo $(touch BAD)\n')
        self.assertNotEqual(self.shell('library.sh','show').returncode,0)
        self.assertFalse((ROOT/'BAD').exists())

if __name__=='__main__': unittest.main()
