"""Desktop tests of real menu strings; these do not emulate the KUAL Java parser."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
EXT=ROOT/'extensions/kindlecoverhome'

class Kual021(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.usb=Path(self.tmp.name)/'usb'
        (self.usb/'documents').mkdir(parents=True)
        subprocess.run(['sh',str(ROOT/'tools/install.sh'),str(self.usb)],check=True,capture_output=True)
        self.ext=self.usb/'extensions/kindlecoverhome'
        self.env=dict(os.environ,KCH_USB_ROOT=str(self.usb))
        self.menu=json.loads((self.ext/'menu.json').read_text())['items']

    def invoke(self,item):
        # KUAL commonly builds a shell command. Validate that contract explicitly,
        # without claiming to reproduce the device's parser/lifecycle.
        params=item['params'].replace('/mnt/us',str(self.usb))
        return subprocess.run(item['action']+' '+params,shell=True,cwd='/',env=self.env,
                              capture_output=True,text=True)

    def entry(self,name):
        return next(i for i in self.menu if name in i['name'])

    def test_minimal_inline_without_extension(self):
        entry=self.entry('Teste 0')
        # It needs no extension file, logging directory, PATH tools or executable bit.
        for p in (self.ext/'bin').glob('*.sh'): p.unlink()
        self.env['PATH']='/not-available'
        result=self.invoke(entry)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.usb/'coverhome-kual-dispatch.txt').read_text(),'KUAL_DISPATCH_0.2.1\n')
        self.assertFalse((self.usb/'coverhome').exists())

    def test_basic_builtins_only(self):
        # Fixed /mnt/us destination is remapped ONLY in this disposable test copy.
        p=self.ext/'bin/kual-basic.sh'
        p.write_text(p.read_text().replace('/mnt/us',str(self.usb)))
        self.env['PATH']='/not-available'
        result=self.invoke(self.entry('Teste basico'))
        self.assertEqual(result.returncode,0,result.stderr)
        text=(self.usb/'coverhome-kual-test.txt').read_text()
        self.assertIn('BASIC_SCRIPT_ENTERED',text)
        self.assertIn('BASIC_SCRIPT_COMPLETED',text)
        self.assertFalse((self.usb/'coverhome').exists())

    def test_progressive_and_main_from_root(self):
        for name in ['Teste progressivo','Iniciar Kindle','Gerar catalogo','Diagnostico 0.2.1']:
            result=self.invoke(self.entry(name))
            self.assertEqual(result.returncode,0,result.stderr)
            trace=(self.usb/'coverhome-bootstrap.log').read_text()
            for marker in ['BOOTSTRAP_ENTERED','SHELL_STARTED','CWD_READY','LOG_WRITE_OK','BOOTSTRAP_EXIT=0']:
                self.assertIn(marker,trace)
        log=(self.usb/'coverhome/logs/session.log').read_text()
        self.assertIn('0.2.1',log)
        self.assertIn('completed mode=diagnose',log)
        self.assertTrue((self.usb/'kindle-cover-home-data/catalog.tsv').exists())
        self.assertTrue((self.usb/'kindle-cover-home-data/demo.tsv').exists())

    def test_directory_failure_before_application_logging(self):
        (self.usb/'coverhome').write_text('user file: do not replace')
        result=self.invoke(self.entry('Teste progressivo'))
        self.assertNotEqual(result.returncode,0)
        trace=(self.usb/'coverhome-bootstrap.log').read_text()
        self.assertIn('LOG_DIRECTORY_FAILED',trace)
        self.assertIn('BOOTSTRAP_EXIT=1',trace)
        self.assertEqual((self.usb/'coverhome').read_text(),'user file: do not replace')

    def test_missing_path_and_syntax_failure(self):
        p=self.ext/'bin/launch.sh'
        original=p.read_text();p.unlink()
        result=self.invoke(self.entry('Iniciar Kindle'))
        self.assertNotEqual(result.returncode,0)
        self.assertIn('SCRIPT_UNREADABLE',(self.usb/'coverhome-bootstrap.log').read_text())
        p.write_text('if then\n')
        result=self.invoke(self.entry('Iniciar Kindle'))
        self.assertNotEqual(result.returncode,0)
        self.assertIn('SHELL_SYNTAX_FAILED',(self.usb/'coverhome-bootstrap.log').read_text())
        p.write_text(original)

    def test_child_status_is_preserved(self):
        (self.ext/'bin/launch.sh').write_text('exit 23\n')
        result=self.invoke(self.entry('Iniciar Kindle'))
        self.assertEqual(result.returncode,23)
        trace=(self.usb/'coverhome-bootstrap.log').read_text()
        self.assertIn('CHILD_EXIT=23',trace)
        self.assertIn('BOOTSTRAP_EXIT=23',trace)

    def test_all_actions_explicit(self):
        def leaves(items):
            for item in items:
                if 'items' in item: yield from leaves(item['items'])
                else: yield item
        for entry in leaves(self.menu):
            self.assertEqual(entry['action'],'/bin/sh')
            self.assertIs(entry['exitmenu'],False)
            self.assertIn('params',entry)
        library=self.entry('Biblioteca visual')['items']
        result=self.invoke(library[0])
        self.assertEqual(result.returncode,3) # eips remains disabled
        self.assertIn('CHILD_EXIT=3',(self.usb/'coverhome-bootstrap.log').read_text())
        self.assertFalse((self.usb/'coverhome/enable-eips').exists())

if __name__=='__main__': unittest.main()
