#theme_detector.py
import logging
from typing import Dict, List, Any, Optional, Tuple
from config import Config

class ThemeDetector:
    """
    Classe pour détecter et consolider les thèmes d'un tweet
    à partir des analyses textuelles et visuelles
    """

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Add import for condition handler
        try:
            from condition_handler import is_pattern_eligible
            self.pattern_matcher = is_pattern_eligible
        except ImportError:
            self.logger.warning("Could not import pattern matching functions")
            self.pattern_matcher = None
    
    def consolidate_themes(self, text_analysis: Dict[str, Any], 
                          media_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidates themes detected in text and media
        
        Args:
            text_analysis: Tweet text analysis
            media_analyses: List of media analyses from the tweet
            
        Returns:
            Dictionary of consolidated themes and relevant data
        """
        # Get themes detected in text
        text_themes = text_analysis.get("detected_themes", {})
        
        # Check if tweet has minimal text
        tweet_text = text_analysis.get("original_text", "").strip()
        has_minimal_text = len(tweet_text) < 15  # Consider tweets with less than 15 chars as minimal
        
        # Initialize consolidated dictionary
        consolidated = {
            "themes": {},
            "is_meme": False,
            "is_crisis": False,
            "crisis_type": None,
            "eligible_sources": [],
            "has_minimal_text": has_minimal_text,
            "primary_source": "text" if not has_minimal_text else "media"
        }
        
        # Ajouter les thèmes du texte
        for theme, matches in text_themes.items():
            if theme not in consolidated["themes"]:
                consolidated["themes"][theme] = []
            consolidated["themes"][theme].extend(matches)
        
        # Si des thèmes ont été trouvés dans le texte
        if text_themes:
            consolidated["eligible_sources"].append("text")
        
        # Process each media analysis
        for idx, media_analysis in enumerate(media_analyses):
            # If the analysis contains errors, log but continue 
            # with available data
            try:
                if "error" in media_analysis:
                    self.logger.warning(f"Error in media {idx} analysis: {media_analysis['error']}")
                    # Add error source for tracking
                    consolidated["eligible_sources"].append(f"media_{idx}_error")
                    continue
                
                # Check special flags
                if media_analysis.get("is_meme", False):
                    consolidated["is_meme"] = True
                
                if media_analysis.get("is_crisis", False):
                    consolidated["is_crisis"] = True
                    if media_analysis.get("crisis_type") and not consolidated["crisis_type"]:
                        consolidated["crisis_type"] = media_analysis["crisis_type"]
                
                # Add media themes
                media_themes = media_analysis.get("detected_themes", {})
                for theme, matches in media_themes.items():
                    if theme not in consolidated["themes"]:
                        consolidated["themes"][theme] = []
                    # Ensure matches is a list of strings
                    if isinstance(matches, list):
                        consolidated["themes"][theme].extend([str(m) for m in matches if m is not None])
                    elif matches is not None:
                        consolidated["themes"][theme].append(str(matches))
                
                # If themes or special flags found in this media
                eligible_media = (media_themes or 
                                 media_analysis.get("is_meme", False) or 
                                 media_analysis.get("is_crisis", False))
                
                if eligible_media:
                    consolidated["eligible_sources"].append(f"media_{idx}")
            except Exception as e:
                self.logger.error(f"Error processing media analysis {idx}: {str(e)}")
                import traceback
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
                # Continue with other media analyses
        
        # Dédupliquer les matches dans chaque thème
        for theme in consolidated["themes"]:
            consolidated["themes"][theme] = list(set(consolidated["themes"][theme]))
        
        return consolidated
    
    def get_primary_theme(self, consolidated_themes: Dict[str, Any]) -> Optional[str]:
        """
        Détermine le thème principal à partir des thèmes consolidés
        
        Args:
            consolidated_themes: Thèmes consolidés
            
        Returns:
            Le thème principal ou None si aucun thème n'est pertinent
        """
        # S'il n'y a pas de thèmes détectés
        if not consolidated_themes["themes"]:
            # Si c'est un mème
            if consolidated_themes["is_meme"]:
                return "meme"
            
            # Si c'est une crise
            if consolidated_themes["is_crisis"]:
                crisis_type = consolidated_themes.get("crisis_type", "").lower()
                if crisis_type:
                    if any(kw in crisis_type for kw in ["natural", "earthquake", "flood", "hurricane"]):
                        return "catastrophe_naturelle"
                    elif any(kw in crisis_type for kw in ["war", "conflict", "attack", "violence"]):
                        return "conflit"
                    elif any(kw in crisis_type for kw in ["economic", "financial", "crash"]):
                        return "crise_economique"
                return "crisis"
            
            return None
        
        # Sélectionner le thème avec le plus de correspondances
        max_matches = 0
        primary_theme = None
        
        for theme, matches in consolidated_themes["themes"].items():
            if len(matches) > max_matches:
                max_matches = len(matches)
                primary_theme = theme
        
        return primary_theme
    
    def is_content_eligible(self, consolidated_themes: Dict[str, Any]) -> bool:
        """Determines if content is eligible for meme coin generation"""
        
        username = consolidated_themes.get("username", "").lower()
        original_text = consolidated_themes.get("original_text", "")
        
        # Import our condition handler here
        try:
            from condition_handler import is_pattern_eligible
            # If pattern eligible, immediately return True
            if is_pattern_eligible(original_text, username):
                self.logger.info("Content eligible based on pattern matching")
                return True
        except ImportError:
            # If import fails, fall back to standard checks
            self.logger.warning("Could not import pattern matching - using standard eligibility")

        # If we have any media content, be more lenient
        media_sources = [source for source in consolidated_themes.get("eligible_sources", []) 
                        if source.startswith("media_")]
        if media_sources:
            return True
        
        # If we have any themes detected, it's eligible
        if consolidated_themes.get("themes", {}):
            return True
        
        # If it's a meme or crisis
        if consolidated_themes.get("is_meme", False) or consolidated_themes.get("is_crisis", False):
            return True
        
        # If we have minimal text but some keywords
        if consolidated_themes.get("has_minimal_text", False) and len(consolidated_themes.get("unique_identifiers", [])) > 0:
            return True
        
        # Default case
        return False
    
    def extract_relevant_keywords(self, text_analysis: Dict[str, Any], 
                                 media_analyses: List[Dict[str, Any]],
                                 primary_theme: str) -> List[str]:
        """
        Extracts relevant keywords based on the primary theme
        
        Args:
            text_analysis: Tweet text analysis
            media_analyses: List of media analyses
            primary_theme: Main detected theme
            
        Returns:
            List of relevant keywords
        """
        keywords = set()
        
        # Check if tweet has minimal text
        tweet_text = text_analysis.get("original_text", "").strip()
        has_minimal_text = len(tweet_text) < 15
        
        # If tweet has minimal text, prioritize media keywords
        if has_minimal_text and media_analyses:
            # Get all keywords from media analyses first
            for media_analysis in media_analyses:
                if "error" in media_analysis:
                    continue
                
                # Add subjects from image analysis (higher priority for image-based tweets)
                if "subjects" in media_analysis:
                    keywords.update(media_analysis["subjects"])
                
                # Add visible text from images
                if "visible_text" in media_analysis:
                    keywords.update(media_analysis["visible_text"])
                    
                # If this is a meme, prioritize that
                if media_analysis.get("is_meme", False) and "description" in media_analysis:
                    # Extract key terms from description
                    description = media_analysis["description"]
                    # Add first few words that are not stopwords and are at least 3 chars
                    from nltk.tokenize import word_tokenize
                    try:
                        words = word_tokenize(description)
                        for word in words:
                            if len(word) >= 3 and word.lower() not in self.config.STOP_WORDS:
                                keywords.add(word)
                    except:
                        # If tokenization fails, just add some words from description
                        for word in description.split()[:5]:
                            if len(word) >= 3:
                                keywords.add(word)
            
            # Only add text keywords as fallback if we don't have enough from media
            if len(keywords) < 3:
                # Add text keywords
                if "unique_identifiers" in text_analysis:
                    keywords.update(text_analysis["unique_identifiers"])
        else:
            # Normal processing for text-based tweets
            # Add the unique identifiers from the text
            if "unique_identifiers" in text_analysis:
                keywords.update(text_analysis["unique_identifiers"])
            
            # Add named entities
            if "named_entities" in text_analysis:
                for entity in text_analysis["named_entities"]:
                    if entity["type"] in ["PERSON", "ORG", "PRODUCT", "EVENT", "LOC", "FAC"]:
                        keywords.add(entity["text"])
            
            # Add hashtags
            if "symbols" in text_analysis:
                for symbol in text_analysis["symbols"]:
                    if symbol.startswith("#"):
                        keywords.add(symbol[1:])  # Remove the #
            
            # Process media keywords as additional context
            for media_analysis in media_analyses:
                if "error" in media_analysis:
                    continue
                
                # Add subjects
                if "subjects" in media_analysis:
                    keywords.update(media_analysis["subjects"])
                
                # Add visible text
                if "visible_text" in media_analysis:
                    keywords.update(media_analysis["visible_text"])
        
        # Filter keywords by theme
        themed_keywords = list(keywords)
        
        # Prioritize keywords related to the primary theme
        if primary_theme in self.config.TRIGGER_THEMES:
            theme_specific = []
            theme_keywords = self.config.TRIGGER_THEMES[primary_theme]
            
            for keyword in themed_keywords:
                # If the keyword contains a theme term
                for theme_term in theme_keywords:
                    if theme_term.lower() in keyword.lower():
                        theme_specific.append(keyword)
                        break
            
            # If theme-specific keywords are found
            if theme_specific:
                return theme_specific[:5]  # Limit to 5 keywords
        
        # Return generic keywords if no theme-specific keywords
        return list(themed_keywords)[:5]  # Limit to 5 keywords