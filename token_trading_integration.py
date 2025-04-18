# token_trading_integration.py
import os
import ssl_config

import json
import time
import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from sell_manager import TokenSellManager
from coin_publisher import CoinPublisher

class TokenTradingIntegration:
    """
    Module d'intégration entre le système de publication de tokens et le système de vente automatique.
    Permet de:
    1. Publier des memecoins via CoinPublisher
    2. Démarrer automatiquement la surveillance et l'application des stratégies de trading via TokenSellManager
    3. Stocker les résultats des transactions
    """
    
    def __init__(self, api_key: Optional[str] = None, config_path: str = "trading_config.json"):
        # Initialiser le logger
        self.logger = logging.getLogger(__name__)
        
        # Initialiser les deux composants
        self.publisher = CoinPublisher(api_key)
        self.sell_manager = TokenSellManager(api_key)
        
        # Enregistrer le callback pour les ventes
        self.sell_manager.register_sale_callback(self.register_sale)
        
        # Chemin vers le fichier de configuration
        self.config_path = config_path
        
        # Données de trading
        self.trading_history = []
        
        # Flag pour savoir si le background task est en cours
        self.is_monitoring = False
        
        # Le task de monitoring
        self.monitoring_task = None
        
        # Charger la configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Charge la configuration du trading depuis un fichier JSON
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                # Charger l'historique des transactions
                self.trading_history = config.get('trading_history', [])
                
                self.logger.info(f"Configuration chargée: {len(self.trading_history)} transactions dans l'historique")
            else:
                self.logger.info(f"Aucun fichier de configuration trouvé à {self.config_path}, utilisation des valeurs par défaut")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
    
    def _save_config(self) -> None:
        """
        Sauvegarde la configuration du trading dans un fichier JSON
        """
        try:
            config = {
                'trading_history': self.trading_history,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Configuration sauvegardée dans {self.config_path}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de la configuration: {str(e)}")
    
    def set_api_key(self, api_key: str) -> None:
        """
        Définit la clé API pour les deux systèmes
        """
        self.publisher.set_api_key(api_key)
        self.sell_manager.pump_api.set_api_key(api_key)
        self._save_config()
    
    async def publish_and_monitor(self, 
                               memecoin_data: Dict[str, Any],
                               image_url: Optional[str] = None,
                               image_path: Optional[str] = None,
                               dev_buy_amount: float = 0.01,
                               dry_run: bool = True,
                               max_monitor_duration: int = 3600,
                               auto_sell: bool = True) -> Dict[str, Any]:
        """
        Publie un memecoin et démarre automatiquement sa surveillance pour le trading
        
        Args:
            memecoin_data: Données du meme coin à publier
            image_url: URL de l'image du tweet (prioritaire)
            image_path: Chemin vers une image déjà téléchargée
            dev_buy_amount: Montant initial d'achat en SOL
            dry_run: Si True, ne fait pas d'achat réel
            max_monitor_duration: Durée maximale de surveillance en secondes
            auto_sell: Si True, active les stratégies de vente automatique
            
        Returns:
            Résultat contenant les informations de publication et de trading
        """
        # Publier le memecoin
        self.logger.info(f"Publication du memecoin: {memecoin_data.get('token_name', 'N/A')}")
        
        publish_result = self.publisher.publish_memecoin(
            memecoin_data=memecoin_data,
            image_url=image_url,
            image_path=image_path,
            dev_buy_amount=dev_buy_amount,
            dry_run=dry_run
        )
        
        # Si la publication a échoué ou si on est en dry_run, on s'arrête ici
        if not publish_result.get("success") or dry_run:
            if not publish_result.get("success"):
                self.logger.error(f"Échec de la publication: {publish_result.get('error', 'Erreur inconnue')}")
            elif dry_run:
                self.logger.info(f"Publication en dry-run réussie, pas de surveillance du token")
            
            return publish_result
        
        # Récupérer l'adresse du token
        mint_address = publish_result.get("mint_address")
        
        if not mint_address:
            self.logger.error("Impossible de récupérer l'adresse du token depuis le résultat de publication")
            return publish_result
        
        # Si auto_sell est activé, démarrer la surveillance du token
        if auto_sell:
            self.logger.info(f"Démarrage de la surveillance et des stratégies de vente pour {mint_address}")
            
            # Créer une entrée pour cette transaction
            transaction_entry = {
                "token_name": memecoin_data.get("token_name"),
                "token_symbol": memecoin_data.get("token_symbol"),
                "mint_address": mint_address,
                "initial_investment": dev_buy_amount,
                "publication_signature": publish_result.get("signature"),
                "publication_timestamp": datetime.now().isoformat(),
                "trading_status": "monitoring",
                "sales": []
            }
            
            # Ajouter à l'historique
            self.trading_history.append(transaction_entry)
            self._save_config()
            
            # Démarrer la surveillance dans un task séparé
            asyncio.create_task(self._monitor_token(mint_address, dev_buy_amount, max_monitor_duration))
            
            # Ajouter les infos de surveillance au résultat
            publish_result["trading_started"] = True
            publish_result["max_monitor_duration"] = max_monitor_duration
        
        return publish_result
    
    async def _monitor_token(self, mint_address: str, initial_investment: float, max_duration: int = 3600) -> None:
        """
        Méthode interne pour surveiller un token et exécuter les stratégies de vente
        """
        try:
            self.logger.info(f"Démarrage de la surveillance pour {mint_address} pendant {max_duration} secondes maximum")
            
            # Connecter au websocket si pas déjà fait
            if not self.sell_manager.is_connected:
                await self.sell_manager.connect_to_websocket()
            
            # Démarrer la stratégie de vente automatique
            await self.sell_manager.automate_sell_strategy(
                mint_address=mint_address,
                initial_investment_sol=initial_investment,
                max_duration_seconds=max_duration
            )
            
            # Mettre à jour le statut dans l'historique
            for entry in self.trading_history:
                if entry.get("mint_address") == mint_address:
                    entry["trading_status"] = "completed"
                    self._save_config()
                    break
            
            self.logger.info(f"Fin de la surveillance pour {mint_address}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la surveillance du token {mint_address}: {str(e)}")
            
            # Mettre à jour le statut en cas d'erreur
            for entry in self.trading_history:
                if entry.get("mint_address") == mint_address:
                    entry["trading_status"] = "error"
                    entry["error"] = str(e)
                    self._save_config()
                    break
    
    async def start_background_monitoring(self) -> None:
        """
        Démarre un task en arrière-plan pour surveiller les websockets et traiter les trades
        """
        if self.is_monitoring:
            self.logger.info("Le monitoring est déjà en cours")
            return
        
        self.is_monitoring = True
        
        try:
            # Connecter au websocket
            await self.sell_manager.connect_to_websocket()
            
            # Démarrer l'écoute des trades
            self.monitoring_task = asyncio.create_task(self.sell_manager.listen_for_trades())
            
            self.logger.info("Monitoring en arrière-plan démarré")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du démarrage du monitoring: {str(e)}")
            self.is_monitoring = False
    
    def stop_background_monitoring(self) -> None:
        """
        Arrête le task de monitoring en arrière-plan
        """
        if not self.is_monitoring:
            return
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            self.monitoring_task = None
        
        self.is_monitoring = False
        self.sell_manager.close()
        
        self.logger.info("Monitoring en arrière-plan arrêté")
    
    def register_sale(self, mint_address: str, percentage: str, transaction_result: Dict[str, Any]) -> None:
        """
        Enregistre une vente dans l'historique
        
        Args:
            mint_address: Adresse du token vendu
            percentage: Pourcentage vendu
            transaction_result: Résultat de la transaction
        """
        # Trouver l'entrée correspondante dans l'historique
        for entry in self.trading_history:
            if entry.get("mint_address") == mint_address:
                # Ajouter la vente à la liste des ventes
                sale_entry = {
                    "percentage": percentage,
                    "signature": transaction_result.get("signature"),
                    "timestamp": datetime.now().isoformat(),
                    "success": transaction_result.get("success", False)
                }
                
                if not transaction_result.get("success", False):
                    sale_entry["error"] = transaction_result.get("error", "Erreur inconnue")
                
                entry["sales"].append(sale_entry)
                
                # Vérifier si c'est une vente à 100% et mettre à jour le statut
                if percentage == "100%" and transaction_result.get("success", False):
                    entry["trading_status"] = "sold"
                
                self._save_config()
                self.logger.info(f"Vente de {percentage} enregistrée pour {mint_address}")
                return
        
        self.logger.warning(f"Impossible de trouver le token {mint_address} dans l'historique pour enregistrer la vente")
    
    def get_trading_history(self) -> List[Dict[str, Any]]:
        """
        Récupère l'historique complet des transactions
        
        Returns:
            Liste des transactions
        """
        return self.trading_history
    
    def get_token_trading_status(self, mint_address: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le statut de trading d'un token
        
        Args:
            mint_address: Adresse du token
            
        Returns:
            Informations sur le trading du token, ou None si non trouvé
        """
        for entry in self.trading_history:
            if entry.get("mint_address") == mint_address:
                return entry
        
        return None
    
    async def add_existing_token_to_monitoring(self, mint_address: str, initial_investment: float, max_duration: int = 3600) -> bool:
        """
        Ajoute un token existant à la surveillance
        
        Args:
            mint_address: Adresse du token
            initial_investment: Montant initial investi en SOL
            max_duration: Durée maximale de surveillance en secondes
            
        Returns:
            True si le token a été ajouté avec succès, False sinon
        """
        try:
            # Vérifier si le token est déjà surveillé
            for entry in self.trading_history:
                if entry.get("mint_address") == mint_address:
                    if entry.get("trading_status") in ["monitoring", "sold", "completed"]:
                        self.logger.warning(f"Le token {mint_address} est déjà surveillé ou a déjà été traité")
                        return False
                    
                    # Réinitialiser le statut
                    entry["trading_status"] = "monitoring"
                    self._save_config()
                    
                    # Démarrer la surveillance
                    asyncio.create_task(self._monitor_token(mint_address, initial_investment, max_duration))
                    return True
            
            # Si on arrive ici, le token n'est pas dans l'historique
            self.logger.info(f"Ajout d'un nouveau token {mint_address} à la surveillance")
            
            # Créer une nouvelle entrée
            transaction_entry = {
                "token_name": "Unknown",  # On ne connaît pas le nom
                "token_symbol": "UNKNOWN",  # On ne connaît pas le symbole
                "mint_address": mint_address,
                "initial_investment": initial_investment,
                "monitoring_started": datetime.now().isoformat(),
                "trading_status": "monitoring",
                "sales": []
            }
            
            # Ajouter à l'historique
            self.trading_history.append(transaction_entry)
            self._save_config()
            
            # Démarrer la surveillance
            asyncio.create_task(self._monitor_token(mint_address, initial_investment, max_duration))
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout du token {mint_address} à la surveillance: {str(e)}")
            return False