# Générateur Automatique de Meme Coins

Ce projet permet de générer automatiquement des meme coins basés sur des tweets populaires et leur contenu multimédia.

## Caractéristiques

- Analyse de tweets pour détecter des thèmes spécifiques
- Analyse d'images avec OpenAI Vision pour la compréhension du contenu visuel
- Extraction de la première frame des vidéos pour analyse
- Détection de thèmes pertinents (catastrophes naturelles, conflits, technologie, etc.)
- Génération de noms et tickers de meme coins adaptés au contenu et au thème
- Simulateur de tweets pour tester sans API X (Twitter)

## Prérequis

- Python 3.8+
- Clé API OpenAI avec accès à GPT-4 et Vision
- (Optionnel) Clé API Twitter pour la version finale

## Installation

1. Clonez ce dépôt:
```bash
git clone https://github.com/votre-utilisateur/memecoin-generator.git
cd memecoin-generator
```

2. Installez les dépendances: (attention manque dépendances)
```bash
pip install -r requirements.txt
```

3. Créez un fichier `.env` à la racine du projet avec les clés API:
```
OPENAI_API_KEY=votre_cle_api_openai
TWITTER_BEARER_TOKEN=votre_token_twitter
```

## Utilisation

### Mode Simulateur

Pour tester le système sans API Twitter:

```bash
python main.py --mode simulator --data-dir simulator_data
```

Le simulateur vous permettra de:
- Créer des tweets fictifs avec du texte et des URL d'images/vidéos
- Traiter ces tweets pour générer des meme coins
- Voir les résultats d'analyse et de génération

### Structure des fichiers (principaux)

- `config.py` - Configuration globale et thèmes à détecter
- `tweet_analyzer.py` - Analyse du texte des tweets
- `media_analyzer.py` - Analyse des images et vidéos avec OpenAI Vision
- `theme_detector.py` - Détection et consolidation des thèmes
- `memecoin_generator.py` - Générateur de meme coins avec prompts adaptés
- `data_storage.py` - Stockage des données et résultats
- `simulator.py` - Simulateur pour tester sans API Twitter
- `main.py` - Point d'entrée principal

## Fonctionnement détaillé

1. **Récupération du tweet** - Via API ou simulateur
2. **Analyse du texte** - Extraction d'entités, thèmes, mots-clés
3. **Analyse des médias** - Utilisation d'OpenAI Vision pour comprendre les images
4. **Consolidation des thèmes** - Fusion des analyses textuelles et visuelles
5. **Détection du thème principal** - Pour l'adaptation du prompt
6. **Génération du meme coin** - Nom, ticker, slogan et description adaptés au thème

## Futurs développements

- Implémentation de l'écouteur d'API Twitter
- Amélioration de la détection des thèmes
- Intégration avec des plateformes de création de meme coins
- Interface web pour visualiser les résultats
