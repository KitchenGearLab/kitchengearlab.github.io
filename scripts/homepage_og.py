"""Bounded, idempotent update of the two homepage social image references.

JPEG is the primary social asset; WebP is an equivalent optimized derivative.
Neither asset participates in hero rendering or seasonal switching.
"""
from pathlib import Path
import argparse,json,re

ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://kitchengearlab.github.io'
OLD_URL=ORIGIN+'/assets/images/og/home-og-1200x630.webp'
IMAGE_PATH='assets/images/og/home-og-v2-1200x630.jpg'
WEBP_PATH='assets/images/og/home-og-v2-1200x630.webp'
IMAGE_URL=ORIGIN+'/'+IMAGE_PATH

def upgrade_homepage_metadata(source):
    """Change only known image fields, retaining all bilingual editorial metadata."""
    def set_content(text,key,attribute,value,allowed):
        pattern=re.compile(r'(<meta '+attribute+'="'+re.escape(key)+r'" content=")([^"]+)(" />)')
        matches=list(pattern.finditer(text))
        if len(matches)!=1 or matches[0][2] not in allowed:
            raise ValueError('Ambiguous or unknown homepage metadata: '+key)
        return pattern.sub(lambda m:m[1]+value+m[3],text,count=1)
    source=set_content(source,'og:image','property',IMAGE_URL,{OLD_URL,IMAGE_URL})
    source=set_content(source,'og:image:type','property','image/jpeg',{'image/webp','image/jpeg'})
    source=set_content(source,'twitter:image','name',IMAGE_URL,{OLD_URL,IMAGE_URL})
    if 'property="og:image:secure_url"' in source:
        source=set_content(source,'og:image:secure_url','property',IMAGE_URL,{OLD_URL,IMAGE_URL})
    else:
        tag='<meta property="og:image" content="'+IMAGE_URL+'" />'
        source=source.replace(tag,tag+'\n  <meta property="og:image:secure_url" content="'+IMAGE_URL+'" />',1)
    return source

def update(check=False):
    outputs={}
    for path in ['index.html','fr/index.html']:
        before=(ROOT/path).read_text(encoding='utf8');after=upgrade_homepage_metadata(before)
        if before!=after:outputs[path]=after
    if not check:
        for path,after in outputs.items():(ROOT/path).write_text(after,encoding='utf8',newline='\n')
    return {'pages':2,'changed':list(outputs),'image':IMAGE_URL}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=update(args.check);print(json.dumps(result));raise SystemExit(bool(args.check and result['changed']))
