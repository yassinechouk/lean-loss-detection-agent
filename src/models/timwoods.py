"""
Définitions de la typologie TIMWOODS pour la classification des pertes Lean.
"""
from enum import Enum
from typing import Dict, List
from dataclasses import dataclass


class TimwoodsCategory(str, Enum):
    """Énumération des 8 catégories de pertes TIMWOODS."""
    
    TRANSPORT = "Transport"
    INVENTORY = "Inventory"
    MOTION = "Motion"
    WAITING = "Waiting"
    OVER_PROCESSING = "OverProcessing"
    OVER_PRODUCTION = "OverProduction"
    DEFECTS = "Defects"
    SKILLS = "Skills"


@dataclass
class TimwoodsDefinition:
    """Définition complète d'une catégorie TIMWOODS."""
    
    name: str
    description: str
    examples: List[str]
    indicators: List[str]


# Définitions complètes de chaque catégorie TIMWOODS
TIMWOODS_DEFINITIONS: Dict[TimwoodsCategory, TimwoodsDefinition] = {
    TimwoodsCategory.TRANSPORT: TimwoodsDefinition(
        name="Transport",
        description="Déplacements inutiles de matériaux, produits ou informations qui n'ajoutent pas de valeur au produit final.",
        examples=[
            "Déplacements excessifs de pièces entre postes de travail éloignés",
            "Multiples manipulations de matériaux avant utilisation",
            "Flux logistiques non optimisés avec va-et-vient",
            "Transport de pièces vers des zones de stockage intermédiaires inutiles",
            "Trajets excessifs pour chercher des outils ou des composants"
        ],
        indicators=[
            "Distance totale parcourue par les produits",
            "Nombre de manutentions par pièce",
            "Temps de transport entre postes",
            "Nombre de déplacements de chariots/transpalettes",
            "Coût de la logistique interne"
        ]
    ),
    
    TimwoodsCategory.INVENTORY: TimwoodsDefinition(
        name="Inventaire",
        description="Stock excédentaire de matières premières, en-cours de production ou produits finis qui immobilise du capital et masque les problèmes.",
        examples=[
            "Sur-stockage de matières premières par précaution",
            "En-cours excessifs entre postes de travail",
            "Produits finis stockés avant livraison client",
            "Pièces obsolètes ou périmées dans les stocks",
            "Composants commandés en trop grande quantité"
        ],
        indicators=[
            "Taux de rotation des stocks",
            "Valeur du stock immobilisé",
            "Nombre de jours de stock disponible",
            "Taux d'obsolescence",
            "Espace de stockage utilisé"
        ]
    ),
    
    TimwoodsCategory.MOTION: TimwoodsDefinition(
        name="Mouvement",
        description="Mouvements inutiles des opérateurs qui ne créent pas de valeur ajoutée (gestes inefficaces, déplacements).",
        examples=[
            "Opérateur qui se retourne pour prendre des outils mal positionnés",
            "Mouvements répétitifs excessifs pour atteindre des composants",
            "Recherche d'outils ou de documents mal rangés",
            "Déplacements fréquents vers imprimantes ou armoires éloignées",
            "Gestes inutiles dans les séquences opératoires"
        ],
        indicators=[
            "Temps de cycle opérateur",
            "Distance parcourue par l'opérateur",
            "Nombre de gestes par opération",
            "Temps de recherche d'outils",
            "Ergonomie du poste de travail"
        ]
    ),
    
    TimwoodsCategory.WAITING: TimwoodsDefinition(
        name="Attente",
        description="Temps d'attente machines, opérateurs ou pièces sans création de valeur (attente de pièces, de décisions, de réglages).",
        examples=[
            "Machine en attente de matière première",
            "Opérateur en attente de l'autorisation de démarrage",
            "Attente de validation qualité avant passage au poste suivant",
            "File d'attente devant une machine goulot",
            "Attente d'informations ou de décisions",
            "Temps de synchronisation entre postes déséquilibrés"
        ],
        indicators=[
            "Temps d'attente cumulé",
            "Taux d'utilisation des machines",
            "Temps de cycle vs temps de valeur ajoutée",
            "Durée moyenne des files d'attente",
            "Nombre d'arrêts pour attente"
        ]
    ),
    
    TimwoodsCategory.OVER_PROCESSING: TimwoodsDefinition(
        name="Sur-traitement",
        description="Opérations, contrôles ou traitements qui dépassent les exigences client et n'ajoutent pas de valeur perçue.",
        examples=[
            "Contrôles qualité redondants ou excessifs",
            "Finitions ou tolérances plus strictes que nécessaire",
            "Saisie multiple des mêmes informations",
            "Rapports détaillés jamais exploités",
            "Traitements de surface non demandés par le client",
            "Contrôles à 100% alors qu'un échantillonnage suffirait"
        ],
        indicators=[
            "Nombre de contrôles par pièce",
            "Temps de contrôle qualité",
            "Nombre d'opérations vs exigences client",
            "Taux de sur-qualité",
            "Temps de traitement administratif"
        ]
    ),
    
    TimwoodsCategory.OVER_PRODUCTION: TimwoodsDefinition(
        name="Surproduction",
        description="Production en quantité supérieure à la demande immédiate ou production trop précoce par rapport aux besoins.",
        examples=[
            "Production par lots trop importants pour lisser la charge",
            "Fabrication anticipée de pièces non commandées",
            "Production continue malgré une commande client en attente",
            "Lancement de séries avant confirmation de commande",
            "Stocks de sécurité surdimensionnés"
        ],
        indicators=[
            "Taux de rotation des produits finis",
            "Écart entre production et ventes",
            "Taille des lots de production",
            "Délai de fabrication vs délai de livraison",
            "Stock de produits finis en jours"
        ]
    ),
    
    TimwoodsCategory.DEFECTS: TimwoodsDefinition(
        name="Défauts",
        description="Rebuts, retouches, non-conformités qui nécessitent du travail supplémentaire et impactent la qualité.",
        examples=[
            "Pièces rebutées pour non-conformité dimensionnelle",
            "Retouches après contrôle qualité",
            "Réparations sur produits finis",
            "Réclamations clients pour défauts",
            "Tests échoués nécessitant un re-travail",
            "Dérogations qualité fréquentes"
        ],
        indicators=[
            "Taux de rebut",
            "Taux de retouche",
            "Nombre de non-conformités",
            "Coût de la non-qualité",
            "Taux de réclamation client",
            "First Pass Yield (FPY)"
        ]
    ),
    
    TimwoodsCategory.SKILLS: TimwoodsDefinition(
        name="Sous-utilisation des compétences",
        description="Non-exploitation du potentiel humain : compétences, créativité, idées d'amélioration ignorées.",
        examples=[
            "Opérateurs qualifiés affectés à des tâches simples",
            "Suggestions d'amélioration non écoutées",
            "Formation insuffisante sur les nouveaux équipements",
            "Polyvalence inexploitée",
            "Absence d'implication dans la résolution de problèmes",
            "Expertise métier non valorisée dans les projets d'amélioration"
        ],
        indicators=[
            "Taux de participation aux groupes d'amélioration",
            "Nombre de suggestions d'amélioration déposées",
            "Écart entre compétences disponibles et utilisées",
            "Heures de formation par opérateur",
            "Taux de polyvalence",
            "Turnover du personnel qualifié"
        ]
    )
}


def get_timwoods_description(category: TimwoodsCategory) -> str:
    """
    Retourne la description d'une catégorie TIMWOODS.
    
    Args:
        category: La catégorie TIMWOODS
        
    Returns:
        Description de la catégorie
    """
    return TIMWOODS_DEFINITIONS[category].description


def get_timwoods_examples(category: TimwoodsCategory) -> List[str]:
    """
    Retourne les exemples industriels d'une catégorie TIMWOODS.
    
    Args:
        category: La catégorie TIMWOODS
        
    Returns:
        Liste d'exemples concrets
    """
    return TIMWOODS_DEFINITIONS[category].examples


def get_timwoods_indicators(category: TimwoodsCategory) -> List[str]:
    """
    Retourne les indicateurs associés à une catégorie TIMWOODS.
    
    Args:
        category: La catégorie TIMWOODS
        
    Returns:
        Liste des indicateurs
    """
    return TIMWOODS_DEFINITIONS[category].indicators


def get_all_categories() -> List[TimwoodsCategory]:
    """
    Retourne toutes les catégories TIMWOODS.
    
    Returns:
        Liste de toutes les catégories
    """
    return list(TimwoodsCategory)
