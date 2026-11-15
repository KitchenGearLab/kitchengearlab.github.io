"""Reconcile the default branch and explicitly request its existing Pages build.

Uses the job-scoped GITHUB_TOKEN only; no PAT, external scheduler or image encoder.
"""
import json, os, subprocess, time, urllib.error, urllib.request
from seasonal_hero import ROOT, ALL_PAGES, update

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def api(method,path):
    token=os.environ['GH_TOKEN']
    request=urllib.request.Request('https://api.github.com/'+path,method=method,headers={
        'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
    try:
        with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
    except urllib.error.HTTPError as error:
        if method=='GET' and error.code==404:return None
        # Never print headers, credentials or a response containing unexpected data.
        raise RuntimeError(f'GitHub {method} failed with HTTP {error.code}') from None

def needs_build(latest,head):
    return not(latest and latest.get('commit')==head and latest.get('status') in {'built','building','queued'})

def ensure_pages(repo,head,call=api,pause=time.sleep,attempts=36):
    config=call('GET',f'repos/{repo}/pages')
    if not config or config.get('build_type')!='legacy' or config.get('source')!={'branch':'main','path':'/'}:
        raise RuntimeError('Pages configuration changed; refusing to change deployment settings')
    endpoint=f'repos/{repo}/pages/builds/latest'
    latest=call('GET',endpoint)
    previous=latest
    requested=needs_build(latest,head)
    if requested:call('POST',f'repos/{repo}/pages/builds')
    # Recover on a later run if a previous push succeeded but its build request failed.
    # A no-change run with this exact head already deployed makes no build request.
    for attempt in range(attempts):
        if latest and latest.get('commit')==head:
            if latest.get('status')=='built':return {'requested':requested,'status':'built','commit':head}
            if latest.get('status')=='errored' and (not requested or latest!=previous):raise RuntimeError('Pages build failed')
        if attempt+1<attempts:
            pause(10);latest=call('GET',endpoint)
    raise RuntimeError('Pages has not confirmed this commit; rerun to reconcile without another hero commit')

def main():
    repo=os.environ.get('GITHUB_REPOSITORY')
    if repo!='KitchenGearLab/kitchengearlab.github.io' or os.environ.get('GITHUB_REF')!='refs/heads/main':
        raise RuntimeError('Only this repository default branch may be updated')
    if git('status','--porcelain'):raise RuntimeError('Checkout must be clean before reconciliation')
    git('fetch','--quiet','origin','main')
    git('merge','--ff-only','--quiet','FETCH_HEAD')
    result=update(root=ROOT)
    changed=result['changed']
    if changed:
        # Stage only the four allowed HTML files. No broad add, forced push or keepalive commit.
        if not set(changed)<=set(ALL_PAGES):raise RuntimeError('Unexpected write scope')
        git('add','--',*changed)
        git('-c','user.name=github-actions[bot]','-c','user.email=41898282+github-actions[bot]@users.noreply.github.com',
            'commit','-m',f'chore: select {result["season"]} seasonal heroes')
        git('push','origin','HEAD:main')
    head=git('rev-parse','HEAD')
    result.update({'commit':head,'pages':ensure_pages(repo,head)})
    print(json.dumps(result))
    summary=os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary,'a',encoding='utf8') as stream:
            stream.write(f'### Homepage and Ninja seasonal heroes\n\nSeason: **{result["season"]}** ({result["timezone"]}).\n\n'
                f'HTML files changed: **{len(changed)}**. Pages build requested: **{result["pages"]["requested"]}**.\n\n'
                f'Verified Pages commit: `{head}`.\n')
if __name__=='__main__':main()
