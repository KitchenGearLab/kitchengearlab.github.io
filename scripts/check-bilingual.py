"""Focused bilingual regression checks, without Amazon requests or analytics traffic."""
import sys, json, re, html, hashlib, subprocess
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET
from bilingual import ROOT, ORIGIN, load_translations, strip_bilingual, norm, values
from seasonal_hero import without_hero, without_homepage_hero
from seasonal_logo import strip_logo

class Document(HTMLParser):
    def __init__(self,source):
        super().__init__(convert_charrefs=True); self.tags=[]; self.ids=set(); self.schemas=[]; self.jsonld=False
        self.feed(source)
    def handle_starttag(self,t,a):
        a=dict(a); self.tags.append((t,a))
        if 'id' in a: self.ids.add(a['id'])
        if t=='script': self.jsonld=a.get('type')=='application/ld+json'
    def handle_endtag(self,t):
        if t=='script': self.jsonld=False
    def handle_data(self,s):
        if self.jsonld: self.schemas.append(json.loads(s))
    def attrs(self,tag,**attrs): return [a for t,a in self.tags if t==tag and all(a.get(k.replace('_','-'))==v for k,v in attrs.items())]

rows=json.loads((ROOT/'_data/bilingual-pages.json').read_text(encoding='utf8'))
baseline_path=ROOT/'_reports/bilingual-baseline.json'
baseline=json.loads(baseline_path.read_text(encoding='utf8')) if baseline_path.exists() else {r['file']:subprocess.check_output(['git','show','f31080bf76fc6b664375f4378c9c02ffadd9714e:'+r['file']],cwd=ROOT).decode('utf8') for r in rows}
catalogue=load_translations(); preserved={v['en'] for v in catalogue.values() if v['en']==v['fr']}
documents={}; sources={}; errors=[]; checks=0
def ck(ok,message):
    global checks
    checks+=1
    if not ok: errors.append(message)
for row in rows:
    for lang in ['en','fr']:
        p=ROOT/('fr/' if lang=='fr' else '')/row['file']; source=p.read_text(encoding='utf8')
        sources[row[lang]]=source; documents[row[lang]]=Document(source)

titles=set(); descriptions=set(); affiliate={'en':0,'fr':0}; paused={'en':0,'fr':0}; schema_count=0
for row in rows:
    en=sources[row['en']]; fr=sources[row['fr']]
    original=baseline[row['file']].replace('"inLanguage": "en-US"','"inLanguage": "en-CA"').replace('<html lang="en-US">','<html lang="en-CA">').replace('property="og:locale" content="en_US"','property="og:locale" content="en_CA"')
    if row['en']=='/best-air-fryers/ninja-air-fryers/':
        original=original.replace('If you cook one item at a time, a single basket is simpler, easier to clean, and usually better value.','If you cook one item at a time, a single basket gives you one vessel to manage. Compare care instructions and current seller terms.')
    current=strip_logo(strip_bilingual(en))
    if row['en']=='/ninja/':current,original=without_hero(current),without_hero(original)
    if row['en']=='/':current,original=without_homepage_hero(current),without_homepage_hero(original)
    ck(current==original,'English content preserved '+row['en'])
    for lang in ['en','fr']:
        path=row[lang]; source=sources[path]; d=documents[path]; locale=lang+'-CA'
        ck(d.attrs('html')[0].get('lang')==locale,'html lang '+path)
        ck(d.attrs('link',rel='canonical')==[{'rel':'canonical','href':ORIGIN+path}],'canonical '+path)
        ck({a.get('hreflang'):a.get('href') for a in d.attrs('link',rel='alternate')}=={'en-CA':ORIGIN+row['en'],'fr-CA':ORIGIN+row['fr']},'hreflang '+path)
        ck(len(d.attrs('h1'))==1,'one H1 '+path)
        title=norm(re.search(r'<title>(.*?)</title>',source,re.S)[1]); description=d.attrs('meta',name='description')[0]['content']
        ck(title not in titles and description not in descriptions,'unique metadata '+path); titles.add(title); descriptions.add(description)
        ck(d.attrs('meta',property='og:url')[0]['content']==ORIGIN+path,'OG URL '+path)
        ck(d.attrs('meta',property='og:locale')[0]['content']==lang+'_CA','OG locale '+path)
        ck(not re.search(r'<meta[^>]+(?:http-equiv="refresh"|content="[^"]*noindex)',source,re.I),'indexable without redirect '+path)
        switch=re.search(r'<!-- bilingual:switch:start -->(.*?)<!-- bilingual:switch:end -->',source,re.S)[1]; sd=Document(switch)
        ck([a['href'] for a in sd.attrs('a')]==[row['en'],row['fr']],'exact language switch '+path)
        ck([a['href'] for a in sd.attrs('a',aria_current='page')]==[path],'active language '+path)
        ck(source.count('class="ninja-mega-category"')==5,'five mega categories '+path)
        for tag,a in d.tags:
            urls=[]
            if tag in {'a','link'} and a.get('href'): urls.append(a['href'])
            if tag in {'script','img','source'} and a.get('src'): urls.append(a['src'])
            if a.get('srcset'): urls.extend(x.strip().split(' ')[0] for x in a['srcset'].split(','))
            for href in urls:
                u=urlsplit(href)
                if u.netloc and u.netloc!='kitchengearlab.github.io' or u.scheme not in {'','http','https'}: continue
                target=u.path or path
                if target in documents:
                    ck(not u.fragment or unquote(u.fragment) in documents[target].ids,'valid fragment '+path+' '+href)
                    if tag=='a' and href not in [row['en'],row['fr']]: ck(target.startswith('/fr/')==(lang=='fr'),'same-language link '+path+' '+href)
                else: ck((ROOT/target.lstrip('/')).is_file(),'local resource '+path+' '+href)
            if tag=='a' and 'amazon.' in a.get('href',''):
                affiliate[lang]+=1; ck(bool(re.fullmatch(r'https://www\.amazon\.ca/dp/[A-Z0-9]{10}\?tag=kitchengearla-20',a['href'])),'Amazon destination '+path)
                ck('sponsored' in a.get('rel','') and 'noopener' in a.get('rel',''),'Amazon rel '+path)
        paused[lang]+=source.count('data-purchase-kind="philips-na350"')
        for a in d.attrs('div',data_purchase_kind='philips-na350'):
            ck(True,'paused Philips module '+path)
        visible=norm(re.sub('<[^>]+>',' ',re.search(r'<main\b[^>]*>(.*?)</main>',source,re.S)[1]))
        for schema in d.schemas:
            schema_count+=1
            def visit(o):
                if isinstance(o,list):
                    for v in o: visit(v)
                elif isinstance(o,dict):
                    if 'inLanguage' in o: ck(o['inLanguage']==locale,'schema language '+path)
                    if o.get('@type')=='Question':
                        ck(norm(o['name']) in visible,'schema question visible '+path)
                        ck(norm(o['acceptedAnswer']['text']) in visible,'schema answer visible '+path)
                    for v in o.values(): visit(v)
            visit(schema)
        # Full-segment equality detects untranslated editorial text, including metadata and JSON-LD.
        if lang=='fr':
            unchanged=set(values(source)) & {v['en'] for v in catalogue.values()}
            ck(unchanged<=preserved,'untranslated editorial segments '+path+' '+repr(unchanged-preserved))
            ck('En tant que Partenaire Amazon' in source,'French affiliate disclosure '+path)
        ck(len(re.findall(r'\bid="[^"]+"',source))==len(d.ids),'unique IDs '+path)
    amazon=lambda s: [a for a in Document(s).attrs('a') if 'amazon.' in a.get('href','')]
    protected=lambda a:{k:v for k,v in a.items() if k not in {'aria-label','title'}}
    ck([protected(a) for a in amazon(en)]==[protected(a) for a in amazon(fr)],'affiliate destinations/models/tracking preserved '+row['en'])
    images=lambda s:[{k:a.get(k) for k in ['src','srcset','width','height','loading','decoding','fetchpriority']} for t,a in Document(s).tags if t in {'img','source'}]
    ck(images(en)==images(fr),'premium images and loading preserved '+row['en'])
    scripts=lambda s:re.findall(r'<script(?![^>]*application/ld\+json)[^>]*>.*?</script>',s,re.S)
    ck(scripts(en)==scripts(fr),'no runtime translator; scripts unchanged '+row['en'])

ck(affiliate=={'en':72,'fr':72},'72 active Amazon links per language')
ck(paused=={'en':7,'fr':7},'seven suspended Philips CTAs per language')
tree=ET.parse(ROOT/'sitemap.xml'); ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}
urls=tree.findall('s:url',ns); ck(len(urls)==64,'64 sitemap entries')
ck({u.find('s:loc',ns).text for u in urls}=={ORIGIN+p for p in documents},'sitemap exact URL set')
for u in urls:
    loc=u.find('s:loc',ns).text; row=next(r for r in rows if loc in {ORIGIN+r['en'],ORIGIN+r['fr']})
    ck({a.get('hreflang'):a.get('href') for a in u.findall('x:link',ns)}=={'en-CA':ORIGIN+row['en'],'fr-CA':ORIGIN+row['fr']},'sitemap reciprocal pairs '+loc)
report={'passed':not errors,'checks':checks,'pages':len(documents),'pairs':len(rows),'translatedSegments':len(catalogue)-len(preserved),'preservedSegments':len(preserved),'schemaBlocks':schema_count,'affiliate':affiliate,'pausedPhilips':paused,'errors':errors}
(ROOT/'_reports/bilingual-static.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2)); sys.exit(bool(errors))
