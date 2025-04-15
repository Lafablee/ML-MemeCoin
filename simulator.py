#simulator.py
import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from config import Config
from tweet_analyzer import TweetAnalyzer
from media_analyzer import MediaAnalyzer
from theme_detector import ThemeDetector
from memecoin_generator import MemecoinsGenerator
from data_storage import DataStorage

class TweetSimulator:
    """Simulateur de tweets pour tester le système sans API Twitter"""

    def __init__(self, config: Config, data_dir="simulator_data"):
        self.config = config
        self.data_dir = data_dir
        
        # Initialiser le logger
        self.logger = logging.getLogger(__name__)
        
        # Initialiser les composants
        self.storage = DataStorage(data_dir=data_dir)
        self.tweet_analyzer = TweetAnalyzer(config)
        self.media_analyzer = MediaAnalyzer(config)
        self.theme_detector = ThemeDetector(config)
        self.memecoin_generator = MemecoinsGenerator(config)
        
        # Créer le répertoire de données
        os.makedirs(data_dir, exist_ok=True)
    
    def create_fake_tweet(self, username: str, text: str, 
                         media_urls: List[Dict[str, str]] = None,
                         likes: int = 0, retweets: int = 0) -> str:
        """
        Crée un tweet fictif avec les données fournies
        
        Args:
            username: Nom d'utilisateur du compte Twitter
            text: Texte du tweet
            media_urls: Liste des URLs des médias
                Format: [{"type": "photo/video", "url": "http://..."}]
            likes: Nombre de likes
            retweets: Nombre de retweets
            
        Returns:
            ID du tweet créé
        """
        # Générer un ID unique pour le tweet
        tweet_id = str(uuid.uuid4()).replace("-", "")[:19]
        
        # Créer un objet tweet similaire à la structure de Twitter
        tweet = {
            "id": tweet_id,
            "text": username + ' ' + text,
            "created_at": datetime.now().isoformat(),
            "public_metrics": {
                "like_count": likes,
                "retweet_count": retweets,
                "reply_count": 0,
                "quote_count": 0
            }
        }
        
        # Ajouter des médias si fournis
        if media_urls:
            tweet["media"] = []
            for idx, media_item in enumerate(media_urls):
                media_type = media_item.get("type", "photo")
                media_url = media_item.get("url", "")
                
                tweet["media"].append({
                    "type": media_type,
                    "url": media_url,
                    "preview_image_url": media_url,
                    "media_key": f"media_key_{tweet_id}_{idx}"
                })
        
        # Sauvegarder le tweet
        self.storage.save_tweet(tweet, username)
        
        self.logger.info(f"Tweet fictif créé avec l'ID {tweet_id} pour @{username}")
        return tweet_id
    
    def process_tweet(self, username: str, tweet_id: str) -> Optional[Dict[str, Any]]:
        """
        Traite un tweet fictif en utilisant uniquement les conditions pour déterminer l'éligibilité
        """
        self.logger.info(f"Traitement du tweet {tweet_id} de @{username}")
        
        # 1. Récupérer le tweet
        tweet = self.storage.get_tweet(username, tweet_id)
        if not tweet:
            self.logger.error(f"Tweet {tweet_id} non trouvé pour @{username}")
            return None

        # 2. Analyser le texte du tweet
        self.logger.info("Analyse du texte du tweet...")
        text_analysis = self.tweet_analyzer.extract_keywords(tweet)
        text_analysis["username"] = username  # Ajouter l'username pour la détection
        self.storage.save_analysis(text_analysis, username)
        
        # 3. Analyser les médias du tweet
        media_analyses = []
        first_media_analysis = None
        
        if "media" in tweet and tweet["media"]:
            self.logger.info(f"Analyse de {len(tweet['media'])} médias...")
            
            for idx, media in enumerate(tweet["media"]):
                media_url = media.get("url") or media.get("preview_image_url")
                media_type = media.get("type", "photo")
                
                if media_url:
                    # Sauvegarder les métadonnées du média
                    self.storage.save_media(tweet_id, username, media_url, media_type, idx)
                    
                    # Analyser le média
                    if media_type == "photo":
                        media_analysis = self.media_analyzer.analyze_image(media_url)
                    elif media_type == "video":
                        media_analysis = self.media_analyzer.process_video(media_url)
                    else:
                        self.logger.warning(f"Type de média non pris en charge: {media_type}")
                        media_analysis = {"error": f"Type de média non pris en charge: {media_type}"}
                    
                    # Sauvegarder l'analyse du média
                    self.storage.save_media_analysis(tweet_id, username, idx, media_analysis)
                    media_analyses.append(media_analysis)

                    # Conserver la première analyse média pour les vérifications
                    if idx == 0:
                        first_media_analysis = media_analysis
        
        # 4. DÉCISION D'ÉLIGIBILITÉ SIMPLIFIÉE: Uniquement basée sur les conditions
        try:
            from condition_handler import extract_ticker_info, is_pattern_eligible
            
            # Vérifier d'abord avec extract_ticker_info (conditions textuelles)
            ticker_info = extract_ticker_info(tweet["text"])
            if ticker_info:
                self.logger.info(f"Tweet éligible via extract_ticker_info: {ticker_info}")
                is_eligible = True
                condition_match = ticker_info
            else:
                # Ensuite vérifier avec is_pattern_eligible (inclut analyse média)
                pattern_result = is_pattern_eligible(tweet["text"], username, first_media_analysis)
                if isinstance(pattern_result, tuple):
                    is_eligible, condition_match = pattern_result
                else: 
                    is_eligible = pattern_result    
                    condition_match = "Détecté via pattern matching"
                self.logger.info(f"Tweet éligible via is_pattern_eligible: {is_eligible}")
            
        except ImportError as e:
            self.logger.error(f"Erreur d'importation de condition_handler: {e}")
            # Fallback via PatternMatcher
            from pattern_matcher import PatternMatcher
            is_eligible = PatternMatcher.is_eligible(tweet["text"], username, first_media_analysis)
            self.logger.info(f"Tweet éligible via PatternMatcher fallback: {is_eligible}")
            condition_match = "Détecté via pattern matcher fallback"
        
        # Si non éligible, sortir immédiatement
        if not is_eligible:
            self.logger.info("Tweet non éligible - aucune condition validée")
            print("\nCe tweet n'est pas éligible pour la génération d'un meme coin:")
            print(f"- Tweet: \"{tweet['text']}\"")
            print("- Aucune condition validée")
            return None
        
        # 5. Extraire les mots-clés pertinents (pour le prompt uniquement)
        relevant_keywords = self.theme_detector.extract_relevant_keywords(
            text_analysis, media_analyses)
        self.logger.info(f"Mots-clés pertinents: {relevant_keywords}")
        
        # 6. Obtenir des instructions de format basées sur les conditions
        from pattern_matcher import PatternMatcher
        memecoin_format = PatternMatcher.get_memecoin_format(tweet["text"], username)
        
        # 7. Générer le meme coin
        self.logger.info("Generating meme coin...")
        memecoin = self.memecoin_generator.generate_memecoin(
            username, 
            tweet["text"], 
            relevant_keywords,
            is_image_primary=(len(tweet["text"].strip()) < 15 and len(media_analyses) > 0),
            format_guidance=memecoin_format,
            media_analysis=first_media_analysis,
            condition_match=condition_match  # Passer la condition déclenchée
        )

        # Vérifier si un code de statut spécial a été retourné
        status_code = memecoin.get("status_code")
        if status_code in [801, 802, 803, 804]:
            # Coder les messages spécifiques pour chaque code
            status_messages = {
                801: "Contenu Elon insuffisamment viral ou impulsif",
                802: "Contenu Trump insuffisamment choquant ou humoristique",
                803: "Contenu de marque sociale trop générique",
                804: "Contenu de marque Elon insuffisamment impactant"
            }
            
            message = status_messages.get(status_code, "Contenu ne répondant pas aux critères de condition")
            self.logger.warning(f"Génération annulée: {message} (code {status_code})")
            print(f"\nGénération non effectuée: {message}")
            
            # Vous pouvez encore enregistrer cet échec pour analyse ultérieure
            self.storage.save_rejected_tweet(tweet_id, username, status_code, message)

            return None
            
        # 8. Sauvegarder le meme coin
        self.storage.save_memecoin(memecoin, username, tweet_id)
        
        self.logger.info(f"Meme coin généré: {memecoin['token_name']} ({memecoin['token_symbol']})")
        
        return memecoin
       
        
    def run_interactive_mode(self):
        """
        Launch an interactive mode to create and process simulated tweets
        """
        print("\n========================================")
        print("TWEET AND MEME COIN SIMULATOR")
        print("========================================\n")
        
        while True:
            print("\nWhat would you like to do?")
            print("1. Create a new simulated tweet")
            print("2. Process an existing tweet")
            print("3. Exit")
            
            choice = input("\nYour choice (1-3): ")
            
            if choice == "1":
                username = input("\nNom d'utilisateur (@username): ")
                if username.startswith("@"):
                    username = username[1:]
                
                text = input("Texte du tweet: ")
                
                media_count = input("Nombre de médias (0-5): ")
                media_count = int(media_count) if media_count.isdigit() else 0
                
                media_urls = []
                print("\nIMPORTANT: Pour les images, utilisez des URL directes d'images (se terminant par .jpg, .png, etc.)")
                print("Les URL de posts Twitter/X, Instagram ou Facebook ne fonctionneront pas correctement.")
                print("Exemples d'URL valides: https://i.imgur.com/example.jpg, https://example.com/image.png\n")
                
                for i in range(min(media_count, 5)):
                    media_type = input(f"Type du média {i+1} (photo/video): ").lower()
                    if media_type not in ["photo", "video"]:
                        media_type = "photo"
                    
                    media_url = input(f"URL du média {i+1}: ")
                    if media_url:
                        # Avertissement pour les URL non directes
                        if media_type == "photo" and not media_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            print("ATTENTION: Cette URL ne semble pas être une URL directe d'image.")
                            continue_anyway = input("Continuer quand même? (o/n): ")
                            if continue_anyway.lower() not in ["o", "oui", "y", "yes"]:
                                continue
                        
                        media_urls.append({"type": media_type, "url": media_url})
                
                likes = input("Nombre de likes (optionnel, défaut=0): ")
                likes = int(likes) if likes.isdigit() else 0
                
                retweets = input("Nombre de retweets (optionnel, défaut=0): ")
                retweets = int(retweets) if retweets.isdigit() else 0
                
                tweet_id = self.create_fake_tweet(
                    username, text, media_urls, likes, retweets)
                
                process_now = input("\nTraiter ce tweet maintenant? (o/n): ")
                if process_now.lower() in ["o", "oui", "y", "yes"]:
                    memecoin = self.process_tweet(username, tweet_id)
                    
                    if memecoin:
                        print("\n========================================")
                        print(f"GENERATED MEME COIN: {memecoin['token_name']} ({memecoin['token_symbol']})")
                        print("========================================\n")
                
            elif choice == "2":
                username = input("\nNom d'utilisateur (@username): ")
                if username.startswith("@"):
                    username = username[1:]
                
                # Afficher les tweets disponibles pour cet utilisateur
                tweets_dir = os.path.join(self.data_dir, "tweets")
                if not os.path.exists(tweets_dir):
                    print(f"Aucun tweet trouvé")
                    continue
                    
                available_tweets = [f for f in os.listdir(tweets_dir) 
                                   if f.startswith(f"{username}_")]
                
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
                        
                        memecoin = self.process_tweet(username, tweet_id)
                        
                        if memecoin:
                            print("\n========================================")
                            print(f"GENERATED MEME COIN: {memecoin['token_name']} ({memecoin['token_symbol']})")
                            print("========================================\n")
                    else:
                        print("Choix invalide")
                except ValueError:
                    print("Veuillez entrer un numéro valide")
            
            elif choice == "3":
                print("\nMerci d'avoir utilisé le simulateur. À bientôt !")
                break
            
            else:
                print("\nChoix invalide, veuillez réessayer")