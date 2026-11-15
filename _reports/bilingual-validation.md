# KitchenGearLab — validation bilingue du 15 novembre 2026

32 pages anglaises inventoriées et conservées; 32 équivalents français complets sous `/fr/`, soit 64 pages canoniques. Les chemins anglais restent inchangés. L’inventaire et les correspondances sont dans `_data/bilingual-pages.json`.

2 319 segments uniques examinés : 2 185 traductions et 134 éléments volontairement identiques (marques, modèles, unités, nombres, noms techniques ou mots communs aux deux langues). Français canadien; aucun service de traduction injecté et aucune génération du contenu au chargement. Le catalogue explicite refuse les traductions manquantes.

## Vérifications réussies avant publication

- 9 338 contrôles statiques : 64 pages, canonical autoréférentielles, langues canadiennes, hreflang réciproques, métadonnées uniques, 66 blocs JSON-LD valides, réponses FAQ cohérentes avec le contenu visible, liens et ancres internes, sitemap de 64 URL annotées.
- 128 rendus Chrome : chaque page à 320 et 1440 px, sans débordement ni image brisée. Navigation partagée vérifiée aussi à 375, 430, 768, 1024 px et en paysage, avec agrandissement du texte à 200 %.
- 266 contrôles navigateur hors axe réussis : correspondances EN/FR, navigation sans JavaScript, cinq catégories du méga-menu, fermeture avec Échap, liens d’achat et événements d’affiliation synthétiques sans requête Amazon.
- Après correction des noms accessibles des liens de langue et des CTA français, analyse axe des 64 pages sans violation détectée (WCAG A/AA et règles de bonnes pratiques sélectionnées).
- Lighthouse mobile local sur la fiche Crispi FN101CGY : EN 99/100/100/100 et FR 99/100/100/100 pour performance/accessibilité/bonnes pratiques/SEO; LCP environ 1,95 s, CLS 0, temps de blocage 0 ms. Analytics bloqué pendant ces mesures de laboratoire.
- Images, srcset, dimensions, chargement et scripts de production conservés; aucune dépendance JavaScript ajoutée. Ajout CSS limité au sélecteur et à son placement responsive.
- Par langue : 72 liens Amazon.ca actifs avec les mêmes destinations, ASIN, attributs commerciaux, données de suivi et tag `kitchengearla-20`; sept CTA Philips suspendus avec avertissements électriques. Aucun prix, stock, modèle ou niveau de vérification commerciale ajouté.
- Génération reproductible : `python -X utf8 scripts/bilingual.py build --check` ne produit aucun changement.

## Correction historique ciblée

Une réponse visible de la FAQ du guide des friteuses Ninja différait de sa réponse JSON-LD. Le texte visible est aligné sur la formulation prudente déjà présente dans le schéma, en anglais et en français. Les autres contenus éditoriaux anglais, titres, descriptions et canonical sont conservés. Les anciens marqueurs `en-US` sont harmonisés vers `en-CA`.

## Réserves et publication

Aucun dépôt ApocalypseGearLab trouvé dans les emplacements locaux examinés. Aucun essai physique ni nouvelle caractéristique commerciale inventés. Les noms officiels des programmes et couleurs restent parfois en anglais, comme repères techniques.

Les analyses axe ne sont pas une certification d’accessibilité. Les mesures Lighthouse sont locales, sans validation des Core Web Vitals réels ni garantie de classement. Les réserves préexistantes sur les variantes, garanties et tensions électriques restent visibles.

Le moteur Jekyll n’est pas disponible dans le PATH local. Le site publie du HTML statique : la compilation GitHub Pages et l’intégrité des fichiers publics seront vérifiées après le push autorisé. Le rapport final de déploiement sera consigné dans `_reports/bilingual-release.md`.
