"""Native Jekyll header ownership and one-time source migration helpers."""
from pathlib import Path
import argparse,json,re
ROOT=Path(__file__).resolve().parents[1]
FRONT='---\nlayout: null\n---\n'
HEAD_INCLUDE='{% include header.html part="head" %}'
HEADER_INCLUDE='{% include header.html %}'
HEADER=re.compile(r'<!-- shared:header:start -->[\s\S]*?<!-- shared:header:end -->')
HEAD=re.compile(r'<!-- seasonal:logo:head:start -->[\s\S]*?<!-- seasonal:logo:head:end -->\n')

def body(source):
    return re.sub(r'\A---\n[\s\S]*?\n---\n','',source,count=1)

def without_header(source):
    source=body(source)
    source=HEAD.sub('',source).replace(HEAD_INCLUDE+'\n','')
    # The head include also contains critical navigation setup.
    source=re.sub(r'<!-- header:head:start -->[\s\S]*?<!-- header:head:end -->\n','',source)
    return HEADER.sub('HEADER',source).replace(HEADER_INCLUDE,'HEADER')

def migrate(source):
    source=body(source)
    if HEADER_INCLUDE not in source:
        if len(HEADER.findall(source))!=1:raise ValueError('Expected one legacy header')
        source=HEADER.sub(lambda _:HEADER_INCLUDE,source)
    if HEAD_INCLUDE not in source:
        if len(HEAD.findall(source))!=1:raise ValueError('Expected one seasonal head block')
        source=HEAD.sub(lambda _:HEAD_INCLUDE+'\n',source)
    if source.count(HEADER_INCLUDE)!=1 or source.count(HEAD_INCLUDE)!=1:raise ValueError('Ambiguous includes')
    return FRONT+source

def pages():
    rows=json.loads((ROOT/'_data/bilingual-pages.json').read_text(encoding='utf8'))
    return [prefix+row['file'] for row in rows for prefix in ('','fr/')]

def update(check=False):
    outputs={}
    for path in pages():
        old=(ROOT/path).read_text(encoding='utf8');new=migrate(old)
        if new!=old:outputs[path]=new
    if not check:
        for path,new in outputs.items():(ROOT/path).write_text(new,encoding='utf8',newline='\n')
    return {'pages':len(pages()),'changed':list(outputs)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args();result=update(args.check)
    print(json.dumps(result))
    if args.check and result['changed']:raise SystemExit(1)
