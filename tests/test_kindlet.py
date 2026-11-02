import io
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
from zipfile import ZipFile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]

def mobi_fixture(image,encrypted=False):
    author=b'Autor real';title=b'Titulo real'
    exth=b'EXTH'+struct.pack('>II',12+8+len(author)+12,2)
    exth+=struct.pack('>II',100,8+len(author))+author+struct.pack('>III',201,12,0)
    rec=bytearray(16+232)
    struct.pack_into('>H',rec,12,2 if encrypted else 0)
    rec[16:20]=b'MOBI';struct.pack_into('>I',rec,20,232)
    struct.pack_into('>I',rec,28,65001)
    struct.pack_into('>II',rec,84,len(rec)+len(exth),len(title))
    struct.pack_into('>I',rec,108,1);struct.pack_into('>I',rec,128,64)
    rec+=exth+title
    header=bytearray(94);header[60:68]=b'BOOKMOBI';struct.pack_into('>H',header,76,2)
    struct.pack_into('>I',header,78,94);struct.pack_into('>I',header,86,94+len(rec))
    return header+rec+image

class KindletTest(unittest.TestCase):
    def test_legacy_artifact_contents(self):
        with ZipFile(ROOT/'documents/KindleCoverHome-0.2.1.azw2') as z:
            self.assertEqual(z.testzip(),None)
            classes=[n for n in z.namelist() if n.endswith('.class')]
            self.assertIn('coverhome/CoverHome.class',classes)
            self.assertFalse(any(n.startswith('com/amazon/') for n in classes))
            self.assertTrue(all(struct.unpack('>H',z.read(n)[6:8])[0]<=48 for n in classes))
            for alias in ['DKTEST','DITEST','DNTEST']:
                self.assertIn('META-INF/'+alias+'.RSA',z.namelist())
            self.assertFalse(any(n.endswith('.keystore') for n in z.namelist()))

    @unittest.skipUnless(shutil.which('java'),'Java compiler/runtime unavailable')
    def test_native_core(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);docs=base/'documents';docs.mkdir()
            image=io.BytesIO();Image.new('L',(20,30),128).save(image,format='PNG')
            (docs/'real.mobi').write_bytes(mobi_fixture(image.getvalue()))
            (docs/'notes.txt').write_text('read only')
            (docs/'sample.epub').write_bytes(b'not an EPUB; should use placeholder')
            (docs/'ignored.azw2').write_bytes(b'not a book')
            encrypted=base/'encrypted.azw';encrypted.write_bytes(mobi_fixture(image.getvalue(),True))
            invalid=base/'invalid.mobi';invalid.write_bytes(b'invalid')
            before={p:p.read_bytes() for p in docs.iterdir()}
            src=ROOT/'kindlet/src/coverhome'
            files=[src/(name+'.java') for name in ['Book','Catalog','Mobi','Navigation','Renderer']]
            subprocess.run(['java','-m','jdk.compiler/com.sun.tools.javac.Main','-d',str(base/'classes'),*map(str,files),str(ROOT/'kindlet/test/coverhome/CoreTest.java')],check=True,capture_output=True)
            preview=ROOT/'build/native-preview.png';preview.parent.mkdir(exist_ok=True)
            r=subprocess.run(['java','-Djava.awt.headless=true','-cp',str(base/'classes'),'coverhome.CoreTest',str(docs),str(encrypted),str(invalid),str(preview)],check=True,capture_output=True,text=True)
            self.assertIn('JAVA_CORE_OK',r.stdout)
            self.assertEqual(before,{p:p.read_bytes() for p in before})
