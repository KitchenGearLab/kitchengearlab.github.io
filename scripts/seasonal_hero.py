"""Static bilingual homepage and Ninja heroes. No browser code or dependencies."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import argparse, hashlib, html, json, re

ROOT=Path(__file__).resolve().parents[1]
TIMEZONE='America/Toronto'
PAGES={'en':'ninja/index.html','fr':'fr/ninja/index.html'}
HOME_PAGES={'en':'index.html','fr':'fr/index.html'}
ALL_PAGES=(*PAGES.values(),*HOME_PAGES.values())
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
HOME_HERO=re.compile(r'<div class="hero-media" aria-label="[^"]*">[\s\S]*?</div>')
HOME_PRELOAD=re.compile(r'^[ \t]*<link\s+rel="preload"\s+as="image"[\s\S]*?/>',re.M)
HOME_ALT_TEXT={
    'en':{'classic':'Ninja air fryer, blender and multicooker on a marble counter in a bright kitchen with plants and fresh fruit.',
          'christmas':'Ninja air fryer, blender and multicooker on a marble counter in a Christmas kitchen with a decorated tree, lights and gifts.'},
    'fr':{'classic':'Friteuse à air, mélangeur et multicuiseur Ninja sur un comptoir en marbre dans une cuisine lumineuse avec plantes et fruits frais.',
          'christmas':'Friteuse à air, mélangeur et multicuiseur Ninja sur un comptoir en marbre dans une cuisine de Noël avec sapin décoré, lumières et cadeaux.'}}

def alt_translations():
    return {alts['en'][season]:alts['fr'][season] for alts in (ALT_TEXT,HOME_ALT_TEXT) for season in ('classic','christmas')}

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

def homepage_picture(season,language):
    if season not in {'classic','christmas'} or language not in HOME_PAGES:raise ValueError('Unsupported season or language')
    base='/assets/images/hero/homepage/homepage-'+season
    def srcset(ext):return ', '.join(f'{base}-{w}.{ext} {w}w' for w in WIDTHS)
    label='Hero image' if language=='en' else 'Image principale'
    return (f'<div class="hero-media" aria-label="{label}"><picture data-seasonal-homepage-hero="{season}">'
        f'<source type="image/avif" srcset="{srcset("avif")}" sizes="{SIZES}" />'
        f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{SIZES}" />'
        f'<img src="{base}-960.jpg" srcset="{srcset("jpg")}" sizes="{SIZES}" width="1672" height="941" '
        f'alt="{html.escape(HOME_ALT_TEXT[language][season],quote=True)}" style="aspect-ratio:1600/840;object-fit:cover;object-position:center" loading="eager" decoding="async" fetchpriority="high" />'
        '</picture></div>')

def homepage_hero(source):
    matches=HOME_HERO.findall(source)
    if len(matches)!=1:raise ValueError('Expected exactly one homepage hero')
    return matches[0]

def without_homepage_hero(source):
    # Only the previous competing image preload may change outside this container.
    return HOME_PRELOAD.sub('',source.replace(homepage_hero(source),'<div class="hero-media">HOMEPAGE_HERO</div>',1))

def replace_homepage_hero(source,season,language):
    if 'id="ninja-discovery"' not in source:raise ValueError('Expected the homepage layout')
    preloads=HOME_PRELOAD.findall(source)
    if len(preloads)>1 or any('/assets/images/hero/home-hero-' not in p for p in preloads):raise ValueError('Unexpected image preload; review before replacement')
    return HOME_PRELOAD.sub('',source.replace(homepage_hero(source),homepage_picture(season,language),1))

def validate_asset_set(root,manifest_path,folder,prefix):
    manifest=json.loads((root/manifest_path).read_text(encoding='utf8'))
    if (manifest['width'],manifest['height'])!=(1672,941) or manifest['widths']!=list(WIDTHS):raise ValueError('Unexpected source geometry')
    for season in ('classic','christmas'):
        assets=manifest['seasons'][season]['assets']
        expected={f'assets/images/hero/{folder}/{prefix}-{season}-{w}.{ext}' for w in WIDTHS for ext in ('avif','webp','jpg')}
        if {a['file'] for a in assets}!=expected or len(assets)!=len(expected):raise ValueError('Incomplete asset set')
        for asset in assets:
            data=(root/asset['file']).read_bytes()
            if len(data)!=asset['bytes'] or hashlib.sha256(data).hexdigest()!=asset['sha256']:raise ValueError('Missing or changed image: '+asset['file'])
            if asset['width'] not in WIDTHS or asset['height']!=round(asset['width']*941/1672):raise ValueError('Invalid responsive dimensions')

def validate_assets(root=ROOT):
    validate_asset_set(root,'_data/seasonal-ninja-hero.json','ninja-collection','ninja-collection')
    validate_asset_set(root,'_data/seasonal-homepage-hero.json','homepage','homepage')

def update(root=ROOT,instant=None,check=False):
    season=season_for(instant);validate_assets(root)
    # Validate all assets and all four documents before writing any document.
    outputs={}
    for pages,replace in ((PAGES,replace_hero),(HOME_PAGES,replace_homepage_hero)):
        for language,path in pages.items():
            file=root/path;prior=file.read_text(encoding='utf8');current=replace(prior,season,language)
            if current!=prior:outputs[path]=current
    if not check:
        for path,current in outputs.items():(root/path).write_text(current,encoding='utf8',newline='\n')
    return {'season':season,'timezone':TIMEZONE,'changed':list(outputs)}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=update(check=args.check);print(json.dumps(result))
    if args.check and result['changed']:raise SystemExit(1)
if __name__=='__main__':main()
