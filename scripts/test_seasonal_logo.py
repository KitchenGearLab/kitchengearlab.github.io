"""Logo contract, native-JS calendar parity and bounded static changes."""
import hashlib,json,re,subprocess,unittest
from datetime import datetime,timezone
from seasonal_hero import ROOT,season_for,hero,homepage_hero
from seasonal_logo import ORIGINAL_IMG,SCRIPT,BLOCK,HEAD_BLOCK,head_markup,markup,replace_logo,strip_logo,update

class LogoTests(unittest.TestCase):
    def test_every_static_page_has_the_same_logo(self):
        rows=json.loads((ROOT/'_data/bilingual-pages.json').read_text(encoding='utf8'))
        for row in rows:
            for prefix in ('','fr/'):
                path=prefix+row['file'];source=(ROOT/path).read_text(encoding='utf8')
                rendered=(ROOT/'_site/header2'/path).read_text(encoding='utf8')
                with self.subTest(path=path):
                    self.assertEqual(BLOCK.findall(rendered),[markup()])
                    self.assertEqual(HEAD_BLOCK.findall(rendered),[head_markup()])
                    self.assertEqual(replace_logo(source),source)
                    self.assertEqual(strip_logo(rendered).count(ORIGINAL_IMG),1)
        self.assertEqual(update(check=True)['changed'],[])
    def test_ambiguous_logo_fails_closed(self):
        with self.assertRaises(ValueError):replace_logo(ORIGINAL_IMG*2)
        with self.assertRaises(ValueError):replace_logo(markup()*2)
        with self.assertRaises(ValueError):replace_logo('<header></header>')
    def test_markup_keeps_static_original_and_accessibility(self):
        source=markup()
        self.assertEqual(source.count('<img '),1)
        self.assertEqual(source.count('media="not all"'),2)
        self.assertIn('width="44" height="44" alt=""',source)
        self.assertIn('object-fit:contain;aspect-ratio:1',source)
        self.assertIn('this.onerror=null',source)
        self.assertIn("querySelectorAll('source')",source)
        self.assertNotIn('fetchpriority',source)
        self.assertNotIn('document.write',source)
        self.assertNotIn('src="https:',source)
        self.assertNotIn('<script>',source)
        self.assertIn('MutationObserver',head_markup())
        self.assertIn('class="brand-logo"',source)
    def test_asset_integrity_and_original_preserved(self):
        manifest=json.loads((ROOT/'_data/seasonal-logo.json').read_text(encoding='utf8'))
        self.assertEqual((manifest['sourceWidth'],manifest['sourceHeight']),(1254,1254))
        self.assertEqual(hashlib.sha256((ROOT/manifest['original']).read_bytes()).hexdigest(),manifest['sourceSha256'])
        self.assertEqual(len(manifest['assets']),6)
        for row in manifest['assets']:
            data=(ROOT/row['file']).read_bytes()
            self.assertEqual(len(data),row['bytes']);self.assertEqual(hashlib.sha256(data).hexdigest(),row['sha256'])
            self.assertIn(row['width'],(64,128,192));self.assertEqual(row['height'],row['width'])
            self.assertTrue(data.startswith(b'\x89PNG') or data.startswith(b'RIFF'))
    def test_native_javascript_matches_shared_toronto_calendar(self):
        instants=[]
        for year in range(2026,2037):
            for month,day in ((1,1),(10,31),(11,1),(12,26),(12,27),(12,31)):
                for hour in (0,4,5,23):instants.append(datetime(year,month,day,hour,0,0,tzinfo=timezone.utc).isoformat())
        instants+=['2026-11-01T03:59:59+00:00','2026-11-01T04:00:00+00:00','2026-12-27T04:59:59+00:00','2026-12-27T05:00:00+00:00','2027-03-14T07:00:00+00:00','2027-11-07T06:00:00+00:00']
        js="""const vm=require('node:vm'),fs=require('node:fs');const input=JSON.parse(fs.readFileSync(0,'utf8'));let results=[];class Observer{constructor(callback){this.callback=callback}observe(){this.callback()}disconnect(){}}for(const iso of input.instants){const sources=[{media:'not all'},{media:'not all'}];class FrozenDate extends Date{constructor(){super(iso)}}vm.runInNewContext(input.script,{Intl,Date:FrozenDate,MutationObserver:Observer,document:{documentElement:{},querySelector:()=>({querySelector:()=>({}),querySelectorAll:()=>sources})}});results.push(sources.every(s=>s.media==='all')?'christmas':'classic')}const sources=[{media:'not all'}];vm.runInNewContext(input.script,{Intl:{DateTimeFormat(){throw Error('unsupported')}},document:{}});console.log(JSON.stringify({results,fallback:sources[0].media==='not all'}));"""
        result=subprocess.run(['node','-e',js],input=json.dumps({'script':SCRIPT,'instants':instants}),text=True,capture_output=True,check=True)
        result=json.loads(result.stdout)
        self.assertEqual(result['results'],[season_for(datetime.fromisoformat(s)) for s in instants]);self.assertTrue(result['fallback'])
    def test_hero_and_workflow_contract_still_unchanged(self):
        # Calendar operations do not depend on the new browser enhancement.
        for file,get in (('index.html',homepage_hero),('fr/index.html',homepage_hero),('ninja/index.html',hero),('fr/ninja/index.html',hero)):
            source=(ROOT/file).read_text(encoding='utf8')
            self.assertEqual(get(source),get(strip_logo(source)))
        workflow=(ROOT/'.github/workflows/seasonal-ninja-hero.yml').read_text(encoding='utf8')
        self.assertNotIn('seasonal_logo',workflow)

if __name__=='__main__':unittest.main()
