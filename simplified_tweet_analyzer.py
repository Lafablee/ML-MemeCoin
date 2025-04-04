# simplified_tweet_analyzer.py
import re
import spacy
import logging
from typing import Dict, List, Any

class SimplifiedTweetAnalyzer:
    """Version simplifiée de l'analyseur de tweets pour le simulateur"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Mots à ignorer dans l'analyse (liste standard)
        self.stop_words = [
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
        
        # Initialisation de SpaCy pour NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("Modèle SpaCy non trouvé. Installation en cours...")
            import subprocess
            subprocess.call([
                "python", "-m", "spacy", "download", "en_core_web_sm"
            ])
            self.nlp = spacy.load("en_core_web_sm")
    
    def extract_keywords(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les mots-clés importants d'un tweet
        
        Args:
            tweet: Dictionnaire contenant les informations du tweet
        
        Returns:
            Dictionnaire avec les informations d'analyse du tweet
        """
        text = tweet["text"]
        
        # Analyse avec SpaCy
        doc = self.nlp(text)
        
        # Extraction des entités nommées
        named_entities = [
            {"text": ent.text, "type": ent.label_}
            for ent in doc.ents
        ]
        
        # Extraction des mots commençant par une majuscule (hors début de phrase)
        capital_pattern = r'(?<=[\.\!\?\s])[A-Z][a-zA-Z]+'
        capital_words = re.findall(capital_pattern, text)
        
        # Extraction des mots avec symboles spéciaux
        special_symbol_pattern = r'[\$\#\@][a-zA-Z0-9]+'
        symbols = re.findall(special_symbol_pattern, text)
        
        # Extraction des substantifs importants
        important_nouns = [
            token.text for token in doc
            if token.pos_ == "NOUN"
            and token.text.lower() not in self.stop_words
            and len(token.text) > 3
        ]
        
        # Identifiants uniques pour le tweet
        unique_identifiers = list(set(
            capital_words + symbols +
            [ent["text"] for ent in named_entities if ent["type"] in ["PERSON", "ORG", "PRODUCT"]] +
            important_nouns
        ))
        
        # Filtrage des mots vides
        unique_identifiers = [
            word for word in unique_identifiers
            if word.lower() not in self.stop_words
        ]
        
        # Création de l'identité du tweet
        tweet_identity = " ".join(unique_identifiers[:5])  # Limité aux 5 premiers identifiants
        
        # Résultats de l'analyse
        analysis = {
            "tweet_id": tweet["id"],
            "original_text": text,
            "named_entities": named_entities,
            "capital_words": capital_words,
            "symbols": symbols,
            "important_nouns": important_nouns,
            "unique_identifiers": unique_identifiers,
            "tweet_identity": tweet_identity
        }
        
        return analysis