"""Install the same progressive seasonal logo on all static EN/FR pages.

No scheduled task or network dependency: a head script selects picture sources in
a DOM microtask before paint. Disabled JavaScript, unavailable Intl or failed assets use
the original img. Only the header logo markup is managed.
"""
import argparse, json, re
from seasonal_hero import ROOT, TIMEZONE

ORIGINAL_IMG='<img src="/assets/images/brand/kitchengearlab-logo-64.webp" srcset="/assets/images/brand/kitchengearlab-logo-64.webp 1x, /assets/images/brand/kitchengearlab-logo-128.webp 2x" width="32" height="32" alt="" decoding="async" />'
SCRIPT='''(function(){try{var d={};new Intl.DateTimeFormat('en-CA',{timeZone:'TIMEZONE',calendar:'gregory',numberingSystem:'latn',month:'numeric',day:'numeric'}).formatToParts(new Date()).forEach(function(v){d[v.type]=+v.value});if(d.month===11||(d.month===12&&d.day<=26)){var o=new MutationObserver(function(){var p=document.querySelector('[data-seasonal-logo]');if(p&&p.querySelector('img')){o.disconnect();p.querySelectorAll('source').forEach(function(s){s.media='all'})}});o.observe(document.documentElement,{childList:true,subtree:true})}}catch(e){}})();'''.replace('TIMEZONE',TIMEZONE)
FALLBACK="this.onerror=null;this.parentNode.querySelectorAll('source').forEach(function(s){s.remove()})"
BLOCK=re.compile(r'<!-- seasonal:logo:start -->[\s\S]*?<!-- seasonal:logo:end -->')
HEAD_BLOCK=re.compile(r'<!-- seasonal:logo:head:start -->[\s\S]*?<!-- seasonal:logo:head:end -->\n')

def head_markup():
    return '<!-- seasonal:logo:head:start --><script>'+SCRIPT+'</script><!-- seasonal:logo:head:end -->\n'

def markup():
    def source(ext,mime):
        images=', '.join(f'/assets/images/brand/kitchengearlab-logo-christmas-{w}.{ext} {density}x' for density,w in [(1,64),(2,128),(3,192)])
        return f'<source type="image/{mime}" media="not all" srcset="{images}" />'
    img=ORIGINAL_IMG.replace(' decoding="async"',f' style="object-fit:contain;aspect-ratio:1" onerror="{FALLBACK}" decoding="async"')
    return ('<!-- seasonal:logo:start --><picture data-seasonal-logo="" style="display:block;flex:0 0 32px;width:32px;height:32px">'+source('webp','webp')+source('png','png')+
            img+'</picture><!-- seasonal:logo:end -->')

def strip_logo(source):
    matches=BLOCK.findall(source)
    if len(matches)>1 or len(HEAD_BLOCK.findall(source))>1:raise ValueError('Duplicate managed logo')
    return HEAD_BLOCK.sub('',BLOCK.sub(lambda _:ORIGINAL_IMG,source))

def replace_logo(source):
    original=strip_logo(source)
    if original.count(ORIGINAL_IMG)!=1 or original.count('</head>')!=1:raise ValueError('Expected exactly one original header logo and document head')
    return original.replace(ORIGINAL_IMG,markup(),1).replace('</head>',head_markup()+'</head>',1)

def update(check=False):
    rows=json.loads((ROOT/'_data/bilingual-pages.json').read_text(encoding='utf8'))
    outputs={}
    for row in rows:
        for prefix in ('','fr/'):
            path=prefix+row['file'];before=(ROOT/path).read_text(encoding='utf8');after=replace_logo(before)
            if before!=after:outputs[path]=after
    if not check:
        for path,after in outputs.items():(ROOT/path).write_text(after,encoding='utf8',newline='\n')
    return {'pages':len(rows)*2,'changed':list(outputs)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=update(args.check);print(json.dumps(result))
    if args.check and result['changed']:raise SystemExit(1)
