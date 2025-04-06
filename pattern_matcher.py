# pattern_matcher.py
import re
from typing import Dict, List, Any, Optional

class PatternMatcher:
    """Simple pattern matcher based on tweet content"""
    
    @staticmethod
    def is_eligible(tweet_text: str, username: str = None, media_analysis: Optional[Dict] = None) -> bool:
        """
        Version qui délègue directement à condition_handler.is_pattern_eligible et extract_ticker_info
        """
        try:
            # Première vérification: extract_ticker_info - contient beaucoup de patterns
            from condition_handler import extract_ticker_info
            ticker_info = extract_ticker_info(tweet_text)
            if ticker_info:
                return True
                
            # Deuxième vérification: complet is_pattern_eligible
            from condition_handler import is_pattern_eligible
            return is_pattern_eligible(tweet_text, username, media_analysis)
            
        except ImportError as e:
            print(f"Erreur d'importation de condition_handler: {e}")
            # Fallback plus complet en cas d'échec d'importation
            return PatternMatcher._complete_fallback_check(tweet_text, username, media_analysis)
    
    @staticmethod
    def _complete_fallback_check(tweet_text: str, username: str = None, media_analysis: Optional[Dict] = None) -> bool:
        """
        Fallback d'urgence qui reproduit plus complètement les conditions du condition_handler
        """
        tweet_lower = tweet_text.lower()
        words = tweet_text.split()
        
        # Vérification des "$" suivis d'un mot
        if "$" in tweet_text:
            for word in words:
                if word.startswith('$') and len(word) > 1:
                    return True
        
        # Vérification de "elon"
        if 'elon' in tweet_lower:
            return True
            
        # Vérification de "kanye west"
        if 'kanye west' in tweet_lower or 'ye' in tweet_lower:
            return True
            
        # Vérification des mots négatifs
        negative_words = {'pain', 'wounded', 'broken', 'defeated', 'stealing', 'shattered', 
                        'ruined', 'damaged', 'crushed', 'bankrupt', 'destroyed', 'helpless',
                        'devastated', 'exhausted', 'collapsed', 'sunk', 'despair', 'stranded'}
        if any(word.lower() in negative_words for word in words):
            return True
            
        # Vérification des mots de mort
        death_words = {'dead', 'deceased', 'gone', 'perished', 'buried', 'withered', 'died', 'rip', 'killed'}
        if any(word.lower() in death_words for word in words):
            return True
            
        # Vérification des mots de mascottes
        mascot_words = {'mascot', 'logo', 'character', 'fictional character'}
        if any(word.lower() in mascot_words for word in words):
            return True
            
        # Vérification des mots de crime
        crime_words = {'charged', 'arrested', 'detained', 'indicted', 'convicted', 'gun', 'knife'}
        if any(word.lower() in crime_words for word in words):
            return True
            
        # Vérification "hat"
        if 'hat' in tweet_lower or 'wif' in tweet_lower:
            return True
            
        # Vérification des mots des toilettes
        toilet_words = {'pee', 'poo', 'wee-wee', 'tinkle', 'whiz', 'piddle', 'poop', 'doo-doo', 
                    'dookie', 'number two', 'pee-pee', 'potty', 'dump', 'bm'}
        if any(word.lower() in toilet_words for word in words):
            return True
            
        # Vérification des réseaux sociaux
        social_media_brands = {'twitter', 'kfc', 'x', 'duolingo', 'reddit', 'twitch', 'minecraft', 'walmart'}
        if any(word.lower() in social_media_brands for word in words):
            return True
            
        # Vérification des animaux
        animals = {'lion', 'elephant', 'giraffe', 'zebra', 'tiger', 'bear', 'monkey', 'gorilla',
                'hippopotamus', 'rhinoceros', 'crocodile', 'snake', 'flamingo', 'ostrich',
                'kangaroo', 'koala', 'panda', 'wolf', 'cheetah', 'dog', 'cat'}
        if any(word.lower() in animals for word in words):
            return True
            
        # Vérification des meme coins
        meme_coins = {'pepe', 'doge', 'shiba', 'floki', 'bonk', 'dogwifhat', 'popcat'}
        if any(word.lower() in meme_coins for word in words):
            return True
            
        # Vérification des mots crypto
        crypto_words = {'bitcoin', 'ethereum', 'stablecoin', 'solana', 'doge'}
        if any(word.lower() in crypto_words for word in words):
            return True
            
        # Vérification "Strategic Reserve"
        if 'strategic reserve' in tweet_lower:
            return True
            
        # Vérification des marques d'Elon
        elon_brands = {'spacex', 'optimus', 'boringcompany', 'tesla', 'cybertruck'}
        if any(word.lower() in elon_brands for word in words):
            return True
        
        # Vérification des délinquants sexuels
        sex_offender_words = {'sexual predator', 'sexual abuser', 'rapist', 'child molester', 
                            'pedophile', 'statutory rapist', 'sex offender'}
        if any(offense in tweet_lower for offense in sex_offender_words):
            return True
        
        # Vérification des mots de toucher
        touch_words = {'touching', 'caress', 'fondle', 'stroke', 'massage', 'embrace', 'cuddle', 'rub', 'tease'}
        if any(word.lower() in touch_words for word in words):
            return True
            
        # Vérification "meme"
        if 'meme' in tweet_lower:
            return True
        
        # Vérification des styles
        style_words = ['anime', 'style', 'ghibli', 'cartoon', 'pixel']
        if any(style in tweet_lower for style in style_words):
            return True
        
        # --- VÉRIFICATION DES PATTERNS COMME DANS is_pattern_eligible ---
        
        # Vérification des célébrités
        celebrity_usernames = ["elonmusk", "kanyewest", "ye", "drake", "trump", "biden", 
                            "kimkardashian", "justinbieber"]
        if username and any(celeb.lower() in username.lower() for celeb in celebrity_usernames):
            return True
        
        # Vérification des termes spéciaux
        special_terms = ["meme", "hat", "style", "anime", "justice", "wif"]
        if any(term in tweet_lower for term in special_terms):
            return True
        
        # Vérification de l'analyse média
        if media_analysis:
            # Si c'est un mème
            if media_analysis.get("is_meme", False):
                return True
            
            # Vérification des sujets intéressants
            subjects = media_analysis.get("subjects", [])
            interesting_subjects = ["animal", "dog", "cat", "person", "celebrity", "hat", "computer"]
            subject_text = " ".join([str(s).lower() for s in subjects if s]) if subjects else ""
            if any(subj in subject_text for subj in interesting_subjects):
                return True
        
        return False
    
    @staticmethod
    def get_format_guidance(tweet_text: str, username: str = None, media_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get format guidance for memecoin generation, with direct call to condition_handler if possible
        """
        try:
            from condition_handler import get_prompt_instructions
            instructions = get_prompt_instructions(tweet_text, media_analysis)
            
            # Convert condition handler instructions to format guidance
            result = {
                "format_type": "standard" if not instructions["base_instruction"] else "custom",
                "ticker_format": instructions["ticker_format"],
                "name_format": instructions["name_format"],
                "example_ticker": None,
                "example_name": None
            }
            
            # Add example if available
            if instructions["examples"] and len(instructions["examples"]) > 0:
                first_example = instructions["examples"][0]
                result["example_ticker"] = first_example.get("ticker", "")
                result["example_name"] = first_example.get("name", "")
                
            return result
                
        except ImportError:
            # Fallback to basic pattern detection
            return PatternMatcher._fallback_format_guidance(tweet_text, username, media_analysis)
    
    @staticmethod
    def _fallback_format_guidance(tweet_text: str, username: str = None, media_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Fallback format guidance detection
        """
        tweet_lower = tweet_text.lower()
        result = {
            "format_type": "standard",
            "ticker_format": None,
            "name_format": None,
            "example_ticker": None,
            "example_name": None
        }
        
        # Death pattern
        death_patterns = ["dead", "died", "death", "rip", "passed away"]
        if any(pattern in tweet_lower for pattern in death_patterns):
            result["format_type"] = "rip"
            result["ticker_format"] = "RIPXXX"
            result["name_format"] = "rip [subject]"
            result["example_ticker"] = "RIPVAL"
            result["example_name"] = "rip val"
            return result
        
        # Dollar sign -> Direct token reference
        dollar_match = re.search(r'\$([A-Za-z0-9]+)', tweet_text)
        if dollar_match:
            token = dollar_match.group(1)
            result["format_type"] = "dollar"
            result["ticker_format"] = token.upper()
            result["name_format"] = token.lower()
            result["example_ticker"] = token.upper()
            result["example_name"] = token.lower()
            return result
        
        # Hat/wearing references -> WIF format
        if "hat" in tweet_lower or "wif" in tweet_lower:
            result["format_type"] = "wif"
            result["ticker_format"] = "XWY"
            result["name_format"] = "[subject] wif [item]"
            result["example_ticker"] = "DWH"
            result["example_name"] = "dog wif hat"
            return result
        
        return result
    
    @staticmethod
    def get_memecoin_format(tweet_text: str, username: str = None) -> Dict[str, Any]:
        """
        # Delegate to get_format_guidance which now integrates with condition_handler
        """
        # Delegate to get_format_guidance which now integrates with condition_handler
        return PatternMatcher.get_format_guidance(tweet_text, username)
        
        # Vérification de "elon"
        if 'elon' in tweet_lower:
            return True
            
        # Vérification de "kanye west"
        if 'kanye west' in tweet_lower or 'ye' in tweet_lower:
            return True
            
        # Vérification des mots négatifs
        negative_words = {'pain', 'wounded', 'broken', 'defeated', 'stealing', 'shattered', 
                         'ruined', 'damaged', 'crushed', 'bankrupt', 'destroyed', 'helpless'}
        if any(word.lower() in negative_words for word in tweet_text.split()):
            return True
            
        # Vérification des mots de mort
        death_words = {'dead', 'deceased', 'gone', 'perished', 'buried', 'withered', 'died', 'rip', 'killed'}
        if any(word.lower() in death_words for word in tweet_text.split()):
            return True
            
        # Vérification des mots de mascottes
        mascot_words = {'mascot', 'logo', 'character', 'fictional character'}
        if any(word.lower() in mascot_words for word in tweet_text.split()):
            return True
            
        # Vérification des mots de crime
        crime_words = {'charged', 'arrested', 'detained', 'indicted', 'convicted', 'gun', 'knife'}
        if any(word.lower() in crime_words for word in tweet_text.split()):
            return True
            
        # Vérification "hat"
        if 'hat' in tweet_lower or 'wif' in tweet_lower:
            return True
            
        # Vérification des réseaux sociaux
        social_media_brands = {'twitter', 'kfc', 'x', 'duolingo', 'reddit', 'twitch', 'minecraft', 'walmart'}
        if any(word.lower() in social_media_brands for word in tweet_text.split()):
            return True
            
        # Vérification des animaux
        animals = {'lion', 'elephant', 'giraffe', 'zebra', 'tiger', 'bear', 'monkey', 'dog', 'cat'}
        if any(word.lower() in animals for word in tweet_text.split()):
            return True
            
        # Vérification des meme coins
        meme_coins = {'pepe', 'doge', 'shiba'}
        if any(word.lower() in meme_coins for word in tweet_text.split()):
            return True
            
        # Vérification des mots crypto
        crypto_words = {'bitcoin', 'ethereum', 'stablecoin', 'solana', 'doge'}
        if any(word.lower() in crypto_words for word in tweet_text.split()):
            return True
            
        # Vérification "Strategic Reserve"
        if 'strategic reserve' in tweet_lower:
            return True
            
        # Vérification des marques d'Elon
        elon_brands = {'spacex', 'optimus', 'boringcompany', 'tesla', 'cybertruck'}
        if any(word.lower() in elon_brands for word in tweet_text.split()):
            return True
            
        # Vérification "meme"
        if 'meme' in tweet_lower:
            return True
        
        # --- VÉRIFICATION DES PATTERNS COMME DANS is_pattern_eligible ---
        
        # Vérification des célébrités
        celebrity_usernames = ["elonmusk", "kanyewest", "ye", "drake", "trump", "biden", 
                              "kimkardashian", "justinbieber"]
        if username and any(celeb.lower() in username.lower() for celeb in celebrity_usernames):
            return True
        
        # Vérification des termes spéciaux
        special_terms = ["meme", "hat", "style", "anime", "justice", "wif"]
        if any(term in tweet_lower for term in special_terms):
            return True
        
        # Vérification de l'analyse média
        if media_analysis:
            # Si c'est un mème
            if media_analysis.get("is_meme", False):
                return True
            
            # Vérification des sujets intéressants
            subjects = media_analysis.get("subjects", [])
            interesting_subjects = ["animal", "dog", "cat", "person", "celebrity", "hat", "computer"]
            if subjects and any(subj in " ".join(str(s).lower() for s in subjects if s) for subj in interesting_subjects):
                return True
        
        return False
    
    @staticmethod
    def get_format_guidance(tweet_text: str, username: str = None, media_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get format guidance for memecoin generation, with direct call to condition_handler if possible
        """
        try:
            from condition_handler import get_prompt_instructions
            instructions = get_prompt_instructions(tweet_text, media_analysis)
            
            # Convert condition handler instructions to format guidance
            result = {
                "format_type": "standard" if not instructions["base_instruction"] else "custom",
                "ticker_format": instructions["ticker_format"],
                "name_format": instructions["name_format"],
                "example_ticker": None,
                "example_name": None
            }
            
            # Add example if available
            if instructions["examples"] and len(instructions["examples"]) > 0:
                first_example = instructions["examples"][0]
                result["example_ticker"] = first_example.get("ticker", "")
                result["example_name"] = first_example.get("name", "")
                
            return result
                
        except ImportError:
            # Fallback to basic pattern detection
            return PatternMatcher._fallback_format_guidance(tweet_text, username, media_analysis)
    
    @staticmethod
    def _fallback_format_guidance(tweet_text: str, username: str = None, media_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Fallback format guidance detection
        """
        tweet_lower = tweet_text.lower()
        result = {
            "format_type": "standard",
            "ticker_format": None,
            "name_format": None,
            "example_ticker": None,
            "example_name": None
        }
        
        # Death pattern
        death_patterns = ["dead", "died", "death", "rip", "passed away"]
        if any(pattern in tweet_lower for pattern in death_patterns):
            result["format_type"] = "rip"
            result["ticker_format"] = "RIPXXX"
            result["name_format"] = "rip [subject]"
            result["example_ticker"] = "RIPVAL"
            result["example_name"] = "rip val"
            return result
        
        # Dollar sign -> Direct token reference
        dollar_match = re.search(r'\$([A-Za-z0-9]+)', tweet_text)
        if dollar_match:
            token = dollar_match.group(1)
            result["format_type"] = "dollar"
            result["ticker_format"] = token.upper()
            result["name_format"] = token.lower()
            result["example_ticker"] = token.upper()
            result["example_name"] = token.lower()
            return result
        
        # Hat/wearing references -> WIF format
        if "hat" in tweet_lower or "wif" in tweet_lower:
            result["format_type"] = "wif"
            result["ticker_format"] = "XWY"
            result["name_format"] = "[subject] wif [item]"
            result["example_ticker"] = "DWH"
            result["example_name"] = "dog wif hat"
            return result
        
        return result
    
    @staticmethod
    def get_memecoin_format(tweet_text: str, username: str = None) -> Dict[str, Any]:
        """
        Get appropriate memecoin format based on tweet content - with direct call to condition_handler
        """
        # Delegate to get_format_guidance which now integrates with condition_handler
        return PatternMatcher.get_format_guidance(tweet_text, username)