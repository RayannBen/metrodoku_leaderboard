# AGENTS.md

## Vision du projet

Ce projet extrait des messages WhatsApp Metrodoku pour construire un leaderboard Streamlit deployable.
L'application doit fonctionner avec des exports WhatsApp reels, puis offrir un affichage leaderboard + dashboard.

## Organisation actuelle (source de verite)

Le code applicatif vit sous `app/`.

- `app/app.py`
  - Entree Streamlit principale.
  - UI (leaderboard + dashboard) et chargement des donnees.

- `app/src/message.py`
  - Modeles de donnees `Message`, `MetrodokuMessage`, `MessageFactory`.

- `app/src/extract.py`
  - Parsing des exports WhatsApp en objets metier.
  - Support de plusieurs formats de ligne d'en-tete (ancien et nouveau format WhatsApp).

- `app/data/`
  - Exports WhatsApp versionnes dans le repo.
  - L'app peut auto-selectionner l'extract le plus recent via le nom de fichier `extract_dd_mm(.txt|_yyyy.txt)`.

- `tests/`
  - Tests unitaires de parsing/message.

## Regle importante d'execution

- Working directory attendu: `app/`.
- Lancement local recommande:

```bash
cd app
uv run streamlit run app.py
```

- Deploiement Streamlit Cloud:
  - Main file path: `app/app.py`
  - Working directory: `app`

## Conventions de code

- Changements incrementaux et testes.
- Pas de refactor massif sans besoin explicite.
- Garder la logique metier dans `app/src/*` (et non dans la couche UI).
- Ajouter/adapter les tests quand le parsing evolue.

## Notes parsing

- Formats d'en-tete supportes:
  - `dd/mm/yyyy, hh:mm - Auteur: ...`
  - `[dd/mm/yyyy hh:mm:ss] Auteur: ...`
- Detection Metrodoku basee sur le contenu du message.
- Score attendu au format `Score : N/900`.