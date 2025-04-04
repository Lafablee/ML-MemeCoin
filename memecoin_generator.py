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
        1. The name must be SHORT, catchy and memorable (maximum 10 characters preferred)
        2. It must have a DIRECT connection to the tweet content
        3. NEVER include the word "coin" in the name
        4. Be creative, unexpected, and humorous
        5. Use wordplay, puns, or references from the tweet
        6. If the tweet mentions a person, incorporate their name

        Rules for the ticker:
        1. The ticker must be between 3 and 10 characters 
        2. CAPITAL LETTERS ONLY
        3. It must be directly related to the name or main subject
        4. Can include numbers as letter replacements (E->3, A->4, O->0)
        5. Should be extremely memorable and distinctive

        Provide ONLY a JSON with these fields:
        - token_name: the meme coin name (without the word "coin")
        - token_symbol: the ticker (without the word "COIN")
        """
        
        # Theme-specific prompts
        self.theme_prompts = {
            "catastrophe_naturelle": """
            For tweets about natural disasters:
            - The name could reference rescue, safety, or recovery concepts
            - The ticker could include "SOS" or "HELP"
            - Example: For a tsunami tweet, "TSUNAMI" with ticker "WAVE"
            """,
            
            "conflit": """
            For tweets about conflicts:
            - The name could reference peace or the region
            - The ticker should be sharp and impactful
            - Example: For a war tweet, "PEACEOUT" with ticker "PEACE"
            """,
            
            "crise_economique": """
            For tweets about economic crises:
            - The name could reference bulls, bears, or recovery
            - The ticker should be financial-themed
            - Example: For a stock market crash, "STONKS" with ticker "STNK"
            """,
            
            "justice": """
            For tweets about justice:
            - The name could reference justice concepts
            - The ticker should be legal-themed
            - Example: For a court case tweet, "JUDGED" with ticker "JDGE"
            """,
            
            "technologie": """
            For tweets about technology:
            - The name could reference the specific tech (AI, blockchain, etc.)
            - The ticker should be tech-themed
            - Example: For an AI breakthrough, "SKYNET" with ticker "AI"
            """,
            
            "celebrite": """
            For tweets about celebrities:
            - The name should be a play on their name or something they're known for
            - The ticker should be related to their persona
            - Example: For Elon Musk, "TECHKING" with ticker "ELON"
            """,
            
            "meme": """
            For tweets containing memes:
            - The name should directly reference the meme or use meme language
            - The ticker should be funny and meme-related
            - Example: For a doge meme, "MUCHW0W" with ticker "DOGE"
            """,
            
            "crisis": """
            For tweets about crisis situations:
            - The name should be direct but not insensitive
            - The ticker should be simple but impactful
            - Example: For a company crisis, "RUGPULL" with ticker "RUG"
            """,
        }
    
    def generate_memecoin(self, username: str, tweet_content: str, 
                         relevant_keywords: List[str], primary_theme: Optional[str] = None,
                         max_retries: int = 3, is_image_primary: bool = False,
                         format_guidance: Optional[Dict] = None,
                         media_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a meme coin based on a tweet and its analysis
        
        Args:
            username: Twitter account username
            tweet_content: Tweet text content
            relevant_keywords: List of relevant keywords
            primary_theme: Main detected theme (optional)
            max_retries: Maximum number of retry attempts
            is_image_primary: Whether the image is the primary content (not the text)
            
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
        try:
            matching_examples = self.example_learner.find_matching_examples(tweet_content, relevant_keywords)
        except Exception as e:
            self.logger.warning(f"Error finding matching examples: {str(e)}")
            matching_examples = []

        # Build the system prompt using the instructions
        system_prompt = self.base_prompt
        
        # Add format guidance if available
        if format_guidance:
            if format_guidance["format_type"] != "standard":
                system_prompt += f"\n\nUse this special format: {format_guidance['format_type']}\n"
                
                if format_guidance["ticker_format"]:
                    system_prompt += f"Ticker format: {format_guidance['ticker_format']}\n"
                    
                if format_guidance["name_format"]:
                    system_prompt += f"Name format: {format_guidance['name_format']}\n"
                    
                if format_guidance["example_ticker"] and format_guidance["example_name"]:
                    system_prompt += f"Example: ticker '{format_guidance['example_ticker']}', name '{format_guidance['example_name']}'\n"
        
        # Add specific instructions if available
        if prompt_instructions["base_instruction"]:
            system_prompt += f"\n\nSpecial instruction: {prompt_instructions['base_instruction']}"
        
        if prompt_instructions["ticker_format"]:
            system_prompt += f"\n\nTicker format: {prompt_instructions['ticker_format']}"
        
        if prompt_instructions["name_format"]:
            system_prompt += f"\n\nName format: {prompt_instructions['name_format']}"
        
        # Add examples if available from our tranding data set
        if matching_examples:
            system_prompt += "\n\nUse these high-quality examples as inspiration:"
            for example in matching_examples:
                system_prompt += f"\n- For a tweet about '{example['tweet_text'][:30]}...': {example['name']} with ticker {example['ticker']}"
        
        # Add theme-specific prompts
        if primary_theme and primary_theme in self.theme_prompts:
            system_prompt += self.theme_prompts[primary_theme]
        
        # Build the user prompt (rest of your existing code)
        if is_image_primary:
            user_prompt = f"""
            Generate a meme coin for a tweet by @{username} that contains primarily an image.
            
            The tweet has minimal or no text: "{tweet_content}"
            
            The image analysis detected these elements: {', '.join(relevant_keywords)}
            
            Create a funny, creative meme coin name and ticker that captures the essence of what's in the image.
            
            Remember the special instructions and follow examples provided when applicable.
            """
        else:
            user_prompt = f"""
            Generate a meme coin for this tweet by @{username}:
            
            "{tweet_content}"
            
            Relevant keywords: {', '.join(relevant_keywords)}
            
            Create a funny, clever meme coin name and ticker that follows the special format instructions when applicable.
            
            Remember the special instructions and follow examples provided when applicable.
            """
        
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
                        # If no block, just look for braces
                        json_pattern = r'\{[\s\S]*\}'
                        matches = re.search(json_pattern, response_text)
                        if matches:
                            try:
                                memecoin_data = json.loads(matches.group(0))
                            except json.JSONDecodeError:
                                raise json.JSONDecodeError("Could not find valid JSON", response_text, 0)
                
                # Check that all required fields are present
                required_fields = ["token_name", "token_symbol"]
                if all(field in memecoin_data for field in required_fields):
                    # Complete with metadata
                    memecoin_data["tweet_author"] = username
                    memecoin_data["primary_theme"] = primary_theme
                    memecoin_data["relevant_keywords"] = relevant_keywords
                    memecoin_data["generated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    return memecoin_data
                else:
                    missing = [f for f in required_fields if f not in memecoin_data]
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
            "is_fallback": True
        }