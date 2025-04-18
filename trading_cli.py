# trading_cli.py

import os
import ssl_config

import sys
import json
import logging
import asyncio
import argparse
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

from token_trading_integration import TokenTradingIntegration

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("token_trading.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

def check_environment():
    """Vérifie que les variables d'environnement nécessaires sont définies"""
    api_key = os.getenv("PUMPORTAL_API_KEY")
    
    if not api_key:
        logger.warning("PUMPORTAL_API_KEY n'est pas définie dans les variables d'environnement.")
        logger.warning("Vous pouvez la définir dans un fichier .env ou la fournir en paramètre.")
        return False
    
    return True

async def publish_and_trade_token(api_key: str, memecoin_data: Dict[str, Any], 
                                image_url: Optional[str] = None,
                                image_path: Optional[str] = None,
                                dev_buy_amount: float = 0.01,
                                dry_run: bool = True,
                                max_duration: int = 3600):
    """
    Publie un memecoin et le surveille pour le trading
    """
    # Initialiser l'intégration
    integration = TokenTradingIntegration(api_key)
    
    # Publier et surveiller
    result = await integration.publish_and_monitor(
        memecoin_data=memecoin_data,
        image_url=image_url,
        image_path=image_path,
        dev_buy_amount=dev_buy_amount,
        dry_run=dry_run,
        max_monitor_duration=max_duration,
        auto_sell=True
    )
    
    # Afficher le résultat
    if result.get("success"):
        logger.info("Publication réussie!")
        
        if result.get("is_dry_run", True):
            logger.info("Mode simulation : aucune transaction réelle n'a été effectuée")
        else:
            logger.info(f"Transaction: {result.get('signature', 'N/A')}")
            logger.info(f"Explorer: {result.get('explorer_url', 'N/A')}")
            
            if result.get("trading_started"):
                logger.info("Surveillance de trading démarrée")
                logger.info(f"Durée maximale: {result.get('max_monitor_duration', 3600)} secondes")
    else:
        logger.error(f"Publication échouée: {result.get('error', 'Erreur inconnue')}")
    
    return result

async def monitor_existing_token(api_key: str, mint_address: str, initial_investment: float, max_duration: int = 3600):
    """
    Surveille un token existant pour le trading
    """
    # Initialiser l'intégration
    integration = TokenTradingIntegration(api_key)
    
    # Démarrer le monitoring en arrière-plan
    await integration.start_background_monitoring()
    
    # Ajouter le token à la surveillance
    success = await integration.add_existing_token_to_monitoring(
        mint_address=mint_address,
        initial_investment=initial_investment,
        max_duration=max_duration
    )
    
    if success:
        logger.info(f"Surveillance démarrée pour {mint_address}")
        logger.info(f"Durée maximale: {max_duration} secondes")
        
        # Attendre que la surveillance se termine
        logger.info("Attente de la fin de la surveillance...")
        
        # Monitorer pendant la durée maximale plus une marge
        await asyncio.sleep(max_duration + 30)
        
        # Afficher le statut final
        status = integration.get_token_trading_status(mint_address)
        if status:
            logger.info(f"Statut final: {status.get('trading_status', 'inconnu')}")
            
            # Afficher les ventes effectuées
            sales = status.get("sales", [])
            if sales:
                logger.info(f"Ventes effectuées: {len(sales)}")
                for i, sale in enumerate(sales):
                    logger.info(f"Vente {i+1}: {sale.get('percentage')} - {'Réussie' if sale.get('success') else 'Échouée'}")
                    if sale.get("signature"):
                        logger.info(f"  Transaction: https://solscan.io/tx/{sale['signature']}")
            else:
                logger.info("Aucune vente effectuée")
        else:
            logger.error(f"Impossible de récupérer le statut final pour {mint_address}")
    else:
        logger.error(f"Impossible de démarrer la surveillance pour {mint_address}")
    
    # Arrêter le monitoring
    integration.stop_background_monitoring()

async def interactive_mode(api_key: Optional[str] = None):
    """
    Mode interactif pour l'interface de ligne de commande
    """
    print("\n========================================")
    print("MEMECOIN PUBLISHER & TRADING MANAGER")
    print("========================================\n")
    
    # Initialiser l'intégration
    integration = TokenTradingIntegration(api_key)
    
    # Vérifier la clé API
    if not api_key and not integration.publisher.pump_api.api_key:
        api_key = input("Clé API PumpPortal: ")
        if api_key:
            integration.set_api_key(api_key)
    
    if integration.publisher.pump_api.api_key:
        print("✅ Clé API PumpPortal configurée")
    else:
        print("❌ Aucune clé API PumpPortal configurée")
        print("Les opérations seront en mode simulation uniquement")
    
    # Boucle principale du mode interactif
    while True:
        print("\nQue souhaitez-vous faire?")
        print("1. Publier un nouveau memecoin et surveiller le trading")
        print("2. Surveiller un token existant")
        print("3. Afficher l'historique de trading")
        print("4. Configurer l'API PumpPortal")
        print("5. Quitter")
        
        choice = input("\nVotre choix (1-5): ")
        
        if choice == "1":
            # Publier un nouveau memecoin
            print("\n=== PUBLICATION D'UN NOUVEAU MEMECOIN ===")
            
            token_name = input("Nom du token: ")
            token_symbol = input("Symbole du token (en majuscules): ")
            description = input("Description (optionnel): ")
            
            # Demander l'URL de l'image
            image_url = input("URL de l'image (optionnel): ")
            
            # Créer les données du memecoin
            memecoin_data = {
                "token_name": token_name,
                "token_symbol": token_symbol.upper(),
                "description": description
            }
            
            # Demander le montant d'achat
            dev_buy_amount_str = input("Montant d'achat en SOL (défaut=0.01): ")
            try:
                dev_buy_amount = float(dev_buy_amount_str) if dev_buy_amount_str else 0.01
            except ValueError:
                dev_buy_amount = 0.01
                print(f"Valeur invalide, utilisation de la valeur par défaut: {dev_buy_amount} SOL")
            
            # Demander le mode (simulation ou réel)
            dry_run_str = input("Mode simulation? (o/n, défaut=o): ")
            dry_run = dry_run_str.lower() not in ["n", "non", "no"]
            
            # Durée maximale de surveillance
            max_duration_str = input("Durée maximale de surveillance en secondes (défaut=3600): ")
            try:
                max_duration = int(max_duration_str) if max_duration_str else 3600
            except ValueError:
                max_duration = 3600
                print(f"Valeur invalide, utilisation de la valeur par défaut: {max_duration} secondes")
            
            # Confirmation finale
            if not dry_run:
                confirm = input("\n⚠️ ATTENTION: Mode réel activé - des transactions réelles seront effectuées.\nConfirmer? (o/n): ")
                if confirm.lower() not in ["o", "oui", "y", "yes"]:
                    print("Opération annulée")
                    continue
            
            # Démarrer le task de monitoring en arrière-plan
            await integration.start_background_monitoring()
            
            # Publier et surveiller
            print("\nPublication en cours...")
            result = await integration.publish_and_monitor(
                memecoin_data=memecoin_data,
                image_url=image_url if image_url else None,
                dev_buy_amount=dev_buy_amount,
                dry_run=dry_run,
                max_monitor_duration=max_duration,
                auto_sell=True
            )
            
            # Afficher le résultat
            if result.get("success"):
                print("\n=== PUBLICATION RÉUSSIE ===")
                print(f"Token: {memecoin_data['token_name']} ({memecoin_data['token_symbol']})")
                
                if result.get("is_dry_run", True):
                    print("Mode: SIMULATION (aucune transaction réelle)")
                else:
                    print("Mode: RÉEL")
                    print(f"Transaction: {result.get('signature', 'N/A')}")
                    
                    if result.get("explorer_url"):
                        print(f"Explorer: {result.get('explorer_url')}")
                    
                    mint_address = result.get("mint_address")
                    if mint_address and result.get("trading_started"):
                        print("\nSurveillance de trading démarrée")
                        print(f"Token: {mint_address}")
                        print(f"Durée maximale: {max_duration} secondes")
                        print("\nLes résultats du trading seront enregistrés...")
                        
                        # Attendre un certain temps pour voir quelques données
                        wait_time = min(max_duration, 60)  # Attendre au max 60 secondes
                        print(f"\nAttente de {wait_time} secondes pour voir les premières données...")
                        await asyncio.sleep(wait_time)
                        
                        # Afficher les données récentes
                        status = integration.get_token_trading_status(mint_address)
                        if status and status.get("sales"):
                            print("\nVentes effectuées:")
                            for sale in status.get("sales", []):
                                print(f"- {sale.get('percentage')}: {'Réussie' if sale.get('success') else 'Échouée'}")
                                if sale.get("signature"):
                                    print(f"  Transaction: https://solscan.io/tx/{sale['signature']}")
                        else:
                            print("\nAucune vente effectuée pour l'instant")
                            print("La surveillance continue en arrière-plan")
            else:
                print("\n❌ PUBLICATION ÉCHOUÉE")
                print(f"Erreur: {result.get('error', 'Erreur inconnue')}")
        
        elif choice == "2":
            # Surveiller un token existant
            print("\n=== SURVEILLANCE D'UN TOKEN EXISTANT ===")
            
            mint_address = input("Adresse du token (mint address): ")
            
            if not mint_address:
                print("Adresse du token requise")
                continue
            
            # Demander l'investissement initial
            investment_str = input("Investissement initial en SOL (défaut=0.01): ")
            try:
                investment = float(investment_str) if investment_str else 0.01
            except ValueError:
                investment = 0.01
                print(f"Valeur invalide, utilisation de la valeur par défaut: {investment} SOL")
            
            # Durée maximale de surveillance
            max_duration_str = input("Durée maximale de surveillance en secondes (défaut=3600): ")
            try:
                max_duration = int(max_duration_str) if max_duration_str else 3600
            except ValueError:
                max_duration = 3600
                print(f"Valeur invalide, utilisation de la valeur par défaut: {max_duration} secondes")
            
            # Démarrer le monitoring
            print(f"\nDémarrage de la surveillance pour {mint_address}...")
            await monitor_existing_token(
                api_key=integration.publisher.pump_api.api_key,
                mint_address=mint_address,
                initial_investment=investment,
                max_duration=max_duration
            )
        
        elif choice == "3":
            # Afficher l'historique de trading
            print("\n=== HISTORIQUE DE TRADING ===")
            
            history = integration.get_trading_history()
            
            if not history:
                print("Aucune transaction dans l'historique")
                continue
            
            print(f"Nombre total de transactions: {len(history)}")
            
            for i, entry in enumerate(history):
                print(f"\n{i+1}. {entry.get('token_name', 'Unknown')} ({entry.get('token_symbol', 'UNKNOWN')})")
                print(f"   Mint Address: {entry.get('mint_address', 'N/A')}")
                print(f"   Statut: {entry.get('trading_status', 'inconnu')}")
                print(f"   Investissement: {entry.get('initial_investment', 0)} SOL")
                
                # Afficher les ventes
                sales = entry.get("sales", [])
                if sales:
                    print(f"   Ventes: {len(sales)}")
                    for j, sale in enumerate(sales):
                        print(f"     {j+1}. {sale.get('percentage')}: {'Réussie' if sale.get('success') else 'Échouée'}")
                        if sale.get("signature"):
                            print(f"        Transaction: https://solscan.io/tx/{sale['signature']}")
                else:
                    print("   Aucune vente")
        
        elif choice == "4":
            # Configurer l'API PumpPortal
            print("\n=== CONFIGURATION DE L'API PUMPORTAL ===")
            
            current_key = integration.publisher.pump_api.api_key
            masked_key = "••••" + current_key[-4:] if current_key else "Non configurée"
            
            print(f"Clé API actuelle: {masked_key}")
            
            new_key = input("Nouvelle clé API (laisser vide pour conserver la clé actuelle): ")
            
            if new_key:
                integration.set_api_key(new_key)
                print("✅ Nouvelle clé API configurée")
        
        elif choice == "5":
            # Quitter
            print("\nMerci d'avoir utilisé le gestionnaire de trading. À bientôt!")
            break
        
        else:
            print("Choix invalide, veuillez réessayer")

async def main():
    """
    Point d'entrée principal du programme
    """
    parser = argparse.ArgumentParser(description='Gestionnaire de trading pour memecoins')
    parser.add_argument('--api-key', help='Clé API PumpPortal')
    parser.add_argument('--publish', action='store_true', help='Publier un nouveau memecoin')
    parser.add_argument('--monitor', help='Surveiller un token existant (fournir l\'adresse mint)')
    parser.add_argument('--name', help='Nom du token (pour --publish)')
    parser.add_argument('--symbol', help='Symbole du token (pour --publish)')
    parser.add_argument('--image', help='URL ou chemin de l\'image (pour --publish)')
    parser.add_argument('--investment', type=float, default=0.01, help='Investissement initial en SOL')
    parser.add_argument('--duration', type=int, default=3600, help='Durée maximale de surveillance en secondes')
    parser.add_argument('--dry-run', action='store_true', help='Mode simulation (pas de transaction réelle)')
    parser.add_argument('--interactive', action='store_true', help='Mode interactif')
    
    args = parser.parse_args()
    
    # Vérifier l'environnement
    env_ok = check_environment()
    
    # Déterminer la clé API à utiliser
    api_key = args.api_key or os.getenv("PUMPORTAL_API_KEY")
    
    if args.interactive:
        # Mode interactif
        await interactive_mode(api_key)
    elif args.publish:
        # Vérifier les arguments requis
        if not args.name or not args.symbol:
            logger.error("--name et --symbol sont requis avec --publish")
            sys.exit(1)
        
        # Créer les données du memecoin
        memecoin_data = {
            "token_name": args.name,
            "token_symbol": args.symbol.upper(),
            "description": f"Token {args.name} created via trading CLI"
        }
        
        # Déterminer si c'est une URL ou un chemin local
        image_url = None
        image_path = None
        
        if args.image:
            if args.image.startswith(('http://', 'https://')):
                image_url = args.image
            else:
                image_path = args.image
        
        # Publier et surveiller
        await publish_and_trade_token(
            api_key=api_key,
            memecoin_data=memecoin_data,
            image_url=image_url,
            image_path=image_path,
            dev_buy_amount=args.investment,
            dry_run=args.dry_run,
            max_duration=args.duration
        )
    elif args.monitor:
        # Surveiller un token existant
        await monitor_existing_token(
            api_key=api_key,
            mint_address=args.monitor,
            initial_investment=args.investment,
            max_duration=args.duration
        )
    else:
        # Afficher l'aide si aucune action n'est spécifiée
        parser.print_help()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOpération interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erreur non gérée: {str(e)}", exc_info=True)
        sys.exit(1)