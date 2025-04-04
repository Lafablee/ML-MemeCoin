# test_twitter_api.py
import os
import logging
from dotenv import load_dotenv
from config import Config
from twitter_client import TwitterClient
from tweet_analyzer import TweetAnalyzer
from data_storage import DataStorage
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

cached_tweets = {}

def test_twitter_connection():
    """Teste la connexion à l'API Twitter"""
    logger.info("Test de connexion à l'API Twitter...")
    
    config = Config()
    client = TwitterClient(config)
    
    # Vérifier la présence du token
    if not config.TWITTER_BEARER_TOKEN:
        logger.error("Token Twitter manquant. Vérifiez votre fichier .env")
        return False
    
    # Testez avec un compte connu
    test_account = config.CELEBRITY_ACCOUNTS[0]
    tweets = client.get_recent_tweets(test_account["id"])
    
    if not tweets:
        logger.error(f"Échec de récupération des tweets pour {test_account['username']}")
        return False
    
    logger.info(f"Connexion réussie! {len(tweets)} tweets récupérés pour {test_account['username']}")
    
    # Afficher un exemple de tweet
    if tweets:
        logger.info(f"Exemple de tweet: {tweets[0]['text'][:100]}...")
    
    return True

def test_tweet_analysis():
    """Teste l'analyse des tweets"""
    logger.info("Test de l'analyse des tweets...")
    
    config = Config()
    client = TwitterClient(config)
    analyzer = TweetAnalyzer(config)
    
    # Récupérer quelques tweets pour l'analyse
    test_account = config.CELEBRITY_ACCOUNTS[0]
    #tweets = client.get_recent_tweets(test_account["id"], limit=3)
    tweets = cached_tweets.get('elonmusk')
    if not tweets:
        tweets = client.get_recent_tweets(test_account["id"])
        cached_tweets['elonmusk'] = tweets
        logger.error("Impossible de tester l'analyse: aucun tweet récupéré")
        return False
    
    # Analyser chaque tweet
    for idx, tweet in enumerate(tweets):
        logger.info(f"Analyse du tweet {idx+1}...")
        
        analysis = analyzer.extract_keywords(tweet)
        
        logger.info(f"Tweet original: {tweet['text'][:100]}...")
        logger.info(f"Identité du tweet: {analysis['tweet_identity']}")
        logger.info(f"Entités nommées: {analysis['named_entities']}")
        logger.info(f"Symboles: {analysis['symbols']}")
        logger.info(f"Mots avec majuscule: {analysis['capital_words']}")
        logger.info(f"Identifiants uniques: {analysis['unique_identifiers']}")
        logger.info("-" * 50)
    
    return True

def test_data_storage():
    """Teste le stockage des données"""
    logger.info("Test du stockage des données...")
    
    config = Config()
    client = TwitterClient(config)
    analyzer = TweetAnalyzer(config)
    storage = DataStorage(data_dir="test_data")
    
    # Récupérer un tweet pour le test
    test_account = config.CELEBRITY_ACCOUNTS[0]
    tweets = client.get_recent_tweets(test_account["id"], limit=1)
    
    if not tweets:
        logger.error("Impossible de tester le stockage: aucun tweet récupéré")
        return False
    
    tweet = tweets[0]
    username = test_account["username"]
    
    # Sauvegarder le tweet
    storage.save_tweet(tweet, username)
    logger.info(f"Tweet {tweet['id']} sauvegardé")
    
    # Analyser et sauvegarder l'analyse
    analysis = analyzer.extract_keywords(tweet)
    storage.save_analysis(analysis, username)
    logger.info(f"Analyse du tweet {tweet['id']} sauvegardée")
    
    # Vérifier que les fichiers existent
    tweet_file = os.path.join(storage.data_dir, "tweets", f"{username}_{tweet['id']}.json")
    analysis_file = os.path.join(storage.data_dir, "analysis", f"{username}_{tweet['id']}.json")
    
    if os.path.exists(tweet_file) and os.path.exists(analysis_file):
        logger.info("Stockage des données réussi!")
        return True
    else:
        logger.error("Échec du stockage des données")
        return False

def test_full_pipeline():
    """Teste tout le pipeline de A à Z"""
    logger.info("Test du pipeline complet...")
    
    config = Config()
    client = TwitterClient(config)
    analyzer = TweetAnalyzer(config)
    storage = DataStorage(data_dir="test_data")
    
    # Choisir un compte
    test_account = config.CELEBRITY_ACCOUNTS[0]
    username = test_account["username"]
    user_id = test_account["id"]
    
    logger.info(f"Traitement des tweets de {username}...")
    
    # Récupérer les tweets
    tweets = client.get_recent_tweets(user_id, limit=5)
    
    if not tweets:
        logger.error(f"Aucun tweet récupéré pour {username}")
        return False
    
    logger.info(f"{len(tweets)} tweets récupérés")
    
    # Traiter chaque tweet
    for tweet in tweets:
        # Sauvegarder le tweet
        storage.save_tweet(tweet, username)
        
        # Analyser et sauvegarder l'analyse
        analysis = analyzer.extract_keywords(tweet)
        storage.save_analysis(analysis, username)
        
        # Traiter les médias
        if "media" in tweet:
            for media in tweet["media"]:
                media_url = media.get("url") or media.get("preview_image_url")
                if media_url:
                    storage.save_media(
                        tweet["id"], 
                        username, 
                        media_url, 
                        media["type"]
                    )
        
        logger.info(f"Tweet {tweet['id']} traité - Identité: {analysis['tweet_identity']}")
    
    logger.info("Pipeline complet testé avec succès!")
    return True

if __name__ == "__main__":
    print("=== TESTS DE L'INDEXATION TWITTER ===")
    
    # Exécuter les tests
    connection_ok = test_twitter_connection()
    
    if not connection_ok:
        print("❌ Échec de connexion à l'API Twitter. Tests arrêtés.")
        exit(1)
    
    analysis_ok = test_tweet_analysis()
    storage_ok = test_data_storage()
    pipeline_ok = test_full_pipeline()
    
    # Résumé
    print("\n=== RÉSUMÉ DES TESTS ===")
    print(f"1. Connexion API Twitter: {'✅ OK' if connection_ok else '❌ Échec'}")
    print(f"2. Analyse des tweets: {'✅ OK' if analysis_ok else '❌ Échec'}")
    print(f"3. Stockage des données: {'✅ OK' if storage_ok else '❌ Échec'}")
    print(f"4. Pipeline complet: {'✅ OK' if pipeline_ok else '❌ Échec'}")
    
    if all([connection_ok, analysis_ok, storage_ok, pipeline_ok]):
        print("\n✅ TOUS LES TESTS ONT RÉUSSI")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")