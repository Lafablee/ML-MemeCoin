# condition_handler.py
import re
from typing import Dict, Optional, List, Union, Tuple

# Import the existing function with all its condition logic
def extract_ticker_info(text):
    # Listes de mots pour chaque condition
    negative_words = {'pain', 'hurting', 'hurt', 'wound', 'wounded', 'wounding', 'defeat', 'defeated', 'defeating', 'steal', 'stolen', 'stealing', 'shatter', 'shattered', 'shattering', 'ruin', 'ruined', 'ruining', 'damage', 'damaged', 'damaging', 'crush', 'crushed', 'crushing', 'bankrupt', 'bankrupted', 'bankrupting', 'destroy', 'destroyed', 'destroying', 'help', 'helpless', 'helping', 'devastate', 'devastated', 'devastating', 'exhaust', 'exhausted', 'exhausting', 'collapse', 'collapsed', 'collapsing', 'sink', 'sunk', 'sinking', 'despair', 'despaired', 'despairing', 'strand', 'stranded', 'stranding', 'war'}
    death_words = {'die', 'dead', 'died', 'decease', 'deceased', 'deceasing', 'go', 'gone', 'went', 'perish', 'perished', 'perishing', 'bury', 'buried', 'buried', 'wither', 'withered', 'withering', 'expire', 'expired', 'expiring', 'pass', 'passed', 'passing', 'succumb', 'succumbed', 'succumbing', 'depart', 'departed', 'departing', 'fade', 'faded', 'fading', 'live', 'lifeless', 'lived', 'extinguish', 'extinct', 'extinguished', 'lose', 'lost', 'lost', 'slay', 'slain', 'slaying', 'kill', 'killed', 'killing', 'murder', 'murdered', 'murdering', 'execute', 'executed', 'executing', 'vanish', 'vanished', 'vanishing', 'fall', 'felled', 'felling', 'rest', 'resting', 'rested', 'dies', 'death'}
    mascot_words = {'mascot', 'logo', 'symbol', 'icon', 'badge', 'figure', 'character', 'avatar', 'entity', 'fictional character', 'cartoon', 'illustration', 'caricature', 'creature', 'totem', 'puppet', 'alter ego', 'creature', 'imaginary figure', 'fantasy being', 'virtual character', 'animated figure'}
    crime_words = {'charge', 'charged', 'charging', 'arrest', 'arrested', 'arresting', 'detain', 'detained', 'detaining', 'indict', 'indicted', 'indicting', 'convict', 'convicted', 'convicting', 'gun', 'gunned', 'gunning', 'shoot', 'shot', 'shooting', 'knife', 'knifed', 'knifing', 'stab', 'stabbed', 'stabbing', 'accuse', 'accused', 'accusing', 'assault', 'assaulted', 'assaulting', 'attack', 'attacked', 'attacking', 'rob', 'robbed', 'robbing', 'accuse', 'accused', 'accusing', 'assault', 'assaulted', 'assaulting', 'attack', 'attacked', 'attacking', 'rob', 'robbed', 'robbing'}
    toilet_words = {'pee', 'peed', 'peeing', 'poo', 'pooed', 'pooing', 'wee-wee', 'wee-weed', 'wee-weeing', 'tinkle', 'tinkled', 'tinkling', 'whiz', 'whizzed', 'whizzing', 'piddle', 'piddled', 'piddling', 'poop', 'pooped', 'pooping', 'doo-doo', 'doo-dooed', 'doo-dooing', 'dookie', 'dookied', 'dookieing', 'number two', 'number twoed', 'number twoing', 'pee-pee', 'pee-peed', 'pee-peeing', 'potty', 'pottied', 'pottying', 'dump', 'dumped', 'dumping', 'bm', 'bmed', 'bming'}
    social_media_brands = {'twitter', 'x', 'duolingo', 'reddit', 'twitch', 'minecraft', 'walmart', 'discord', 'mcdonald\'s', 'pumpfun', 'colonel sanders'}
    animals = {'lion', 'elephant', 'giraffe', 'zebra', 'tiger', 'bear', 'monkey', 'gorilla', 'hippopotamus', 'rhinoceros', 'crocodile', 'snake', 'flamingo', 'ostrich', 'kangaroo', 'koala', 'panda', 'wolf', 'cheetah'}
    meme_coins = {'pepe', 'doge', 'dogwifhat'}
    crypto_words = {'bitcoin', 'ethereum', 'stablecoin', 'solana', 'doge', 'shiba', 'pepe', 'floki', 'bonk', 'dogwifhat', 'popcat', 'floki', 'bonk'}
    elon_brands = {'spacex', 'optimus', 'boringcompany', 'tesla', 'cybertruck', 'neuralink'}
    sex_offender_words = {'sexual predator', 'sexual abuser', 'rapist', 'child molester', 'pedophile', 'statutory rapist', 'sexual assailant', 'sex criminal', 'registered sex offender', 'sexual deviant', 'perpetrator', 'sexual delinquent', 'sexual violator', 'incest offender', 'exhibitionist', 'voyeur', 'sexual exploiter', 'pornography offender', 'sex trafficker', 'sexual coercer', 'indecency', 'p*dophile', 'sex'}
    touch_words = {'touch', 'touched', 'touching', 'caress', 'caressed', 'caressing', 'fondle', 'fondled', 'fondling', 'stroke', 'stroked', 'stroking', 'cuddle', 'cuddled', 'cuddling', 'rub', 'rubbed', 'rubbing', 'tease', 'teased', 'teasing'}

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
        if word == 'hat' or word == "hats" or word == 'cap' or word == 'caps':
            return "Create a memecoin concept where ticker is first letter of person + WH (max 10 chars), name is '[person] Wif Hat' (if no name found create one)"

        # Condition 2: Elon
        if word == 'elon':
            return "Create a memecoin concept that captures Elon Musk’s eccentric and futuristic persona—only if the event is weird, impulsive, or techy in a viral way; avoid standard Tesla/SpaceX updates unless there's meme potential; if it doesn’t qualify, return status 801."

        # Condition 10: Style (simulé ici pour texte, à adapter pour images)
        if word == 'style' or word =='styles':
            return "Create a memecoin concept where ticker is the style identified, name is the style simplified + 'ification' (e.g., Anime -> Animification)"

        if word == 'meme' or word == 'memes':
            return "If the word 'meme' appears in the text, create a meme-related concept, but the name must never contain the word 'Coin'"

    # Condition 3: Kanye West
    if 'kanye west' in text_lower:
        return "Create a memecoin concept where ticker and name are related to Kanye West"

    # Condition 4: Mots négatifs
    if any(word.lower() in negative_words for word in words):
        return "Create a memecoin concept where ticker is the first proper noun or random name (max 10 chars), name is 'Justice for [noun/name]'"

    # Condition 5: Mots de mort
    if any(word.lower() in death_words for word in words):
        return "Create a memecoin concept where, ticker is the name of the person associated with the event or create a name if none is given (max 10 chars), name is 'RIP name. The event has to be in the recent time not long ago. refers to the person concerned rather than the environment.'"

    # Condition 6: Mascottes
    if any(word.lower() in mascot_words for word in words):
        return "Create a memecoin where the ticker is the mascot’s name (or a random name if unknown, max 10 chars), and the name must strictly be 'New [Company] Mascot', where [Company] is the name of the company where the mascot appears."

    # Condition 7: Crime
    if any(word.lower() in crime_words for word in words):
        return "Create a memecoin concept where ticker is person's name (max 10 chars, use first name if multiple), name is 'Jail [first name]' (if no name, use 'billy')"

    # Condition 9: Mots de toilette
    if any(word.lower() in toilet_words for word in words):
        return "Create a memecoin concept where ticker is related to the most shocking toilet word action (max 10 chars), name is the most shocking action involving the toilet word"

    # Condition 11: Trump
    if 'trump' in text_lower:
        return "Create a memecoin concept that captures Trump’s chaotic, exaggerated, or meme-worthy energy, only if the event involves a viral quote, bizarre facial expression, funny behavior, or outrageous claim. Ignore all basic political updates, travel appearances, or traditional media events unless there’s clear meme potential. If it’s not instantly funny, shocking, or absurd in a way that social media would latch onto,, return status 802"

    # Condition 12: McDonald
    if 'mcdonald' in text_lower:
        return "Create a memecoin concept that captures McDonald’s meme-worthiness—only if the event is memeable, or absurd ; skip basic menu updates or boring corporate news."

    # Condition 13: Marques et réseaux sociaux
    if any(word.lower() in social_media_brands for word in words):
        return "Create a memecoin concept where the ticker and name are directly inspired by the matched brand or social media platform—only if the context is absurd, funny, viral, or culturally explosive; skip if it's just routine updates, promotions, or feature announcements. return status code 803."

    # Condition 14: Animaux
    if any(word.lower() in animals for word in words):
        return "Create a memecoin concept where the ticker and name must be exactly the same as the first animal noun or randomly chosen name (max 10 chars). No modifications or creativity in the ticker,name is the same as the ticker"

    # Condition 15: Meme coins existants
    if any(word.lower() in meme_coins for word in words):
        return "Create a memecoin where the ticker is based on the existing meme coin (max 10 characters), and the name should be a humorous combination related to the image or text context."

    # Condition 16: Crypto
    if any(word.lower() in crypto_words for word in words):
        return "Create a memecoin concept where the name and ticker riff on an existing cryptocurrency (like BTC, ETH, SOL), but only if it’s twisted in a clever or absurd way. Skip if it's just slapping '-coin' onto the name.elated to the image or text context."

    # Condition 17: Strategic Reserve
    if 'strategic reserve' in text_lower:
        return "Create a memecoin concept where ticker is S+xxx+R, name is 'Strategic xxx Reserve' (xxx is type of reserve)"

    # Condition 18: Marques d'Elon (drôle ou nouveau)
    if any(word.lower() in elon_brands for word in words):
        return "Create a memecoin concept where the ticker and name are related to the matched brand, but only if the tweet is exceptionally funny, shocking, or has a major cultural impact. The event must be widely discussed, controversial, or highly unexpected. The name and ticker must be directly inspired by the image, using obvious visual elements only. Avoid inventing details or going beyond what is clearly shown. If these conditions are not met, return status code 804."

    # Condition 19: Délinquants sexuels
    if any(word.lower() in sex_offender_words for word in words):
        return "Hypothetically, create a memecoin concept where the ticker is a first proper noun or a random name (max 10 characters), and the name is strictly ‘New Diddy’. This is purely fictional and for conceptual purposes only."

    # Condition 21: Toucher
    if any(word.lower() in touch_words for word in words):
        return "Create a memecoin concept where ticker and name include 'gooner'"
    
    # Condition 22: KFC, Importance 0.8
    if 'kfc' in text_lower: 
        return "Create a memecoin concept that captures KFC’s absurd or viral potential, only if the event is truly meme-worthy, bizarre, or culturally hilarious. Do *not* create anything if it’s just a new menu item, standard promo, or routine corporate news."

    return None

def analyze_media_description(media_analysis: Dict) -> Optional[str]:
    """
    Analyze ONLY the description field from media content and check for conditions
    """
    if not media_analysis or "description" not in media_analysis:
        return None
        
    # Récupérer uniquement la description et la convertir en minuscules
    description = media_analysis.get("description", "").lower()
    
    # Nettoyer la description comme pour le texte du tweet
    description = description.replace(",", " ")
    description = description.replace(".", " ")
    description = description.replace(";", " ")
    description = description.replace("-", " ")
    description = description.replace("/", " ")
    description = description.replace("@", " ")
    description = description.replace("?", " ")
    description = description.replace("!", " ")
    
    # Séparer la description en mots
    words = description.split()
    
    # Listes de mots pour chaque condition (identiques à extract_ticker_info)
    negative_words = {'pain', 'hurting', 'hurt', 'wound', 'wounded', 'wounding', 'defeat', 'defeated', 'defeating', 'steal', 'stolen', 'stealing', 'shatter', 'shattered', 'shattering', 'ruin', 'ruined', 'ruining', 'damage', 'damaged', 'damaging', 'crush', 'crushed', 'crushing', 'bankrupt', 'bankrupted', 'bankrupting', 'destroy', 'destroyed', 'destroying', 'help', 'helpless', 'helping', 'devastate', 'devastated', 'devastating', 'exhaust', 'exhausted', 'exhausting', 'collapse', 'collapsed', 'collapsing', 'sink', 'sunk', 'sinking', 'despair', 'despaired', 'despairing', 'strand', 'stranded', 'stranding'}
    death_words = {'die', 'dead', 'died', 'dies', 'decease', 'deceased', 'deceasing', 'go', 'gone', 'went', 'perish', 'perished', 'perishing', 'bury', 'buried', 'buried', 'wither', 'withered', 'withering', 'expire', 'expired', 'expiring', 'pass', 'passed', 'passing', 'succumb', 'succumbed', 'succumbing', 'depart', 'departed', 'departing', 'fade', 'faded', 'fading', 'live', 'lifeless', 'lived', 'extinguish', 'extinct', 'extinguished', 'lose', 'lost', 'lost', 'slay', 'slain', 'slaying', 'kill', 'killed', 'killing', 'murder', 'murdered', 'murdering', 'execute', 'executed', 'executing', 'vanish', 'vanished', 'vanishing', 'fall', 'felled', 'felling', 'rest', 'resting', 'rested', 'death'}
    mascot_words = {'mascot', 'logo', 'symbol', 'icon', 'badge', 'figure', 'character', 'avatar', 'entity', 'fictional character', 'cartoon', 'illustration', 'caricature', 'creature', 'totem', 'puppet', 'alter ego', 'creature', 'imaginary figure', 'fantasy being', 'virtual character', 'animated figure', 'action figure', 'toy', 'doll'}
    crime_words = {'charge', 'charged', 'charging', 'arrest', 'arrested', 'arresting', 'detain', 'detained', 'detaining', 'indict', 'indicted', 'indicting', 'convict', 'convicted', 'convicting', 'gun', 'gunned', 'gunning', 'shoot', 'shot', 'shooting', 'knife', 'knifed', 'knifing', 'stab', 'stabbed', 'stabbing', 'accuse', 'accused', 'accusing', 'assault', 'assaulted', 'assaulting', 'attack', 'attacked', 'attacking', 'rob', 'robbed', 'robbing', 'accuse', 'accused', 'accusing', 'assault', 'assaulted', 'assaulting', 'attack', 'attacked', 'attacking', 'rob', 'robbed', 'robbing', 'prison', 'jail', 'handcuff', 'weapon'}
    toilet_words = {'pee', 'peed', 'peeing', 'poo', 'pooed', 'pooing', 'wee-wee', 'wee-weed', 'wee-weeing', 'tinkle', 'tinkled', 'tinkling', 'whiz', 'whizzed', 'whizzing', 'piddle', 'piddled', 'piddling', 'poop', 'pooped', 'pooping', 'doo-doo', 'doo-dooed', 'doo-dooing', 'dookie', 'dookied', 'dookieing', 'number two', 'number twoed', 'number twoing', 'pee-pee', 'pee-peed', 'pee-peeing', 'potty', 'pottied', 'pottying', 'dump', 'dumped', 'dumping', 'bm', 'bmed', 'bming', 'toilet', 'bathroom', 'urinal'}
    social_media_brands = {'twitter', 'x', 'duolingo', 'reddit', 'twitch', 'minecraft', 'walmart', 'discord', 'mcdonald', 'pumpfun', 'colonel sanders', 'burger king', 'wendy', 'taco bell', 'facebook', 'instagram', 'tiktok', 'snapchat', 'youtube'}
    animals = {'lion', 'elephant', 'giraffe', 'zebra', 'tiger', 'bear', 'monkey', 'gorilla', 'hippopotamus', 'rhinoceros', 'crocodile', 'snake', 'flamingo', 'ostrich', 'kangaroo', 'koala', 'panda', 'wolf', 'cheetah', 'dog', 'cat', 'pet', 'animal'}
    meme_coins = {'pepe', 'doge', 'dogwifhat', 'shib', 'shiba', 'bonk', 'wojak', 'floki'}
    crypto_words = {'bitcoin', 'ethereum', 'stablecoin', 'solana', 'doge', 'shiba', 'pepe', 'floki', 'bonk', 'dogwifhat', 'popcat', 'floki', 'bonk', 'crypto', 'cryptocurrency', 'btc', 'eth', 'sol'}
    elon_brands = {'spacex', 'optimus', 'boringcompany', 'tesla', 'cybertruck', 'neuralink', 'x', 'twitter', 'rocket', 'mars', 'electric car'}
    sex_offender_words = {'sexual predator', 'sexual abuser', 'rapist', 'child molester', 'pedophile', 'statutory rapist', 'sexual assailant', 'sex criminal', 'registered sex offender', 'sexual deviant', 'perpetrator', 'sexual delinquent', 'sexual violator', 'incest offender', 'exhibitionist', 'voyeur', 'sexual exploiter', 'pornography offender', 'sex trafficker', 'sexual coercer', 'indecency', 'p*dophile', 'sex'}
    touch_words = {'touch', 'touched', 'touching', 'caress', 'caressed', 'caressing', 'fondle', 'fondled', 'fondling', 'stroke', 'stroked', 'stroking', 'cuddle', 'cuddled', 'cuddling', 'rub', 'rubbed', 'rubbing', 'tease', 'teased', 'teasing', 'hold', 'holding', 'embrace'}
    style_words = {'anime', 'cartoon', 'pixel', 'style', 'ghibli', 'pixel art', 'drawing', 'illustration', 'sketch', 'animated', 'artistic', 'stylized', 'noir', 'vintage', 'retro', 'futuristic'}
    
    # Vérifier pour chaque catégorie de mots
    
   # 1. Hats/Caps/Accessoires
    if any(word in description for word in ['hat', 'hats', 'cap', 'caps']):
        return "Create a memecoin concept where ticker is first letter of visible entity + WH (max 10 chars), name is '[entity] Wif Hat' (if no entity visible, create one based on image context)"
    
    # 2. Elon Musk
    if any(word in description for word in ['elon', 'musk']):
        return "Create a memecoin concept that captures Elon Musk’s eccentric and futuristic persona—only if the event is weird, impulsive, or techy in a viral way; avoid standard Tesla/SpaceX updates unless there's meme potential; if it doesn’t qualify, return status code 801."
    
    # 3. Style (verfication nécessaire !)
    for style in style_words:
        if style in words or (len(style.split()) > 1 and style in description):
            return f"Create a memecoin concept where ticker is based on the {style} style identified, name is the style simplified + 'ification' (e.g., Anime -> Animification)"
    
    # 4. Meme
    if 'meme' in words or 'memes' in words:
        return "Create a meme-related memecoin concept based on the visual elements in the image, but the name must never contain the word 'Coin'"
    
    # 5. Deaths
    if any(word in death_words for word in words):
        return "Create a memecoin concept where, ticker is the name of the person visible in the image or create a name if none is given (max 10 chars), name is 'RIP [name]'"
    
    # 6. Negative/Defeated concepts
    if any(word in negative_words for word in words):
        return "Create a memecoin concept where ticker is the first proper noun or visible subject (max 10 chars), name is 'Justice for [noun/name]'"
    
    # 7. Mascot/Character/Figure
    if any(word in mascot_words for word in words):
        return "Create a memecoin where the ticker is based on the visible character or mascot (max 10 chars), and the name must include the character's distinctive features"
    
    # 8. Crime/Jail
    if any(word in crime_words for word in words):
        return "Create a memecoin concept where ticker is related to any person visible in the image (max 10 chars), name is 'Jail [name]' (if no name, use 'billy')"
    
    # 9. Toilet/Bathroom
    if any(word in toilet_words for word in words):
        return "Create a memecoin concept where ticker is related to the toilet/bathroom context shown in the image (max 10 chars), name is a humorous take on the bathroom situation"
    
    # 10. Trump
    if 'trump'in words or 'donald trump' in words:
        return "Create a memecoin concept that captures Trump’s chaotic, exaggerated, or meme-worthy energy, only if the event involves a viral quote, bizarre facial expression, funny behavior, or outrageous claim. Ignore all basic political updates, travel appearances, or traditional media events unless there’s clear meme potential. If it’s not instantly funny, shocking, or absurd in a way that social media would latch onto, return 902"
    
    # 11. McDonald's/Fast Food
    if any(word in ['mcdonald', 'mcdonalds', 'mcdo'] for word in words):
        return "Create a memecoin concept that captures the fast food or McDonald's elements visible in the image"
    
    # 12. Social Media Brands
    if any(word in social_media_brands for word in words):
        for brand in social_media_brands:
            if brand in words:
                return f"Create a memecoin concept where the ticker and name are directly inspired by the matched brand or social media platform—only if the context is absurd, funny, viral, or culturally explosive; return status code 803 if it's just routine updates, promotions, or feature announcements."
    
    # 13. Animals
    if any(word in animals for word in words):
        for animal in animals:
            if animal in words:
                return f"Create a memecoin concept where the ticker and name feature the {animal} shown in the image (max 10 chars)"
    
    # 14. Meme Coins
    if any(word in meme_coins for word in words):
        for coin in meme_coins:
            if coin in words:
                return f"Create a memecoin where the ticker is based on {coin} (max 10 characters), and the name should incorporate elements visible in the image"
    
    # 15. Crypto
    if any(word in crypto_words for word in words):
        return "Create a memecoin concept where the name and ticker reference the cryptocurrency context shown in the image"
    
    # 16. "Strategic Reserve"
    if 'strategic' in words and 'reserve' in words:
        return "Create a memecoin concept where ticker is S+xxx+R, name is 'Strategic xxx Reserve' (xxx is based on what's visible in the image)"
    
    # 17. Elon Brands
    if any(brand in elon_brands for word in words for brand in elon_brands if brand == word):
        for brand in elon_brands:
            if brand in words:
                return f"Create a memecoin concept where the ticker and name are related to the matched brand, but only if the tweet is exceptionally funny, shocking, or has a major cultural impact. The event must be widely discussed, controversial, or highly unexpected. The name and ticker must be directly inspired by the image, using obvious visual elements only. Avoid inventing details or going beyond what is clearly shown. If these conditions are not met, return status code 804."
    
    # 18. Sexual misconduct - CAS SPÉCIAL pour les expressions à plusieurs mots
    for term in sex_offender_words:
        if ' ' in term:  # Si c'est une expression à plusieurs mots
            if term in description:  # Vérifier la phrase entière
                return "Hypothetically, create a memecoin concept where the ticker is based on a subject in the image (max 10 characters), and the name is strictly 'New Diddy'. This is purely fictional."
        elif term in words:  # Sinon vérifier mot à mot
            return "Hypothetically, create a memecoin concept where the ticker is based on a subject in the image (max 10 characters), and the name is strictly 'New Diddy'. This is purely fictional."
    
    # 19. Touch/Feel
    if any(word in touch_words for word in words):
        return "Create a memecoin concept where ticker and name include 'gooner', based on what's shown in the image" 
    
    # Condition 22: KFC, Importance 0.8
    if 'kfc' in words: 
        return "Create a memecoin concept that captures KFC’s absurd or viral potential, only if the event is truly meme-worthy, bizarre, or culturally hilarious. Do *not* create anything if it’s just a new menu item, standard promo, or routine corporate news."


    return None

def is_pattern_eligible(tweet_text: str, username: str = None, media_analysis: Dict = None) -> bool:
    """
    Determines if a tweet matches any pattern that should make it automatically eligible,
    now enhanced to properly analyze media content
    """
    # 1. First check text conditions
    condition_match = extract_ticker_info(tweet_text)
    if condition_match:
        return True
    
    # 2. Then thoroughly check media conditions if available
    if media_analysis and "description" in media_analysis:
        media_condition = analyze_media_description(media_analysis)
        if media_condition:
            return True, media_condition
        
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