"""
Agent Recommender pour générer des recommandations d'amélioration Lean.
Supporte le mode LLM (OpenAI) et le mode fallback heuristique.
"""
import json
import uuid
from typing import List, Dict, Any

from src.utils.config import get_settings
from src.prompts.templates import RECOMMENDER_SYSTEM_PROMPT, RECOMMENDER_HUMAN_TEMPLATE
from src.models.timwoods import TimwoodsCategory


class RecommenderAgent:
    """Agent de génération de recommandations d'amélioration."""
    
    def __init__(self, llm=None):
        """
        Initialise l'agent recommender.
        
        Args:
            llm: Instance LLM optionnelle (ChatOpenAI). Si None, utilise la config.
        """
        self.settings = get_settings()
        self.llm = llm
        self.chain = None
        
        # Si une clé API est configurée et pas de LLM fourni, créer un LLM
        if self.llm is None and self.settings.is_api_configured():
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model=self.settings.llm_model,
                    temperature=self.settings.llm_temperature,
                    api_key=self.settings.openai_api_key
                )
                self._create_chain()
            except Exception as e:
                print(f"⚠️  Impossible d'initialiser le LLM : {e}")
                print("   → Mode fallback heuristique activé")
                self.llm = None
    
    def _create_chain(self):
        """Crée la chaîne LangChain pour les recommandations."""
        if self.llm is None:
            return
        
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import JsonOutputParser
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", RECOMMENDER_SYSTEM_PROMPT),
                ("human", RECOMMENDER_HUMAN_TEMPLATE)
            ])
            
            self.chain = prompt | self.llm | JsonOutputParser()
        except Exception as e:
            print(f"⚠️  Erreur lors de la création de la chaîne : {e}")
            self.llm = None
            self.chain = None
    
    def recommend(self, analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Génère des recommandations d'amélioration à partir des analyses.
        
        Args:
            analysis_results: Liste des analyses de pertes
            
        Returns:
            Liste de recommandations priorisées
        """
        if not analysis_results:
            print("⚠️  Aucune analyse à traiter")
            return []
        
        # Formater les analyses pour le LLM
        analyses_str = json.dumps(analysis_results, indent=2, ensure_ascii=False)
        
        # Mode LLM si disponible
        if self.chain is not None:
            try:
                result = self.chain.invoke({"analysis_results": analyses_str})
                recommendations = result.get("recommendations", [])
                print(f"✅ Mode LLM : {len(recommendations)} recommandations générées")
                return recommendations
            except Exception as e:
                print(f"⚠️  Erreur LLM : {e}")
                print("   → Basculement vers mode heuristique")
        
        # Mode fallback heuristique
        return self._heuristic_recommend(analysis_results)
    
    def _heuristic_recommend(self, analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mode fallback : génération de recommandations heuristiques.
        
        Args:
            analysis_results: Analyses de pertes
            
        Returns:
            Liste de recommandations
        """
        print("🔧 Mode heuristique activé (sans API)")
        
        recommendations = []
        
        for analysis in analysis_results:
            # Générer des recommandations selon la catégorie TIMWOODS
            timwoods_category = analysis.get("timwoods_category", "")
            loss_id = analysis.get("loss_id", "")
            estimated_cost = analysis.get("estimated_cost_eur", 0)
            severity = analysis.get("severity", "medium")
            
            # Générer 1-2 recommandations par analyse
            category_recommendations = self._get_recommendations_for_category(
                timwoods_category, 
                loss_id, 
                estimated_cost,
                severity
            )
            
            recommendations.extend(category_recommendations)
        
        # Trier par priorité (puis par gain estimé)
        recommendations.sort(key=lambda x: (x["priority"], -x["estimated_gain_eur"]))
        
        print(f"✅ Mode heuristique : {len(recommendations)} recommandations générées")
        return recommendations
    
    def _get_recommendations_for_category(
        self, 
        timwoods_category: str, 
        loss_id: str,
        estimated_cost: float,
        severity: str
    ) -> List[Dict[str, Any]]:
        """
        Génère des recommandations spécifiques à une catégorie TIMWOODS.
        
        Args:
            timwoods_category: Catégorie TIMWOODS
            loss_id: ID de la perte
            estimated_cost: Coût estimé de la perte
            severity: Sévérité
            
        Returns:
            Liste de recommandations
        """
        recommendations = []
        
        # Templates de recommandations par catégorie
        templates = {
            TimwoodsCategory.WAITING.value: [
                {
                    "title": "Mise en place d'une maintenance préventive systématique",
                    "description": "Établir un planning de maintenance préventive hebdomadaire avec check-lists "
                                 "détaillées pour les équipements critiques. Former 2 techniciens aux diagnostics "
                                 "préventifs et au remplacement préventif des pièces d'usure. Installer des capteurs "
                                 "de vibration pour anticiper les pannes.",
                    "priority": 1,
                    "gain_ratio": 0.70,
                    "implementation_effort": "medium",
                    "timeline_weeks": 6,
                    "responsible_department": "Maintenance"
                },
                {
                    "title": "Optimisation des temps de changement de série (SMED)",
                    "description": "Appliquer la méthode SMED pour réduire les temps de changement d'outils et de séries. "
                                 "Objectif : réduire de 50% les temps de changement actuels. Externaliser les opérations "
                                 "possibles, standardiser les procédures, former les opérateurs.",
                    "priority": 2,
                    "gain_ratio": 0.40,
                    "implementation_effort": "medium",
                    "timeline_weeks": 8,
                    "responsible_department": "Production"
                }
            ],
            TimwoodsCategory.DEFECTS.value: [
                {
                    "title": "Déploiement de contrôle statistique des procédés (SPC)",
                    "description": "Mettre en place des cartes de contrôle sur les paramètres critiques du process. "
                                 "Former les opérateurs à la lecture et réaction aux cartes SPC. Installer des systèmes "
                                 "d'alarme automatiques en cas de dérive. Objectif : réduire le taux de rebut de 60%.",
                    "priority": 1,
                    "gain_ratio": 0.75,
                    "implementation_effort": "medium",
                    "timeline_weeks": 10,
                    "responsible_department": "Qualité"
                },
                {
                    "title": "Programme de formation qualité avancée",
                    "description": "Former tous les opérateurs aux techniques de détection précoce des défauts et aux "
                                 "bonnes pratiques qualité. Inclure des modules sur la prévention des défauts et "
                                 "l'auto-contrôle. Certification interne des opérateurs.",
                    "priority": 2,
                    "gain_ratio": 0.50,
                    "implementation_effort": "low",
                    "timeline_weeks": 4,
                    "responsible_department": "Ressources Humaines"
                }
            ],
            TimwoodsCategory.OVER_PROCESSING.value: [
                {
                    "title": "Révision et optimisation des plans de contrôle",
                    "description": "Analyser tous les points de contrôle qualité et éliminer les contrôles redondants. "
                                 "Passer à un échantillonnage statistique là où le contrôle à 100% n'est pas justifié. "
                                 "Automatiser les contrôles dimensionnels répétitifs.",
                    "priority": 1,
                    "gain_ratio": 0.60,
                    "implementation_effort": "low",
                    "timeline_weeks": 3,
                    "responsible_department": "Qualité"
                },
                {
                    "title": "Simplification des processus administratifs",
                    "description": "Cartographier les processus administratifs et éliminer les étapes sans valeur ajoutée. "
                                 "Digitaliser les documents papier. Mettre en place une signature électronique pour "
                                 "les validations.",
                    "priority": 3,
                    "gain_ratio": 0.35,
                    "implementation_effort": "medium",
                    "timeline_weeks": 6,
                    "responsible_department": "Administration"
                }
            ],
            TimwoodsCategory.SKILLS.value: [
                {
                    "title": "Programme de polyvalence et formation croisée",
                    "description": "Former chaque opérateur sur au moins 3 postes différents. Créer une matrice de "
                                 "compétences visuelle. Mettre en place un système de tutorat interne. Objectif : "
                                 "atteindre 70% de polyvalence sur les postes critiques.",
                    "priority": 1,
                    "gain_ratio": 0.55,
                    "implementation_effort": "medium",
                    "timeline_weeks": 12,
                    "responsible_department": "Ressources Humaines"
                },
                {
                    "title": "Système de suggestions d'amélioration (Kaizen)",
                    "description": "Lancer un programme de suggestions d'amélioration avec reconnaissance et récompenses. "
                                 "Objectif : 2 suggestions par opérateur par trimestre. Créer des groupes de résolution "
                                 "de problèmes hebdomadaires.",
                    "priority": 2,
                    "gain_ratio": 0.45,
                    "implementation_effort": "low",
                    "timeline_weeks": 4,
                    "responsible_department": "Direction"
                }
            ],
            TimwoodsCategory.INVENTORY.value: [
                {
                    "title": "Mise en place d'un système Kanban",
                    "description": "Déployer un système Kanban pour gérer les flux de matières et réduire les stocks. "
                                 "Commencer par les pièces à forte rotation. Former les équipes au principe du Juste-à-Temps. "
                                 "Objectif : réduire les stocks de 40%.",
                    "priority": 1,
                    "gain_ratio": 0.50,
                    "implementation_effort": "medium",
                    "timeline_weeks": 10,
                    "responsible_department": "Logistique"
                },
                {
                    "title": "Partenariat fournisseurs (VMI)",
                    "description": "Négocier avec les fournisseurs clés pour mettre en place du Vendor Managed Inventory. "
                                 "Le fournisseur gère les stocks et approvisionne selon consommation réelle. "
                                 "Réduire les stocks de sécurité.",
                    "priority": 2,
                    "gain_ratio": 0.40,
                    "implementation_effort": "high",
                    "timeline_weeks": 16,
                    "responsible_department": "Achats"
                }
            ],
            TimwoodsCategory.TRANSPORT.value: [
                {
                    "title": "Réimplantation des postes en flux continu",
                    "description": "Réorganiser l'implantation machines pour créer un flux continu et minimiser les "
                                 "déplacements. Utiliser la méthode Value Stream Mapping. Rapprocher les postes "
                                 "séquentiels. Objectif : réduire les déplacements de 60%.",
                    "priority": 1,
                    "gain_ratio": 0.65,
                    "implementation_effort": "high",
                    "timeline_weeks": 20,
                    "responsible_department": "Engineering"
                },
                {
                    "title": "Système de livraison au bord de ligne",
                    "description": "Mettre en place des tournées logistiques (water spider) pour approvisionner les "
                                 "postes de travail. Les opérateurs restent à leur poste. Installer des racks bord "
                                 "de ligne ergonomiques.",
                    "priority": 2,
                    "gain_ratio": 0.45,
                    "implementation_effort": "medium",
                    "timeline_weeks": 8,
                    "responsible_department": "Logistique"
                }
            ],
            TimwoodsCategory.MOTION.value: [
                {
                    "title": "Étude ergonomique et optimisation des postes",
                    "description": "Réaliser une étude MTM (Methods-Time Measurement) des postes critiques. Optimiser "
                                 "l'implantation des outils et composants pour minimiser les gestes. Installer des "
                                 "équipements d'aide (manipulateurs, bras articulés).",
                    "priority": 1,
                    "gain_ratio": 0.50,
                    "implementation_effort": "medium",
                    "timeline_weeks": 8,
                    "responsible_department": "Engineering"
                },
                {
                    "title": "Programme 5S sur tous les postes",
                    "description": "Déployer la méthodologie 5S (Seiri, Seiton, Seiso, Seiketsu, Shitsuke) sur "
                                 "l'ensemble des postes de travail. Standardiser le rangement des outils. "
                                 "Audits hebdomadaires 5S.",
                    "priority": 2,
                    "gain_ratio": 0.35,
                    "implementation_effort": "low",
                    "timeline_weeks": 6,
                    "responsible_department": "Production"
                }
            ],
            TimwoodsCategory.OVER_PRODUCTION.value: [
                {
                    "title": "Mise en place d'une production tirée (Pull)",
                    "description": "Transformer la production de push vers pull basé sur la demande client réelle. "
                                 "Réduire les tailles de lots. Implémenter un système MRP optimisé. "
                                 "Objectif : stock produits finis < 5 jours.",
                    "priority": 1,
                    "gain_ratio": 0.55,
                    "implementation_effort": "high",
                    "timeline_weeks": 16,
                    "responsible_department": "Planification"
                },
                {
                    "title": "Réduction des temps de changement (SMED)",
                    "description": "Appliquer la méthode SMED pour permettre la production en petits lots sans perte "
                                 "de productivité. Former les équipes. Standardiser les procédures de changement.",
                    "priority": 2,
                    "gain_ratio": 0.45,
                    "implementation_effort": "medium",
                    "timeline_weeks": 10,
                    "responsible_department": "Production"
                }
            ]
        }
        
        # Récupérer les templates pour cette catégorie
        category_templates = templates.get(timwoods_category, templates[TimwoodsCategory.WAITING.value])
        
        # Ajuster la priorité selon la sévérité
        priority_adjustment = {
            "critical": 0,
            "high": 0,
            "medium": 1,
            "low": 2
        }
        adjustment = priority_adjustment.get(severity, 1)
        
        # Générer les recommandations
        for i, template in enumerate(category_templates[:2]):  # Max 2 recommandations par perte
            rec_id = f"REC_{str(uuid.uuid4())[:8]}"
            
            # Calculer le gain estimé (pourcentage du coût de la perte)
            estimated_gain = estimated_cost * template["gain_ratio"]
            
            recommendation = {
                "recommendation_id": rec_id,
                "loss_id": loss_id,
                "title": template["title"],
                "description": template["description"],
                "priority": min(5, template["priority"] + adjustment),
                "estimated_gain_eur": round(estimated_gain, 2),
                "implementation_effort": template["implementation_effort"],
                "timeline_weeks": template["timeline_weeks"],
                "responsible_department": template["responsible_department"]
            }
            
            recommendations.append(recommendation)
        
        return recommendations
