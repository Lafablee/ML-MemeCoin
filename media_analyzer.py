#media_analyzer.py
import logging
import requests
import tempfile
import os
import json
from typing import Dict, List, Any, Optional, Tuple
import cv2
from openai import OpenAI
from config import Config

class MediaAnalyzer:
    """Classe pour analyser les médias des tweets avec OpenAI Vision"""

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialiser le client OpenAI
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        
    def is_valid_image_url(self, url: str) -> bool:
        """
        Checks if the URL appears to be a valid image URL
        
        Args:
            url: URL to check
            
        Returns:
            True if the URL appears valid, False otherwise
        """
        # Check if the URL is a direct X/Twitter media URL
        twitter_media_patterns = [
            'pbs.twimg.com/media/',
            'pbs.twimg.com/ext_tw_video_thumb/',
            'pbs.twimg.com/profile_images/',
            'pbs.twimg.com/profile_banners/',
            'video.twimg.com/'
        ]
        
        if any(pattern in url for pattern in twitter_media_patterns):
            return True
            
        # Check if URL has an image extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
        
        if any(url.lower().endswith(ext) for ext in valid_extensions):
            return True
            
        # Check if URL is from a known image hosting service
        image_hosts = ['imgur.com/a/', 'i.imgur.com', 'imgbb.com', 'postimg.cc', 
                      'ibb.co', 'flickr.com', 'i.redd.it', 'i.pinimg.com']
        
        if any(host in url.lower() for host in image_hosts):
            return True
            
        # Check for X/Twitter status URLs that we might need to extract media from
        if 'twitter.com/status' in url.lower() or 'x.com/status' in url.lower():
            self.logger.info(f"X/Twitter status URL detected: {url}. Will attempt to extract media.")
            return True  # We'll try to handle it
            
        # Default to assuming it's a valid URL for now
        return True
        
    def extract_media_from_tweet_url(self, tweet_url: str) -> str:
        """
        Attempts to extract a direct media URL from a tweet URL
        
        Args:
            tweet_url: URL of a tweet that contains media
            
        Returns:
            Direct media URL if successful, original URL otherwise
        """
        # In a production environment, this would use Twitter's API
        # or scraping techniques to extract the media URLs
        
        # For now we'll implement a mock version that shows how it would work
        # In production, this would be replaced with actual API calls
        
        self.logger.info(f"Attempting to extract media from tweet URL: {tweet_url}")
        
        # Check if this is a tweet URL with photo reference
        import re
        tweet_pattern = r'(twitter|x)\.com/\w+/status/(\d+)(/photo/\d+)?'
        match = re.search(tweet_pattern, tweet_url)
        
        if match:
            tweet_id = match.group(2)
            photo_num = match.group(3) if match.group(3) else '/photo/1'
            
            # In production, you would:
            # 1. Call the Twitter API to get the tweet details
            # 2. Extract the media entities
            # 3. Return the direct media URL
            
            # For now, return a mock URL based on the tweet ID
            mock_media_id = f"{tweet_id}_{photo_num.replace('/photo/', '')}"
            return f"https://pbs.twimg.com/media/{mock_media_id}.jpg"
        
        # If not a recognized format, return original
        return tweet_url
    
    def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """
        Analyzes an image using OpenAI Vision
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Results of the image analysis
        """
        try:
            self.logger.info(f"Analyzing image: {image_url}")
            
            # Check if this is a tweet URL and try to extract direct media URL
            if 'twitter.com/status' in image_url.lower() or 'x.com/status' in image_url.lower():
                direct_url = self.extract_media_from_tweet_url(image_url)
                self.logger.info(f"Extracted direct media URL: {direct_url}")
                image_url = direct_url
            
            # Check URL validity
            if not self.is_valid_image_url(image_url):
                self.logger.warning(f"Potentially invalid image URL: {image_url}")
                return {
                    "error": "Invalid or inaccessible image URL",
                    "detected_themes": {},
                    "description": "Unable to access the image. It may be a non-direct URL."
                }
            
            # Construire le prompt pour l'analyse
            vision_prompt = """
            Analyze this image in detail. Identify:
            1. Main subjects (people, objects, places)
            2. Actions or events depicted
            3. Overall mood or tone
            4. Any visible text in the image
            5. Emotional themes (joy, sadness, fear, etc.)
            6. Whether it's a meme or humorous image
            7. If the image shows a disaster, conflict, or crisis situation
            
            Respond in JSON format with this structure:
            {
                "description": "Complete description of the image",
                "subjects": ["List of main subjects"],
                "actions": ["List of actions or events"],
                "mood": "Overall mood",
                "visible_text": ["List of visible texts"],
                "emotional_themes": ["List of emotional themes"],
                "is_meme": true/false,
                "is_crisis": true/false,
                "crisis_type": "Type of crisis if applicable"
            }
            """
            
            # Appel à l'API Vision
            # Appel à l'API Vision avec gestion des erreurs
            try:
                response = self.client.chat.completions.create(
                    model=self.config.OPENAI_VISION_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": vision_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_url,
                                        "detail": "high"  # Pour une analyse détaillée de l'image
                                    }
                                }
                            ]
                        }
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=1000
                )
            except Exception as e:
                self.logger.warning(f"Erreur avec le format JSON pour Vision, essai sans format spécifié: {str(e)}")
                # Essayer sans spécifier le format de réponse
                response = self.client.chat.completions.create(
                    model=self.config.OPENAI_VISION_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": vision_prompt + "\nRéponds UNIQUEMENT au format JSON."},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_url,
                                        "detail": "high"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1000
                )
            
            # Traiter la réponse
            analysis_result = {}
            try:
                # Convertir la réponse en JSON
                analysis_text = response.choices[0].message.content
                try:
                    # D'abord essayer de parser directement
                    analysis_result = json.loads(analysis_text)
                except json.JSONDecodeError:
                    # Si échec, chercher un bloc JSON valide
                    self.logger.warning("Première tentative de parsing JSON échouée, recherche de bloc JSON")
                    # Chercher un bloc JSON entre ``` ou ```json
                    import re
                    json_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', analysis_text)
                    
                    if json_blocks:
                        # Essayer chaque bloc trouvé
                        for block in json_blocks:
                            try:
                                analysis_result = json.loads(block.strip())
                                break  # Sortir si un bloc est valide
                            except json.JSONDecodeError:
                                continue
                    else:
                        # Si pas de bloc, chercher juste les accolades
                        json_pattern = r'\{[\s\S]*\}'
                        matches = re.search(json_pattern, analysis_text)
                        if matches:
                            try:
                                analysis_result = json.loads(matches.group(0))
                            except json.JSONDecodeError:
                                # Si toujours pas de JSON valide, créer un dict minimal avec le texte brut
                                self.logger.error("Impossible de parser la réponse JSON de Vision")
                                analysis_result = {
                                    "description": analysis_text[:500],  # Tronquer si trop long
                                    "subjects": [],
                                    "actions": [],
                                    "error": "Impossible de parser la réponse JSON"
                                }
                
                # Détection des thèmes
                detected_themes = self.detect_themes_from_analysis(analysis_result)
                analysis_result["detected_themes"] = detected_themes
                
            except Exception as e:
                self.logger.error(f"Erreur lors du traitement de la réponse Vision API: {str(e)}")
                analysis_result = {
                    "error": str(e),
                    "raw_response": response.choices[0].message.content
                }
                
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de l'image: {str(e)}")
            return {"error": str(e)}
    
    def extract_first_frame(self, video_url: str) -> Optional[str]:
        """
        Extrait la première frame d'une vidéo
        
        Args:
            video_url: URL de la vidéo
            
        Returns:
            Chemin temporaire vers l'image extraite ou None en cas d'échec
        """
        try:
            self.logger.info(f"Extraction de la première frame de: {video_url}")
            
            # Télécharger la vidéo dans un fichier temporaire
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            temp_dir = tempfile.gettempdir()
            video_path = os.path.join(temp_dir, "temp_video.mp4")
            
            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extraire la première frame
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                self.logger.error("Impossible d'extraire un frame de la vidéo")
                return None
            
            # Sauvegarder le frame
            frame_path = os.path.join(temp_dir, "first_frame.jpg")
            cv2.imwrite(frame_path, frame)
            
            return frame_path
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction du frame: {str(e)}")
            return None
            
    def process_video(self, video_url: str) -> Dict[str, Any]:
        """
        Traite une vidéo en extrayant la première frame et en l'analysant
        
        Args:
            video_url: URL de la vidéo
            
        Returns:
            Résultats de l'analyse de la première frame
        """
        frame_path = self.extract_first_frame(video_url)
        
        if not frame_path:
            return {"error": "Impossible d'extraire un frame de la vidéo"}
        
        # Transformer le chemin local en URL accessible par OpenAI
        # Dans un environnement réel, vous devriez uploader cette image
        # vers un service de stockage comme S3 et utiliser l'URL publique
        # Pour ce prototype, nous allons simuler cela
        
        try:
            # Lire l'image pour l'envoyer à l'API
            with open(frame_path, "rb") as image_file:
                import base64
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                
            # Créer une URL data pour l'image
            data_url = f"data:image/jpeg;base64,{encoded_image}"
            
            # Analyser l'image
            return self.analyze_image(data_url)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de la frame: {str(e)}")
            return {"error": str(e)}
        finally:
            # Nettoyer les fichiers temporaires
            try:
                os.remove(frame_path)
            except:
                pass
    
    def detect_themes_from_analysis(self, analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Detects themes based on image analysis
        
        Args:
            analysis: Image analysis results
            
        Returns:
            Dictionary of detected themes with corresponding terms
        """
        detected_themes = {}
        
        # Safely handle None values and create text from analysis for keyword search
        description = analysis.get("description", "") or ""
        
        # Safely handle lists that might be None
        subjects = analysis.get("subjects", []) or []
        actions = analysis.get("actions", []) or []
        visible_text = analysis.get("visible_text", []) or []
        emotional_themes = analysis.get("emotional_themes", []) or []
        
        # Safely handle other fields that might be None
        mood = analysis.get("mood", "") or ""
        crisis_type = analysis.get("crisis_type", "") or ""
        
        # Create the analysis text for keyword search
        analysis_text = " ".join([
            description,
            " ".join([str(s) for s in subjects if s is not None]),
            " ".join([str(a) for a in actions if a is not None]),
            mood,
            " ".join([str(t) for t in visible_text if t is not None]),
            " ".join([str(e) for e in emotional_themes if e is not None]),
            crisis_type
        ]).lower()
        
        # Détecter les thèmes basés sur les mots-clés
        for theme, keywords in self.config.TRIGGER_THEMES.items():
            matches = []
            for keyword in keywords:
                if keyword.lower() in analysis_text:
                    matches.append(keyword)
            
            if matches:
                detected_themes[theme] = matches
                
        # Vérifier si l'analyse a détecté une crise
        if analysis.get("is_crisis", False):
            crisis_type = analysis.get("crisis_type", "").lower()
            
            # Associer le type de crise à un thème
            if any(kw in crisis_type for kw in ["natural", "earthquake", "flood", "hurricane"]):
                if "catastrophe_naturelle" not in detected_themes:
                    detected_themes["catastrophe_naturelle"] = ["detected from image"]
            elif any(kw in crisis_type for kw in ["war", "conflict", "attack", "violence"]):
                if "conflit" not in detected_themes:
                    detected_themes["conflit"] = ["detected from image"]
            elif any(kw in crisis_type for kw in ["economic", "financial", "crash"]):
                if "crise_economique" not in detected_themes:
                    detected_themes["crise_economique"] = ["detected from image"]
        
        return detected_themes
    
    def is_media_eligible(self, analysis: Dict[str, Any]) -> bool:
        """
        Détermine si un média est éligible pour la génération d'un meme coin
        
        Args:
            analysis: Résultats de l'analyse du média
            
        Returns:
            True si le média est éligible, False sinon
        """
        # Vérifier s'il y a une erreur dans l'analyse
        if "error" in analysis:
            return False
        
        # Vérifier si des thèmes ont été détectés
        if analysis.get("detected_themes", {}):
            return True
        
        # Vérifier si l'image est un mème
        if analysis.get("is_meme", False):
            return True
        
        # Vérifier si l'image montre une crise
        if analysis.get("is_crisis", False):
            return True
        
        # Vérifier si l'image a du texte visible
        if analysis.get("visible_text", []):
            return True
        
        # Vérifier l'émotionalité de l'image
        emotional_themes = analysis.get("emotional_themes", [])
        strong_emotions = ["fear", "anger", "shock", "surprise", "excitement", "peur", "colère", "choc", "surprise", "excitation"]
        
        if any(emotion in " ".join(emotional_themes).lower() for emotion in strong_emotions):
            return True
            
        return False
    
    def get_main_theme(self, analysis: Dict[str, Any]) -> Optional[str]:
        """
        Détermine le thème principal d'un média pour l'adaptation du prompt
        
        Args:
            analysis: Résultats de l'analyse du média
            
        Returns:
            Le thème principal ou None si aucun thème n'est détecté
        """
        if "error" in analysis:
            return None
            
        detected_themes = analysis.get("detected_themes", {})
        
        if not detected_themes:
            # Si pas de thème mais c'est un mème
            if analysis.get("is_meme", False):
                return "meme"
                
            # Si pas de thème mais c'est une crise
            if analysis.get("is_crisis", False):
                crisis_type = analysis.get("crisis_type", "").lower()
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
        main_theme = None
        
        for theme, matches in detected_themes.items():
            if len(matches) > max_matches:
                max_matches = len(matches)
                main_theme = theme
                
        return main_theme