#theme_detector.py
import logging
from typing import Dict, List, Any, Optional, Tuple
from config import Config

class ThemeDetector:
    """
    Classe simplifiée pour détecter l'éligibilité et extraire des mots-clés pertinents,
    en se basant principalement sur les conditions du condition_handler.py
    """

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Import pattern matcher from condition_handler
        try:
            from condition_handler import is_pattern_eligible
            self.pattern_matcher = is_pattern_eligible
        except ImportError:
            self.logger.warning("Could not import pattern matching functions")
            self.pattern_matcher = None
    
    def consolidate_themes(self, text_analysis: Dict[str, Any], 
                          media_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Version simplifiée qui collecte les informations essentielles sans 
        se focaliser sur les thèmes spécifiques
        """
        # Get only basic information from text
        tweet_text = text_analysis.get("original_text", "").strip()
        has_minimal_text = len(tweet_text) < 15

        # Initialize consolidated dictionary with minimal theme information
        consolidated = {
            "is_meme": False,
            "is_crisis": False,
            "eligible_sources": [],
            "has_minimal_text": has_minimal_text,
            "primary_source": "text" if not has_minimal_text else "media",
            "username": text_analysis.get("username", ""),
            "original_text": tweet_text,
            "unique_identifiers": text_analysis.get("unique_identifiers", []),
            "named_entities": text_analysis.get("named_entities", [])
        }
        
        # Process each media analysis for essential flags only
        for idx, media_analysis in enumerate(media_analyses):
            try:
                if "error" in media_analysis:
                    self.logger.warning(f"Error in media {idx} analysis: {media_analysis['error']}")
                    consolidated["eligible_sources"].append(f"media_{idx}_error")
                    continue
                
                # Check only special flags that matter for conditions
                if media_analysis.get("is_meme", False):
                    consolidated["is_meme"] = True
                    consolidated["eligible_sources"].append(f"media_{idx}_meme")
                
                if media_analysis.get("is_crisis", False):
                    consolidated["is_crisis"] = True
                    consolidated["eligible_sources"].append(f"media_{idx}_crisis")
                
                # Store important elements from media analysis
                if "subjects" in media_analysis:
                    consolidated["media_subjects"] = media_analysis.get("subjects", [])
                    consolidated["eligible_sources"].append(f"media_{idx}_subjects")
                
                if "visible_text" in media_analysis:
                    consolidated["media_text"] = media_analysis.get("visible_text", [])
                    consolidated["eligible_sources"].append(f"media_{idx}_text")
                
                # Store full description for prompt use
                if "description" in media_analysis:
                    consolidated["media_description"] = media_analysis.get("description", "")
                    consolidated["eligible_sources"].append(f"media_{idx}_description")
                
            except Exception as e:
                self.logger.error(f"Error processing media analysis {idx}: {str(e)}")
        
        return consolidated
    
    def get_primary_theme(self, consolidated_themes: Dict[str, Any]) -> Optional[str]:
        """
        Version simplifiée qui retourne un thème générique basé sur les flags
        sans complexité excessive
        """
        # Default theme based on flags
        if consolidated_themes.get("is_meme", False):
            return "meme"
        
        if consolidated_themes.get("is_crisis", False):
            return "crisis"
        
        # Check media elements
        if "media_subjects" in consolidated_themes:
            subjects = " ".join([str(s) for s in consolidated_themes["media_subjects"] if s]).lower()
            
            # Basic content type detection
            if any(term in subjects for term in ["dog", "cat", "animal"]):
                return "animal"
                
            if any(term in subjects for term in ["person", "human", "people"]):
                return "person"
            
            if any(term in subjects for term in ["tech", "computer", "digital"]):
                return "technologie"
        
        # Default generic theme
        return "general"
    
    def is_content_eligible(self, consolidated_themes: Dict[str, Any]) -> bool:
        """
        Déterminer l'éligibilité principalement avec condition_handler.is_pattern_eligible
        """
        username = consolidated_themes.get("username", "").lower()
        original_text = consolidated_themes.get("original_text", "")
        
        # Get media analysis if available for the condition handler
        media_analysis = None
        if "media_description" in consolidated_themes:
            media_analysis = {
                "description": consolidated_themes.get("media_description", ""),
                "subjects": consolidated_themes.get("media_subjects", []),
                "is_meme": consolidated_themes.get("is_meme", False),
                "is_crisis": consolidated_themes.get("is_crisis", False)
            }
        
        # Primary eligibility check using condition handler
        try:
            from condition_handler import is_pattern_eligible
            if is_pattern_eligible(original_text, username, media_analysis):
                self.logger.info("Content eligible based on pattern matching")
                return True
        except Exception as e:
            self.logger.error(f"Error with pattern eligibility check: {str(e)}")
        
        # Backup checks if pattern matcher fails
        if consolidated_themes.get("is_meme", False) or consolidated_themes.get("is_crisis", False):
            return True
            
        if len(consolidated_themes.get("eligible_sources", [])) > 0:
            return True
            
        return False
    
    def extract_relevant_keywords(self, text_analysis: Dict[str, Any], 
                                 media_analyses: List[Dict[str, Any]],
                                 primary_theme: Optional[str] = None) -> List[str]:
        """
        Extracts relevant keywords focusing on entities and media content
        without theme-based filtering
        """
        keywords = set()
        
        # Extract from text analysis
        if "unique_identifiers" in text_analysis:
            keywords.update(text_analysis["unique_identifiers"])
        
        # Add named entities with higher priority
        if "named_entities" in text_analysis:
            for entity in text_analysis["named_entities"]:
                if entity["type"] in ["PERSON", "ORG", "PRODUCT", "EVENT", "LOC", "FAC"]:
                    keywords.add(entity["text"])
        
        # Extract from media analyses
        for media_analysis in media_analyses:
            if "error" in media_analysis:
                continue
            
            # Add subjects from image analysis
            if "subjects" in media_analysis and isinstance(media_analysis["subjects"], list):
                for subject in media_analysis["subjects"]:
                    if subject:
                        keywords.add(str(subject))
            
            # Add visible text from images
            if "visible_text" in media_analysis and isinstance(media_analysis["visible_text"], list):
                for text in media_analysis["visible_text"]:
                    if text and len(str(text)) > 2:
                        keywords.add(str(text))
        
        # Filter out stopwords and short keywords
        filtered_keywords = [kw for kw in keywords 
                            if len(str(kw)) > 2 and str(kw).lower() not in self.config.STOP_WORDS]
        
        return filtered_keywords[:10]  # Return up to 10 keywords