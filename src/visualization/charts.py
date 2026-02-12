"""
Fonctions de visualisation Plotly pour les résultats d'analyse Lean.
"""
from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
from src.models.schemas import DetectedLoss, Recommendation, AnalysisResult


# Palette de couleurs TIMWOODS
TIMWOODS_COLORS = {
    "Transport": "#FF6B6B",
    "Inventory": "#4ECDC4",
    "Motion": "#45B7D1",
    "Waiting": "#FFA07A",
    "OverProcessing": "#98D8C8",
    "OverProduction": "#F7DC6F",
    "Defects": "#E74C3C",
    "Skills": "#9B59B6"
}


def create_timwoods_distribution(losses: List[DetectedLoss]) -> go.Figure:
    """
    Crée un diagramme en barres de la distribution des pertes par catégorie TIMWOODS.
    
    Args:
        losses: Liste des pertes détectées
        
    Returns:
        Figure Plotly
    """
    if not losses:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune perte détectée",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Compter les pertes par catégorie
    category_counts = Counter(loss.timwoods_category for loss in losses)
    
    categories = list(category_counts.keys())
    counts = list(category_counts.values())
    colors = [TIMWOODS_COLORS.get(cat, "#95A5A6") for cat in categories]
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=counts,
            marker_color=colors,
            text=counts,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Nombre de pertes: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Distribution des pertes par catégorie TIMWOODS",
        xaxis_title="Catégorie",
        yaxis_title="Nombre de pertes",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_loss_severity_heatmap(losses: List[DetectedLoss]) -> go.Figure:
    """
    Crée une heatmap de la sévérité des pertes par catégorie et machine.
    
    Args:
        losses: Liste des pertes détectées
        
    Returns:
        Figure Plotly
    """
    if not losses:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune perte détectée",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Créer une matrice catégorie x sévérité
    severity_levels = ["low", "medium", "high", "critical"]
    categories = list(set(loss.timwoods_category for loss in losses))
    
    # Matrice de comptage
    matrix = []
    for category in categories:
        row = []
        for severity in severity_levels:
            count = sum(
                1 for loss in losses 
                if loss.timwoods_category == category and loss.severity == severity
            )
            row.append(count)
        matrix.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=["Faible", "Moyen", "Élevé", "Critique"],
        y=categories,
        colorscale='RdYlGn_r',
        text=matrix,
        texttemplate='%{text}',
        textfont={"size": 12},
        hovertemplate='<b>%{y}</b><br>Sévérité: %{x}<br>Nombre: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Heatmap : Sévérité des pertes par catégorie",
        xaxis_title="Niveau de sévérité",
        yaxis_title="Catégorie TIMWOODS",
        height=400,
    )
    
    return fig


def create_timeline_chart(losses: List[DetectedLoss]) -> go.Figure:
    """
    Crée une timeline des pertes détectées (par fréquence).
    
    Args:
        losses: Liste des pertes détectées
        
    Returns:
        Figure Plotly
    """
    if not losses:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune perte détectée",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Trier par fréquence décroissante
    sorted_losses = sorted(losses, key=lambda x: x.frequency, reverse=True)[:15]
    
    titles = [loss.title[:40] + "..." if len(loss.title) > 40 else loss.title 
              for loss in sorted_losses]
    frequencies = [loss.frequency for loss in sorted_losses]
    categories = [loss.timwoods_category for loss in sorted_losses]
    colors_list = [TIMWOODS_COLORS.get(cat, "#95A5A6") for cat in categories]
    
    fig = go.Figure(data=[
        go.Bar(
            y=titles,
            x=frequencies,
            orientation='h',
            marker_color=colors_list,
            text=frequencies,
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Fréquence: %{x}<br>Catégorie: %{customdata}<extra></extra>',
            customdata=categories
        )
    ])
    
    fig.update_layout(
        title="Top 15 des pertes par fréquence d'occurrence",
        xaxis_title="Fréquence",
        yaxis_title="",
        height=500,
        showlegend=False,
        yaxis=dict(autorange="reversed"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_cost_impact_chart(losses: List[DetectedLoss]) -> go.Figure:
    """
    Crée un diagramme de Pareto des pertes par impact financier.
    
    Args:
        losses: Liste des pertes détectées
        
    Returns:
        Figure Plotly
    """
    if not losses:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune perte détectée",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Trier par coût décroissant
    sorted_losses = sorted(losses, key=lambda x: x.estimated_cost_eur, reverse=True)[:10]
    
    titles = [loss.title[:30] + "..." if len(loss.title) > 30 else loss.title 
              for loss in sorted_losses]
    costs = [loss.estimated_cost_eur for loss in sorted_losses]
    categories = [loss.timwoods_category for loss in sorted_losses]
    
    # Calcul du cumul pour Pareto
    total_cost = sum(costs)
    cumulative_pct = []
    cumsum = 0
    for cost in costs:
        cumsum += cost
        cumulative_pct.append((cumsum / total_cost * 100) if total_cost > 0 else 0)
    
    colors_list = [TIMWOODS_COLORS.get(cat, "#95A5A6") for cat in categories]
    
    # Créer la figure avec deux axes Y
    fig = go.Figure()
    
    # Barres de coûts
    fig.add_trace(go.Bar(
        x=titles,
        y=costs,
        name="Coût (EUR)",
        marker_color=colors_list,
        yaxis='y',
        text=[f"{c:,.0f} €" for c in costs],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Coût: %{y:,.2f} EUR<extra></extra>'
    ))
    
    # Ligne de cumul Pareto
    fig.add_trace(go.Scatter(
        x=titles,
        y=cumulative_pct,
        name="Cumul %",
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='#E74C3C', width=2),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Cumul: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Pareto : Top 10 des pertes par impact financier",
        xaxis_title="",
        yaxis=dict(
            title="Coût estimé (EUR)",
            side='left'
        ),
        yaxis2=dict(
            title="Cumul (%)",
            side='right',
            overlaying='y',
            range=[0, 105]
        ),
        height=500,
        showlegend=True,
        legend=dict(x=0.7, y=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45
    )
    
    return fig


def create_recommendations_priority_matrix(recommendations: List[Recommendation]) -> go.Figure:
    """
    Crée une matrice effort/impact des recommandations (scatter plot).
    
    Args:
        recommendations: Liste des recommandations
        
    Returns:
        Figure Plotly
    """
    if not recommendations:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune recommandation disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Mapper effort à une échelle numérique
    effort_map = {"low": 1, "medium": 2, "high": 3}
    
    efforts = [effort_map.get(rec.implementation_effort, 2) for rec in recommendations]
    gains = [rec.estimated_gain_eur for rec in recommendations]
    titles = [rec.title[:50] + "..." if len(rec.title) > 50 else rec.title 
              for rec in recommendations]
    priorities = [rec.priority for rec in recommendations]
    
    # Couleur selon priorité
    priority_colors = {1: "#27AE60", 2: "#F39C12", 3: "#E67E22", 4: "#E74C3C", 5: "#95A5A6"}
    colors = [priority_colors.get(p, "#95A5A6") for p in priorities]
    
    # Taille des bulles proportionnelle au gain
    max_gain = max(gains) if gains else 1
    sizes = [30 + (gain / max_gain * 40) for gain in gains]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=efforts,
        y=gains,
        mode='markers+text',
        marker=dict(
            size=sizes,
            color=colors,
            line=dict(width=2, color='white'),
            opacity=0.7
        ),
        text=[f"P{p}" for p in priorities],
        textposition="middle center",
        textfont=dict(color='white', size=10, family='Arial Black'),
        customdata=list(zip(titles, priorities)),
        hovertemplate='<b>%{customdata[0]}</b><br>Effort: %{x}<br>Gain: %{y:,.0f} EUR<br>Priorité: %{customdata[1]}<extra></extra>'
    ))
    
    # Ajouter les quadrants
    fig.add_hline(y=sum(gains)/len(gains) if gains else 0, line_dash="dash", 
                  line_color="gray", opacity=0.5)
    fig.add_vline(x=2, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Annotations des quadrants
    max_y = max(gains) if gains else 1000
    fig.add_annotation(x=1.5, y=max_y*0.9, text="Quick Wins ✨", showarrow=False, 
                       font=dict(size=12, color="green"), opacity=0.6)
    fig.add_annotation(x=2.5, y=max_y*0.9, text="Projets majeurs 🎯", showarrow=False,
                       font=dict(size=12, color="orange"), opacity=0.6)
    
    fig.update_layout(
        title="Matrice Effort / Impact des recommandations",
        xaxis=dict(
            title="Effort d'implémentation",
            tickmode='array',
            tickvals=[1, 2, 3],
            ticktext=['Faible', 'Moyen', 'Élevé'],
            range=[0.5, 3.5]
        ),
        yaxis=dict(
            title="Gain estimé (EUR)"
        ),
        height=500,
        showlegend=False,
        plot_bgcolor='rgba(240,240,240,0.3)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_summary_kpi_cards(analysis_result: AnalysisResult) -> Dict[str, Any]:
    """
    Retourne les métriques KPI pour affichage dans des cartes.
    
    Args:
        analysis_result: Résultat complet de l'analyse
        
    Returns:
        Dictionnaire de KPIs
    """
    summary_stats = analysis_result.summary_stats
    
    kpis = {
        "total_losses": summary_stats.get("total_losses", 0),
        "total_cost_eur": summary_stats.get("total_cost_eur", 0),
        "total_recommendations": summary_stats.get("total_recommendations", 0),
        "potential_gain_eur": summary_stats.get("total_potential_gain_eur", 0),
        "roi_percentage": summary_stats.get("roi_percentage", 0),
        "top_category": summary_stats.get("top_category", "N/A"),
        "top_category_count": summary_stats.get("top_category_count", 0),
        "quick_wins_count": summary_stats.get("quick_wins_count", 0),
        "high_priority_count": summary_stats.get("high_priority_count", 0),
        "severity_critical": summary_stats.get("severity_distribution", {}).get("critical", 0),
        "severity_high": summary_stats.get("severity_distribution", {}).get("high", 0)
    }
    
    return kpis
