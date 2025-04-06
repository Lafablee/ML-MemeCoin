# condition_handler.py
import re
from typing import Dict, Optional, List

# Import the existing function with all its condition logic
def extract_ticker_info(text):
    # Listes de mots pour chaque condition
    negative_words = {'Pain', 'Hurting', 'Hurt', 'Wound', 'Wounded', 'Wounding', 'Defeat', 'Defeated', 'Defeating', 'Steal', 'Stolen', 'Stealing', 'Shatter', 'Shattered', 'Shattering', 'Ruin', 'Ruined', 'Ruining', 'Damage', 'Damaged', 'Damaging', 'Crush', 'Crushed', 'Crushing', 'Bankrupt', 'Bankrupted', 'Bankrupting', 'Destroy', 'Destroyed', 'Destroying', 'Help', 'Helpless', 'Helping', 'Devastate', 'Devastated', 'Devastating', 'Exhaust', 'Exhausted', 'Exhausting', 'Collapse', 'Collapsed', 'Collapsing', 'Sink', 'Sunk', 'Sinking', 'Despair', 'Despaired', 'Despairing', 'Strand', 'Stranded', 'Stranding'}
    death_words = {'Die', 'Dead', 'Died', 'Decease', 'Deceased', 'Deceasing', 'Go', 'Gone', 'Went', 'Perish', 'Perished', 'Perishing', 'Bury', 'Buried', 'Buried', 'Wither', 'Withered', 'Withering', 'Expire', 'Expired', 'Expiring', 'Pass', 'Passed', 'Passing', 'Succumb', 'Succumbed', 'Succumbing', 'Depart', 'Departed', 'Departing', 'Fade', 'Faded', 'Fading', 'Live', 'Lifeless', 'Lived', 'Extinguish', 'Extinct', 'Extinguished', 'Lose', 'Lost', 'Lost', 'Slay', 'Slain', 'Slaying', 'Kill', 'Killed', 'Killing', 'Murder', 'Murdered', 'Murdering', 'Execute', 'Executed', 'Executing', 'Vanish', 'Vanished', 'Vanishing', 'Fall', 'Felled', 'Felling', 'Rest', 'Resting', 'Rested', 'dies', 'death'}
    mascot_words = {'Mascot', 'Logo', 'Symbol', 'Icon', 'Badge', 'Figure', 'Character', 'Avatar', 'Entity', 'Fictional Character', 'Cartoon ', 'Illustration', 'Caricature', 'Creature', 'Totem', 'Puppet', 'Alter Ego', 'Creature', 'Imaginary Figure', 'Fantasy Being', 'Virtual Character', 'Animated Figure'}
    crime_words = {'Charge', 'Charged', 'Charging', 'Arrest', 'Arrested', 'Arresting', 'Detain', 'Detained', 'Detaining', 'Indict', 'Indicted', 'Indicting', 'Convict', 'Convicted', 'Convicting', 'Gun', 'Gunned', 'Gunning', 'Shoot', 'Shot', 'Shooting', 'Knife', 'Knifed', 'Knifing', 'Stab', 'Stabbed', 'Stabbing', 'Accuse', 'Accused', 'Accusing', 'Assault', 'Assaulted', 'Assaulting', 'Attack', 'Attacked', 'Attacking', 'Rob', 'Robbed', 'Robbing', 'Accuse', 'Accused', 'Accusing', 'Assault', 'Assaulted', 'Assaulting', 'Attack', 'Attacked', 'Attacking', 'Rob', 'Robbed', 'Robbing'}
    toilet_words = {'Pee', 'Peed', 'Peeing', 'Poo', 'Pooed', 'Pooing', 'Wee-wee', 'Wee-weed', 'Wee-weeing', 'Tinkle', 'Tinkled', 'Tinkling', 'Whiz', 'Whizzed', 'Whizzing', 'Piddle', 'Piddled', 'Piddling', 'Poop', 'Pooped', 'Pooping', 'Doo-doo', 'Doo-dooed', 'Doo-dooing', 'Dookie', 'Dookied', 'Dookieing', 'Number two', 'Number twoed', 'Number twoing', 'Pee-pee', 'Pee-peed', 'Pee-peeing', 'Potty', 'Pottied', 'Pottying', 'Dump', 'Dumped', 'Dumping', 'BM', 'BMed', 'BMing'}
    social_media_brands = {'twitter', 'KFC', 'X', 'Duolingo', 'reddit', 'twitch', 'Minecraft', 'Walmart', 'Discord', 'McDonald\'s', 'pumpfun', 'Colonel Sanders'}
    animals = {'Lion', 'Elephant', 'Giraffe', 'Zebra', 'Tiger', 'Bear', 'Monkey', 'Gorilla', 'Hippopotamus', 'Rhinoceros', 'Crocodile', 'Snake', 'Flamingo', 'Ostrich', 'Kangaroo', 'Koala', 'Panda', 'Wolf', 'Cheetah'}
    meme_coins = {'Pepe', 'doge'}
    crypto_words = {'bitcoin', 'ethereum', 'stablecoin', 'Solana', 'DOGE', 'Shiba', 'Pepe', 'Floki', 'Bonk', 'Dogwifhat', 'Popcat', 'Floki', 'Bonk'}
    elon_brands = {'spacex', 'Optimus', 'boringcompany', 'Tesla', 'cybertruck', 'neuralink'}
    sex_offender_words = {'Sexual Predator', 'Sexual Abuser', 'Rapist', 'Child Molester', 'Pedophile', 'Statutory Rapist', 'Sexual Assailant', 'Sex Criminal', 'Registered Sex Offender', 'Sexual Deviant', 'Perpetrator', 'Sexual Delinquent', 'Sexual Violator', 'Incest Offender', 'Exhibitionist', 'Voyeur', 'Sexual Exploiter', 'Pornography Offender', 'Sex Trafficker', 'Sexual Coercer', 'indecency', 'P*dophile'}
    touch_words = {'Touch', 'Touched', 'Touching', 'Caress', 'Caressed', 'Caressing', 'Fondle', 'Fondled', 'Fondling', 'Stroke', 'Stroked', 'Stroking', 'Cuddle', 'Cuddled', 'Cuddling', 'Rub', 'Rubbed', 'Rubbing', 'Tease', 'Teased', 'Teasing'}
    

    text_lower = text.lower()
    text_lower = text_lower.replace(","," ")
    text_lower = text_lower.replace("."," ")
    text_lower = text_lower.replace(";"," ")
    text_lower = text_lower.replace("-"," ")
    text_lower = text_lower.replace("/"," ")
    text_lower = text_lower.replace("@"," ")
    text_lower = text_lower.replace("?"," ")
    text_lower = text_lower.replace("!"," ")

    words = text_lower.split()

    # Condition 1: '$' suivi d'un mot (à supprimer carrément)
    for word in words:
        if word.startswith('$') and len(word) > 1:
            # Extrait la partie après le '$'
            ticker_part = word[1:]
             # Vérifie si cette partie contient au moins une lettre (pour exclure les montants)
            if any(c.isalpha() for c in ticker_part):
                return "Create a memecoin concept where ticker is the word following '$' (uppercase, max 10 chars, abbreviate if longer), name is the word following '$' + ' Coin'"
        
        if word == 'hat' or word == "hats":
            return "Create a memecoin concept where ticker is first letter of person + WH (max 8 chars), name is '[person] Wif " + word + "' (default person: no coin if no name found)"

        # Condition 2: Elon
        if word == 'elon':
            return "Create a memecoin concept that captures Elon Musk’s eccentric and futuristic persona—only if the event is weird, impulsive, or techy in a viral way; avoid standard Tesla/SpaceX updates unless there's meme potential; if it doesn’t qualify, do nothing."

        # Condition 10: Style (simulé ici pour texte, à adapter pour images)
        if word == 'style' or word =='styles':
            return "Create a memecoin concept where ticker is the style identified, name is the style simplified + 'ification' (e.g., Anime -> Animification)"

        if word == 'meme' or word == 'memes':
            return "Create a memecoin concept where ticker and name are related to memes"

    # Condition 3: Kanye West
    if 'kanye west' in text_lower:
        return "Create a memecoin concept where ticker and name are related to Kanye West"

    # Condition 4: Mots négatifs
    if any(word.lower() in negative_words for word in words):
        return "Create a memecoin concept where ticker is the first proper noun or random name (max 10 chars), name is 'Justice for [noun/name]'"

    # Condition 5: Mots de mort
    if any(word.lower() in death_words for word in words):
        return "Create a memecoin concept where ticker is the first proper noun or random name (max 10 chars), name is 'RIP [noun]'"

    # Condition 6: Mascottes
    if any(word.lower() in mascot_words for word in words):
        return "Create a memecoin concept where ticker is mascot name or random name (max 10 chars), name is 'New [mascot] Mascot'"

    # Condition 7: Crime
    if any(word.lower() in crime_words for word in words):
        return "Create a memecoin concept where ticker is person's name (max 10 chars, use first name if multiple), name is 'Jail [first name]' (if no name, use 'billy')"

    # Condition 9: Mots de toilette
    if any(word.lower() in toilet_words for word in words):
        return "Create a memecoin concept where ticker is related to the most shocking toilet word action (max 10 chars), name is the most shocking action involving the toilet word"

    # Condition 11: Trump
    if 'trump' in text_lower:
        return "Create a memecoin concept where ticker and name are related to Trump"

    # Condition 12: McDonald
    if 'mcdonald' in text_lower:
        return "Create a memecoin concept where ticker and name are related to McDonald"

    # Condition 13: Marques et réseaux sociaux
    if any(word.lower() in social_media_brands for word in words):
        return "Create a memecoin concept where ticker and name are related to the matched brand or social media"

    # Condition 14: Animaux
    if any(word.lower() in animals for word in words):
        return "Create a memecoin concept where ticker is first proper noun or random name (max 10 chars), name is ‘same as ticker’"

    # Condition 15: Meme coins existants
    if any(word.lower() in meme_coins for word in words):
        return "Create a memecoin concept where ticker is first proper noun or random name (max 10 chars), name is ‘same as ticker’"

    # Condition 16: Crypto
    if any(word.lower() in crypto_words for word in words):
        return "Create a memecoin concept where ticker and name are related to the matched cryptocurrency"

    # Condition 17: Strategic Reserve
    if 'strategic reserve' in text_lower:
        return "Create a memecoin concept where ticker is S+xxx+R, name is 'Strategic xxx Reserve' (xxx is type of reserve)"

    # Condition 18: Marques d'Elon (drôle ou nouveau)
    if any(word.lower() in elon_brands for word in words):
        return "Create a memecoin concept where ticker and name are related to the matched brand, only if funny or new"

    # Condition 19: Délinquants sexuels
    if any(word.lower() in sex_offender_words for word in words):
        return "Create a memecoin concept where ticker is first proper noun or random name (max 10 chars), name is ‘new diddy’"

    # Condition 21: Toucher
    if any(word.lower() in touch_words for word in words):
        return "Create a memecoin concept where ticker and name include 'gooner'"

    return None

def is_pattern_eligible(tweet_text: str, username: str = None, media_analysis: Dict = None) -> bool:
    """
    Determines if a tweet matches any pattern that should make it automatically eligible
    """
    # Check direct conditions from the original function
    condition_match = extract_ticker_info(tweet_text)
    if condition_match:
        return True
    
    return False

    # Check for death-related terms
    death_words = ["dead", "deceased", "gone", "perished", "died", "rip", "killed", "passed"]
    tweet_lower = tweet_text.lower()
    if any(word in tweet_lower for word in death_words):
        return True
    
    # Check for specific usernames (case-insensitive)
    celebrity_usernames = ["elonmusk", "kanyewest", "ye", "drake", "trump", "biden", "kimkardashian", "justinbieber"]
    if username and any(celeb.lower() in username.lower() for celeb in celebrity_usernames):
        return True
    
    # Check for dollar sign references
    if "$" in tweet_text:
        return True
    
    # Check for memes, hats, styles in text
    special_terms = ["meme", "hat", "style", "anime", "justice", "wif"]
    if any(term in tweet_lower for term in special_terms):
        return True
    
    # Check media analysis if provided
    if media_analysis:
        # If it's a meme, automatically eligible
        if media_analysis.get("is_meme", False):
            return True
        
        # If it contains specific subjects of interest
        subjects = media_analysis.get("subjects", [])
        interesting_subjects = ["animal", "dog", "cat", "person", "celebrity", "hat", "computer"]
        if any(subj in " ".join(subjects).lower() for subj in interesting_subjects):
            return True
    
    return False
    
# New function to provide more detailed instructions
def get_prompt_instructions(tweet_text: str, media_analysis: Optional[Dict] = None) -> Dict:
    """
    Analyzes tweet text and media analysis to generate specific prompt instructions
    
    Returns:
        Dictionary with instruction fields:
        - base_instruction: General approach to use
        - ticker_format: Specific format for ticker
        - name_format: Specific format for name
        - examples: Relevant examples to guide generation
    """
    # First check if we have a direct condition match from original function
    basic_instruction = extract_ticker_info(tweet_text)
    
    # Initialize response
    result = {
        "base_instruction": basic_instruction if basic_instruction else "Generate based on tweet content",
        "ticker_format": None,
        "name_format": None,
        "examples": []
    }
    
    # Check for specific patterns that should influence formats
    
    # 1. Check for $ symbol (direct token reference)
    dollar_pattern = r'\$([A-Za-z0-9]+)'
    dollar_matches = re.findall(dollar_pattern, tweet_text)
    if dollar_matches:
        result["ticker_format"] = f"Use '{dollar_matches[0].upper()}' as ticker"
        result["name_format"] = f"Base name on '{dollar_matches[0]}'"
        result["examples"] = [
            {"ticker": dollar_matches[0].upper(), "name": dollar_matches[0]}
        ]
        return result
    
    # 2. Check for "hat" mentions (dogwifhat pattern)
    if "hat" in tweet_text.lower():
        result["ticker_format"] = "Use format [first letter + WH]"
        result["name_format"] = "[subject] WIF HAT"
        result["examples"] = [
            {"ticker": "DWH", "name": "dog wif hat"},
            {"ticker": "EWH", "name": "elon wif hat"}
        ]
    
    # 3. Check for negative events
    negative_words = ["pain", "wounded", "broken", "defeated", "stealing", 
                      "shattered", "ruined", "damaged", "crushed"]
    if any(word in tweet_text.lower() for word in negative_words):
        result["ticker_format"] = "Use format based on subject name"
        result["name_format"] = "JUSTICE FOR [subject]"
        result["examples"] = [
            {"ticker": "LARRY", "name": "justice for larry"},
            {"ticker": "PEPE", "name": "justice for pepe"}
        ]
    
    # 4. Check for death references
    death_words = ["rip", "dead", "deceased", "gone", "perished", "buried", "died"]
    if any(word in tweet_text.lower() for word in death_words):
        result["ticker_format"] = "Use format RIP [initial letters]"
        result["name_format"] = "RIP [subject]"
        result["examples"] = [
            {"ticker": "RIPVAL", "name": "rip val"},
            {"ticker": "SARAHF", "name": "rip sarah"}
        ]
    
    # 5. Check for style/AI transformations
    style_words = ["style", "anime", "ghibli", "ai", "transform"]
    if any(word in tweet_text.lower() for word in style_words):
        result["ticker_format"] = "Use the style name"
        result["name_format"] = "[style]ification"
        result["examples"] = [
            {"ticker": "ANIME", "name": "animification"},
            {"ticker": "KNIT", "name": "knitification"}
        ]
    
    # Add image analysis based rules if media analysis is provided
    if media_analysis:
        # Check for meme detection in image
        if media_analysis.get("is_meme", False):
            result["base_instruction"] = "Create a memecoin based on a meme image"
            result["examples"].append({"ticker": "MEME", "name": "memecoin"})
        
        # Check for anime/style detection
        description = media_analysis.get("description", "").lower()
        if any(style in description for style in ["anime", "cartoon", "pixar", "disney", "animated"]):
            result["name_format"] = "[style]ification"
            result["ticker_format"] = "Use the style name"
            result["examples"].append({"ticker": "ANIME", "name": "animification"})
        
        # Check for animals in image
        subjects = media_analysis.get("subjects", [])
        animals = ["dog", "cat", "bear", "frog", "bird", "monkey", "ape", "lion", "tiger", "animal"]
        detected_animals = [subj for subj in subjects if any(animal in subj.lower() for animal in animals)]
        
        if detected_animals:
            animal = detected_animals[0]
            
            # Check for "wif" pattern (animal wearing something)
            actions = media_analysis.get("actions", [])
            wearing_terms = ["wearing", "with", "hat", "clothes", "costume", "dressed"]
            if any(term in " ".join(actions).lower() for term in wearing_terms):
                worn_item = None
                # Try to detect what the animal is wearing
                for action in actions:
                    if any(term in action.lower() for term in wearing_terms):
                        worn_items = ["hat", "cap", "helmet", "glasses", "tie", "shirt", "coat"]
                        for item in worn_items:
                            if item in action.lower():
                                worn_item = item
                                break
                
                if worn_item:
                    result["name_format"] = f"{animal} wif {worn_item}"
                    result["ticker_format"] = f"{animal[0:1]}W{worn_item[0:1]}"
                    result["examples"].append({"ticker": "DWH", "name": "dog wif hat"})
        
        # Check for person detection
        person_detected = any("person" in subj.lower() for subj in subjects)
        if person_detected:
            # Detect celebrities
            celebrities = ["elon", "musk", "trump", "biden", "kanye", "Carti", "playboicarti", "kardashian", "bieber", "celebrity"]
            celebrity_match = None
            for celeb in celebrities:
                if celeb in description.lower() or celeb in tweet_text.lower():
                    celebrity_match = celeb
                    break
            
            if celebrity_match:
                result["name_format"] = f"{celebrity_match} + relevant action/object"
                result["ticker_format"] = f"{celebrity_match[:3].upper()}"
                if celebrity_match == "elon":
                    result["examples"].append({"ticker": "ELON", "name": "elonking"})
                elif celebrity_match == "trump":
                    result["examples"].append({"ticker": "TRM", "name": "trumpcycle"})
        
        # Check for negative or tragic imagery
        emotional_themes = media_analysis.get("emotional_themes", [])
        negative_emotions = ["sadness", "fear", "anger", "disgust", "tragedy", "suffering"]
        if any(emotion in " ".join(emotional_themes).lower() for emotion in negative_emotions):
            # Try to find a subject to apply "justice for" format
            if subjects and len(subjects) > 0:
                subject = subjects[0].split()[0]  # Take first word of first subject
                result["name_format"] = f"justice for {subject}"
                result["ticker_format"] = subject.upper()
                result["examples"].append({"ticker": "LARRY", "name": "justice for larry"})
        
        # Check for death-related imagery
        death_related = ["death", "funeral", "grave", "deceased", "memorial", "rip"]
        if any(term in description.lower() for term in death_related):
            if subjects and len(subjects) > 0:
                subject = subjects[0].split()[0]  # Take first word of first subject
                result["name_format"] = f"rip {subject}"
                result["ticker_format"] = f"RIP{subject[:3].upper()}"
                result["examples"].append({"ticker": "RIPVAL", "name": "rip val"})
    
    return result