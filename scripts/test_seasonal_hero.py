import json, tempfile, unittest, subprocess, os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
from seasonal_hero import ROOT, PAGES, WIDTHS, ALT_TEXT, season_for, picture, hero, without_hero, replace_hero, update, validate_assets
from seasonal_workflow import ensure_pages, needs_build
import seasonal_workflow

class CalendarTests(unittest.TestCase):
    def test_every_year_and_boundary(self):
        for year in range(2026,2037):
            for month,day,expected in [(1,1,'classic'),(10,31,'classic'),(11,1,'christmas'),(12,26,'christmas'),(12,27,'classic'),(12,31,'classic')]:
                for hour,minute,second in [(0,0,0),(23,59,59)]:
                    with self.subTest(year=year,month=month,day=day,hour=hour):
                        self.assertEqual(season_for(datetime(year,month,day,hour,minute,second,tzinfo=ZoneInfo('America/Toronto'))),expected)
    def test_utc_to_toronto_and_dst(self):
        for instant,expected in [('2026-11-01T03:59:59+00:00','classic'),('2026-11-01T04:00:00+00:00','christmas'),
                ('2026-12-27T04:59:59+00:00','christmas'),('2026-12-27T05:00:00+00:00','classic'),
                ('2027-01-01T04:59:59+00:00','classic'),('2027-03-14T06:59:59+00:00','classic'),
                ('2027-03-14T07:00:00+00:00','classic'),('2027-11-07T05:59:59+00:00','christmas'),('2027-11-07T06:00:00+00:00','christmas')]:
            with self.subTest(instant=instant):self.assertEqual(season_for(datetime.fromisoformat(instant)),expected)
    def test_naive_date_rejected(self):
        with self.assertRaises(ValueError):season_for(datetime(2026,11,1))

class AssetAndPageTests(unittest.TestCase):
    def test_all_30_assets_and_dimensions(self):validate_assets()
    def test_each_season_and_language_markup(self):
        for season in ('classic','christmas'):
            for lang in PAGES:
                markup=picture(season,lang)
                self.assertEqual(markup.count('<img '),1)
                self.assertEqual(markup.count('<source '),2)
                self.assertIn('width="1672" height="941"',markup)
                self.assertIn('loading="eager"',markup)
                self.assertEqual(markup.count('fetchpriority="high"'),1)
                self.assertNotIn('object-fit:cover',markup)
                self.assertIn('aspect-ratio:1672/941;object-fit:contain',markup)
                self.assertNotIn('javascript',markup)
    def test_replacement_is_bounded_and_idempotent(self):
        for lang,path in PAGES.items():
            source=(ROOT/path).read_text(encoding='utf8')
            for season in ('classic','christmas'):
                after=replace_hero(source,season,lang)
                self.assertEqual(without_hero(after),without_hero(source))
                self.assertEqual(replace_hero(after,season,lang),after)
                self.assertEqual(hero(after),picture(season,lang))
    def test_duplicate_hero_fails_closed(self):
        source='<section class="collection-hero">'+picture('classic','en')*2+'</section>'
        with self.assertRaises(ValueError):replace_hero(source,'christmas','en')
    def test_missed_runs_reconcile_current_season(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for lang,path in PAGES.items():
                p=root/path;p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text('<section class="collection-hero">'+picture('christmas',lang)+'</section>',encoding='utf8')
            with patch('seasonal_hero.validate_assets'):
                first=update(root,datetime(2028,1,5,tzinfo=timezone.utc))
                self.assertEqual(set(first['changed']),set(PAGES.values()))
                before={p:(root/p).stat().st_mtime_ns for p in PAGES.values()}
                second=update(root,datetime(2028,1,6,tzinfo=timezone.utc))
                self.assertEqual(second['changed'],[])
                self.assertEqual(before,{p:(root/p).stat().st_mtime_ns for p in PAGES.values()})
                self.assertEqual(update(root,datetime(2028,11,4,tzinfo=timezone.utc))['season'],'christmas')
    def test_bilingual_references_match_even_before_a_delayed_run(self):
        import re
        seasons=set()
        for lang,path in PAGES.items():
            markup=hero((ROOT/path).read_text(encoding='utf8'))
            current=re.search(r'data-seasonal-ninja-hero="(classic|christmas)"',markup)[1]
            seasons.add(current);self.assertEqual(markup,picture(current,lang))
        self.assertEqual(len(seasons),1)

class DeploymentTests(unittest.TestCase):
    CONFIG={'build_type':'legacy','source':{'branch':'main','path':'/'}}
    def fake(self,latest):
        calls=[]
        def api(method,path):
            calls.append((method,path))
            if path.endswith('/pages'):return self.CONFIG
            if method=='POST':return {'status':'queued'}
            return latest
        return calls,api
    def test_no_build_or_commit_needed_when_current(self):
        calls,api=self.fake({'status':'built','commit':'HEAD'})
        for _ in range(2):self.assertFalse(ensure_pages('owner/repo','HEAD',api,pause=lambda _:None,attempts=1)['requested'])
        self.assertFalse(any(method=='POST' for method,_ in calls))
    def test_recover_missing_build_after_successful_push(self):
        calls=[];gets=iter([{'status':'built','commit':'OLDER'},{'status':'built','commit':'HEAD'}])
        def api(method,path):
            calls.append((method,path))
            if path.endswith('/pages'):return self.CONFIG
            if method=='POST':return {'status':'queued'}
            return next(gets)
        self.assertTrue(ensure_pages('owner/repo','HEAD',api,pause=lambda _:None,attempts=2)['requested'])
        self.assertEqual(sum(method=='POST' for method,_ in calls),1)
    def test_active_same_commit_is_not_queued_again(self):
        calls=[];gets=iter([{'status':'building','commit':'HEAD'},{'status':'built','commit':'HEAD'}])
        def api(method,path):
            calls.append((method,path));return self.CONFIG if path.endswith('/pages') else next(gets)
        self.assertFalse(ensure_pages('owner/repo','HEAD',api,pause=lambda _:None,attempts=2)['requested'])
        self.assertFalse(any(method=='POST' for method,_ in calls))
    def test_failed_build_is_retried(self):self.assertTrue(needs_build({'status':'errored','commit':'HEAD'},'HEAD'))
    def test_changed_pages_configuration_is_never_rewritten(self):
        calls=[]
        def api(method,path):calls.append((method,path));return {'build_type':'workflow'}
        with self.assertRaises(RuntimeError):ensure_pages('owner/repo','HEAD',api,attempts=1)
        self.assertEqual([m for m,_ in calls],['GET'])
    def test_workflow_permissions_and_concurrency(self):
        workflow=(ROOT/'.github/workflows/seasonal-ninja-hero.yml').read_text(encoding='utf8')
        for value in ['permissions: {}','contents: write','pages: write','cancel-in-progress: false','workflow_dispatch:','timezone: America/Toronto','17 0 * * *']:
            self.assertIn(value,workflow)
        self.assertNotIn('actions: write',workflow)
        self.assertNotIn('id-token: write',workflow)
        self.assertNotIn('pull_request_target',workflow)

class GitIntegrationTests(unittest.TestCase):
    def test_two_workflow_runs_push_only_one_bounded_commit(self):
        # Real Git operations against an isolated local bare remote, never GitHub.
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);remote=folder/'remote.git';checkout=folder/'checkout'
            def run(*args,cwd=None):
                return subprocess.check_output(['git',*args],cwd=cwd,stderr=subprocess.DEVNULL,text=True).strip()
            run('init','--bare','--initial-branch=main',str(remote))
            run('clone',str(remote),str(checkout))
            run('config','user.name','Seasonal fixture',cwd=checkout);run('config','user.email','fixture@example.invalid',cwd=checkout)
            initial='classic' if season_for()=='christmas' else 'christmas'
            for lang,path in PAGES.items():
                p=checkout/path;p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text('<section class="collection-hero">'+picture(initial,lang)+'</section>',encoding='utf8')
            (checkout/'unrelated.txt').write_text('unchanged\n',encoding='utf8')
            run('add','.',cwd=checkout);run('commit','-m','fixture',cwd=checkout);run('push','origin','main',cwd=checkout)
            before=run('rev-parse','HEAD',cwd=checkout)
            with patch.object(seasonal_workflow,'ROOT',checkout),patch('seasonal_hero.validate_assets'),patch.object(seasonal_workflow,'ensure_pages',return_value={'requested':False,'status':'built'}),patch.dict(os.environ,{'GITHUB_REPOSITORY':'KitchenGearLab/kitchengearlab.github.io','GITHUB_REF':'refs/heads/main','GITHUB_STEP_SUMMARY':''}):
                seasonal_workflow.main();first=run('rev-parse','HEAD',cwd=checkout)
                self.assertNotEqual(before,first)
                seasonal_workflow.main();second=run('rev-parse','HEAD',cwd=checkout)
                self.assertEqual(first,second)
            self.assertEqual(run('rev-list','--count','HEAD',cwd=checkout),'2')
            self.assertEqual(set(run('diff-tree','--no-commit-id','--name-only','-r','HEAD',cwd=checkout).splitlines()),set(PAGES.values()))
            self.assertEqual(run('status','--porcelain',cwd=checkout),'')
            self.assertEqual((checkout/'unrelated.txt').read_text(encoding='utf8'),'unchanged\n')

if __name__=='__main__':unittest.main()
