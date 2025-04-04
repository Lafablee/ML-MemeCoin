#twitter_client.py
import requests
import time
import logging
from typing import List, Dict, Any
from config import Config

class TwitterClient:
    """Client pour l'API Twitter v2"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {config.TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)
    
    def get_recent_tweets(self, user_id: str, since_id: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """
        Récupère les tweets récents d'un utilisateur spécifique
        Args:
            user_id: ID Twitter de l'utilisateur
            since_id: ID du dernier tweet récupéré (pour pagination)
            limit: Nombre maximum de tweets à récupérer (optionnel)
        Returns:
            Liste de tweets avec leurs détails
        """
        endpoint = f"{self.base_url}/users/{user_id}/tweets"
        
        params = {
            "max_results": self.config.TWEETS_FETCH_LIMIT,
            "expansions": "attachments.media_keys,author_id,referenced_tweets.id",
            "tweet.fields": "id,text,created_at,attachments,entities,public_metrics",
            "media.fields": "type,url,preview_image_url,media_key",
            "user.fields": "name,username,profile_image_url"
        }
        
        if since_id:
            params["since_id"] = since_id
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Traitement pour inclure les médias dans les tweets
            if "data" not in data:
                self.logger.info(f"Aucun nouveau tweet pour l'utilisateur {user_id}")
                return []
            
            tweets = data["data"]
            
            # Traitement des médias
            if "includes" in data and "media" in data["includes"]:
                media_dict = {m["media_key"]: m for m in data["includes"]["media"]}
                
                for tweet in tweets:
                    if "attachments" in tweet and "media_keys" in tweet["attachments"]:
                        tweet["media"] = [
                            media_dict.get(media_key) 
                            for media_key in tweet["attachments"]["media_keys"]
                            if media_key in media_dict
                        ]
            if limit is not None and tweets:
                tweets = tweets[:limit] 

            if response.status_code == 429:
                retry_after = int(response.headers('retry-after', 60))
                self.logger.warning(f"Rate limit Twitter atteint. Attente de {retry_after} secondes.")
                time.sleep(retry_after)               
            
            return tweets
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur lors de la récupération des tweets: {str(e)}")
            if response.status_code == 429:
                # Rate limit atteint, attendre avant de réessayer
                self.logger.warning("Rate limit Twitter atteint. Attente avant nouvel essai.")
                time.sleep(60)  # Attendre 1 minute
            return []