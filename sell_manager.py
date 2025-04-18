# sell_manager.py - Version modifiée
import websockets
from ssl_config import configure_ssl

import time
import logging
import json
import asyncio
import requests
from typing import Dict, Any, Optional, List, Tuple, Callable
from datetime import datetime




class TokenSellManager:
    """
    Gestionnaire de vente automatique pour les memecoins
    Implémente différentes stratégies de vente basées sur les conditions de prix
    et utilise l'API PumpPortal pour exécuter les transactions
    """
    
    def __init__(self, api_key: Optional[str] = None):
        # Initialiser le logger
        self.logger = logging.getLogger(__name__)
        
        # Initialiser l'API PumpPortal
        from pumportal_api import PumpPortalAPI
        self.pump_api = PumpPortalAPI(api_key)
        
        # Stocker les données de trading
        self.trading_data = {}
        
        # Websocket pour les données en temps réel
        self.ws = None
        
        # Flag pour savoir si on est connecté au websocket
        self.is_connected = False
        
        # Callback pour enregistrer les ventes
        self.sale_callback = None
    
    def register_sale_callback(self, callback: Callable[[str, str, Dict[str, Any]], None]) -> None:
        """
        Enregistre un callback qui sera appelé après chaque vente
        
        Args:
            callback: Fonction à appeler avec (mint_address, percentage, result)
        """
        self.sale_callback = callback
    
    async def connect_to_websocket(self):
        """Se connecte au websocket de PumpPortal pour les données en temps réel"""
        if self.is_connected:
            return
        
        try:
            self.logger.info("Connexion au websocket PumpPortal...")
            
            # Utiliser le contexte SSL configuré correctement
            ssl_context = configure_ssl()
            
            # Se connecter avec le contexte SSL sécurisé
            self.ws = await websockets.connect(
                "wss://pumpportal.fun/api/data",
                ssl=ssl_context
            )
            
            self.is_connected = True
            self.logger.info("Connexion websocket établie avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors de la connexion au websocket: {str(e)}")
            self.is_connected = False
    
    async def subscribe_to_token(self, mint_address: str):
        """S'abonne aux données de trading d'un token spécifique"""
        if not self.is_connected:
            await self.connect_to_websocket()
            
        try:
            # Format de la requête d'abonnement selon la doc PumpPortal
            payload = {
                "method": "subscribeTokenTrade",
                "keys": [mint_address]
            }
            
            await self.ws.send(json.dumps(payload))
            self.logger.info(f"Abonné aux trades du token {mint_address}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'abonnement au token {mint_address}: {str(e)}")
    
    async def listen_for_trades(self):
        """Écoute les messages du websocket et met à jour les données de trading"""
        if not self.is_connected:
            self.logger.error("Impossible d'écouter les trades: non connecté au websocket")
            return
            
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                
                    # La clé est ici - au lieu de vérifier "type" == "trade"
                    # Vérifier si c'est un message de trading (txType présent)
                    if "txType" in data and "mint" in data and "solAmount" in data:
                        mint_address = data.get("mint")
                        if mint_address:
                            # Récupérer le txType des données
                            tx_type = data.get("txType", "unknown")
                            
                            # Calculer le prix par token en SOL
                            token_amount = float(data.get("tokenAmount", 0))
                            sol_amount = float(data.get("solAmount", 0))
                            market_cap = float(data.get("marketCapSol", 0))
                            
                            # Éviter division par zéro
                            if token_amount > 0:
                                price = sol_amount / token_amount
                            else:
                                price = 0
                            
                            # Initialiser les données si c'est le premier trade
                            if mint_address not in self.trading_data:
                                self.logger.info(f"📊 Initialisation des données pour {mint_address}")
                                self.trading_data[mint_address] = {
                                    "price_history": [],
                                    "highest_price": price,
                                    "current_price": price,
                                    "initial_price": price, # Pour tracer l'évolution depuis le début
                                    "volume_24h": 0,
                                    "market_cap": market_cap,
                                    "last_updated": datetime.now()
                                }
                                old_price = price
                                old_highest = price
                            else:
                                old_price = self.trading_data[mint_address]["current_price"]
                                old_highest = self.trading_data[mint_address]["highest_price"]
                            
                            # Mettre à jour le prix actuel
                            self.trading_data[mint_address]["current_price"] = price
                            self.trading_data[mint_address]["market_cap"] = market_cap
                            
                            # Mettre à jour le prix le plus élevé
                            if price > old_highest:
                                self.trading_data[mint_address]["highest_price"] = price
                                self.logger.info(f"🔼 NOUVEAU RECORD: {mint_address}: {old_highest:.10f} → {price:.10f} SOL/token (+{((price-old_highest)/old_highest)*100:.2f}%)")
                            
                            # Ajouter à l'historique des prix
                            self.trading_data[mint_address]["price_history"].append({
                                "price": price,
                                "timestamp": datetime.now(),
                                "tx_type": tx_type  # Maintenant tx_type est bien défini
                            })
                            
                            # Limiter l'historique des prix
                            if len(self.trading_data[mint_address]["price_history"]) > 100:
                                self.trading_data[mint_address]["price_history"].pop(0)
                            
                            # Mettre à jour le timestamp
                            self.trading_data[mint_address]["last_updated"] = datetime.now()
                            
                            # Calculer les variations de prix
                            price_change = ((price - old_price) / old_price * 100) if old_price > 0 else 0
                            price_symbol = "📈" if price > old_price else "📉" if price < old_price else "➡️"
                            
                            # Log détaillé du trade
                            self.logger.info(
                                f"{price_symbol} {tx_type.upper()}: {mint_address}: "
                                f"Prix = {price:.10f} SOL/token "
                                f"({price_change:+.2f}%), "
                                f"Montant = {token_amount:.2f} tokens pour {sol_amount:.6f} SOL, "
                                f"MarketCap = {market_cap:.2f} SOL"
                            )
                        
                    else:
                        # Message d'un autre type
                        if "type" in data:
                            self.logger.info(f"ℹ️ Message de type '{data.get('type')}' reçu")
                        else:
                            self.logger.info(f"⚠️ Message sans type reconnu: {json.dumps(data)[:200]}...")
                            
                except json.JSONDecodeError as e:
                    self.logger.error(f"❌ Impossible de parser le message JSON: {str(e)}")
                except Exception as e:
                    self.logger.error(f"❌ Erreur lors du traitement du message: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'écoute des trades: {str(e)}")
            self.is_connected = False
    
    def get_position_data(self, mint_address: str, initial_investment_sol: float) -> Dict[str, Any]:
        """
        Récupère les données actuelles de position pour un token
        
        Args:
            mint_address: Adresse du token
            initial_investment_sol: Investissement initial en SOL
            
        Returns:
            Données de position incluant le pourcentage de profit
        """
        if mint_address not in self.trading_data:
            self.logger.warning(f"⚠️ Aucune donnée disponible pour {mint_address}, utilisation des valeurs par défaut")
            return {
                "profit_percent": 0,
                "current_price": 0,
                "highest_price": 0,
                "price_drop_percent": 0,
                "price_history": [],
                "data_available": False
            }
            
        data = self.trading_data[mint_address]
        current_price = data["current_price"]
        highest_price = data["highest_price"]
        price_history = data.get("price_history", [])
        market_cap = data.get("market_cap", 0)
        initial_price = data.get("initial_price", initial_investment_sol)
        
        # Calcul du pourcentage de profit
        profit_percent = ((current_price - initial_price) / initial_price) * 100 if initial_price > 0 else 0
        
        # Calcul du pourcentage de chute depuis le plus haut
        price_drop_percent = 0
        if highest_price > 0:
            price_drop_percent = ((highest_price - current_price) / highest_price) * 100
        
        self.logger.info(
            f"📊 POSITION {mint_address}: "
            f"Prix actuel: {current_price:.10f} SOL/token, "
            f"Plus haut: {highest_price:.10f} SOL/token, "
            f"Profit: {profit_percent:.2f}%, "
            f"Chute depuis le plus haut: {price_drop_percent:.2f}%, "
            f"MarketCap: {market_cap:.2f} SOL"
        )

        return {
            "profit_percent": profit_percent,
            "current_price": current_price,
            "highest_price": highest_price,
            "price_drop_percent": price_drop_percent,
            "price_history": price_history,
            "market_cap": market_cap,
            "data_available": True
        }
    
    def sell_token(self, mint_address: str, percentage: str, slippage: int = 50, priority_fee: float = 0.001) -> Dict[str, Any]:
        """
        Vend un pourcentage du token via l'API PumpPortal
        
        Args:
            mint_address: Adresse du token à vendre
            percentage: Pourcentage à vendre (ex: "25%", "50%", "100%")
            slippage: Pourcentage de slippage autorisé
            priority_fee: Frais prioritaires
            
        Returns:
            Résultat de la transaction
        """
        try:
            # Construire les paramètres de la transaction
            tx_params = {
                "action": "sell",
                "mint": mint_address,
                "amount": percentage,  # PumpPortal accepte le format "X%" pour vendre un pourcentage de votre holding
                "denominatedInSol": "false",  # On vend un pourcentage de tokens, pas un montant en SOL
                "slippage": slippage,
                "priorityFee": priority_fee,
                "pool": "pump"
            }
            
            self.logger.info(f"Vente de {percentage} du token {mint_address}")
            
            # Exécuter la transaction via l'API PumpPortal
            result = self.pump_api.execute_trade_lightning(tx_params)
            
            if result.get("success"):
                self.logger.info(f"Vente réussie: {result.get('signature', 'N/A')}")
                
                if result.get("signature"):
                    self.logger.info(f"Transaction: https://solscan.io/tx/{result['signature']}")
            else:
                self.logger.error(f"Vente échouée: {result.get('error', 'Erreur inconnue')}")
            
            # Appeler le callback si défini
            if self.sale_callback:
                self.sale_callback(mint_address, percentage, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Exception lors de la vente: {str(e)}")
            result = {
                "success": False,
                "error": str(e)
            }
            
            # Appeler le callback même en cas d'erreur
            if self.sale_callback:
                self.sale_callback(mint_address, percentage, result)
                
            return result
    
    async def automate_sell_strategy(self, mint_address: str, initial_investment_sol: float = 1.0, max_duration_seconds: int = 20):
        """
        Implémentation de la stratégie de vente automatique
        
        Args:
            mint_address: Adresse du token à surveiller et vendre
            initial_investment_sol: Investissement initial en SOL
            max_duration_seconds: Durée maximale de surveillance en secondes
        """
        self.logger.info(f"🚀 Démarrage de la stratégie de vente pour {mint_address}...")
        self.logger.info(f"⏱️ Durée maximale: {max_duration_seconds} secondes")
        self.logger.info(f"💰 Investissement initial (prix): {initial_investment_sol:.10f} SOL")    
            
        # S'abonner au token pour recevoir les mises à jour
        await self.subscribe_to_token(mint_address)
        
        # Créer une tâche d'écoute seulement si aucune n'est en cours
        listen_task = None
        if not self.is_connected or not any(task for task in asyncio.all_tasks() if 'listen_for_trades' in str(task)):
            listen_task = asyncio.create_task(self.listen_for_trades())
            self.logger.info("🎧 Tâche d'écoute des trades créée")
        else:
            self.logger.info("🎧 Utilisation de la tâche d'écoute existante")
        
        # Variables pour les conditions de vente
        start_time = time.time()
        highest_price_seen = 0
        sold_25_percent = False

        first_price_received = False
        initial_price = 0

        # Ajouter un compteur d'intervalles pour espacer les logs
        interval_count = 0
        
        # On surveille pendant la durée spécifiée maximum
        while time.time() - start_time < max_duration_seconds:
            # Récupérer les données actuelles
            data = self.get_position_data(mint_address, initial_investment_sol)
            
            # Si c'est la première fois qu'on reçoit des données valides
            if data.get("data_available", False) and not first_price_received:
                initial_price = data["current_price"]
                # Stocker le prix initial dans les données du token
                if mint_address in self.trading_data:
                    self.trading_data[mint_address]["initial_price"] = initial_price
                first_price_received = True
                self.logger.info(f"💲 Prix initial enregistré: {initial_price:.10f} SOL/token")

            profit_percent = data["profit_percent"]
            current_price = data["current_price"]
            highest_price = data["highest_price"]
            price_drop_percent = data["price_drop_percent"]
            data_available = data.get("data_available", False)
            
            highest_price_seen = max(highest_price_seen, current_price)
            
            # Calcul des métriques pour les conditions
            # Si on a le prix initial enregistré, utiliser celui-ci au lieu de initial_investment_sol
            if first_price_received:
                price_increase_percent = ((current_price - initial_price) / initial_price) * 100 if initial_price > 0 else 0
            else:
                price_increase_percent = ((current_price - initial_investment_sol) / initial_investment_sol) * 100 if initial_investment_sol > 0 else 0
                        
            # Log d'état périodique (toutes les 5 secondes)
            if interval_count % 5 == 0:
                elapsed_time = time.time() - start_time
                self.logger.info(
                    f"⏱️ {elapsed_time:.1f}s/{max_duration_seconds}s écoulées | "
                    f"Données disponibles: {data_available} | "
                    f"Prix: {current_price:.10f} SOL | "
                    f"Profit: {profit_percent:.2f}% | "
                    f"Chute: {price_drop_percent:.2f}%"
                )
            
            interval_count += 1
            
            # Évaluation détaillée des conditions (avec logs)
            # ==================================================
        
            # CONDITION 2: Si la position monte de 100%
            if profit_percent >= 100 and not sold_25_percent:
                self.logger.info(f"🔔 CONDITION 2 ACTIVÉE: Profit +100% détecté ({profit_percent:.2f}%)")
                self.logger.info(f"📊 Détails: Prix initial={initial_investment_sol:.10f}, Prix actuel={current_price:.10f}, Profit={profit_percent:.2f}%")
                
                # Vente de 25%
                self.logger.info("💰 VENTE 25% (Première étape)")
                result_25 = self.sell_token(mint_address, "25%")
                
                if not result_25.get("success"):
                    self.logger.error(f"❌ Échec de la première vente: {result_25.get('error', 'Erreur inconnue')}")
                    continue
                    
                sold_25_percent = True
                await asyncio.sleep(2)  # Attente de 2 secondes
                
                # Vente de 50% du restant
                self.logger.info("💰 VENTE 50% du supply restant (Deuxième étape)")
                result_50 = self.sell_token(mint_address, "50%")
                result_50 = self.sell_token(mint_address, "50%")
                
                if not result_50.get("success"):
                    self.logger.error(f"Échec de la deuxième vente: {result_50.get('error', 'Erreur inconnue')}")
                    continue
                    
                await asyncio.sleep(3)  # Attente de 3 secondes
                
                # Vente du reste
                self.logger.info("Vente finale: 100% du restant")
                result_final = self.sell_token(mint_address, "100%")
                
                if not result_final.get("success"):
                    self.logger.error(f"Échec de la vente finale: {result_final.get('error', 'Erreur inconnue')}")
                
                # Fin de la stratégie
                if listen_task:
                    listen_task.cancel()
                return
            
            # CONDITION 3: Si profit ≥ 75% puis chute de 25% depuis le sommet
            if profit_percent >= 75 and price_drop_percent >= 25:
                self.logger.info(f"Condition 3 activée: Hausse de {price_increase_percent:.2f}% puis chute de {price_drop_percent:.2f}%")
                
                # Vente de 100%
                self.logger.info("Vente de 100%")
                result = self.sell_token(mint_address, "100%")
                
                if not result.get("success"):
                    self.logger.error(f"Échec de la vente: {result.get('error', 'Erreur inconnue')}")
                
                # Fin de la stratégie
                if listen_task:
                    listen_task.cancel()
                return
            
            # CONDITION 4: Si profit entre +10% et +75% puis chute de 15% (trailing stop)
            if 10 <= profit_percent < 75 and price_drop_percent >= 15:
                self.logger.info(f"Condition 4 activée: Hausse de {price_increase_percent:.2f}% (entre 10% et 75%) puis chute de {price_drop_percent:.2f}%")
                
                # Vente de 100% (trailing stop)
                self.logger.info("Vente de 100% (trailing stop)")
                result = self.sell_token(mint_address, "100%")
                
                if not result.get("success"):
                    self.logger.error(f"Échec de la vente: {result.get('error', 'Erreur inconnue')}")
                
                # Fin de la stratégie
                if listen_task:
                    listen_task.cancel()
                return
            
            # Attente avant la prochaine vérification
            await asyncio.sleep(1)
        
        # CONDITION 1: Si aucune autre condition n'a été déclenchée après la durée maximale
        self.logger.info(f"Condition 1 activée: {max_duration_seconds} secondes écoulées sans autre condition déclenchée")
        
        # Vente de 100%
        self.logger.info("Vente de 100%")
        result = self.sell_token(mint_address, "100%")
        
        if not result.get("success"):
            self.logger.error(f"Échec de la vente: {result.get('error', 'Erreur inconnue')}")
        
        # Fin de la stratégie
        if listen_task:
            listen_task.cancel()
    
    def close(self):
        """Ferme proprement les connexions"""
        if self.ws:
            asyncio.create_task(self.ws.close())
            self.is_connected = False
            self.logger.info("Connexion websocket fermée")