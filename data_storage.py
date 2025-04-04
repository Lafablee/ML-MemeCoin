#data_storage.py
import json
import os
import datetime
import logging
from typing import Dict, List, Any, Optional

class DataStorage:
    """Stockage des données des tweets indexés et des meme coins générés"""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.ensure_data_dir()
        self.latest_tweet_ids = self.load_latest_tweet_ids()
        self.logger = logging.getLogger(__name__)

    def ensure_data_dir(self):
        """Assure que le répertoire de données existe"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Créer les sous-répertoires nécessaires
        for subdir in ["tweets", "analysis", "media", "media_analysis", "memecoins"]:
            path = os.path.join(self.data_dir, subdir)
            if not os.path.exists(path):
                os.makedirs(path)

    def load_latest_tweet_ids(self) -> Dict[str, str]:
        """Charge les derniers IDs de tweets traités par utilisateur"""
        latest_ids_file = os.path.join(self.data_dir, "latest_tweet_ids.json")
        
        if os.path.exists(latest_ids_file):
            with open(latest_ids_file, "r") as f:
                return json.load(f)
        return {}

    def save_latest_tweet_ids(self):
        """Sauvegarde les derniers IDs de tweets traités"""
        latest_ids_file = os.path.join(self.data_dir, "latest_tweet_ids.json")
        
        with open(latest_ids_file, "w") as f:
            json.dump(self.latest_tweet_ids, f)

    def save_tweet(self, tweet: Dict[str, Any], username: str):
        """Sauvegarde un tweet dans le stockage"""
        tweet_file = os.path.join(self.data_dir, "tweets", f"{username}_{tweet['id']}.json")
        
        with open(tweet_file, "w") as f:
            json.dump(tweet, f, indent=2)
        
        # Mise à jour du dernier ID de tweet pour cet utilisateur
        self.latest_tweet_ids[username] = tweet["id"]
        self.save_latest_tweet_ids()
        return tweet_file

    def save_analysis(self, analysis: Dict[str, Any], username: str):
        """Sauvegarde l'analyse d'un tweet"""
        analysis_file = os.path.join(self.data_dir, "analysis", 
                                    f"{username}_{analysis['tweet_id']}.json")
        
        with open(analysis_file, "w") as f:
            json.dump(analysis, f, indent=2)
        return analysis_file

    def save_media(self, tweet_id: str, username: str, media_url: str, 
                  media_type: str, media_index: int = 0) -> str:
        """
        Sauvegarde l'URL d'un média et ses métadonnées
        
        Args:
            tweet_id: ID du tweet
            username: Nom d'utilisateur
            media_url: URL du média
            media_type: Type de média (photo, video, etc.)
            media_index: Index du média dans le tweet
            
        Returns:
            Chemin du fichier média sauvegardé
        """
        media_data = {
            "tweet_id": tweet_id,
            "username": username,
            "media_url": media_url,
            "media_type": media_type,
            "media_index": media_index,
            "indexed_at": datetime.datetime.now().isoformat()
        }
        
        media_file = os.path.join(self.data_dir, "media", 
                               f"{username}_{tweet_id}_{media_index}.json")
        
        with open(media_file, "w") as f:
            json.dump(media_data, f, indent=2)
        return media_file

    def save_media_analysis(self, tweet_id: str, username: str, 
                           media_index: int, analysis: Dict[str, Any]) -> str:
        """
        Sauvegarde l'analyse d'un média
        
        Args:
            tweet_id: ID du tweet
            username: Nom d'utilisateur
            media_index: Index du média dans le tweet
            analysis: Résultats de l'analyse du média
            
        Returns:
            Chemin du fichier d'analyse sauvegardé
        """
        media_analysis_file = os.path.join(self.data_dir, "media_analysis", 
                                      f"{username}_{tweet_id}_{media_index}.json")
        
        with open(media_analysis_file, "w") as f:
            json.dump(analysis, f, indent=2)
        return media_analysis_file

    def save_memecoin(self, memecoin_data: Dict[str, Any], username: str, tweet_id: str) -> str:
        """
        Sauvegarde les données d'un meme coin généré
        
        Args:
            memecoin_data: Données du meme coin
            username: Nom d'utilisateur
            tweet_id: ID du tweet
            
        Returns:
            Chemin du fichier meme coin sauvegardé
        """
        memecoin_file = os.path.join(self.data_dir, "memecoins", 
                                    f"{username}_{tweet_id}.json")
        
        with open(memecoin_file, "w") as f:
            json.dump(memecoin_data, f, indent=2)
        return memecoin_file

    def get_latest_tweet_id(self, username: str) -> Optional[str]:
        """Récupère le dernier ID de tweet pour un utilisateur donné"""
        return self.latest_tweet_ids.get(username)
    
    def get_tweet(self, username: str, tweet_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un tweet stocké"""
        tweet_file = os.path.join(self.data_dir, "tweets", f"{username}_{tweet_id}.json")
        
        if os.path.exists(tweet_file):
            with open(tweet_file, "r") as f:
                return json.load(f)
        return None
    
    def get_analysis(self, username: str, tweet_id: str) -> Optional[Dict[str, Any]]:
        """Récupère l'analyse d'un tweet"""
        analysis_file = os.path.join(self.data_dir, "analysis", f"{username}_{tweet_id}.json")
        
        if os.path.exists(analysis_file):
            with open(analysis_file, "r") as f:
                return json.load(f)
        return None
    
    def get_media(self, username: str, tweet_id: str, media_index: int = 0) -> Optional[Dict[str, Any]]:
        """Récupère les métadonnées d'un média"""
        media_file = os.path.join(self.data_dir, "media", 
                               f"{username}_{tweet_id}_{media_index}.json")
        
        if os.path.exists(media_file):
            with open(media_file, "r") as f:
                return json.load(f)
        return None
    
    def get_media_analysis(self, username: str, tweet_id: str, 
                          media_index: int = 0) -> Optional[Dict[str, Any]]:
        """Récupère l'analyse d'un média"""
        media_analysis_file = os.path.join(self.data_dir, "media_analysis", 
                                      f"{username}_{tweet_id}_{media_index}.json")
        
        if os.path.exists(media_analysis_file):
            with open(media_analysis_file, "r") as f:
                return json.load(f)
        return None
    
    def get_memecoin(self, username: str, tweet_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les données d'un meme coin"""
        memecoin_file = os.path.join(self.data_dir, "memecoins", f"{username}_{tweet_id}.json")
        
        if os.path.exists(memecoin_file):
            with open(memecoin_file, "r") as f:
                return json.load(f)
        return None