# pumpfun_formatter.py
import re
import json
import os
import logging
from typing import Dict, Any, Optional, List
import hashlib

class PumpFunFormatter:
    """
    Classe pour formater les données des tweets analysés pour l'API PumpFun
    """
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        
        # Mots tendance qui peuvent rendre un meme coin plus attractif
        self.trending_keywords = [
            "moon", "pump", "gem", "pepe", "doge", "shiba", "chad", "wojak", 
            "bullish", "elon", "giga", "mega", "alpha", "based", "rare", "epic",
            "crypto", "diamond", "hodl", "fomo", "ape", "rocket", "x"
        ]
        
    def _extract_trending_keyword(self, text: str) -> Optional[str]:
        """Extrait un mot tendance du texte s'il existe"""
        lowercase_text = text.lower()
        for keyword in self.trending_keywords:
            if keyword in lowercase_text:
                # Trouver le mot complet contenant le keyword
                pattern = r'\b\w*' + re.escape(keyword) + r'\w*\b'
                matches = re.findall(pattern, lowercase_text)
                if matches:
                    return matches[0]
        return None
    
    def _generate_token_name(self, username: str, analysis: Dict[str, Any]) -> str:
        """Génère un nom accrocheur pour le token"""
        # Essayer de trouver un mot tendance dans le tweet
        trending_word = self._extract_trending_keyword(analysis["original_text"])
        
        # Chercher des entités nommées intéressantes
        product_entities = [ent["text"] for ent in analysis["named_entities"] 
                            if ent["type"] in ["PRODUCT", "ORG", "EVENT"]]
        
        # Chercher des mots avec symboles (hashtags, $)
        symbol_words = [word.strip("#$@") for word in analysis["symbols"]]
        
        # Priorité: Trending word > Product entities > Symbol words > Important nouns
        if trending_word:
            base_name = trending_word.title()
        elif product_entities:
            base_name = product_entities[0]
        elif symbol_words:
            base_name = symbol_words[0].title()
        elif analysis["important_nouns"]:
            base_name = analysis["important_nouns"][0].title()
        else:
            # Fallback
            base_name = f"{username}Tweet"
        
        # Ajouter un préfixe ou suffixe lié à l'auteur
        if not username.lower() in base_name.lower():
            return f"{username}{base_name}"
        return base_name
    
    def _generate_token_symbol(self, token_name: str, analysis: Dict[str, Any]) -> str:
        """Génère un symbole court (3-5 caractères) pour le token"""
        # Méthode 1: Acronyme des mots du nom du token
        words = re.findall(r'[A-Z][a-z]*', token_name)
        if words and len(words) >= 2:
            symbol = ''.join([word[0] for word in words])
            if 3 <= len(symbol) <= 5:
                return symbol.upper()
        
        # Méthode 2: Utiliser des hashtags du tweet s'ils existent
        hashtags = [tag.strip('#') for tag in analysis["symbols"] if tag.startswith('#')]
        if hashtags and 3 <= len(hashtags[0]) <= 5:
            return hashtags[0].upper()
        
        # Méthode 3: Première partie du token_name
        if len(token_name) >= 3:
            return token_name[:min(5, len(token_name))].upper()
        
        # Fallback: Hash du tweet_id
        tweet_id = analysis["tweet_id"]
        hash_obj = hashlib.md5(tweet_id.encode())
        return hash_obj.hexdigest()[:4].upper()
    
    def _generate_description(self, username: str, analysis: Dict[str, Any], tweet: Dict[str, Any]) -> str:
        """Génère une description concise et pertinente du meme coin"""
        # Commencer par une intro captivante
        if "public_metrics" in tweet and "like_count" in tweet["public_metrics"] and tweet["public_metrics"]["like_count"] > 1000:
            intro = f"Viral tweet by {username} with {tweet['public_metrics']['like_count']} likes! "
        else:
            intro = f"{username}'s tweet that shook the cryptosphere! "
        
        # Ajouter des mots-clés
        if analysis["unique_identifiers"]:
            keywords = ", ".join(analysis["unique_identifiers"][:3])
            keyword_part = f"About: {keywords}. "
        else:
            keyword_part = ""
        
        # Ajouter une courte citation du tweet (max 50 caractères)
        text = analysis["original_text"]
        if len(text) > 50:
            # Trouver la fin d'un mot proche de 50 caractères
            cutoff = text.rfind(" ", 30, 50)
            if cutoff == -1:  # Pas d'espace trouvé
                cutoff = 50
            short_text = text[:cutoff] + "..."
        else:
            short_text = text
        
        return intro + keyword_part + f'"{short_text}"'
    
    def format_for_pumpfun(self, username: str, tweet_id: str) -> Dict[str, Any]:
        """
        Formate les données pour PumpFun à partir des fichiers stockés
        
        Args:
            username: Nom d'utilisateur du compte Twitter
            tweet_id: ID du tweet
            
        Returns:
            Dictionnaire formaté pour l'API PumpFun
        """
        # Lire les fichiers stockés
        tweet_file = os.path.join(self.data_dir, "tweets", f"{username}_{tweet_id}.json")
        analysis_file = os.path.join(self.data_dir, "analysis", f"{username}_{tweet_id}.json")
        
        if not (os.path.exists(tweet_file) and os.path.exists(analysis_file)):
            self.logger.error(f"Fichiers manquants pour {username}_{tweet_id}")
            return {}
        
        with open(tweet_file, "r") as f:
            tweet_data = json.load(f)
        
        with open(analysis_file, "r") as f:
            analysis_data = json.load(f)
        
        # Trouver l'URL de média pour l'image de profil
        profile_image_url = None
        if "media" in tweet_data and tweet_data["media"]:
            for media in tweet_data["media"]:
                # Priorité aux images
                if media["type"] == "photo":
                    profile_image_url = media.get("url") or media.get("preview_image_url")
                    break
            
            # Si pas d'image, prendre le premier média disponible
            if not profile_image_url and tweet_data["media"]:
                profile_image_url = tweet_data["media"][0].get("url") or tweet_data["media"][0].get("preview_image_url")
        
        # Générer le nom et le symbole du token
        token_name = self._generate_token_name(username, analysis_data)
        token_symbol = self._generate_token_symbol(token_name, analysis_data)
        
        # Générer la description
        description = self._generate_description(username, analysis_data, tweet_data)
        
        # Structure pour PumpFun
        pumpfun_data = {
            "token_name": token_name,
            "token_symbol": token_symbol,
            "description": description,
            "tweet_reference": tweet_id,
            "tweet_identity": analysis_data["tweet_identity"],
            "tweet_author": username,
            "profile_image_url": profile_image_url,
            "original_tweet_text": analysis_data["original_text"],
            "metadata": {
                "named_entities": analysis_data["named_entities"],
                "symbols": analysis_data["symbols"],
                "unique_identifiers": analysis_data["unique_identifiers"],
                "important_nouns": analysis_data["important_nouns"],
                "public_metrics": tweet_data.get("public_metrics", {})
            }
        }
        
        return pumpfun_data