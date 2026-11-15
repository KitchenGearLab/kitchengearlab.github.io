"""Encode supplied compositions without cropping, rearranging, recolouring or upscaling.

Pillow is an offline preparation dependency only. Scheduled switching uses stdlib.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
try:
    from PIL import Image, features
except ImportError:
    import sys
    sys.path.insert(0, 'C:/Users/1995/AppData/Local/Temp/kgl-phase1a/lib')
    from PIL import Image, features

ROOT=Path(__file__).resolve().parents[1]
WIDTHS=(480,640,960,1280,1672)
SETTINGS={'avif':{'quality':72,'speed':5,'subsampling':'4:4:4'},'webp':{'quality':88,'method':6},'jpg':{'quality':90,'subsampling':0,'optimize':True,'progressive':True}}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare(classic,christmas):
    if not features.check('avif') or not features.check('webp'):raise RuntimeError('Pillow AVIF and WebP support required for offline preparation')
    output=ROOT/'assets/images/hero/ninja-collection';output.mkdir(parents=True,exist_ok=True)
    originals=ROOT/'_originals/seasonal-ninja';originals.mkdir(parents=True,exist_ok=True)
    manifest={'width':1672,'height':941,'widths':list(WIDTHS),'encoding':SETTINGS,'seasons':{}}
    for season,source in [('classic',classic),('christmas',christmas)]:
        source=source.resolve();original=originals/f'ninja-collection-{season}.png'
        with Image.open(source) as im:
            if im.size!=(1672,941) or im.mode!='RGB':raise ValueError('Unexpected original dimensions or mode: '+str(source))
            if source!=original.resolve():shutil.copyfile(source,original)
            record={'original':original.relative_to(ROOT).as_posix(),'sha256':sha(original),'bytes':original.stat().st_size,'assets':[]}
            for width in WIDTHS:
                height=round(width*im.height/im.width)
                resized=im.copy() if width==im.width else im.resize((width,height),Image.Resampling.LANCZOS)
                for ext,options in SETTINGS.items():
                    target=output/f'ninja-collection-{season}-{width}.{ext}'
                    resized.save(target,format={'jpg':'JPEG','avif':'AVIF','webp':'WEBP'}[ext],**options)
                    with Image.open(target) as check:
                        check.load()
                        if check.size!=(width,height):raise ValueError('Invalid encoded dimensions')
                    record['assets'].append({'file':target.relative_to(ROOT).as_posix(),'width':width,'height':height,'bytes':target.stat().st_size,'sha256':sha(target)})
            manifest['seasons'][season]=record
    destination=ROOT/'_data/seasonal-ninja-hero.json'
    destination.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'originals':[{'season':s,'sha256':v['sha256']} for s,v in manifest['seasons'].items()],'assets':sum(len(v['assets']) for v in manifest['seasons'].values()),'bytesBySeason':{s:sum(a['bytes'] for a in v['assets']) for s,v in manifest['seasons'].items()},'mobile960':{s:{Path(a['file']).suffix:a['bytes'] for a in v['assets'] if a['width']==960} for s,v in manifest['seasons'].items()}},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--classic',required=True,type=Path);p.add_argument('--christmas',required=True,type=Path);a=p.parse_args();prepare(a.classic,a.christmas)
