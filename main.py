#main.py
import os
import logging
import argparse
from dotenv import load_dotenv

from config import Config
from simulator import TweetSimulator
# Le tweet_listener sera implémenté plus tard quand l'API sera disponible

def setup_logging():
    """Configure le système de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("memecoin_generator.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_environment():
    """Vérifie que les variables d'environnement nécessaires sont définies"""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(
            f"Variables d'environnement manquantes: {', '.join(missing_vars)}. "
            "Veuillez définir ces variables dans un fichier .env."
        )

def main():
    """Point d'entrée principal du programme"""
    # Charger les variables d'environnement
    load_dotenv()
    
    # Configuration du logging
    logger = setup_logging()
    logger.info("Démarrage du générateur de meme coins")
    
    # Vérifier les variables d'environnement
    try:
        check_environment()
    except EnvironmentError as e:
        logger.error(str(e))
        return
    
    # Charger la configuration
    config = Config()
    
    # Parser les arguments de ligne de commande
    parser = argparse.ArgumentParser(description='Générateur de meme coins basé sur les tweets')
    parser.add_argument('--mode', choices=['simulator', 'listener'], default='simulator',
                      help='Mode de fonctionnement (simulator: pour tests, listener: pour l\'API)')
    parser.add_argument('--data-dir', default='data',
                      help='Répertoire pour le stockage des données')
    
    args = parser.parse_args()
    
    # Mode de fonctionnement
    if args.mode == 'simulator':
        logger.info("Démarrage en mode simulateur")
        simulator = TweetSimulator(config, data_dir=args.data_dir)
        simulator.run_interactive_mode()
    
    elif args.mode == 'listener':
        logger.info("Démarrage en mode écouteur d'API")
        logger.warning("Mode écouteur d'API non implémenté pour le moment")
        # Cette partie sera implémentée plus tard quand l'API sera disponible
        # tweet_listener = TweetListener(config, data_dir=args.data_dir)
        # tweet_listener.start()
    
if __name__ == "__main__":
    main()