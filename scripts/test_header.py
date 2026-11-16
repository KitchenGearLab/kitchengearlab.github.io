"""Shared-source, rendered-link and content-preservation contracts."""
import json,re,subprocess,unittest
from html.parser import HTMLParser
from header import ROOT,FRONT,HEAD_INCLUDE,HEADER_INCLUDE,HEADER,without_header,pages,update
from seasonal_hero import hero,homepage_hero,without_hero,without_homepage_hero,replace_hero,replace_homepage_hero

class Links(HTMLParser):
    def __init__(self,source):super().__init__();self.links=[];self.feed(source)
    def handle_starttag(self,t,a):
        a=dict(a)
        if t=='a':self.links.append(a.get('href'))

class HeaderTests(unittest.TestCase):
    def test_every_source_uses_one_include_and_no_copied_header(self):
        self.assertEqual(len(pages()),64)
        for path in pages():
            s=(ROOT/path).read_text(encoding='utf8')
            self.assertTrue(s.startswith(FRONT));self.assertEqual(s.count(HEAD_INCLUDE),1);self.assertEqual(s.count(HEADER_INCLUDE),1)
            self.assertNotIn('<header',s);self.assertNotIn('data-seasonal-logo',s)
        self.assertEqual(update(check=True)['changed'],[])
    def test_rendered_navigation_and_all_existing_links(self):
        rows=json.loads((ROOT/'_data/bilingual-pages.json').read_text(encoding='utf8'))
        for row in rows:
            for lang,prefix in [('en',''),('fr','fr/')]:
                path=prefix+row['file'];s=(ROOT/'_site/header2'/path).read_text(encoding='utf8');header=HEADER.search(s)[0]
                old=subprocess.check_output(['git','show','525617b7862105d329fa9160e9a8650f1a3a1ec0:'+path],cwd=ROOT).decode('utf8')
                with self.subTest(path=path):
                    self.assertEqual(s.count('<header '),1);self.assertNotIn('{%',s);self.assertNotIn('{{',s)
                    self.assertTrue(set(Links(HEADER.search(old)[0]).links)<=set(Links(header).links))
                    self.assertEqual(header.count('class="ninja-mega-category"'),5)
                    self.assertEqual(header.count('<picture data-seasonal-logo'),1)
                    switch=re.search(r'<!-- bilingual:switch:start -->(.*?)<!-- bilingual:switch:end -->',header,re.S)[1]
                    self.assertEqual(Links(switch).links,[row['en'],row['fr']])
                    normalize=lambda text:without_header(text)
                    if row['en']=='/':normalize=lambda text:without_header(without_homepage_hero(text))
                    elif row['en']=='/ninja/':normalize=lambda text:without_header(without_hero(text))
                    self.assertEqual(normalize(s),normalize(old))
    def test_existing_hero_workflow_and_assets_are_unchanged(self):
        base='525617b7862105d329fa9160e9a8650f1a3a1ec0'
        for path,replace,mask in [('index.html',replace_homepage_hero,without_homepage_hero),('fr/index.html',replace_homepage_hero,without_homepage_hero),('ninja/index.html',replace_hero,without_hero),('fr/ninja/index.html',replace_hero,without_hero)]:
            source=(ROOT/path).read_text(encoding='utf8')
            for season in ('classic','christmas'):
                after=replace(source,season,'fr' if path.startswith('fr/') else 'en')
                self.assertEqual(mask(after),mask(source))
                self.assertIn(HEAD_INCLUDE,after);self.assertIn(HEADER_INCLUDE,after)
        self.assertEqual(subprocess.check_output(['git','diff',base,'--','.github/workflows/','scripts/seasonal_hero.py','scripts/seasonal_workflow.py','assets/images/','favicon.ico','site.webmanifest'],cwd=ROOT),b'')

if __name__=='__main__':unittest.main()
