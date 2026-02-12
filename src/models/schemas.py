"""
Schémas Pydantic v2 pour toutes les structures de données de l'agent.
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from src.models.timwoods import TimwoodsCategory


class ProductionLog(BaseModel):
    """Log de production d'un événement machine."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    timestamp: datetime = Field(description="Horodatage de l'événement")
    machine_id: str = Field(description="Identifiant de la machine")
    event_type: Literal["arret", "micro_arret", "ralentissement", "normal"] = Field(
        description="Type d'événement"
    )
    duration_minutes: float = Field(ge=0, description="Durée en minutes")
    description: str = Field(description="Description de l'événement")
    line_id: str = Field(description="Identifiant de la ligne de production")
    operator_id: Optional[str] = Field(default=None, description="Identifiant de l'opérateur")
    shift: Literal["matin", "apres-midi", "nuit"] = Field(description="Équipe de travail")


class QualityRecord(BaseModel):
    """Enregistrement qualité d'un défaut ou non-conformité."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    timestamp: datetime = Field(description="Horodatage de l'enregistrement")
    product_id: str = Field(description="Identifiant du produit")
    defect_type: Literal["rebut", "retouche", "sur_controle", "non_conformite"] = Field(
        description="Type de défaut"
    )
    quantity: int = Field(ge=1, description="Quantité de pièces concernées")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="Sévérité du défaut"
    )
    description: str = Field(description="Description du défaut")
    machine_id: str = Field(description="Machine concernée")
    line_id: str = Field(description="Ligne de production")


class IncidentReport(BaseModel):
    """Rapport d'incident industriel."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    timestamp: datetime = Field(description="Horodatage de l'incident")
    incident_id: str = Field(description="Identifiant unique de l'incident")
    category: Literal[
        "panne_mecanique", 
        "panne_electrique", 
        "defaut_qualite", 
        "probleme_logistique", 
        "erreur_operateur"
    ] = Field(description="Catégorie d'incident")
    description: str = Field(description="Description détaillée")
    impact_level: int = Field(ge=1, le=5, description="Niveau d'impact (1-5)")
    resolution_time_hours: float = Field(ge=0, description="Temps de résolution en heures")
    root_cause: str = Field(description="Cause racine identifiée")
    machine_id: str = Field(description="Machine concernée")
    line_id: str = Field(description="Ligne de production")


class DetectedLoss(BaseModel):
    """Perte Lean détectée par l'agent."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    loss_id: str = Field(description="Identifiant unique de la perte")
    timwoods_category: TimwoodsCategory = Field(description="Catégorie TIMWOODS")
    title: str = Field(description="Titre de la perte")
    description: str = Field(description="Description détaillée")
    frequency: int = Field(ge=1, description="Fréquence d'occurrence")
    total_duration_hours: float = Field(ge=0, description="Durée totale en heures")
    estimated_cost_eur: float = Field(ge=0, description="Coût estimé en euros")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="Sévérité de la perte"
    )
    source_events: List[str] = Field(
        default_factory=list, 
        description="Liste des identifiants d'événements sources"
    )
    confidence_score: float = Field(
        ge=0, le=1, 
        description="Score de confiance de la détection (0-1)"
    )
    affected_machines: List[str] = Field(
        default_factory=list,
        description="Machines affectées"
    )
    affected_lines: List[str] = Field(
        default_factory=list,
        description="Lignes de production affectées"
    )


class RootCauseAnalysis(BaseModel):
    """Analyse de cause racine d'une perte."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    loss_id: str = Field(description="Identifiant de la perte analysée")
    method: Literal["five_whys", "ishikawa"] = Field(
        description="Méthode d'analyse utilisée"
    )
    causes: List[dict] = Field(
        description="Liste des causes avec niveau et description",
        default_factory=list
    )
    root_cause: str = Field(description="Cause racine principale identifiée")
    contributing_factors: List[str] = Field(
        default_factory=list,
        description="Facteurs contributifs"
    )


class Recommendation(BaseModel):
    """Recommandation d'amélioration Lean."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    recommendation_id: str = Field(description="Identifiant unique de la recommandation")
    loss_id: str = Field(description="Identifiant de la perte concernée")
    title: str = Field(description="Titre de la recommandation")
    description: str = Field(description="Description détaillée de l'action")
    priority: int = Field(ge=1, le=5, description="Priorité (1=haute, 5=basse)")
    estimated_gain_eur: float = Field(ge=0, description="Gain estimé en euros")
    implementation_effort: Literal["low", "medium", "high"] = Field(
        description="Effort d'implémentation"
    )
    timeline_weeks: int = Field(ge=1, description="Timeline en semaines")
    responsible_department: str = Field(description="Département responsable")


class AnalysisResult(BaseModel):
    """Résultat complet de l'analyse par l'agent."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    detected_losses: List[DetectedLoss] = Field(
        default_factory=list,
        description="Liste des pertes détectées"
    )
    root_cause_analyses: List[RootCauseAnalysis] = Field(
        default_factory=list,
        description="Analyses de causes racines"
    )
    recommendations: List[Recommendation] = Field(
        default_factory=list,
        description="Recommandations d'amélioration"
    )
    summary_stats: dict = Field(
        default_factory=dict,
        description="Statistiques résumées"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Date de génération du rapport"
    )
