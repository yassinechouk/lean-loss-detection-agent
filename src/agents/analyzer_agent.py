"""
Agent Analyzer pour la classification TIMWOODS et l'analyse de causes racines.
Supporte le mode LLM (OpenAI) et le mode fallback heuristique.
"""
import json
import uuid
from typing import List, Dict, Any, Optional

from src.utils.config import get_settings
from src.prompts.templates import ANALYZER_SYSTEM_PROMPT, ANALYZER_HUMAN_TEMPLATE
from src.models.timwoods import TimwoodsCategory


class AnalyzerAgent:
    """Agent d'analyse et classification TIMWOODS."""
    
    def __init__(self, llm=None):
        """
        Initialise l'agent analyzer.
        
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
        """Crée la chaîne LangChain pour l'analyse."""
        if self.llm is None:
            return
        
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import JsonOutputParser
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", ANALYZER_SYSTEM_PROMPT),
                ("human", ANALYZER_HUMAN_TEMPLATE)
            ])
            
            self.chain = prompt | self.llm | JsonOutputParser()
        except Exception as e:
            print(f"⚠️  Erreur lors de la création de la chaîne : {e}")
            self.llm = None
            self.chain = None
    
    def analyze(self, detected_losses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyse les pertes détectées : classification TIMWOODS + causes racines.
        
        Args:
            detected_losses: Liste des pertes détectées par le parser
            
        Returns:
            Liste d'analyses avec classification TIMWOODS et causes racines
        """
        if not detected_losses:
            print("⚠️  Aucune perte à analyser")
            return []
        
        # Formater les pertes pour l'analyse
        losses_str = json.dumps(detected_losses, indent=2, ensure_ascii=False)
        
        # Mode LLM si disponible
        if self.chain is not None:
            try:
                result = self.chain.invoke({"detected_losses": losses_str})
                analyses = result.get("analyses", [])
                print(f"✅ Mode LLM : {len(analyses)} analyses effectuées")
                return analyses
            except Exception as e:
                print(f"⚠️  Erreur LLM : {e}")
                print("   → Basculement vers mode heuristique")
        
        # Mode fallback heuristique
        return self._heuristic_analyze(detected_losses)
    
    def _heuristic_analyze(self, detected_losses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mode fallback : classification heuristique basée sur des mots-clés.
        
        Args:
            detected_losses: Pertes détectées
            
        Returns:
            Liste d'analyses
        """
        print("🔧 Mode heuristique activé (sans API)")
        
        analyses = []
        
        for loss in detected_losses:
            # Classification TIMWOODS basée sur mots-clés
            timwoods_category, justification = self._classify_timwoods(loss)
            
            # Génération d'une analyse de causes racines simplifiée
            root_cause_analysis = self._generate_root_cause_analysis(loss, timwoods_category)
            
            # Estimation du coût
            estimated_cost = self._estimate_cost(loss)
            
            analysis = {
                "loss_id": loss["loss_id"],
                "timwoods_category": timwoods_category,
                "justification": justification,
                "root_cause_analysis": root_cause_analysis,
                "estimated_cost_eur": estimated_cost,
                "severity": loss.get("severity", "medium")
            }
            
            analyses.append(analysis)
        
        print(f"✅ Mode heuristique : {len(analyses)} analyses effectuées")
        return analyses
    
    def _classify_timwoods(self, loss: Dict[str, Any]) -> tuple[str, str]:
        """
        Classifie une perte selon TIMWOODS basé sur mots-clés.
        
        Args:
            loss: Perte à classifier
            
        Returns:
            Tuple (catégorie, justification)
        """
        title = loss.get("title", "").lower()
        description = loss.get("description", "").lower()
        text = title + " " + description
        
        # Règles de classification par mots-clés
        if "micro-arrêt" in text or "attente" in text or "waiting" in text:
            return (
                TimwoodsCategory.WAITING.value,
                "Les micro-arrêts et temps d'attente génèrent des pertes de type Waiting (attente). "
                "La machine ou l'opérateur est disponible mais ne peut pas produire."
            )
        
        if "rebut" in text or "défaut" in text or "non-conform" in text or "qualité" in text:
            return (
                TimwoodsCategory.DEFECTS.value,
                "Les rebuts et défauts qualité sont des pertes de type Defects. "
                "Ils nécessitent du re-travail ou génèrent des pièces inutilisables."
            )
        
        if "sur-contrôle" in text or "contrôle" in text and "excessif" in text:
            return (
                TimwoodsCategory.OVER_PROCESSING.value,
                "Les contrôles excessifs ou redondants sont des pertes de type Over-processing. "
                "Ils n'ajoutent pas de valeur mais consomment du temps et des ressources."
            )
        
        if "ralentissement" in text or "cadence" in text or "vitesse" in text:
            return (
                TimwoodsCategory.WAITING.value,
                "Les ralentissements de cadence génèrent des temps d'attente (Waiting). "
                "La machine fonctionne en dessous de sa capacité optimale."
            )
        
        if "shift" in text or "équipe" in text or "nuit" in text:
            return (
                TimwoodsCategory.SKILLS.value,
                "Les problèmes liés aux shifts peuvent indiquer une sous-utilisation des compétences (Skills). "
                "Formation insuffisante ou manque de supervision peuvent en être la cause."
            )
        
        if "stock" in text or "inventaire" in text or "encours" in text:
            return (
                TimwoodsCategory.INVENTORY.value,
                "Les problèmes de stock et en-cours sont des pertes de type Inventory. "
                "Ils immobilisent du capital et masquent les problèmes."
            )
        
        if "transport" in text or "déplacement" in text or "manutention" in text:
            return (
                TimwoodsCategory.TRANSPORT.value,
                "Les déplacements et manutentions excessifs sont des pertes de type Transport. "
                "Ils n'ajoutent pas de valeur au produit."
            )
        
        if "mouvement" in text or "geste" in text or "ergonomie" in text:
            return (
                TimwoodsCategory.MOTION.value,
                "Les mouvements inutiles des opérateurs sont des pertes de type Motion. "
                "Ils fatiguent l'opérateur sans créer de valeur."
            )
        
        # Par défaut : Waiting (le plus courant en industrie)
        return (
            TimwoodsCategory.WAITING.value,
            "Cette perte génère principalement des temps d'attente (Waiting) dans le processus de production."
        )
    
    def _generate_root_cause_analysis(
        self, 
        loss: Dict[str, Any], 
        timwoods_category: str
    ) -> Dict[str, Any]:
        """
        Génère une analyse de causes racines simplifiée (5 Pourquoi).
        
        Args:
            loss: Perte à analyser
            timwoods_category: Catégorie TIMWOODS
            
        Returns:
            Dictionnaire d'analyse de causes racines
        """
        # Générer des causes génériques selon la catégorie
        causes_map = {
            TimwoodsCategory.WAITING.value: [
                {"level": 1, "cause": "Arrêts machines fréquents"},
                {"level": 2, "cause": "Maintenance préventive insuffisante"},
                {"level": 3, "cause": "Absence de plan de maintenance structuré"},
                {"level": 4, "cause": "Ressources maintenance limitées"},
                {"level": 5, "cause": "Priorisation budgétaire insuffisante"}
            ],
            TimwoodsCategory.DEFECTS.value: [
                {"level": 1, "cause": "Taux de rebut élevé"},
                {"level": 2, "cause": "Dérive des paramètres process"},
                {"level": 3, "cause": "Absence de contrôle en cours de process (SPC)"},
                {"level": 4, "cause": "Formation opérateurs limitée"},
                {"level": 5, "cause": "Système qualité non déployé complètement"}
            ],
            TimwoodsCategory.OVER_PROCESSING.value: [
                {"level": 1, "cause": "Contrôles qualité redondants"},
                {"level": 2, "cause": "Manque de confiance dans le process"},
                {"level": 3, "cause": "Historique de problèmes qualité"},
                {"level": 4, "cause": "Absence de capabilité process démontrée"},
                {"level": 5, "cause": "Culture de sur-contrôle vs prévention"}
            ],
            TimwoodsCategory.SKILLS.value: [
                {"level": 1, "cause": "Performance variable selon les shifts"},
                {"level": 2, "cause": "Niveaux de compétence hétérogènes"},
                {"level": 3, "cause": "Formation insuffisante"},
                {"level": 4, "cause": "Plan de formation non structuré"},
                {"level": 5, "cause": "Gestion des compétences non priorisée"}
            ],
            TimwoodsCategory.INVENTORY.value: [
                {"level": 1, "cause": "Sur-stockage de composants"},
                {"level": 2, "cause": "Peur de rupture de stock"},
                {"level": 3, "cause": "Fiabilité fournisseurs variable"},
                {"level": 4, "cause": "Absence de relation partenaire fournisseur"},
                {"level": 5, "cause": "Logique push vs pull non transformée"}
            ],
            TimwoodsCategory.TRANSPORT.value: [
                {"level": 1, "cause": "Déplacements excessifs de pièces"},
                {"level": 2, "cause": "Implantation machines non optimisée"},
                {"level": 3, "cause": "Évolution historique de l'usine"},
                {"level": 4, "cause": "Absence de revue des flux"},
                {"level": 5, "cause": "Investissement implantation non priorisé"}
            ],
            TimwoodsCategory.MOTION.value: [
                {"level": 1, "cause": "Mouvements opérateurs inefficaces"},
                {"level": 2, "cause": "Ergonomie postes non optimisée"},
                {"level": 3, "cause": "Absence d'analyse MTM/temps"},
                {"level": 4, "cause": "Pas d'implication opérateurs dans conception postes"},
                {"level": 5, "cause": "Culture ergonomie peu développée"}
            ],
            TimwoodsCategory.OVER_PRODUCTION.value: [
                {"level": 1, "cause": "Production par lots trop importants"},
                {"level": 2, "cause": "Temps de changement de série trop longs"},
                {"level": 3, "cause": "Méthode SMED non appliquée"},
                {"level": 4, "cause": "Culture du 'just in case'"},
                {"level": 5, "cause": "Transition vers lean manufacturing incomplète"}
            ]
        }
        
        causes = causes_map.get(
            timwoods_category,
            causes_map[TimwoodsCategory.WAITING.value]  # Default
        )
        
        root_cause_analysis = {
            "method": "five_whys",
            "causes": causes,
            "root_cause": causes[-1]["cause"],
            "contributing_factors": [
                "Vieillissement des équipements",
                "Complexité croissante des produits",
                "Pression sur les délais",
                "Turnover du personnel"
            ]
        }
        
        return root_cause_analysis
    
    def _estimate_cost(self, loss: Dict[str, Any]) -> float:
        """
        Estime le coût financier d'une perte.
        
        Args:
            loss: Perte à estimer
            
        Returns:
            Coût estimé en EUR
        """
        # Hypothèses de coûts horaires
        MACHINE_HOUR_COST = 150  # EUR/h
        OPERATOR_HOUR_COST = 50  # EUR/h
        DEFECT_UNIT_COST = 25  # EUR/pièce
        
        total_hours = loss.get("total_duration_hours", 0)
        frequency = loss.get("frequency", 1)
        
        # Calcul basé sur le type de perte
        title = loss.get("title", "").lower()
        
        if "rebut" in title or "défaut" in title:
            # Coût des pièces rebutées + temps perdu
            cost = frequency * DEFECT_UNIT_COST + total_hours * MACHINE_HOUR_COST
        elif "micro-arrêt" in title or "arrêt" in title:
            # Coût machine + opérateur
            cost = total_hours * (MACHINE_HOUR_COST + OPERATOR_HOUR_COST)
        elif "contrôle" in title:
            # Principalement coût opérateur
            cost = total_hours * OPERATOR_HOUR_COST
        else:
            # Coût mixte par défaut
            cost = total_hours * (MACHINE_HOUR_COST * 0.7 + OPERATOR_HOUR_COST * 0.3)
        
        return round(cost, 2)
