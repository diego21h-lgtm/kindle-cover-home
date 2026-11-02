import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / 'extensions/kindlecoverhome'

class StageOne(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.usb = Path(self.tmp.name) / 'USB space'
        self.docs = self.usb / 'documents'
        self.docs.mkdir(parents=True)
        self.env = dict(os.environ, KCH_USB_ROOT=str(self.usb))

    def runsh(self, script, *args, ok=True):
        result = subprocess.run(['sh', str(script), *map(str, args)], env=self.env,
                                cwd=EXT, capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def test_scan_preserves_books_and_escapes_paths(self):
        names = ['Livro de ação.MOBI', 'nested/$(touch SENTINEL).azw3',
                 'tab\tline\nslash\\.pdf', 'normal.PRC', 'notes.txt', 'old.azw']
        for name in names + ['ignored.epub', 'KUAL.azw2']:
            p = self.docs / name
            p.parent.mkdir(exist_ok=True)
            p.write_bytes(b'book fixture\x00')
        (self.docs / 'Livro de ação.jpg').write_bytes(b'candidate')
        outside = self.usb / 'outside.mobi'
        outside.write_bytes(b'outside')
        (self.docs / 'linked.mobi').symlink_to(outside)
        (self.docs / 'linked-dir').symlink_to(self.usb, target_is_directory=True)
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.docs.rglob('*') if p.is_file()}
        self.runsh(EXT / 'bin/start.sh')
        catalog = self.usb / 'kindle-cover-home-data/catalog.tsv'
        lines = catalog.read_text().splitlines()
        self.assertEqual(len(lines), 7)
        self.assertTrue(all(len(row.split('\t')) == 6 for row in lines))
        self.assertIn('tab\\tline\\nslash\\\\', catalog.read_text())
        self.assertIn(str(self.docs / 'Livro de ação.jpg'), catalog.read_text())
        self.assertNotIn('linked.mobi', catalog.read_text())
        self.assertFalse((EXT / 'SENTINEL').exists())
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in before})
        first = catalog.read_bytes()
        self.runsh(EXT / 'bin/start.sh')
        self.assertEqual(first, catalog.read_bytes())
        self.assertFalse((catalog.parent / '.lock').exists())
        self.assertIn('No framebuffer writes', (catalog.parent / 'diagnostics.txt').read_text())

    def test_demo_empty_and_lock(self):
        self.runsh(EXT / 'bin/start.sh')
        data = self.usb / 'kindle-cover-home-data'
        original = (data / 'catalog.tsv').read_bytes()
        self.runsh(EXT / 'bin/start.sh', 'demo')
        demo = (data / 'demo.tsv').read_text().splitlines()
        self.assertEqual(len(demo), 7)
        self.assertTrue(all(row.split('\t')[3].startswith('demo://') for row in demo[1:]))
        self.assertEqual(original, (data / 'catalog.tsv').read_bytes())
        (data / '.lock').mkdir()
        self.runsh(EXT / 'bin/start.sh', ok=False)
        self.assertEqual(original, (data / 'catalog.tsv').read_bytes())

    def test_install_uninstall_and_preservation(self):
        self.runsh(ROOT / 'tools/install.sh', self.usb)
        dest = self.usb / 'extensions/kindlecoverhome'
        self.runsh(ROOT / 'tools/install.sh', self.usb, ok=False)
        # Run installed payload, not just source.
        self.runsh(dest / 'bin/start.sh', 'demo')
        (dest / 'user-note.txt').write_text('preserve me')
        self.runsh(ROOT / 'tools/uninstall.sh', self.usb, ok=False)
        self.assertEqual((dest / 'user-note.txt').read_text(), 'preserve me')
        self.assertTrue((self.usb / 'kindle-cover-home-data/demo.tsv').exists())
        (dest / 'user-note.txt').unlink()
        dest.rmdir()
        self.runsh(ROOT / 'tools/install.sh', self.usb)
        self.runsh(ROOT / 'tools/uninstall.sh', self.usb)
        self.runsh(ROOT / 'tools/uninstall.sh', self.usb)
        self.assertFalse(dest.exists())

    def test_symlink_output_and_missing_documents(self):
        target = self.usb / 'keep'
        target.write_text('untouched')
        (self.usb / 'kindle-cover-home-data').symlink_to(self.usb, target_is_directory=True)
        self.runsh(EXT / 'bin/start.sh', ok=False)
        self.assertEqual(target.read_text(), 'untouched')
        (self.usb / 'kindle-cover-home-data').unlink()
        self.docs.rmdir()
        self.runsh(EXT / 'bin/start.sh', ok=False)
        self.assertFalse((self.usb / 'kindle-cover-home-data/catalog.tsv').exists())

    def test_manifest_and_shell_syntax(self):
        tree = ET.parse(EXT / 'config.xml')
        self.assertEqual(tree.findtext('menus/menu'), 'menu.json')
        menu = json.loads((EXT / 'menu.json').read_text())
        self.assertEqual(menu['items'][0]['name'], 'Iniciar Kindle Cover Home')
        for p in list(EXT.rglob('*.sh')) + list((ROOT / 'tools').glob('*.sh')):
            subprocess.run(['sh', '-n', str(p)], check=True)
            self.assertNotIn(b'\r', p.read_bytes())

if __name__ == '__main__':
    unittest.main()
