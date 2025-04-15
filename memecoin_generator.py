#memecoin_generator.py
import json
import logging
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI
from config import Config

class MemecoinsGenerator:
    """Class for generating meme coins based on analyzed tweets"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

        # Init example lerner (apprentissage process)
        from example_learner import ExampleLearner
        self.example_learner = ExampleLearner("exemple_ticker.txt")
        
        # Define the base prompt
        self.base_prompt = """
        Generate a name and ticker for a crypto token based on a tweet.

        Rules for the meme coin name:
        1. The name must be CLEAR, catchy and memorable (maximum 10 characters)
        2. It must have a DIRECT connection to the tweet content or the descritpion(preferably the descritpion and dont be too creative)
        3. NEVER include the word "coin" in the name
        4. If the tweet mentions a person, incorporate their name (important)

        Rules for the ticker:
        1. The ticker must be between 3 and 10 characters(the longer the better but do not add number to make it longer)
        2. CAPITAL LETTERS ONLY
        3. It must be directly related to the name or main subject(important)
        4. Should be memorable and distinctive
        """
    
    def generate_memecoin(self, username: str, tweet_content: str, 
                         relevant_keywords: List[str], primary_theme: Optional[str] = None,
                         max_retries: int = 3, is_image_primary: bool = False,
                         format_guidance: Optional[Dict] = None,
                         media_analysis: Optional[Dict] = None,
                         condition_match: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a meme coin based on a tweet with a simplified prompt structure
        
        Args:
            username: Twitter account username
            tweet_content: Tweet text content
            relevant_keywords: List of relevant keywords
            primary_theme: Main detected theme (optional)
            max_retries: Maximum number of retry attempts
            is_image_primary: Whether the image is the primary content (not the text)
            format_guidance: Format guidance from pattern matcher (not heavily used in simplified version)
            media_analysis: Analysis of media content
            condition_match: The specific condition that was matched to trigger generation
        Returns:
            Dictionary containing meme coin information
        """

        # Build the system prompt using the instructions
        system_prompt = self.base_prompt

        # Complétez le prompt système en expliquant les codes de statut spécifiques
        status_instruction = """
        IMPORTANT: For certain conditions, you must evaluate if the content qualifies:
        
        If you see instructions mentioning status codes (801, 802, 803, 804), you must evaluate:
        
        - For status code 801 (Elon): Is this content weird, impulsive, or techy in a viral way?
        - For status code 802 (Trump): Is this content new, shocking, or funny?
        - For status code 803 (Social Media): Is this about a unique/quirky event, not generic updates?
        - For status code 804 (Elon Brands): Is this content exceptionally funny, shocking, or culturally impactful?
        
        If the content doesn't qualify, ONLY respond with the status code number.
        Example: "801" (without quotes)
        
        If it does qualify, create the memecoin as requested.
        """
        
        # Ajoutez cette instruction uniquement pour les conditions spécifiques
        if condition_match and any(f"status code {code}" in condition_match for code in [801, 802, 803, 804]):
            system_prompt += status_instruction

        # First, check if we match any specific conditions from extract_ticker_info
        try:
            from condition_handler import get_prompt_instructions
            prompt_instructions = get_prompt_instructions(tweet_content, media_analysis)
        except ImportError:
            # Fallback si le module n'est pas disponible
            prompt_instructions = {
                "base_instruction": None,
                "ticker_format": None, 
                "name_format": None,
                "examples": []
            }
         # Find similar examples from our training data
        #try:
             #matching_examples = self.example_learner.find_matching_examples(tweet_content, relevant_keywords)
        #except Exception as e:
            #self.logger.warning(f"Error finding matching examples: {str(e)}")
            #matching_examples = []


         # Add the matched condition if available (prioritize this)
        if condition_match:
            system_prompt += f"\n\n{condition_match}"

        #Finalisation construction base prompt (format output) 
        system_prompt += """

        Provide ONLY a JSON with these fields:
        - name: the meme coin name (without the word "coin")
        - ticker: the ticker (without the word "COIN")
        """   
        
        # Build the user prompt focused on the tweet and media content
        user_prompt = f"""
        Generate a meme coin for this tweet by @{username}:

        "{tweet_content}"
        """
        
        # Toujours ajouter la description du média si disponible, quel que soit le mode
        if media_analysis and "description" in media_analysis and media_analysis["description"]:
            media_desc = media_analysis.get("description", "No description available")
            user_prompt += f"""
            
            The image shows: {media_desc} 
            """

        # Ajouter les mots-clés pertinents extraits
        #if relevant_keywords:
            # Limiter à un nombre raisonnable de mots-clés (par exemple 5)
            #top_keywords = relevant_keywords[:5]
            #keywords_str = ", ".join(top_keywords)
            
            #user_prompt += f"""
            
            #Key terms detected: {keywords_str}
            #"""
            
        # add debug for prompt structure
        self.logger.info(f"SYSTEM PROMPT:\n{system_prompt}")
        self.logger.info(f"USER PROMPT:\n{user_prompt}")
        
        # Multiple attempts in case of error
        for attempt in range(max_retries):
            try:
                # Try first with JSON format
                try:
                    completion = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        response_format={"type": "json_object"},
                        max_tokens=500
                    )
                except Exception as e:
                    self.logger.warning(f"Error with JSON format, trying without specified format: {str(e)}")
                    # Try without specifying response format
                    completion = self.client.chat.completions.create(
                        model=self.config.OPENAI_TEXT_MODEL,
                        messages=[
                            {"role": "system", "content": system_prompt + "\nRespond ONLY with JSON format."},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        response_format={"type": "json_object"},
                        max_tokens=500
                    )
                
                # Extract response
                response_text = completion.choices[0].message.content.strip()
                self.logger.info(f"Raw API response: {response_text}")
                
                # Initialiser memecoin_data ici pour éviter l'erreur
                memecoin_data = {}

                # Vérifier d'abord si c'est juste un code de statut
                status_codes = ["801", "802", "803", "804"]
                if response_text in status_codes:
                    status_code = int(response_text)
                    return {
                        "token_name": None,
                        "token_symbol": None,
                        "tweet_author": username,
                        "relevant_keywords": relevant_keywords,
                        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "condition": condition_match,
                        "status_code": status_code,                            "status_message": f"Content does not qualify per condition criteria (code {status_code})"
                    }
                else:
                    # Vérifier s'il s'agit d'un JSON avec un champ status
                    try:
                        response_json = json.loads(response_text)
                        if "status" in response_json and str(response_json["status"]) in status_codes:
                            # C'est un JSON avec un code de statut
                            status_code = response_json["status"]
                            return {
                                "token_name": None,
                                "token_symbol": None,
                                "tweet_author": username,
                                "relevant_keywords": relevant_keywords,
                                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "condition": condition_match,
                                "status_code": status_code,
                                "status_message": f"Content does not qualify per condition criteria (code {status_code})"
                            }
                        else:
                            # Si c'est un JSON valide sans code de statut, utiliser directement
                            memecoin_data = response_json
                            
                    except json.JSONDecodeError:
                        # Si échec, chercher un bloc JSON valide
                        self.logger.warning("First JSON parsing attempt failed, searching for JSON block")
                        
                        # Chercher du JSON entre ``` ou ```json
                        import re
                        json_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
                        
                        if json_blocks:
                            # Essayer chaque bloc trouvé
                            for block in json_blocks:
                                try:
                                    memecoin_data = json.loads(block.strip())
                                    break  # Sortir si un bloc valide est trouvé
                                except json.JSONDecodeError:
                                    continue 
                        else:
                            # Si pas de bloc, chercher simplement des accolades
                            json_pattern = r'\{[\s\S]*\}'
                            matches = re.search(json_pattern, response_text)
                            if matches:
                                try:
                                    memecoin_data = json.loads(matches.group(0))
                                except json.JSONDecodeError:
                                    raise json.JSONDecodeError("Could not find valid JSON", response_text, 0)

                # Traiter les champs du memecoin
                name_field = memecoin_data.get("name") or memecoin_data.get("token_name")
                symbol_field = memecoin_data.get("ticker") or memecoin_data.get("token_symbol")
                
                if name_field and symbol_field:
                    # Créer la réponse standardisée
                    result = {
                        "token_name": name_field,
                        "token_symbol": symbol_field.upper(),
                        "tweet_author": username,
                        "relevant_keywords": relevant_keywords,
                        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "condition": condition_match,
                        "status_code": 200,  # Code de succès par défaut
                        "status_message": "Generation successful"
                    }
                    
                    return result
                else:
                    missing = []
                    if not name_field:
                        missing.append("name/token_name")
                    if not symbol_field:
                        missing.append("ticker/token_symbol")
                        
                    self.logger.warning(f"Missing fields in OpenAI response: {missing}")
                    # Retourner un message d'erreur avec code d'erreur approprié
                    return {
                        "token_name": None,
                        "token_symbol": None,
                        "tweet_author": username,
                        "relevant_keywords": relevant_keywords,
                        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "condition": condition_match,
                        "status_code": 900,  # Code d'erreur de structure
                        "status_message": f"Missing required fields in response: {', '.join(missing)}"
                    }

            except Exception as e:
                self.logger.error(f"Error calling OpenAI: {str(e)}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # Retourner une erreur après tous les essais
                    return {
                        "token_name": None,
                        "token_symbol": None,
                        "tweet_author": username,
                        "relevant_keywords": relevant_keywords,
                        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "condition": condition_match,
                        "status_code": 999,  # Erreur après tous les essais
                        "status_message": f"Failed after {max_retries} attempts: {str(e)}"
                    }