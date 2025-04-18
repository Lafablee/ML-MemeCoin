# price_analyzer.py
# Script indépendant pour analyser les prix d'un token

import json
import time
import argparse
import websockets
import asyncio
import ssl
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("price_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TokenPriceAnalyzer:
    """Outil d'analyse des prix des tokens en temps réel"""
    
    def __init__(self):
        self.ws = None
        self.is_connected = False
        self.price_data = {}
        self.start_time = datetime.now()
    
    async def connect_to_websocket(self):
        """Se connecte au websocket de PumpPortal"""
        if self.is_connected:
            return
            
        try:
            logger.info("🔌 Connexion au websocket PumpPortal...")
    
            # Se connecter avec le contexte SSL
            self.ws = await websockets.connect(
                "wss://pumpportal.fun/api/data", 
            )
            
            self.is_connected = True
            logger.info("✅ Connexion websocket établie avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la connexion au websocket: {str(e)}")
            
            # Tentative alternative
            try:
                logger.info("🔄 Tentative avec URL alternative...")
                self.ws = await websockets.connect("ws://pumpportal.fun/api/data")
                self.is_connected = True
                logger.info("✅ Connexion alternative établie avec succès")
            except Exception as alt_e:
                logger.error(f"❌ Échec également avec l'URL alternative: {str(alt_e)}")
                self.is_connected = False
    
    async def subscribe_to_token(self, mint_address):
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
            logger.info(f"📡 Abonné aux trades du token {mint_address}")
            
            # Initialiser les données pour ce token
            self.price_data[mint_address] = {
                "prices": [],
                "highest_price": 0,
                "lowest_price": float('inf'),
                "initial_price": None,
                "current_price": 0,
                "buy_trades": 0,
                "sell_trades": 0,
                "volume_sol": 0
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'abonnement au token {mint_address}: {str(e)}")
    
    async def analyze_price_trends(self, mint_address, duration_seconds=60):
        """Analyse les tendances de prix d'un token pendant une durée spécifiée"""
        if not self.is_connected:
            await self.connect_to_websocket()
            
        # S'abonner au token
        await self.subscribe_to_token(mint_address)
        
        logger.info(f"📊 Début de l'analyse du token {mint_address} pendant {duration_seconds} secondes")
        
        # Temps de début
        start_time = time.time()
        
        try:
            # Boucle d'écoute pendant la durée spécifiée
            while time.time() - start_time < duration_seconds:
                message = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
                
                try:
                    data = json.loads(message)
                    
                    # Traiter les messages d'abonnement
                    if "message" in data and "subscribed" in data.get("message", "").lower():
                        logger.info(f"✅ {data.get('message')}")
                        continue
                    
                    # Vérifier si c'est un message de trade pour notre token
                    if "mint" in data and data["mint"] == mint_address and "txType" in data:
                        tx_type = data["txType"]  # "buy" ou "sell"
                        token_amount = float(data.get("tokenAmount", 0))
                        sol_amount = float(data.get("solAmount", 0))
                        market_cap = float(data.get("marketCapSol", 0))
                        
                        # Calculer le prix unitaire
                        if token_amount > 0:
                            price = sol_amount / token_amount
                        else:
                            price = 0
                        
                        # Mettre à jour les statistiques
                        token_data = self.price_data[mint_address]
                        
                        # Stocker le prix initial si c'est le premier
                        if token_data["initial_price"] is None:
                            token_data["initial_price"] = price
                        
                        # Mettre à jour les prix
                        token_data["current_price"] = price
                        token_data["highest_price"] = max(token_data["highest_price"], price)
                        if price > 0:
                            token_data["lowest_price"] = min(token_data["lowest_price"], price)
                        
                        # Compte des trades
                        if tx_type.lower() == "buy":
                            token_data["buy_trades"] += 1
                        elif tx_type.lower() == "sell":
                            token_data["sell_trades"] += 1
                        
                        # Volume
                        token_data["volume_sol"] += sol_amount
                        
                        # Stocker l'historique des prix
                        token_data["prices"].append({
                            "price": price,
                            "timestamp": datetime.now(),
                            "type": tx_type,
                            "sol_amount": sol_amount,
                            "token_amount": token_amount,
                            "market_cap": market_cap
                        })
                        
                        # Calculer les métriques
                        price_change = 0
                        if token_data["initial_price"] and token_data["initial_price"] > 0:
                            price_change = ((price - token_data["initial_price"]) / token_data["initial_price"]) * 100
                        
                        drop_from_high = 0
                        if token_data["highest_price"] > 0:
                            drop_from_high = ((token_data["highest_price"] - price) / token_data["highest_price"]) * 100
                        
                        # Logger les informations
                        logger.info(
                            f"💹 {tx_type.upper()}: Prix={price:.10f} SOL/token, "
                            f"Variation={price_change:+.2f}%, "
                            f"Chute={drop_from_high:.2f}%, "
                            f"Volume={token_data['volume_sol']:.6f} SOL, "
                            f"MarketCap={market_cap:.2f} SOL"
                        )
                        
                        # Afficher un résumé toutes les 10 secondes
                        elapsed = time.time() - start_time
                        if int(elapsed) % 10 == 0 and int(elapsed) > 0:
                            self._print_summary(mint_address, elapsed)
                    
                except json.JSONDecodeError:
                    logger.warning("⚠️ Message non-JSON reçu")
                except Exception as e:
                    logger.error(f"❌ Erreur de traitement: {str(e)}")
                
                # Ne pas attendre si timeout
                await asyncio.sleep(0.1)
                
        except asyncio.TimeoutError:
            # C'est normal, on continue
            pass
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse: {str(e)}")
        
        # Afficher le résumé final
        self._print_final_summary(mint_address, duration_seconds)
        
        return self.price_data.get(mint_address, {})
    
    def _print_summary(self, mint_address, elapsed_seconds):
        """Affiche un résumé périodique des données de prix"""
        data = self.price_data.get(mint_address, {})
        if not data or not data.get("prices"):
            logger.info(f"⏱️ {elapsed_seconds:.1f}s - Aucune donnée disponible pour {mint_address}")
            return
        
        initial = data.get("initial_price", 0)
        current = data.get("current_price", 0)
        highest = data.get("highest_price", 0)
        lowest = data.get("lowest_price", float('inf'))
        
        if lowest == float('inf'):
            lowest = 0
        
        change = ((current - initial) / initial * 100) if initial > 0 else 0
        drop = ((highest - current) / highest * 100) if highest > 0 else 0
        
        logger.info(
            f"⏱️ RÉSUMÉ à {elapsed_seconds:.1f}s: "
            f"Prix={current:.10f} SOL, "
            f"Variation={change:+.2f}%, "
            f"Plus haut={highest:.10f}, "
            f"Plus bas={lowest:.10f}, "
            f"Chute={drop:.2f}%, "
            f"Trades: {data.get('buy_trades', 0)}🟢 {data.get('sell_trades', 0)}🔴"
        )
    
    def _print_final_summary(self, mint_address, duration_seconds):
        """Affiche le résumé final de l'analyse"""
        data = self.price_data.get(mint_address, {})
        if not data or not data.get("prices"):
            logger.info(f"📊 ANALYSE TERMINÉE ({duration_seconds}s) - Aucune donnée pour {mint_address}")
            return
        
        prices = data.get("prices", [])
        initial = data.get("initial_price", 0)
        current = data.get("current_price", 0)
        highest = data.get("highest_price", 0)
        lowest = data.get("lowest_price", float('inf'))
        
        if lowest == float('inf'):
            lowest = 0
        
        change = ((current - initial) / initial * 100) if initial > 0 else 0
        drop = ((highest - current) / highest * 100) if highest > 0 else 0
        volatility = ((highest - lowest) / lowest * 100) if lowest > 0 else 0
        
        logger.info("\n" + "="*50)
        logger.info(f"📊 ANALYSE TERMINÉE - {mint_address} ({duration_seconds}s)")
        logger.info(f"🔢 Nombre de trades: {len(prices)} ({data.get('buy_trades', 0)} achats, {data.get('sell_trades', 0)} ventes)")
        logger.info(f"💰 Volume total: {data.get('volume_sol', 0):.6f} SOL")
        logger.info(f"📈 Prix initial: {initial:.10f} SOL/token")
        logger.info(f"📉 Prix final: {current:.10f} SOL/token")
        logger.info(f"⬆️ Prix le plus haut: {highest:.10f} SOL/token")
        logger.info(f"⬇️ Prix le plus bas: {lowest:.10f} SOL/token")
        logger.info(f"📊 Variation totale: {change:+.2f}%")
        logger.info(f"📉 Chute depuis le sommet: {drop:.2f}%")
        logger.info(f"📊 Volatilité: {volatility:.2f}%")
        
        # Analyse des conditions de vente
        logger.info("\n🤖 ANALYSE DES CONDITIONS DE VENTE:")
        
        # Condition 2: Profit +100%
        profit_100 = change >= 100
        logger.info(f"Condition 2 (Profit +100%): {'✅ ACTIVÉE' if profit_100 else '❌ Non activée'} ({change:.2f}%)")
        
        # Condition 3: Profit +75% puis chute 25%
        profit_75_drop_25 = change >= 75 and drop >= 25
        logger.info(f"Condition 3 (Profit +75% puis chute 25%): {'✅ ACTIVÉE' if profit_75_drop_25 else '❌ Non activée'} (Profit: {change:.2f}%, Chute: {drop:.2f}%)")
        
        # Condition 4: Profit entre 10% et 75% puis chute 15%
        profit_10_75_drop_15 = 10 <= change < 75 and drop >= 15
        logger.info(f"Condition 4 (Profit 10-75% puis chute 15%): {'✅ ACTIVÉE' if profit_10_75_drop_15 else '❌ Non activée'} (Profit: {change:.2f}%, Chute: {drop:.2f}%)")
        
        # Condition activée
        if profit_100:
            logger.info("🚨 STRATÉGIE RECOMMANDÉE: Vendre 25%, puis 50% du reste, puis le reste")
        elif profit_75_drop_25:
            logger.info("🚨 STRATÉGIE RECOMMANDÉE: Vendre 100% immédiatement (protection après forte hausse)")
        elif profit_10_75_drop_15:
            logger.info("🚨 STRATÉGIE RECOMMANDÉE: Vendre 100% immédiatement (trailing stop)")
        else:
            logger.info("🚨 STRATÉGIE RECOMMANDÉE: Vendre 100% après timeout (aucune condition activée)")
        
        logger.info("="*50 + "\n")


async def main():
    parser = argparse.ArgumentParser(description="Analyseur de prix de tokens en temps réel")
    parser.add_argument("--mint", required=True, help="Adresse mint du token")
    parser.add_argument("--duration", type=int, default=60, help="Durée d'analyse en secondes (défaut: 60)")
    
    args = parser.parse_args()
    
    # Désactiver SSL globalement
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    analyzer = TokenPriceAnalyzer()
    
    try:
        await analyzer.analyze_price_trends(args.mint, args.duration)
    except KeyboardInterrupt:
        logger.info("Analyse interrompue par l'utilisateur")
    finally:
        # Fermer la connexion
        if analyzer.ws:
            await analyzer.ws.close()
        logger.info("Analyse terminée")


if __name__ == "__main__":
    asyncio.run(main())