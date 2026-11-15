"""Static bilingual publication: explicit editorial catalogue, no runtime translator."""
from pathlib import Path
from html.parser import HTMLParser
import html, json, re, subprocess
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://kitchengearlab.github.io'
CATALOGUE = ROOT / '_content/bilingual-fr.json'
INVENTORY = ROOT / '_data/bilingual-pages.json'
ATTRS = {'alt', 'aria-label', 'title', 'placeholder'}
META = {'description','og:title','og:description','og:image:alt','twitter:title','twitter:description','twitter:image:alt'}
NARRATIVE = {'name','description','headline','text','caption','articleSection','keywords','alternateName'}

def pages():
    return sorted(p for p in ROOT.rglob('index.html') if not any(x.startswith(('_','.')) or x in {'fr','node_modules','vendor'} for x in p.relative_to(ROOT).parts))

def route(p): return '/' + p.relative_to(ROOT).as_posix().removesuffix('index.html')
def norm(s): return re.sub(r'\s+', ' ', html.unescape(s)).strip()
def narrative(obj):
    if isinstance(obj, dict):
        for k,v in obj.items():
            if k in NARRATIVE and isinstance(v,str): yield v
            elif isinstance(v,(dict,list)): yield from narrative(v)
    elif isinstance(obj,list):
        for v in obj: yield from narrative(v)

class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.skip=None; self.jsonld=False; self.values=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in {'script','style'}: self.skip=tag; self.jsonld=a.get('type')=='application/ld+json'
        for k,v in attrs:
            if v and (k in ATTRS or (tag=='meta' and k=='content' and (a.get('name') or a.get('property')) in META)): self.values.append(norm(v))
    def handle_endtag(self,tag):
        if tag==self.skip: self.skip=None; self.jsonld=False
    def handle_data(self,data):
        if self.jsonld: self.values.extend(norm(x) for x in narrative(json.loads(data)))
        elif not self.skip and norm(data): self.values.append(norm(data))
    # Treat entities within a text node as part of the same segment (feed decoded source).

def values(source):
    p=Extract(); p.feed(source); return p.values

def inventory():
    rows=[]; catalogue=json.loads(CATALOGUE.read_text(encoding='utf8')) if CATALOGUE.exists() else {}
    seen={v['en']:k for k,v in catalogue.items()}
    next_id=max((int(k) for k in catalogue),default=0)+1
    for p in pages():
        source=strip_bilingual(p.read_text(encoding='utf-8')); en=route(p)
        rows.append({'file':p.relative_to(ROOT).as_posix(),'en':en,'fr':'/fr'+en,'title':norm(re.search(r'<title>(.*?)</title>',source,re.S)[1])})
        for s in values(source):
            if s not in seen:
                key=f'{next_id:04}'; next_id+=1; seen[s]=key; catalogue[key]={'en':s,'fr':None,'firstPage':en}
    INVENTORY.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    CATALOGUE.write_text(json.dumps(catalogue,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    baseline=ROOT/'_reports/bilingual-baseline.json'
    if not baseline.exists(): baseline.write_text(json.dumps({row['file']:(ROOT/row['file']).read_text(encoding='utf8') for row in rows},ensure_ascii=False),encoding='utf8')
    print(json.dumps({'pages':len(rows),'segments':len(seen),'words':sum(len(x.split()) for x in seen),'inventory':rows},ensure_ascii=False,indent=2))

def load_translations():
    catalogue=json.loads(CATALOGUE.read_text(encoding='utf8'))
    for v in catalogue.values(): v['fr']=None
    for line in (ROOT/'_content/fr-translations.tsv').read_text(encoding='utf8').splitlines():
        key,value=line.split('\t',1)
        if key not in catalogue: raise ValueError(key)
        catalogue[key]['fr']=value
    preserved=json.loads((ROOT/'_content/fr-preserved.json').read_text(encoding='utf8')) if (ROOT/'_content/fr-preserved.json').exists() else []
    for key in preserved:
        if catalogue[key]['fr'] is not None: raise ValueError('Translated and preserved: '+key)
        catalogue[key]['fr']=catalogue[key]['en']
    from seasonal_hero import alt_translations
    seasonal_alts=alt_translations()
    for value in catalogue.values():
        if value['en'] in seasonal_alts:value['fr']=seasonal_alts[value['en']]
    return catalogue

def missing():
    for k,v in load_translations().items():
        if v['fr'] is None: print(k+' '+v['en'])

def alternate_links(en):
    return ('  <!-- bilingual:seo:start -->\n'
        f'  <link rel="alternate" hreflang="en-CA" href="{ORIGIN}{en}" />\n'
        f'  <link rel="alternate" hreflang="fr-CA" href="{ORIGIN}/fr{en}" />\n'
        '  <meta property="og:locale:alternate" content="fr_CA" />\n'
        '  <!-- bilingual:seo:end -->')

def switch(en, french=False):
    label='Choix de la langue' if french else 'Language selection'
    return ('<!-- bilingual:switch:start -->'
        f'<nav class="language-switch" aria-label="{label}">'
        f'<a href="{en}" lang="en-CA" hreflang="en-CA" aria-label="EN — English"'+('' if french else ' aria-current="page"')+'>EN</a>'
        '<span aria-hidden="true">/</span>'
        f'<a href="/fr{en}" lang="fr-CA" hreflang="fr-CA" aria-label="FR — Français"'+(' aria-current="page"' if french else '')+'>FR</a></nav>'
        '<!-- bilingual:switch:end -->')

def strip_bilingual(s):
    for kind in ['seo','switch']:
        s=re.sub(r'\s*<!-- bilingual:'+kind+r':start -->.*?<!-- bilingual:'+kind+r':end -->', '', s, flags=re.S)
    return s

class French(HTMLParser):
    def __init__(self, translations, routes):
        super().__init__(convert_charrefs=True)
        self.translations=translations; self.routes=routes; self.output=[]; self.skip=None; self.jsonld=False
    def tr(self,s):
        key=norm(s)
        if not key: return s
        if key not in self.translations: raise ValueError('Uncatalogued text: '+key)
        return self.translations[key]
    def url(self,s):
        u=urlsplit(s)
        if u.scheme and u.scheme not in {'http','https'}: return s
        if u.netloc and u.netloc!='kitchengearlab.github.io': return s
        # Fragment-only references retain the current document.
        if u.path in self.routes:
            return urlunsplit((u.scheme,u.netloc,'/fr'+u.path,u.query,u.fragment))
        return s
    def schema(self,o):
        if isinstance(o,list): return [self.schema(v) for v in o]
        if not isinstance(o,dict): return o
        r={}
        for k,v in o.items():
            if k in NARRATIVE and isinstance(v,str): r[k]=self.tr(v)
            elif k=='inLanguage': r[k]='fr-CA'
            elif isinstance(v,(dict,list)): r[k]=self.schema(v)
            elif isinstance(v,str) and v.startswith(ORIGIN): r[k]=self.url(v)
            else: r[k]=v
        # The publisher is a shared organization in both languages.
        if r.get('@type')=='Organization': r['@id']=ORIGIN+'/#organization'; r['url']=ORIGIN+'/'
        if o.get('@id')==ORIGIN+'/#organization': r['@id']=o['@id']
        return r
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); raw=self.get_starttag_text()
        if tag in {'script','style'}: self.skip=tag; self.jsonld=a.get('type')=='application/ld+json'
        def replace(m):
            k=m[1]; value=html.unescape(m[3]); new=value
            if k in ATTRS or (tag=='meta' and k=='content' and (a.get('name') or a.get('property')) in META): new=self.tr(value)
            elif k=='href' and not(tag=='link' and a.get('rel')=='alternate'): new=self.url(value)
            elif tag=='meta' and k=='content' and a.get('property')=='og:url': new=self.url(value)
            elif tag=='meta' and k=='content' and a.get('property')=='og:locale': new='fr_CA'
            elif tag=='meta' and k=='content' and a.get('property')=='og:locale:alternate': new='en_CA'
            elif tag=='html' and k=='lang': new='fr-CA'
            return m[0] if new==value else k+'='+m[2]+html.escape(new,quote=True)+m[2]
        raw=re.sub(r'([\w:-]+)\s*=\s*([\x22\x27])(.*?)\2',replace,raw,flags=re.S)
        self.output.append(raw)
    def handle_startendtag(self,tag,attrs): self.handle_starttag(tag,attrs)
    def handle_endtag(self,tag):
        self.output.append('</'+tag+'>')
        if self.skip==tag: self.skip=None; self.jsonld=False
    def handle_data(self,s):
        if self.jsonld: self.output.append(json.dumps(self.schema(json.loads(s)),ensure_ascii=False,indent=2).replace('<','\\u003c'))
        elif self.skip or not norm(s): self.output.append(s)
        else:
            prefix=re.match(r'^\s*',s)[0]; suffix=re.search(r'\s*$',s)[0]
            self.output.append(prefix+html.escape(self.tr(s),quote=False)+suffix)
    def handle_comment(self,s): self.output.append('<!--'+s+'-->')
    def handle_decl(self,s): self.output.append('<!'+s+'>')

def build(check=False):
    catalogue=load_translations()
    missing=[k for k,v in catalogue.items() if not v['fr']]
    if missing: raise ValueError('Incomplete translation: '+', '.join(missing))
    translations={v['en']:v['fr'] for v in catalogue.values()}
    # Seasonal alt text is maintained with its static hero, independently of the editorial catalogue.
    from seasonal_hero import alt_translations
    translations.update(alt_translations())
    rows=json.loads(INVENTORY.read_text(encoding='utf8')); routes={r['en'] for r in rows}
    changed=[]
    def emit(p,s):
        if p.exists() and p.read_text(encoding='utf8')==s: return
        changed.append(p.relative_to(ROOT).as_posix())
        if not check: p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf8',newline='\n')
    for row in rows:
        p=ROOT/row['file']; source=strip_bilingual(p.read_text(encoding='utf8'))
        source=source.replace('"inLanguage": "en-US"','"inLanguage": "en-CA"').replace('<html lang="en-US">','<html lang="en-CA">').replace('property="og:locale" content="en_US"','property="og:locale" content="en_CA"')
        en=re.sub(r'(<link rel="canonical"[^>]*>)',r'\1\n'+alternate_links(row['en']),source,count=1)
        marker='    </div></div>\n    <script defer src="/assets/js/navigation.js"></script>'
        if en.count(marker)!=1: raise ValueError('Header marker mismatch: '+str(p))
        en=en.replace(marker,'      '+switch(row['en'])+'\n'+marker)
        # Translate the source before inserting language-specific switch labels.
        fr_source=re.sub(r'(<link rel="canonical"[^>]*>)',r'\1\n'+alternate_links(row['en']),source,count=1)
        parser=French(translations,routes); parser.feed(fr_source); parser.close()
        fr=''.join(parser.output).replace(marker,'      '+switch(row['en'],True)+'\n'+marker)
        emit(p,en); emit(ROOT/'fr'/row['file'],fr)
    # Both locales are first-class canonical URLs, with reciprocal sitemap annotations.
    sitemap=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for row in rows:
        for lang in ['en','fr']:
            sitemap.extend(['  <url>',f'    <loc>{ORIGIN}{row[lang]}</loc>','    <lastmod>2026-11-15</lastmod>'])
            for key,locale in [('en','en-CA'),('fr','fr-CA')]: sitemap.append(f'    <xhtml:link rel="alternate" hreflang="{locale}" href="{ORIGIN}{row[key]}" />')
            sitemap.append('  </url>')
    sitemap.append('</urlset>'); emit(ROOT/'sitemap.xml','\n'.join(sitemap)+'\n')
    if not check: CATALOGUE.write_text(json.dumps(catalogue,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'check':check,'changed':changed,'pairs':len(rows),'segments':len(catalogue)},ensure_ascii=False))
    if check and changed: raise SystemExit(1)

if __name__=='__main__':
    import sys
    if sys.argv[1:] == ['inventory']: inventory()
    elif sys.argv[1:] == ['missing']: missing()
    elif sys.argv[1:] == ['build']: build()
    elif sys.argv[1:] == ['build','--check']: build(True)
