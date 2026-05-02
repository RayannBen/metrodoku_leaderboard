# AGENTS.md

## Vision du projet

Ce repository sert a extraire et structurer des messages WhatsApp contenant des resultats de Metrodoku,
afin de construire un leaderboard exploitable dans une application Streamlit puis la deployer.

Contexte metier:
- Les exports WhatsApp contiennent des messages libres + messages de score Metrodoku.
- Un message Metrodoku contient en general: mot-cle `metrodoku`, date, `Score : x/900`, grille 3x3.
- Le leaderboard doit permettre de comparer les joueurs sur la duree.

## Stack et outillage

- Python `>=3.12`
- Gestion projet/deps: `uv` + `pyproject.toml`
- Tests: `pytest`
- Qualite statique: `ruff`, `mypy`
- Dataframe: `pandas`

Commande de verification principale:

```bash
uv run pytest
```

## Organisation du repository

- `src/message.py`
  - Modeles de message:
    - `Message`: message WhatsApp generique (content, author, timestamp)
    - `MetrodokuMessage`: message specialise avec `score` et extraction de grille
  - `MessageFactory`: detection et instanciation du bon type de message.

- `src/extract.py`
  - Classe `Extract` qui:
    - decoupe un export brut en messages individuels,
    - detecte les debuts de message WhatsApp,
    - convertit via `MessageFactory`,
    - expose des methodes d'agregation (`get_all_authors`, filtrage Metrodoku, `to_dataframe`).

- `tests/`
  - Jeux de tests unitaires pour parser, factory, et classes de message.
  - `tests/fixtures/__init__.py` centralise des fixtures texte.

- `data/`
  - Exemples d'exports WhatsApp pour tests manuels / reproductibilite.

- `main.py`
  - Point d'entree minimal actuel.

## Conventions de code observees

- Preferer des classes/methodes simples et lisibles.
- Type hints utilises sur les signatures publiques.
- Parsing tolerant aux formats imparfaits (fallback sur valeurs par defaut).
- Encapsulation metier dans les modeles (`from_txt`, `serialize`, extraction score/grille).
- Tests axes comportement metier plutot que details d'implementation.

## Hypotheses de parsing importantes

- Debut de message WhatsApp detecte par regex:
  - `dd/mm/yyyy, hh:mm - auteur: contenu`
- Detection Metrodoku actuelle:
  - presence du mot `métrodoku` dans le contenu.
- Score Metrodoku:
  - attendu sous la forme `Score : N/900`.
- Grille:
  - basee sur les caracteres `🟩` et `⬜`.

## Style de collaboration attendu pour les agents

- Faire des changements incrementaux et testes.
- Eviter les refactors larges non demandes.
- Ne pas casser les API existantes sans raison explicite.
- Ajouter/mettre a jour les tests avec toute evolution du parsing.
- Prioriser robustesse sur exports reels WhatsApp (accents, lignes vides, messages systeme).

## Roadmap proche

1. Construire l'app Streamlit
   - Chargement d'un fichier texte WhatsApp.
   - Parsing via `Extract`.
   - Construction du leaderboard (score moyen, meilleur score, nombre de parties, evolution temporelle).
   - Visualisations simples (tableau + graphes).

2. Preparer le deploiement
   - Ajouter dependances Streamlit.
   - Ajouter point d'entree app (`streamlit_app.py` ou equivalent).
   - Ajouter instructions d'execution locale dans `README.md`.
   - Choisir cible de deploiement (Streamlit Community Cloud en priorite).

3. Fiabiliser
   - Completer jeux de tests sur cas reels (messages multiline, noms avec caracteres speciaux, variations d'emojis).
   - Verifier qualite statique (`ruff`, `mypy`).

## Definition of Done (phase actuelle)

- Le parsing de base est couvert par tests unitaires.
- Le projet est pret pour la phase suivante: creation de l'interface Streamlit et deploiement.