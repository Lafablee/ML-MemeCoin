# fichier spécifique pour la gestion des erreurs de retour openAI

STATUS_CODES = {
    # Codes de non-qualification pour conditions spécifiques
    801: "Contenu Elon insuffisamment viral ou impulsif",
    802: "Contenu Trump insuffisamment choquant ou humoristique",
    803: "Contenu de marque sociale trop générique",
    804: "Contenu de marque Elon insuffisamment impactant",
    
    # Vous pouvez ajouter d'autres codes au besoin
}

def get_status_message(code):
    """Récupère le message associé à un code de statut"""
    return STATUS_CODES.get(code, "Code de statut inconnu")