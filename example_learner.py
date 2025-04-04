# example_learner.py (version corrigée)
import re
from typing import List, Dict, Any, Optional

class ExampleLearner:
    """Learns from example data to guide memecoin generation"""
    
    def __init__(self, example_file_path: str):
        """Initialize with path to examples file"""
        try:
            self.examples = self._load_examples(example_file_path)
            self.patterns = self._extract_patterns()
            print(f"Successfully loaded {len(self.examples)} examples")
        except Exception as e:
            print(f"Error initializing ExampleLearner: {e}")
            self.examples = []
            self.patterns = []
    
    def _load_examples(self, file_path: str) -> List[Dict]:
        """Load examples from the file"""
        examples = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract example blocks - each contains an input and output section
            blocks = re.findall(r'["\']input["\']:\s*{(.*?)["\']output["\']:\s*{(.*?)}', content, re.DOTALL)
            
            for input_block, output_block in blocks:
                try:
                    # Extract tweet text
                    tweet_match = re.search(r'["\']tweet_text["\']:\s*["\']([^"\']*)["\']', input_block)
                    if not tweet_match:
                        continue
                    tweet_text = tweet_match.group(1)
                    
                    # Extract image URL (optional)
                    image_match = re.search(r'["\']image_url["\']:\s*["\']([^"\']*)["\']', input_block)
                    image_url = image_match.group(1) if image_match else ""
                    
                    # Extract ticker and name
                    ticker_match = re.search(r'["\']ticker["\']:\s*["\']?([^,"\'\}]*)["\']?', output_block)
                    name_match = re.search(r'["\']name["\']:\s*["\']?([^,"\'\}]*)["\']?', output_block)
                    
                    if not ticker_match or not name_match:
                        continue
                    
                    ticker = ticker_match.group(1).strip()
                    name = name_match.group(1).strip()
                    
                    # Try to extract benefit rating (handles both formats)
                    benefit = 0
                    benefit_match = re.search(r'["\']bénéfice["\']:\s*(\d+)', output_block)
                    if benefit_match:
                        benefit = int(benefit_match.group(1))
                    else:
                        benefit_match = re.search(r'["\']benefit_rating["\']:\s*(\d+)', output_block)
                        if benefit_match:
                            benefit = int(benefit_match.group(1))
                    
                    # Create example entry
                    example = {
                        "input": {
                            "tweet_text": tweet_text,
                            "image_url": image_url
                        },
                        "output": {
                            "ticker": ticker,
                            "name": name,
                            "benefit": benefit
                        }
                    }
                    
                    examples.append(example)
                    
                except Exception as e:
                    print(f"Error parsing block: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error reading examples file: {e}")
        
        return examples
    
    def _extract_patterns(self) -> List[Dict]:
        """Extract patterns from examples"""
        patterns = []
        
        for example in self.examples:
            # Extract key features
            tweet_text = example["input"].get("tweet_text", "").lower()
            ticker = example["output"].get("ticker", "").upper()
            name = example["output"].get("name", "").lower()
            benefit = example["output"].get("benefit", 0)
            
            # Only include high-quality examples
            if benefit >= 3:
                # Identify pattern
                pattern_type = self._identify_pattern(tweet_text, ticker, name)
                
                patterns.append({
                    "pattern_type": pattern_type,
                    "tweet_text": tweet_text,
                    "ticker": ticker,
                    "name": name,
                    "benefit": benefit
                })
        
        return patterns
    
    def _identify_pattern(self, tweet_text: str, ticker: str, name: str) -> str:
        """Identify the pattern type of this example"""
        if "wif" in name:
            return "wif_format"
        elif "justice for" in name:
            return "justice_format"
        elif name.startswith("rip "):
            return "rip_format"
        elif name.endswith("ification"):
            return "style_format"
        elif "$" in tweet_text:
            return "dollar_format"
        # Add more pattern types as needed
        return "general"
    
    def find_matching_examples(self, tweet_text: str, keywords: List[str]) -> List[Dict]:
        """Find examples that match the given tweet text and keywords"""
        if not self.patterns:
            print("No patterns available for matching")
            # Return fallback examples for common patterns
            return [
                {
                    "tweet_text": "example tweet about death",
                    "ticker": "RIPVAL",
                    "name": "rip val",
                    "benefit": 3
                },
                {
                    "tweet_text": "example tweet with hat",
                    "ticker": "DWH",
                    "name": "dog wif hat",
                    "benefit": 3
                }
            ]
        
        matches = []
        
        tweet_lower = tweet_text.lower()
        keywords_lower = [k.lower() for k in keywords]
        
        for pattern in self.patterns:
            # Check for word matches
            words_in_tweet = set(re.findall(r'\w+', tweet_lower))
            words_in_pattern = set(re.findall(r'\w+', pattern["tweet_text"]))
            common_words = words_in_tweet.intersection(words_in_pattern)
            
            # Check for keyword matches
            keyword_match = any(k in pattern["tweet_text"] for k in keywords_lower)
            
            # Check for pattern type matches
            pattern_score = 0
            if "dead" in tweet_lower and pattern["pattern_type"] == "rip_format":
                pattern_score = 5
            elif "hat" in tweet_lower and pattern["pattern_type"] == "wif_format":
                pattern_score = 5
            elif "style" in tweet_lower and pattern["pattern_type"] == "style_format":
                pattern_score = 5
            
            # Score the match
            score = len(common_words) + (3 if keyword_match else 0) + pattern_score
            
            if score > 1:  # Lower threshold to ensure matches
                matches.append({
                    "pattern": pattern,
                    "score": score
                })
        
        # Sort by score and return top matches
        matches.sort(key=lambda x: x["score"], reverse=True)
        return [m["pattern"] for m in matches[:3]]  # Return top 3 matches