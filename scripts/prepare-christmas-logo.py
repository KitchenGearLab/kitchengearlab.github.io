"""Lossless logo encodings; retain the supplied source and its full transparent frame."""
import argparse, hashlib, json, shutil, sys
from pathlib import Path
try:from PIL import Image,ImageChops,features
except ImportError:
    sys.path.insert(0,'C:/Users/1995/AppData/Local/Temp/kgl-phase1a/lib')
    from PIL import Image,ImageChops,features
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare(source):
    if not features.check('webp'):raise RuntimeError('Offline Pillow WebP support required')
    original=ROOT/'_originals/seasonal-logo/kitchengearlab-logo-christmas.png';original.parent.mkdir(parents=True,exist_ok=True)
    output=ROOT/'assets/images/brand';records=[]
    with Image.open(source) as image:
        if image.size!=(1254,1254) or image.mode!='RGBA':raise ValueError('Unexpected approved logo geometry or transparency')
        shutil.copyfile(source,original)
        for width in (64,128,192):
            resized=image.resize((width,width),Image.Resampling.LANCZOS)
            for ext in ('png','webp'):
                target=output/f'kitchengearlab-logo-christmas-{width}.{ext}'
                options={'optimize':True,'compress_level':9} if ext=='png' else {'lossless':True,'method':6,'exact':True}
                resized.save(target,**options)
                with Image.open(target) as encoded:
                    encoded.load()
                    if encoded.size!=(width,width) or ImageChops.difference(resized,encoded.convert('RGBA')).getbbox(alpha_only=False):raise ValueError('Lossless pixel verification failed')
                records.append({'file':target.relative_to(ROOT).as_posix(),'width':width,'height':width,'bytes':target.stat().st_size,'sha256':digest(target)})
    manifest={'original':original.relative_to(ROOT).as_posix(),'sourceWidth':1254,'sourceHeight':1254,'sourceBytes':original.stat().st_size,'sourceSha256':digest(original),'encoding':'Full-frame Lanczos resize; lossless PNG and lossless exact WebP; alpha retained','assets':records}
    (ROOT/'_data/seasonal-logo.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);prepare(parser.parse_args().source)
