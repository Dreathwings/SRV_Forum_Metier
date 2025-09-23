# SRV Forum Métier

## Génération automatique de badges

Le dépôt contient maintenant un outil pour produire des badges
d'identification individuels à partir d'un template SVG.

### Pré-requis

* Python 3.9 ou plus récent.
* Les dépendances standard de la bibliothèque standard suffisent pour
  générer des fichiers SVG.
* (Optionnel) [`cairosvg`](https://cairosvg.org/) pour exporter aussi en PDF
  ou en PNG : `pip install cairosvg`.

### Préparer les données

1. Exportez les inscriptions au format CSV depuis l'interface d'administration
   (`dump.csv` est un exemple). Les colonnes `p1_nom`, `p1_prenom`, etc. sont
   interprétées automatiquement.
2. Vérifiez que le fichier est encodé en UTF‑8 (les exports fournis par la
   plateforme le sont).

### Personnaliser le template

Le fichier `static/ressources/badge_template.svg` sert de base à chaque badge.
Il contient des éléments texte avec des identifiants (`id="company"`,

`id="full_name"`, `id="role"`, `id="email"`). Deux zones `image` sont
pré-configurées : `id="logo_geii"` pour le logo du département et
`id="company_logo"` pour le logo de l'entreprise.
=======
`id="full_name"`, `id="role"`, `id="email"`).


* Modifiez le style ou la disposition directement dans le fichier SVG.
* Laissez intacts les attributs `id` des éléments que le script doit remplir.


### Ajouter les logos d'entreprise

Le script intègre automatiquement le logo du département GEII (fichier
`static/ressources/geii_logo.svg`) en haut à gauche du badge.

Pour afficher le logo d'une entreprise en haut à droite :

1. Déposez son fichier image dans le dossier `static/ressources/logos/` (vous
   pouvez créer des sous-dossiers si besoin et fournir un chemin via l'option
   `--logo-dirs`). Les formats `.png`, `.jpg`, `.jpeg`, `.svg` et `.webp` sont
   pris en charge.
2. Nommez le fichier selon le nom de l'entreprise (par exemple
   `Ma_Entreprise.png`). Les accents et caractères spéciaux sont automatiquement
   normalisés.
3. Lors de la génération, le script associera le logo correspondant au badge de
   chaque participant.

Si aucun fichier local n'est trouvé, une recherche automatique est effectuée en
ligne via le service public Clearbit Logo. Le script interroge l'API
`/autocomplete` pour déterminer le domaine de l'entreprise, puis télécharge le
logo depuis `https://logo.clearbit.com/`. Cette étape nécessite un accès réseau
sortant ; en cas d'échec, la zone de logo reste vide. Utilisez l'option
`--no-online-logos` si vous souhaitez désactiver complètement cette recherche.

=======

### Générer les badges

```bash
python generate_badges.py dump.csv static/ressources/badge_template.svg \
    --output generated_badges --formats svg
```

L'exemple ci-dessus crée un badge par participant dans le dossier
`generated_badges/`. Les fichiers sont nommés avec un index et le nom du
participant (`001_Dupont_Jeanne.svg`, etc.).


Si vos logos sont stockés dans un autre dossier, ajoutez l'argument
`--logo-dirs` :

```bash
python generate_badges.py dump.csv static/ressources/badge_template.svg \
    --output generated_badges --formats svg \
    --logo-dirs /chemin/vers/mes/logos
```

=======

Pour exporter également des PDF ou des PNG (nécessite `cairosvg`) :

```bash
python generate_badges.py dump.csv static/ressources/badge_template.svg \
    --output generated_badges --formats svg pdf png
```

### Télécharger les badges depuis l'interface admin

Depuis le tableau de bord (`/forum-metier/admin`), un bouton « Télécharger les badges (ZIP) » permet de générer automatiquement les fichiers SVG pour l'ensemble des participants et de les récupérer sous la forme d'une archive compressée.

### Structure d'un badge généré

Chaque badge reprend les informations suivantes :

* **Entreprise** — Nom de l'organisation (`ent_nom`).
* **Nom et prénom** — Combinaison des champs `pX_nom` et `pX_prenom`.
* **Poste** — Valeur de `pX_poste` si fournie, sinon la mention « Poste ».
* **Adresse e-mail** — Valeur de `pX_email`.

Les champs vides sont automatiquement remplacés par des valeurs par défaut.

