"""
Orchestration LangGraph - Le cœur du système d'analyse Lean.
Coordonne les agents Parser, Analyzer et Recommender dans un workflow séquentiel.
"""
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from langgraph.graph import StateGraph, END
from src.agents.parser_agent import ParserAgent
from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.recommender_agent import RecommenderAgent
from src.data.preprocessor import DataPreprocessor
from src.models.schemas import AnalysisResult, DetectedLoss, RootCauseAnalysis, Recommendation


console = Console()


class GraphState(TypedDict):
    """État du graphe LangGraph."""
    raw_data: Dict[str, Any]
    production_data_text: str
    parsed_losses: List[Dict[str, Any]]
    analysis_results: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    final_report: Optional[AnalysisResult]
    error: Optional[str]


class LeanLossDetectionGraph:
    """Orchestrateur LangGraph pour la détection des pertes Lean."""
    
    def __init__(self, llm=None):
        """
        Initialise le graphe d'orchestration.
        
        Args:
            llm: Instance LLM optionnelle à partager entre agents
        """
        self.llm = llm
        self.parser_agent = ParserAgent(llm=llm)
        self.analyzer_agent = AnalyzerAgent(llm=llm)
        self.recommender_agent = RecommenderAgent(llm=llm)
        self.preprocessor = DataPreprocessor()
        self.graph = None
    
    def parse_node(self, state: GraphState) -> GraphState:
        """
        Node Parser : Extraction des pertes cachées.
        
        Args:
            state: État courant du graphe
            
        Returns:
            État mis à jour
        """
        console.print("\n[bold blue]🔍 Étape 1/4 : Parsing - Extraction des pertes cachées[/bold blue]")
        
        try:
            production_data_text = state.get("production_data_text", "")
            
            if not production_data_text:
                # Préparer les données si pas encore fait
                raw_data = state.get("raw_data", {})
                production_logs = raw_data.get("production_logs", [])
                quality_records = raw_data.get("quality_records", [])
                incident_reports = raw_data.get("incident_reports", [])
                
                production_data_text = self.preprocessor.prepare_for_analysis(
                    production_logs,
                    quality_records,
                    incident_reports
                )
                state["production_data_text"] = production_data_text
            
            # Parser analyse les données
            parsed_losses = self.parser_agent.parse(production_data_text)
            
            state["parsed_losses"] = parsed_losses
            console.print(f"   ✅ {len(parsed_losses)} pertes détectées")
            
        except Exception as e:
            console.print(f"   ❌ Erreur : {str(e)}", style="bold red")
            state["error"] = f"Erreur parsing : {str(e)}"
            state["parsed_losses"] = []
        
        return state
    
    def analyze_node(self, state: GraphState) -> GraphState:
        """
        Node Analyzer : Classification TIMWOODS + Causes racines.
        
        Args:
            state: État courant du graphe
            
        Returns:
            État mis à jour
        """
        console.print("\n[bold green]🧠 Étape 2/4 : Analyse - Classification TIMWOODS & Causes racines[/bold green]")
        
        try:
            parsed_losses = state.get("parsed_losses", [])
            
            if not parsed_losses:
                console.print("   ⚠️  Aucune perte à analyser", style="yellow")
                state["analysis_results"] = []
                return state
            
            # Analyser les pertes
            analysis_results = self.analyzer_agent.analyze(parsed_losses)
            
            state["analysis_results"] = analysis_results
            console.print(f"   ✅ {len(analysis_results)} analyses complètes")
            
        except Exception as e:
            console.print(f"   ❌ Erreur : {str(e)}", style="bold red")
            state["error"] = f"Erreur analyse : {str(e)}"
            state["analysis_results"] = []
        
        return state
    
    def recommend_node(self, state: GraphState) -> GraphState:
        """
        Node Recommender : Génération des recommandations.
        
        Args:
            state: État courant du graphe
            
        Returns:
            État mis à jour
        """
        console.print("\n[bold magenta]💡 Étape 3/4 : Recommandations - Plan d'action[/bold magenta]")
        
        try:
            analysis_results = state.get("analysis_results", [])
            
            if not analysis_results:
                console.print("   ⚠️  Aucune analyse disponible", style="yellow")
                state["recommendations"] = []
                return state
            
            # Générer les recommandations
            recommendations = self.recommender_agent.recommend(analysis_results)
            
            state["recommendations"] = recommendations
            console.print(f"   ✅ {len(recommendations)} recommandations générées")
            
        except Exception as e:
            console.print(f"   ❌ Erreur : {str(e)}", style="bold red")
            state["error"] = f"Erreur recommandations : {str(e)}"
            state["recommendations"] = []
        
        return state
    
    def report_node(self, state: GraphState) -> GraphState:
        """
        Node Report : Compilation du rapport final.
        
        Args:
            state: État courant du graphe
            
        Returns:
            État mis à jour avec le rapport final
        """
        console.print("\n[bold cyan]📊 Étape 4/4 : Génération du rapport final[/bold cyan]")
        
        try:
            parsed_losses = state.get("parsed_losses", [])
            analysis_results = state.get("analysis_results", [])
            recommendations = state.get("recommendations", [])
            
            # Convertir en modèles Pydantic
            detected_losses = []
            for loss_dict, analysis_dict in zip(parsed_losses, analysis_results):
                try:
                    # Fusionner les données de loss et analysis
                    merged = {**loss_dict}
                    merged["timwoods_category"] = analysis_dict.get("timwoods_category", "Waiting")
                    merged["estimated_cost_eur"] = analysis_dict.get("estimated_cost_eur", 0)
                    
                    detected_loss = DetectedLoss.model_validate(merged)
                    detected_losses.append(detected_loss)
                except Exception as e:
                    console.print(f"   ⚠️  Erreur validation perte : {e}", style="yellow")
            
            # Créer les root cause analyses
            root_cause_analyses = []
            for analysis_dict in analysis_results:
                try:
                    rca = RootCauseAnalysis.model_validate({
                        "loss_id": analysis_dict.get("loss_id", ""),
                        "method": analysis_dict.get("root_cause_analysis", {}).get("method", "five_whys"),
                        "causes": analysis_dict.get("root_cause_analysis", {}).get("causes", []),
                        "root_cause": analysis_dict.get("root_cause_analysis", {}).get("root_cause", ""),
                        "contributing_factors": analysis_dict.get("root_cause_analysis", {}).get("contributing_factors", [])
                    })
                    root_cause_analyses.append(rca)
                except Exception as e:
                    console.print(f"   ⚠️  Erreur validation RCA : {e}", style="yellow")
            
            # Créer les recommandations
            recommendation_objects = []
            for rec_dict in recommendations:
                try:
                    rec = Recommendation.model_validate(rec_dict)
                    recommendation_objects.append(rec)
                except Exception as e:
                    console.print(f"   ⚠️  Erreur validation recommandation : {e}", style="yellow")
            
            # Calculer les statistiques résumées
            summary_stats = self._compute_summary_stats(
                detected_losses,
                root_cause_analyses,
                recommendation_objects
            )
            
            # Créer le rapport final
            final_report = AnalysisResult(
                detected_losses=detected_losses,
                root_cause_analyses=root_cause_analyses,
                recommendations=recommendation_objects,
                summary_stats=summary_stats,
                generated_at=datetime.now()
            )
            
            state["final_report"] = final_report
            
            console.print(f"\n[bold green]✨ Rapport généré avec succès![/bold green]")
            console.print(f"   📋 {len(detected_losses)} pertes détectées")
            console.print(f"   🧠 {len(root_cause_analyses)} analyses de causes racines")
            console.print(f"   💡 {len(recommendation_objects)} recommandations")
            console.print(f"   💰 Impact financier estimé : {summary_stats.get('total_cost_eur', 0):,.2f} EUR")
            
        except Exception as e:
            console.print(f"   ❌ Erreur génération rapport : {str(e)}", style="bold red")
            state["error"] = f"Erreur rapport : {str(e)}"
            state["final_report"] = None
        
        return state
    
    def _compute_summary_stats(
        self,
        detected_losses: List[DetectedLoss],
        root_cause_analyses: List[RootCauseAnalysis],
        recommendations: List[Recommendation]
    ) -> Dict[str, Any]:
        """
        Calcule les statistiques résumées.
        
        Args:
            detected_losses: Pertes détectées
            root_cause_analyses: Analyses de causes racines
            recommendations: Recommandations
            
        Returns:
            Dictionnaire de statistiques
        """
        from collections import Counter
        
        # Coût total
        total_cost = sum(loss.estimated_cost_eur for loss in detected_losses)
        
        # Gains potentiels
        total_potential_gain = sum(rec.estimated_gain_eur for rec in recommendations)
        
        # Distribution par catégorie TIMWOODS
        timwoods_distribution = Counter(loss.timwoods_category for loss in detected_losses)
        
        # Distribution par sévérité
        severity_distribution = Counter(loss.severity for loss in detected_losses)
        
        # Top catégorie
        top_category = timwoods_distribution.most_common(1)[0] if timwoods_distribution else ("N/A", 0)
        
        # Quick wins (priorité 1-2 et effort low-medium)
        quick_wins = [
            rec for rec in recommendations 
            if rec.priority <= 2 and rec.implementation_effort in ["low", "medium"]
        ]
        
        return {
            "total_losses": len(detected_losses),
            "total_cost_eur": round(total_cost, 2),
            "total_potential_gain_eur": round(total_potential_gain, 2),
            "roi_percentage": round((total_potential_gain / total_cost * 100) if total_cost > 0 else 0, 1),
            "timwoods_distribution": dict(timwoods_distribution),
            "severity_distribution": dict(severity_distribution),
            "top_category": top_category[0],
            "top_category_count": top_category[1],
            "total_recommendations": len(recommendations),
            "quick_wins_count": len(quick_wins),
            "high_priority_count": len([rec for rec in recommendations if rec.priority == 1])
        }
    
    def should_skip_to_report(self, state: GraphState) -> str:
        """
        Décide si on doit sauter directement au rapport (si aucune perte détectée).
        
        Args:
            state: État courant
            
        Returns:
            "report" si aucune perte, "analyze" sinon
        """
        parsed_losses = state.get("parsed_losses", [])
        return "report" if len(parsed_losses) == 0 else "analyze"
    
    def build_graph(self):
        """
        Construit et compile le graphe LangGraph.
        
        Returns:
            Graphe compilé
        """
        # Créer le graphe
        workflow = StateGraph(GraphState)
        
        # Ajouter les nodes
        workflow.add_node("parse", self.parse_node)
        workflow.add_node("analyze", self.analyze_node)
        workflow.add_node("recommend", self.recommend_node)
        workflow.add_node("report", self.report_node)
        
        # Définir le point d'entrée
        workflow.set_entry_point("parse")
        
        # Ajouter les edges
        workflow.add_conditional_edges(
            "parse",
            self.should_skip_to_report,
            {
                "analyze": "analyze",
                "report": "report"
            }
        )
        workflow.add_edge("analyze", "recommend")
        workflow.add_edge("recommend", "report")
        workflow.add_edge("report", END)
        
        # Compiler le graphe
        self.graph = workflow.compile()
        
        console.print("[bold green]✅ Graphe LangGraph compilé avec succès[/bold green]")
        
        return self.graph
    
    def run(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Exécute le pipeline complet d'analyse.
        
        Args:
            data: Données d'entrée (production_logs, quality_records, incident_reports)
            
        Returns:
            Résultat d'analyse complet
        """
        console.print("\n[bold cyan]" + "="*80 + "[/bold cyan]")
        console.print("[bold cyan]🏭 ANALYSE LEAN - DÉTECTION DES PERTES INVISIBLES[/bold cyan]")
        console.print("[bold cyan]" + "="*80 + "[/bold cyan]")
        
        # Construire le graphe si pas encore fait
        if self.graph is None:
            self.build_graph()
        
        # Initialiser l'état
        initial_state: GraphState = {
            "raw_data": data,
            "production_data_text": "",
            "parsed_losses": [],
            "analysis_results": [],
            "recommendations": [],
            "final_report": None,
            "error": None
        }
        
        # Exécuter le graphe
        try:
            final_state = self.graph.invoke(initial_state)
            
            if final_state.get("error"):
                console.print(f"\n[bold red]⚠️  Erreur pendant l'exécution : {final_state['error']}[/bold red]")
            
            final_report = final_state.get("final_report")
            
            if final_report is None:
                # Créer un rapport vide en cas d'erreur
                console.print("[yellow]⚠️  Création d'un rapport vide suite aux erreurs[/yellow]")
                final_report = AnalysisResult(
                    detected_losses=[],
                    root_cause_analyses=[],
                    recommendations=[],
                    summary_stats={},
                    generated_at=datetime.now()
                )
            
            console.print("\n[bold cyan]" + "="*80 + "[/bold cyan]")
            console.print("[bold green]✅ Analyse terminée avec succès![/bold green]")
            console.print("[bold cyan]" + "="*80 + "[/bold cyan]\n")
            
            return final_report
            
        except Exception as e:
            console.print(f"\n[bold red]❌ Erreur critique : {str(e)}[/bold red]")
            # Retourner un rapport vide
            return AnalysisResult(
                detected_losses=[],
                root_cause_analyses=[],
                recommendations=[],
                summary_stats={"error": str(e)},
                generated_at=datetime.now()
            )
