import re
import spacy
import logging
from typing import Dict, List, Any, Optional, Set
from config import Config

class TweetAnalyzer:
    """Classe pour analyser et extraire les informations importantes des tweets"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
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
            and token.text.lower() not in self.config.STOP_WORDS
            and len(token.text) > 3
        ]
        
        # Extraction des verbes significatifs 
        significant_verbs = [
            token.text for token in doc
            if token.pos_ == "VERB"
            and token.text.lower() not in self.config.STOP_WORDS
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
            if word.lower() not in self.config.STOP_WORDS
        ]
        
        # Création de l'identité du tweet
        tweet_identity = " ".join(unique_identifiers[:5])  # Limité aux 5 premiers identifiants
        
        # Détection des thèmes potentiels
        detected_themes = self.detect_themes(text)

        # Prioritize hashtags, $symbols, and proper nouns
        prioritized_identifiers = []
        
        # Find currency symbols like $DOGE
        currency_pattern = r'\$[A-Za-z0-9]+'
        currency_symbols = re.findall(currency_pattern, text)
        if currency_symbols:
            prioritized_identifiers.extend(currency_symbols)
        
        # Add proper nouns and symbols
        for identifier in unique_identifiers:
            if identifier.startswith('#') or identifier.startswith('$'):
                prioritized_identifiers.append(identifier)
            elif identifier[0].isupper():
                prioritized_identifiers.append(identifier)
        
        # Place prioritized identifiers at the beginning
        unique_identifiers = prioritized_identifiers + [id for id in unique_identifiers if id not in prioritized_identifiers]
        
        # Limit unique identifiers to most relevant ones
        unique_identifiers = unique_identifiers[:10]
        
        # Résultats de l'analyse
        analysis = {
            "tweet_id": tweet["id"],
            "original_text": text,
            "named_entities": named_entities,
            "capital_words": capital_words,
            "symbols": symbols,
            "important_nouns": important_nouns,
            "significant_verbs": significant_verbs,
            "unique_identifiers": unique_identifiers,
            "tweet_identity": tweet_identity,
            "detected_themes": detected_themes
        }
        
        return analysis
    
    def detect_themes(self, text: str) -> Dict[str, List[str]]:
        """
        Détecte les thèmes potentiels dans le texte du tweet
        
        Args:
            text: Texte du tweet
            
        Returns:
            Dictionnaire des thèmes détectés avec les termes correspondants
        """
        text_lower = text.lower()
        detected_themes = {}
        
        for theme, keywords in self.config.TRIGGER_THEMES.items():
            matches = []
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matches.append(keyword)
            
            if matches:
                detected_themes[theme] = matches
                
        return detected_themes
    
    def is_tweet_eligible(self, analysis: Dict[str, Any]) -> bool:
        """
        Détermine si un tweet est éligible pour la génération d'un meme coin
        basé sur son contenu et les thèmes détectés
        
        Args:
            analysis: Résultats de l'analyse du tweet
            
        Returns:
            True si le tweet est éligible, False sinon
        """
        # Vérifier si des thèmes ont été détectés
        if analysis["detected_themes"]:
            return True
        
        # Vérifier s'il y a des hashtags ou mentions intéressants
        if any(symbol.startswith('#') for symbol in analysis["symbols"]):
            hashtags = [s for s in analysis["symbols"] if s.startswith('#')]
            # On pourrait ajouter une logique supplémentaire pour filtrer
            # les hashtags pertinents
            if hashtags:
                return True
        
        # Le tweet doit avoir un minimum de substance
        if len(analysis["unique_identifiers"]) < 2:
            return False
        
        # Vérifier les entités nommées d'intérêt
        interesting_entities = [
            ent for ent in analysis["named_entities"]
            if ent["type"] in ["PERSON", "ORG", "PRODUCT", "EVENT"]
        ]
        
        if len(interesting_entities) > 0:
            return True
            
        return False
    
    def get_main_theme(self, analysis: Dict[str, Any]) -> Optional[str]:
        """
        Détermine le thème principal d'un tweet pour l'adaptation du prompt
        
        Args:
            analysis: Résultats de l'analyse du tweet
            
        Returns:
            Le thème principal ou None si aucun thème n'est détecté
        """
        if not analysis["detected_themes"]:
            return None
        
        # Sélectionner le thème avec le plus de correspondances
        max_matches = 0
        main_theme = None
        
        for theme, matches in analysis["detected_themes"].items():
            if len(matches) > max_matches:
                max_matches = len(matches)
                main_theme = theme
                
        return main_theme