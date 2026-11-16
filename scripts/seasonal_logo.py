"""Read and validate the progressive seasonal logo from the shared Jekyll header.

No scheduled task or network dependency: a head script selects picture sources in
a DOM microtask before paint. Disabled JavaScript, unavailable Intl or failed assets use
the original img. Only the header logo markup is managed.
"""
import argparse, json, re
from seasonal_hero import ROOT, TIMEZONE

ORIGINAL_IMG='<img src="/assets/images/brand/kitchengearlab-logo-64.webp" srcset="/assets/images/brand/kitchengearlab-logo-64.webp 1x, /assets/images/brand/kitchengearlab-logo-128.webp 2x" width="32" height="32" alt="" decoding="async" />'
FALLBACK="this.onerror=null;this.parentNode.querySelectorAll('source').forEach(function(s){s.remove()})"
BLOCK=re.compile(r'<!-- seasonal:logo:start -->[\s\S]*?<!-- seasonal:logo:end -->')
HEAD_BLOCK=re.compile(r'<!-- seasonal:logo:head:start -->[\s\S]*?<!-- seasonal:logo:head:end -->\n')

def head_markup():
    return HEAD_BLOCK.search((ROOT/'_includes/header.html').read_text(encoding='utf8'))[0]

SCRIPT=re.search(r'<script>([\s\S]*?)</script>',head_markup())[1]

def markup():
    return BLOCK.search((ROOT/'_includes/header.html').read_text(encoding='utf8'))[0]

def strip_logo(source):
    matches=BLOCK.findall(source)
    if len(matches)>1 or len(HEAD_BLOCK.findall(source))>1:raise ValueError('Duplicate managed logo')
    return HEAD_BLOCK.sub('',BLOCK.sub(lambda _:ORIGINAL_IMG,source))

def replace_logo(source):
    from header import HEAD_INCLUDE,HEADER_INCLUDE
    if HEAD_INCLUDE in source and HEADER_INCLUDE in source:return source
    original=strip_logo(source)
    if original.count(ORIGINAL_IMG)!=1 or original.count('</head>')!=1:raise ValueError('Expected exactly one original header logo and document head')
    return original.replace(ORIGINAL_IMG,markup(),1).replace('</head>',head_markup()+'</head>',1)

def update(check=False):
    from header import update as update_header
    return update_header(check)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=update(args.check);print(json.dumps(result))
    if args.check and result['changed']:raise SystemExit(1)
