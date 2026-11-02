"""Compile a KDK-1 prototype. SDK/compiler/keystore are explicit external inputs.
No SDK classes or private keys are copied into the artifact. See kindlet/README.md.
"""
import argparse, os, subprocess, struct, hashlib
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
def build(sdk,ecj,keystore):
    out=ROOT/'build/kindlet';out.mkdir(parents=True,exist_ok=True)
    subprocess.run(['java','-jar',str(ecj),'-source','1.4','-target','1.4','-encoding','UTF-8',
                    '-cp',str(sdk)+os.pathsep+str(ROOT/'kindlet/vendor/jailbreak.jar'),'-d',str(out),*map(str,sorted((ROOT/'kindlet/src').rglob('*.java')))],check=True)
    artifact=ROOT/'documents/KindleCoverHome-0.2.1.azw2'
    manifest=('Manifest-Version: 1.0\r\nImplementation-Title: Kindle Cover Home\r\n'
              'Implementation-Version: 0.2.1\r\nImplementation-Vendor: Cover Home\r\n'
              'Main-Class: coverhome.CoverHome\r\n\r\n')
    with ZipFile(artifact,'w',ZIP_DEFLATED) as z:
        z.writestr('META-INF/MANIFEST.MF',manifest)
        for p in sorted(out.rglob('*.class')):
            assert struct.unpack('>H',p.read_bytes()[6:8])[0]==48
            z.write(p,p.relative_to(out))
        with ZipFile(ROOT/'kindlet/vendor/jailbreak.jar') as dependency:
            for name in dependency.namelist():
                if name.endswith('.class'):
                    data=dependency.read(name)
                    if struct.unpack('>H',data[6:8])[0]>48: raise ValueError('Dependency is not Java 1.4 compatible')
                    z.writestr(name,data)
    # Public test keystore supplied by the KUAL project, not a production secret.
    # Match the current KUAL source build: SHA256withRSA / SHA-256.
    for alias in ['dktest','ditest','dntest']:
        subprocess.run(['java','-m','jdk.jartool/sun.security.tools.jarsigner.Main',
                        '-keystore',str(keystore),'-storepass:env','KCH_SIGN_STOREPASS',
                        '-sigalg','SHA256withRSA','-digestalg','SHA-256',str(artifact),alias],check=True)
    print(artifact)
    print('SHA256',hashlib.sha256(artifact.read_bytes()).hexdigest())
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk',type=Path,required=True);p.add_argument('--ecj',type=Path,required=True)
    p.add_argument('--keystore',type=Path,required=True)
    args=p.parse_args();build(args.sdk,args.ecj,args.keystore)
