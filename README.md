# WallPaperS_ColleCtoR

Galerie offline auto-générée d'une collection de fonds d'écran HD **100% gratuits**.

## Description

Outil qui scanne le dossier `WallPaperS/`, détecte tous les "tiroirs" (sous-dossiers) et génère une galerie HTML statique navigable, **100% locale**, sans serveur ni dépendance externe pour fonctionner.

## Fonctionnalités

### Page d'accueil (`index.html` racine)

- **Hero** avec titre shimmer animé, badge flottant **« 100% Gratuit · Téléchargement libre »** et paragraphe descriptif
- **Bandeau de stats** : nombre total de wallpapers, nombre de tiroirs, qualité HD, gratuité
- **Panneau d'intro** expliquant l'usage (clic, Échap, gratuit pour usage personnel)
- **Mosaïque de tuiles** : chaque tiroir affiche un wallpaper preview en background, avec overlay dégradé, pill **« Gratuit »** en coin haut-droite, et tailles variées (`tall`, `wide`) pour rythmer le visuel
- **Fond de secours dégradé feu** (4 couches radiales jaune/orange/rouge + base ember) avec animation `fireFlicker` — visible si une image preview ne charge pas
- Tiroirs vides (zéro image) automatiquement masqués

### Pages tiroirs

- **Galerie** en grille adaptative
- **Pagination automatique** (60 images / page) pour les gros tiroirs — pages reliées (`index.html`, `page-2.html`, ...)
- **Lightbox** : clic sur une image → affichage plein écran. Échap (ou clic) → ferme
- **Sous-dossiers** listés en bas si le tiroir en contient
- **10 thèmes visuels** distincts (Aurora, Neon, Sakura, Ocean, Sunset, Forest, Galaxy, Lava, Mint, Royal) attribués par hash du nom de dossier → chaque tiroir = ambiance différente

### Communes à toutes les pages

- **Thème Clair / Sombre** togglable, persisté via `localStorage`
- **Bouton Accueil** + **Bouton Parent** sur chaque sous-page
- Backgrounds animés, blobs flottants, animations d'apparition par tuile
- Boilerplate (favicon, CSS/JS externe filedn.eu, menu social, header) injecté sur chaque page
- Chemins relatifs partout → fonctionne en double-clic sur le `index.html`

## Structure

```
WallPaperS_ColleCtoR/
├── index.html               # accueil — hero + mosaïque des tiroirs
├── generate_indexes.py      # générateur de galerie
├── .gitignore               # exclut images/vidéos/archives
├── README.md
└── WallPaperS/              # racine des tiroirs
    ├── index.html
    ├── Beaches/
    │   ├── index.html       # galerie tiroir
    │   └── page-2.html      # pagination si > 60 images
    ├── diverse/
    │   ├── index.html
    │   ├── page-2.html
    │   └── ...              # jusqu'à page-16.html (951 images)
    └── ...
```

## Utilisation

### Génération / régénération de la galerie

```bash
python generate_indexes.py
```

À relancer après chaque ajout/suppression d'images ou de tiroirs.

### Visualiser

Ouvrir [index.html](index.html) dans un navigateur (double-clic ou `file://...`).

### Ajouter des images

1. Déposer les images dans un sous-dossier de `WallPaperS/` (créer un nouveau tiroir si besoin)
2. Relancer `python generate_indexes.py`
3. Ouvrir `index.html`

### Formats supportés

`jpg`, `jpeg`, `png`, `gif`, `webp`, `bmp`, `tiff`, `tif`, `avif`, `jfif`

## Configuration

Constantes en tête de [generate_indexes.py](generate_indexes.py) :

| Constante | Défaut | Rôle |
|-----------|--------|------|
| `IMAGES_PER_PAGE` | `60` | Images par page (pagination) |
| `IMG_EXTS` | jpg, png, ... | Extensions reconnues |
| `THEMES` | 10 thèmes | Palette de styles visuels par tiroir |

Les tuiles « feu » de la page d'accueil sont configurées dans `ROOT_EXTRA_CSS` (variable `.tile`) et dans `build_root_page()` (couches `radial-gradient` empilées).

## Stack

- Python 3 (stdlib uniquement, aucune dépendance)
- HTML5 / CSS3 (variables CSS, grid, keyframes, backdrop-filter) / Vanilla JS

## Versionnement

Les médias (images, vidéos, archives) sont **exclus** du dépôt via [.gitignore](.gitignore). Seuls le code Python, les pages HTML générées et les fichiers projet sont versionnés. La structure de dossiers est préservée par les `index.html` générés (et `.gitkeep` pour les tiroirs vides).

## Licence

Wallpapers proposés à titre **gratuit pour usage personnel**.

## Auteur

[Delfosse-Pascal](https://github.com/Delfosse-Pascal)
