# pattern_matcher.py
import re
from typing import Dict, List, Any, Optional

class PatternMatcher:
    """Simple pattern matcher based on tweet content"""
    
    @staticmethod
    def is_eligible(tweet_text: str, username: str = None, media_analysis: Optional[Dict] = None) -> bool:
        """
        Determines if a tweet matches any pattern that should make it automatically eligible
        """
        tweet_lower = tweet_text.lower()
        
        # Pattern 1: Death references
        death_patterns = ["dead", "died", "death", "rip", "passed away", "killed", "funeral"]
        if any(pattern in tweet_lower for pattern in death_patterns):
            return True
        
        # Pattern 2: Celebrity usernames
        celebrity_usernames = ["elonmusk", "kanyewest", "ye", "trump", "drake", "kimkardashian"]
        if username and any(celeb.lower() in username.lower() for celeb in celebrity_usernames):
            return True
        
        # Pattern 3: Dollar sign token references
        if "$" in tweet_text:
            return True
        
        # Pattern 4: Hat/wearing references (dogwifhat pattern)
        if "hat" in tweet_lower or "wearing" in tweet_lower or "wif" in tweet_lower:
            return True
        
        # Pattern 5: Style references
        style_patterns = ["anime", "style", "ghibli", "ification", "knit", "puppet"]
        if any(pattern in tweet_lower for pattern in style_patterns):
            return True
        
        # Pattern 6: Justice/negative references
        justice_patterns = ["justice", "broken", "wounded", "pain", "crushed", "shattered"]
        if any(pattern in tweet_lower for pattern in justice_patterns):
            return True
        
        # Pattern 7: Meme references
        meme_patterns = ["meme", "doge", "pepe", "bonk", "shiba"]
        if any(pattern in tweet_lower for pattern in meme_patterns):
            return True
        
        # Pattern 8: Reserve patterns
        if "strategic reserve" in tweet_lower:
            return True
        
        # Pattern 9: Crime patterns
        crime_patterns = ["jail", "prison", "arrested", "charged", "gun", "crime"]
        if any(pattern in tweet_lower for pattern in crime_patterns):
            return True
        
        # Media-based patterns (if media analysis provided)
        if media_analysis:
            # If it's a meme
            if media_analysis.get("is_meme", False):
                return True
            
            # Check subjects in image
            subjects = media_analysis.get("subjects", [])
            if subjects and isinstance(subjects, list):
                subjects_text = " ".join([str(s).lower() for s in subjects if s])
                interesting_items = ["dog", "cat", "hat", "celebrity", "person", "animal"]
                if any(item in subjects_text for item in interesting_items):
                    return True
                
        return False
    
    @staticmethod
    def get_format_guidance(tweet_text: str, username: str = None, media_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get format guidance for memecoin generation
        
        Args:
            tweet_text: The text content of the tweet
            username: The username who posted the tweet
            media_analysis: Optional dictionary with media analysis results
            
        Returns:
            Dictionary with format guidance
        """
        tweet_lower = tweet_text.lower()
        result = {
            "format_type": "standard",
            "ticker_format": None,
            "name_format": None,
            "example_ticker": None,
            "example_name": None
        }
        
        # Check various patterns and return appropriate guidance
        # Death pattern
        death_patterns = ["dead", "died", "death", "rip", "passed away", "killed"]
        if any(pattern in tweet_lower for pattern in death_patterns):
            result["format_type"] = "rip"
            result["ticker_format"] = "RIPXXX"
            result["name_format"] = "rip [subject]"
            result["example_ticker"] = "RIPVAL"
            result["example_name"] = "rip val"
            return result
        
        # Media-based patterns (if provided)
        if media_analysis:
            # If the media has subjects we can use
            subjects = media_analysis.get("subjects", [])
            if subjects and isinstance(subjects, list):
                subjects_text = " ".join([str(s).lower() for s in subjects if s])
                
                # Check for animals
                animal_terms = ["dog", "cat", "animal", "bird"]
                if any(term in subjects_text for term in animal_terms):
                    # If hat is also detected
                    if "hat" in subjects_text or "hat" in tweet_lower:
                        result["format_type"] = "wif"
                        result["ticker_format"] = "XWH"
                        result["name_format"] = "[animal] wif hat"
                        result["example_ticker"] = "DWH"
                        result["example_name"] = "dog wif hat"
                        return result
        
        return result
    
    @staticmethod
    def get_memecoin_format(tweet_text: str, username: str = None) -> Dict[str, Any]:
        """
        Get appropriate memecoin format based on tweet content
        """
        tweet_lower = tweet_text.lower()
        result = {
            "format_type": "standard",
            "ticker_format": None,
            "name_format": None,
            "example_ticker": None,
            "example_name": None
        }
        
        # Format 1: Death references -> RIP format
        death_patterns = ["dead", "died", "death", "rip", "passed away", "killed"]
        if any(pattern in tweet_lower for pattern in death_patterns):
            result["format_type"] = "rip"
            result["ticker_format"] = "RIPXXX"
            result["name_format"] = "rip [subject]"
            result["example_ticker"] = "RIPVAL"
            result["example_name"] = "rip val"
            return result
        
        # Format 2: Dollar sign -> Direct token reference
        dollar_match = re.search(r'\$([A-Za-z0-9]+)', tweet_text)
        if dollar_match:
            token = dollar_match.group(1)
            result["format_type"] = "dollar"
            result["ticker_format"] = token.upper()
            result["name_format"] = token.lower()
            result["example_ticker"] = token.upper()
            result["example_name"] = token.lower()
            return result
        
        # Format 3: Hat/wearing references -> WIF format
        if "hat" in tweet_lower or "wearing" in tweet_lower or "wif" in tweet_lower:
            result["format_type"] = "wif"
            result["ticker_format"] = "XWY"
            result["name_format"] = "[subject] wif [item]"
            result["example_ticker"] = "DWH"
            result["example_name"] = "dog wif hat"
            return result
        
        # Format 4: Justice/negative references
        justice_patterns = ["justice", "broken", "wounded", "pain", "crushed"]
        if any(pattern in tweet_lower for pattern in justice_patterns):
            result["format_type"] = "justice"
            result["ticker_format"] = "XXX"
            result["name_format"] = "justice for [subject]"
            result["example_ticker"] = "LARRY"
            result["example_name"] = "justice for larry"
            return result
        
        # Format 5: Style references
        style_patterns = ["anime", "style", "ghibli", "cartoon"]
        if any(pattern in tweet_lower for pattern in style_patterns):
            style = next((p for p in style_patterns if p in tweet_lower), "style")
            result["format_type"] = "style"
            result["ticker_format"] = style.upper()
            result["name_format"] = f"{style}ification"
            result["example_ticker"] = "ANIME"
            result["example_name"] = "animification"
            return result
        
        # Format 6: Celebrity format (based on username)
        if username:
            username_lower = username.lower()
            if "elonmusk" in username_lower:
                result["format_type"] = "celebrity"
                result["ticker_format"] = "ELON"
                result["name_format"] = "elon[concept]"
                result["example_ticker"] = "ELON"
                result["example_name"] = "elonking"
                return result
            elif "kanyewest" in username_lower or "ye" in username_lower:
                result["format_type"] = "celebrity"
                result["ticker_format"] = "YE"
                result["name_format"] = "ye[concept]"
                result["example_ticker"] = "YE"
                result["example_name"] = "yeking"
                return result
            elif "trump" in username_lower:
                result["format_type"] = "celebrity"
                result["ticker_format"] = "TRUMP"
                result["name_format"] = "trump[concept]"
                result["example_ticker"] = "TRM"
                result["example_name"] = "trumpcycle"
                return result
        
        return result