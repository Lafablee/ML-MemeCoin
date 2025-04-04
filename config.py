# config.py
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

class Config:
    """Configuration du système d'indexation et de génération de meme coins"""
    
    # Clés API
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Modèles OpenAI
    OPENAI_TEXT_MODEL = "gpt-4"  # Pour la génération de meme coins
    OPENAI_VISION_MODEL = "gpt-4o"  # Pour l'analyse des images (remplace gpt-4-vision-preview)
    
    # Comptes à surveiller (IDs et usernames)
    CELEBRITY_ACCOUNTS = [
        {"username": "elonmusk", "id": "44196397"},
        {"username": "snoopdogg", "id": "36532825"},
        {"username": "kanyewest", "id": "169686021"},
        {"username": "justinbieber", "id": "27260086"},
        {"username": "rihanna", "id": "79293791"},
        {"username": "kevinhart4real", "id": "26257166"},
        {"username": "kimkardashian", "id": "25365536"},
        {"username": "taylorswift13", "id": "17919972"},
        {"username": "cristiano", "id": "155659213"},
        {"username": "Drake", "id": "27195114"}
    ]
    
    # Configuration de l'API Twitter
    TWEETS_FETCH_LIMIT = 50
    POLLING_INTERVAL_SECONDS = 60
    
    # Configuration des thèmes et déclencheurs
    TRIGGER_THEMES = {
        "catastrophe_naturelle": [
            "tremblement de terre", "séisme", "earthquake", "tsunami", 
            "ouragan", "hurricane", "typhon", "typhoon", "inondation", "flood",
            "tornade", "tornado", "incendie", "wildfire", "avalanche",
            "éruption volcanique", "volcanic eruption", "glissement de terrain", "landslide"
        ],
        "conflit": [
            "guerre", "war", "attentat", "attack", "terrorisme", "terrorism",
            "explosion", "bombe", "bomb", "missile", "frappe", "strike",
            "violence", "combat", "fighting", "invasion", "coup d'état", "coup"
        ],
        "crise_economique": [
            "crash", "krach", "recession", "récession", "inflation", "déflation", "deflation",
            "faillite", "bankruptcy", "chute", "drop", "effondrement", "collapse",
            "crise financière", "financial crisis", "bulle", "bubble"
        ],
        "justice": [
            "procès", "trial", "condamnation", "sentence", "verdict", "prison", "jail",
            "accusation", "charges", "justice", "tribunal", "court", "juge", "judge",
            "avocat", "lawyer", "légal", "legal", "illégal", "illegal", "crime"
        ],
        "celebrite": [
            "scandale", "scandal", "divorce", "rupture", "breakup", "mariage", "wedding",
            "relation", "relationship", "bébé", "baby", "grossesse", "pregnancy",
            "rip", "RIP", "death", "controverse", "controversy", "prix", "award", "price"
        ]
    }
    
    # Mots à ignorer dans l'analyse
    STOP_WORDS = [
        "a", "an", "the", "this", "that", "these", "those",
        "is", "are", "was", "were", "be", "been", "being",
        "and", "but", "or", "for", "nor", "on", "at", "to", "from",
        "by", "about", "like", "with", "after", "before", "when",
        "what", "where", "why", "how", "all", "any", "both", "each",
        "few", "more", "most", "some", "such", "no", "nor", "not",
        "only", "own", "same", "so", "than", "too", "very", "can",
        "will", "just", "should", "now", "I", "you", "he", "she",
        "it", "we", "they", "them", "him", "her", "me", "us"
    ]
    
    # Dossier pour le stockage des données
    DATA_DIR = "data"