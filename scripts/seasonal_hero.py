"""Static Ninja collection hero selection. No network, browser code or dependencies."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import argparse, hashlib, html, json, re

ROOT=Path(__file__).resolve().parents[1]
TIMEZONE='America/Toronto'
PAGES={'en':'ninja/index.html','fr':'fr/ninja/index.html'}
WIDTHS=(480,640,960,1280,1672)
SIZES='(min-width: 1120px) 442px, (min-width: 1024px) calc(42.5vw - 34px), (min-width: 768px) calc(100vw - 48px), calc(100vw - 32px)'
ALT_TEXT={
    'en':{
        'classic':'Five Ninja appliances: a frozen-drink maker, blender, glass air fryer, espresso machine and frozen-dessert maker on a peach backdrop.',
        'christmas':'Five Ninja appliances with Christmas greenery, warm lights and gifts: a frozen-drink maker, blender, glass air fryer, espresso machine and frozen-dessert maker.'},
    'fr':{
        'classic':'Cinq appareils Ninja sur fond pêche : machine à boissons glacées, mélangeur, friteuse à air en verre, machine à espresso et appareil à desserts glacés.',
        'christmas':'Cinq appareils Ninja avec branches de Noël, lumières chaleureuses et cadeaux : machine à boissons glacées, mélangeur, friteuse à air en verre, machine à espresso et appareil à desserts glacés.'}}
HERO=re.compile(r'<figure class="hero-media">[\s\S]*?</figure>')

def season_for(instant=None):
    """Use execution time, never the scheduled event's stale date or previous state."""
    instant=instant or datetime.now(ZoneInfo(TIMEZONE))
    if instant.tzinfo is None:raise ValueError('A timezone-aware instant is required')
    date=instant.astimezone(ZoneInfo(TIMEZONE)).date()
    return 'christmas' if (11,1)<=(date.month,date.day)<=(12,26) else 'classic'

def picture(season,language):
    if season not in {'classic','christmas'} or language not in PAGES:raise ValueError('Unsupported season or language')
    base='/assets/images/hero/ninja-collection/ninja-collection-'+season
    def srcset(ext):return ', '.join(f'{base}-{w}.{ext} {w}w' for w in WIDTHS)
    return (f'<figure class="hero-media"><picture data-seasonal-ninja-hero="{season}">'
        f'<source type="image/avif" srcset="{srcset("avif")}" sizes="{SIZES}" />'
        f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{SIZES}" />'
        f'<img src="{base}-960.jpg" srcset="{srcset("jpg")}" sizes="{SIZES}" width="1672" height="941" '
        f'alt="{html.escape(ALT_TEXT[language][season],quote=True)}" style="aspect-ratio:1672/941;object-fit:contain" loading="eager" decoding="async" fetchpriority="high" />'
        '</picture></figure>')

def hero(source):
    matches=HERO.findall(source)
    if len(matches)!=1:raise ValueError('Expected exactly one collection hero; refusing an ambiguous replacement')
    return matches[0]

def replace_hero(source,season,language):
    if 'collection-hero' not in source:raise ValueError('Expected the Ninja collection layout')
    prior=hero(source)
    return source.replace(prior,picture(season,language),1)

def without_hero(source):
    return source.replace(hero(source),'<figure class="hero-media">COLLECTION_HERO</figure>',1)

def validate_assets(root=ROOT):
    manifest=json.loads((root/'_data/seasonal-ninja-hero.json').read_text(encoding='utf8'))
    if (manifest['width'],manifest['height'])!=(1672,941) or manifest['widths']!=list(WIDTHS):raise ValueError('Unexpected source geometry')
    for season in ('classic','christmas'):
        assets=manifest['seasons'][season]['assets']
        expected={f'assets/images/hero/ninja-collection/ninja-collection-{season}-{w}.{ext}' for w in WIDTHS for ext in ('avif','webp','jpg')}
        if {a['file'] for a in assets}!=expected or len(assets)!=len(expected):raise ValueError('Incomplete asset set')
        for asset in assets:
            data=(root/asset['file']).read_bytes()
            if len(data)!=asset['bytes'] or hashlib.sha256(data).hexdigest()!=asset['sha256']:raise ValueError('Missing or changed image: '+asset['file'])
            if asset['width'] not in WIDTHS or asset['height']!=round(asset['width']*941/1672):raise ValueError('Invalid responsive dimensions')

def update(root=ROOT,instant=None,check=False):
    season=season_for(instant);validate_assets(root)
    # Compute and validate both documents before writing either one.
    outputs={}
    for language,path in PAGES.items():
        file=root/path;prior=file.read_text(encoding='utf8');current=replace_hero(prior,season,language)
        if current!=prior:outputs[path]=current
    if not check:
        for path,current in outputs.items():(root/path).write_text(current,encoding='utf8',newline='\n')
    return {'season':season,'timezone':TIMEZONE,'changed':list(outputs)}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=update(check=args.check);print(json.dumps(result))
    if args.check and result['changed']:raise SystemExit(1)
if __name__=='__main__':main()
