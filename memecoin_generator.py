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

        # Build the system prompt using the instructions
        system_prompt = self.base_prompt

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
                except Exception as e:
                    self.logger.warning(f"Error with JSON format, trying without specified format: {str(e)}")
                    # Try without specifying response format (possibilité d'échec...)
                    completion = self.client.chat.completions.create(
                        model=self.config.OPENAI_TEXT_MODEL,
                        messages=[
                            {"role": "system", "content": system_prompt + "\nRespond ONLY with JSON format."},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )    
                
                # Extract response
                response_text = completion.choices[0].message.content.strip()
                
                # Parse JSON - with support for code delimiters
                try:
                    # First try direct parsing
                    memecoin_data = json.loads(response_text)
                except json.JSONDecodeError:
                    # If failed, look for valid JSON block
                    self.logger.warning("First JSON parsing attempt failed, searching for JSON block")
                    # Look for JSON block between ``` or ```json
                    import re
                    json_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
                    
                    if json_blocks:
                        # Try each found block
                        for block in json_blocks:
                            try:
                                memecoin_data = json.loads(block.strip())
                                break  # Exit if valid block found
                            except json.JSONDecodeError:
                                continue
                        else:
                            memecoin_data = {}    
                    else:
                        # If no block, just look for braces
                        json_pattern = r'\{[\s\S]*\}'
                        matches = re.search(json_pattern, response_text)
                        if matches:
                            try:
                                memecoin_data = json.loads(matches.group(0))
                            except json.JSONDecodeError:
                                raise json.JSONDecodeError("Could not find valid JSON", response_text, 0)
                        else:
                            memecoin_data = {}

                # Handle name and ticker variations
                name_field = memecoin_data.get("name") or memecoin_data.get("token_name")
                symbol_field = memecoin_data.get("ticker") or memecoin_data.get("token_symbol")
                
                if name_field and symbol_field:
                    # Create standardized response
                    result = {
                        "token_name": name_field,
                        "token_symbol": symbol_field.upper(),
                        "tweet_author": username,
                        "relevant_keywords": relevant_keywords,
                        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "condition": condition_match
                    }
                    
                    return result
                else:
                    missing = []
                    if not name_field:
                        missing.append("name/token_name")
                    if not symbol_field:
                        missing.append("ticker/token_symbol")
                        
                    self.logger.warning(f"Missing fields in OpenAI response: {missing}")
            
            except Exception as e:
                self.logger.error(f"Error calling OpenAI: {str(e)}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # Fallback response in case of failure
        self.logger.warning("Fallback generation after OpenAI calls failure")
        
        # Basic fallback format - avoid using "coin"
        if relevant_keywords:
            # Use top keyword directly as name if possible
            top_keyword = relevant_keywords[0].upper()
            if len(top_keyword) < 10:
                backup_name = top_keyword
            else:
                # Take first few characters for longer keywords
                backup_name = top_keyword[:10]
        else:
            # Use username if no keywords
            backup_name = username.upper()
            
        # Create ticker from first letters or characters
        if len(backup_name) <= 6:
            backup_symbol = backup_name
        else:
            # Take first letters of words or first characters
            if ' ' in backup_name:
                backup_symbol = ''.join([word[0].upper() for word in backup_name.split()[:3]])
            else:
                backup_symbol = backup_name[:4].upper()
        
        return {
            "token_name": backup_name[:15],  # Limited to 15 characters
            "token_symbol": backup_symbol[:6],  # Limited to 6 characters
            "tweet_author": username,
            "primary_theme": primary_theme,
            "relevant_keywords": relevant_keywords,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_fallback": True,
            "condition": condition_match
        }