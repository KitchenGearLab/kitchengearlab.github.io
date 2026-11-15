# KitchenGearLab — validation du hero Ninja saisonnier

15 novembre 2026, heure de Toronto. État avant publication : Noël.

## Périmètre

La seule modification visuelle est le hero des pages `/ninja/` et `/fr/ninja/`. Leur HTML hors `<figure class="hero-media">` est identique au commit bilingue précédent : titres, navigation, catégories, boutons, produits, canonical, hreflang, JSON-LD, métadonnées sociales, liens et suivi Amazon. Aucun CSS, script visiteur, sitemap ou autre page n’est modifié.

Deux originaux fournis conservés à l’identique sous `_originals/seasonal-ninja/`, exclus du site public. SHA-256 :

- Classique : `a31007957451f2634605324afe3d320fede9bed3e32dcab5a154952349fd3cf3`.
- Noël : `e8e14b6b8b0de6acd120c0bbd2c6bbdcf5c151390b325f6ac59d9e31677046a6`.

30 variantes optimisées dans `assets/images/hero/ninja-collection/` : cinq largeurs, trois formats (AVIF, WebP, JPEG), deux saisons. Dimensions natives 1672 × 941; aucun recadrage, réagencement, changement de texte ou recours à un générateur d’images. En AVIF à 960 px : 70 169 octets pour classique et 132 475 pour Noël. Original PNG de Noël : 2 804 069 octets. Encodage et empreintes dans `_data/seasonal-ninja-hero.json`.

## Automatisation

Workflow : `.github/workflows/seasonal-ninja-hero.yml`, chaque jour à 00 h 17 America/Toronto et sur demande manuelle. Sélection fondée sur la date réelle d’exécution : classique du 1er janvier au 31 octobre, Noël du 1er novembre au 26 décembre inclus, classique du 27 au 31 décembre, chaque année.

Permissions vides au niveau global; seulement `contents: write` et `pages: write` pour le job concerné. Checkout v6 épinglé à son SHA officiel. Concurrence unique, actualisation de `main`, aucune poussée forcée. Seules les deux pages peuvent être commises, uniquement si elles changent. Le job demande explicitement le build Pages legacy habituel, attend le commit exact et répare une publication manquée sans autre commit. Une version déjà publiée ou en cours ne provoque pas une nouvelle compilation.

## Contrôles réussis

- 16 tests automatisés, incluant 132 cas de bornes calendaires pour 2026–2036, neuf cas UTC/DST, assets, idempotence, reprise après exécution manquée et déduplication Pages.
- Intégration Git réelle dans un dépôt temporaire isolé : une transition produit un commit modifiant deux fichiers; une deuxième exécution n’en produit aucun et laisse l’arbre propre.
- 9 360 contrôles bilingues existants sur les 64 pages; génération bilingue reproductible sans changement.
- 40 contrôles navigateur : 12 rendus EN/FR aux largeurs 320, 375, 430, 768, 1024 et 1440 px; géométrie extérieure au hero préservée; aucune image cassée ni débordement; un seul élément image prioritaire.
- Deux analyses axe sans violation. Deux saisons et trois formats testés sans JavaScript, y compris les chemins de repli WebP et JPEG dans des fixtures isolées. Navigation de langue exacte conservée.
- Hero et contenu sans déplacement mesuré. Un très petit mouvement préexistant du logo dans le header est enregistré séparément, également observé sur l’ancienne page; branding et CSS sont conservés conformément au périmètre.
- Lighthouse mobile local `/fr/ninja/` : performance 100, accessibilité 100, bonnes pratiques 100, SEO 100; LCP environ 1,2 s, CLS 0 et temps de blocage 0 ms. Analytics bloqué; résultats de laboratoire.

## Limites de la plateforme

GitHub peut retarder ou abandonner une exécution planifiée. La prochaine exécution réconcilie la date courante. La bascule est donc effective après l’exécution et la compilation Pages, sans garantie à la seconde de minuit.

GitHub désactive les tâches planifiées des dépôts publics sans activité depuis 60 jours. Une réactivation peut alors être nécessaire; aucun faux commit de maintien ni build quotidien inutile n’est ajouté. Un fonctionnement garanti sur un dépôt indéfiniment inactif demanderait un ordonnanceur externe, absent de cette solution GitHub Actions.

Le déploiement et les deux exécutions manuelles seront vérifiés après publication; le rapport final est `_reports/seasonal-release.md`.
