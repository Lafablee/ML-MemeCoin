# manual_tweet_simulator.py
import os
import json
import logging
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv
from simplified_tweet_analyzer import SimplifiedTweetAnalyzer
from data_storage import DataStorage
from openai_formatter import OpenAIFormatter

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("manual_simulator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ManualTweetSimulator:
    """
    Simulateur de tweets manuel qui permet de créer des tweets fictifs
    et de les traiter avec le système existant
    """
    
    def __init__(self, data_dir="manual_data"):
        """
        Initialise le simulateur
        
        Args:
            data_dir: Répertoire de stockage des données
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Créer les sous-répertoires nécessaires
        os.makedirs(os.path.join(data_dir, "tweets"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "analysis"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "pumpfun"), exist_ok=True)
        
        self.storage = DataStorage(data_dir=data_dir)
        self.analyzer = SimplifiedTweetAnalyzer()  # Utilisation de l'analyseur simplifié
        
        # Vérifier que la clé API OpenAI est disponible
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("La clé API OpenAI est manquante. Définissez OPENAI_API_KEY dans le fichier .env")
            raise ValueError("Clé API OpenAI manquante")
        
        self.formatter = OpenAIFormatter(api_key=openai_api_key, data_dir=data_dir)
    
    def create_fake_tweet(self, username, text, likes=0, retweets=0, image_url=None):
        """
        Crée un tweet fictif avec les données fournies
        
        Args:
            username: Nom d'utilisateur du compte Twitter
            text: Texte du tweet
            likes: Nombre de likes (optionnel)
            retweets: Nombre de retweets (optionnel)
            image_url: URL d'une image associée (optionnel)
            
        Returns:
            ID du tweet créé
        """
        # Générer un ID unique pour le tweet
        tweet_id = str(uuid.uuid4()).replace("-", "")[:19]
        
        # Créer un objet tweet similaire à la structure de Twitter
        tweet = {
            "id": tweet_id,
            "text": text,
            "created_at": datetime.now().isoformat(),
            "public_metrics": {
                "like_count": likes,
                "retweet_count": retweets,
                "reply_count": 0,
                "quote_count": 0
            }
        }
        
        # Ajouter une image si fournie
        if image_url:
            tweet["media"] = [{
                "type": "photo",
                "url": image_url,
                "preview_image_url": image_url,
                "media_key": f"media_key_{tweet_id}"
            }]
        
        # Sauvegarder le tweet
        self.storage.save_tweet(tweet, username)
        
        logger.info(f"Tweet fictif créé avec l'ID {tweet_id} pour @{username}")
        return tweet_id
    
    def process_tweet(self, username, tweet_id):
        """
        Traite un tweet fictif en utilisant le pipeline existant
        
        Args:
            username: Nom d'utilisateur du compte Twitter
            tweet_id: ID du tweet à traiter
            
        Returns:
            Données du meme coin généré
        """
        # Lire le tweet sauvegardé
        tweet_file = os.path.join(self.data_dir, "tweets", f"{username}_{tweet_id}.json")
        
        if not os.path.exists(tweet_file):
            logger.error(f"Tweet {tweet_id} non trouvé pour {username}")
            return None
        
        with open(tweet_file, "r") as f:
            tweet = json.load(f)
        
        # Analyser le tweet
        analysis = self.analyzer.extract_keywords(tweet)
        self.storage.save_analysis(analysis, username)
        
        logger.info(f"Analyse du tweet {tweet_id} terminée")
        logger.info(f"Identité extraite: {analysis['tweet_identity']}")
        
        # Générer le meme coin avec OpenAI
        try:
            logger.info("Génération du meme coin avec OpenAI...")
            meme_coin = self.formatter.generate_meme_coin(username, tweet_id)
            
            # Sauvegarder les données formatées
            pumpfun_file = os.path.join(self.data_dir, "pumpfun", f"{username}_{tweet_id}.json")
            
            with open(pumpfun_file, "w") as f:
                json.dump(meme_coin, f, indent=2)
            
            logger.info(f"Meme coin généré avec succès: {meme_coin['token_name']} ({meme_coin['token_symbol']})")
            logger.info(f"Tag line: {meme_coin.get('tag_line', 'N/A')}")
            
            return meme_coin
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du meme coin: {str(e)}")
            return None
    
    def test_custom_prompt(self, username, tweet_id, custom_system_prompt):
        """
        Teste un prompt système personnalisé pour la génération du meme coin
        
        Args:
            username: Nom d'utilisateur du compte Twitter
            tweet_id: ID du tweet à traiter
            custom_system_prompt: Prompt système personnalisé pour OpenAI
            
        Returns:
            Données du meme coin généré
        """
        # Sauvegarder le prompt système original
        original_prompt = self.formatter.system_prompt
        
        try:
            # Définir le nouveau prompt système
            self.formatter.system_prompt = custom_system_prompt
            
            # Générer le meme coin avec le nouveau prompt
            logger.info("Génération du meme coin avec prompt personnalisé...")
            meme_coin = self.formatter.generate_meme_coin(username, tweet_id)
            
            # Sauvegarder les données formatées avec un suffixe spécial
            pumpfun_file = os.path.join(self.data_dir, "pumpfun", f"{username}_{tweet_id}_custom.json")
            
            with open(pumpfun_file, "w") as f:
                json.dump(meme_coin, f, indent=2)
            
            logger.info(f"Meme coin généré avec prompt personnalisé: {meme_coin['token_name']} ({meme_coin['token_symbol']})")
            
            return meme_coin
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du meme coin avec prompt personnalisé: {str(e)}")
            return None
        finally:
            # Restaurer le prompt système original
            self.formatter.system_prompt = original_prompt

def interactive_mode():
    """
    Mode interactif pour créer et traiter des tweets fictifs
    """
    simulator = ManualTweetSimulator()
    
    print("\n========================================")
    print("SIMULATEUR DE TWEETS ET MEME COINS")
    print("========================================\n")
    
    while True:
        print("\nQue souhaitez-vous faire ?")
        print("1. Créer un nouveau tweet fictif")
        print("2. Traiter un tweet existant")
        print("3. Tester un prompt système personnalisé")
        print("4. Quitter")
        
        choice = input("\nVotre choix (1-4): ")
        
        if choice == "1":
            username = input("\nNom d'utilisateur (@username): ")
            if username.startswith("@"):
                username = username[1:]
            
            text = input("Texte du tweet: ")
            likes = input("Nombre de likes (optionnel, défaut=0): ")
            likes = int(likes) if likes else 0
            
            retweets = input("Nombre de retweets (optionnel, défaut=0): ")
            retweets = int(retweets) if retweets else 0
            
            image_url = input("URL de l'image (optionnel): ")
            image_url = image_url if image_url else None
            
            tweet_id = simulator.create_fake_tweet(username, text, likes, retweets, image_url)
            
            process_now = input("\nTraiter ce tweet maintenant? (o/n): ")
            if process_now.lower() == "o" or process_now.lower() == "oui":
                meme_coin = simulator.process_tweet(username, tweet_id)
                if meme_coin:
                    print("\n========================================")
                    print(f"MEME COIN GÉNÉRÉ: {meme_coin['token_name']} ({meme_coin['token_symbol']})")
                    print(f"TAG LINE: {meme_coin.get('tag_line', 'N/A')}")
                    print(f"DESCRIPTION: {meme_coin['description']}")
                    print("========================================\n")
        
        elif choice == "2":
            username = input("\nNom d'utilisateur (@username): ")
            if username.startswith("@"):
                username = username[1:]
            
            # Afficher les tweets disponibles pour cet utilisateur
            tweets_dir = os.path.join(simulator.data_dir, "tweets")
            available_tweets = [f for f in os.listdir(tweets_dir) if f.startswith(f"{username}_")]
            
            if not available_tweets:
                print(f"Aucun tweet trouvé pour @{username}")
                continue
            
            print(f"\nTweets disponibles pour @{username}:")
            for i, tweet_file in enumerate(available_tweets):
                tweet_id = tweet_file.replace(f"{username}_", "").replace(".json", "")
                
                # Lire le tweet pour afficher son texte
                with open(os.path.join(tweets_dir, tweet_file), "r") as f:
                    tweet = json.load(f)
                
                print(f"{i+1}. ID: {tweet_id} - \"{tweet['text'][:50]}...\"")
            
            tweet_choice = input("\nChoisissez un tweet (numéro): ")
            try:
                tweet_index = int(tweet_choice) - 1
                if 0 <= tweet_index < len(available_tweets):
                    tweet_file = available_tweets[tweet_index]
                    tweet_id = tweet_file.replace(f"{username}_", "").replace(".json", "")
                    
                    meme_coin = simulator.process_tweet(username, tweet_id)
                    if meme_coin:
                        print("\n========================================")
                        print(f"MEME COIN GÉNÉRÉ: {meme_coin['token_name']} ({meme_coin['token_symbol']})")
                        print(f"TAG LINE: {meme_coin.get('tag_line', 'N/A')}")
                        print(f"DESCRIPTION: {meme_coin['description']}")
                        print("========================================\n")
                else:
                    print("Choix invalide")
            except ValueError:
                print("Veuillez entrer un numéro valide")
        
        elif choice == "3":
            username = input("\nNom d'utilisateur (@username): ")
            if username.startswith("@"):
                username = username[1:]
            
            # Afficher les tweets disponibles pour cet utilisateur
            tweets_dir = os.path.join(simulator.data_dir, "tweets")
            available_tweets = [f for f in os.listdir(tweets_dir) if f.startswith(f"{username}_")]
            
            if not available_tweets:
                print(f"Aucun tweet trouvé pour @{username}")
                continue
            
            print(f"\nTweets disponibles pour @{username}:")
            for i, tweet_file in enumerate(available_tweets):
                tweet_id = tweet_file.replace(f"{username}_", "").replace(".json", "")
                
                # Lire le tweet pour afficher son texte
                with open(os.path.join(tweets_dir, tweet_file), "r") as f:
                    tweet = json.load(f)
                
                print(f"{i+1}. ID: {tweet_id} - \"{tweet['text'][:50]}...\"")
            
            tweet_choice = input("\nChoisissez un tweet (numéro): ")
            try:
                tweet_index = int(tweet_choice) - 1
                if 0 <= tweet_index < len(available_tweets):
                    tweet_file = available_tweets[tweet_index]
                    tweet_id = tweet_file.replace(f"{username}_", "").replace(".json", "")
                    
                    print("\nEntrez votre prompt système personnalisé (terminez par une ligne vide):")
                    prompt_lines = []
                    while True:
                        line = input()
                        if not line:
                            break
                        prompt_lines.append(line)
                    
                    custom_prompt = "\n".join(prompt_lines)
                    
                    if not custom_prompt:
                        print("Prompt vide, opération annulée")
                        continue
                    
                    meme_coin = simulator.test_custom_prompt(username, tweet_id, custom_prompt)
                    if meme_coin:
                        print("\n========================================")
                        print(f"MEME COIN GÉNÉRÉ (PROMPT PERSONNALISÉ): {meme_coin['token_name']} ({meme_coin['token_symbol']})")
                        print(f"TAG LINE: {meme_coin.get('tag_line', 'N/A')}")
                        print(f"DESCRIPTION: {meme_coin['description']}")
                        print("========================================\n")
                else:
                    print("Choix invalide")
            except ValueError:
                print("Veuillez entrer un numéro valide")
        
        elif choice == "4":
            print("\nMerci d'avoir utilisé le simulateur. À bientôt !")
            break
        
        else:
            print("\nChoix invalide, veuillez réessayer")

if __name__ == "__main__":
    interactive_mode()