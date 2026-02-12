"""
Application Streamlit - Dashboard interactif pour l'analyse Lean.
Point d'entrée principal : streamlit run app.py
"""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime

from src.data.loader import DataLoader
from src.data.synthetic_generator import SyntheticDataGenerator
from src.agents.graph import LeanLossDetectionGraph
from src.visualization.charts import (
    create_timwoods_distribution,
    create_loss_severity_heatmap,
    create_timeline_chart,
    create_cost_impact_chart,
    create_recommendations_priority_matrix,
    create_summary_kpi_cards
)
from src.utils.config import get_settings
from src.models.schemas import AnalysisResult


# Configuration de la page
st.set_page_config(
    page_title="Agent Lean Loss Detection",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialise l'état de session Streamlit."""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False


def ensure_synthetic_data_exists():
    """Génère les données synthétiques si elles n'existent pas."""
    data_dir = Path("data/synthetic")
    files_exist = (
        (data_dir / "production_logs.csv").exists() and
        (data_dir / "quality_records.csv").exists() and
        (data_dir / "incident_reports.csv").exists()
    )
    
    if not files_exist:
        with st.spinner("🔄 Génération des données synthétiques..."):
            generator = SyntheticDataGenerator()
            generator.generate_all()
        st.success("✅ Données synthétiques générées!")


def sidebar():
    """Affiche la sidebar avec les contrôles."""
    st.sidebar.markdown("# 🏭 Lean Loss Detection")
    st.sidebar.markdown("---")
    
    # Informations sur la configuration
    settings = get_settings()
    
    st.sidebar.markdown("### ⚙️ Configuration")
    
    if settings.is_api_configured():
        st.sidebar.success("✅ Clé API configurée")
        st.sidebar.info(f"**Modèle** : {settings.llm_model}")
        st.sidebar.info(f"**Température** : {settings.llm_temperature}")
    else:
        st.sidebar.warning("⚠️ Pas de clé API")
        st.sidebar.info("Mode heuristique activé")
    
    st.sidebar.markdown("---")
    
    # Section upload de fichiers
    st.sidebar.markdown("### 📁 Données")
    
    use_custom_data = st.sidebar.checkbox(
        "Utiliser mes propres données",
        value=False
    )
    
    if use_custom_data:
        st.sidebar.markdown("**Upload CSV** :")
        production_file = st.sidebar.file_uploader(
            "Production logs",
            type=['csv'],
            key="production"
        )
        quality_file = st.sidebar.file_uploader(
            "Quality records",
            type=['csv'],
            key="quality"
        )
        incident_file = st.sidebar.file_uploader(
            "Incident reports",
            type=['csv'],
            key="incident"
        )
        
        if production_file and quality_file and incident_file:
            st.sidebar.success("✅ 3 fichiers uploadés")
        else:
            st.sidebar.info("📤 Uploadez les 3 fichiers CSV")
    else:
        st.sidebar.info("📊 Données synthétiques")
        ensure_synthetic_data_exists()
    
    st.sidebar.markdown("---")
    
    # Bouton d'analyse
    analyze_button = st.sidebar.button(
        "🚀 Lancer l'analyse",
        type="primary",
        use_container_width=True
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 À propos")
    st.sidebar.markdown("""
    Agent IA d'analyse Lean utilisant :
    - LangChain & LangGraph
    - Classification TIMWOODS
    - Analyse causes racines
    - Recommandations priorisées
    """)
    
    return analyze_button, use_custom_data


def load_data(use_custom_data: bool) -> dict:
    """
    Charge les données de production.
    
    Args:
        use_custom_data: Si True, utilise les fichiers uploadés
        
    Returns:
        Dictionnaire de données
    """
    if use_custom_data:
        # TODO: Implémenter le chargement des fichiers uploadés
        st.warning("⚠️ Chargement de fichiers custom non encore implémenté. "
                  "Utilisation des données synthétiques.")
        use_custom_data = False
    
    if not use_custom_data:
        loader = DataLoader("data/synthetic")
        data = loader.load_all()
        return data


def run_analysis(data: dict):
    """
    Exécute l'analyse complète.
    
    Args:
        data: Données de production
    """
    try:
        graph = LeanLossDetectionGraph()
        result = graph.run(data)
        st.session_state.analysis_result = result
        st.session_state.data_loaded = True
        return True
    except Exception as e:
        st.error(f"❌ Erreur pendant l'analyse : {str(e)}")
        return False


def display_overview_tab(result: AnalysisResult):
    """Affiche l'onglet Vue d'ensemble."""
    st.markdown("## 📊 Vue d'ensemble")
    
    # KPIs
    kpis = create_summary_kpi_cards(result)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔍 Pertes détectées",
            value=kpis['total_losses'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="💰 Coût estimé",
            value=f"{kpis['total_cost_eur']:,.0f} €",
            delta=None
        )
    
    with col3:
        st.metric(
            label="💡 Recommandations",
            value=kpis['total_recommendations'],
            delta=f"{kpis['quick_wins_count']} quick wins",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="📈 Gain potentiel",
            value=f"{kpis['potential_gain_eur']:,.0f} €",
            delta=f"ROI {kpis['roi_percentage']:.0f}%",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_timwoods_distribution(result.detected_losses),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            create_timeline_chart(result.detected_losses),
            use_container_width=True
        )


def display_losses_tab(result: AnalysisResult):
    """Affiche l'onglet Pertes détectées."""
    st.markdown("## 🔍 Pertes détectées")
    
    if not result.detected_losses:
        st.info("Aucune perte détectée.")
        return
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = list(set(loss.timwoods_category for loss in result.detected_losses))
        selected_category = st.selectbox(
            "Filtrer par catégorie",
            ["Toutes"] + categories
        )
    
    with col2:
        severities = ["Toutes", "critical", "high", "medium", "low"]
        selected_severity = st.selectbox(
            "Filtrer par sévérité",
            severities
        )
    
    with col3:
        sort_by = st.selectbox(
            "Trier par",
            ["Coût (décroissant)", "Fréquence (décroissant)", "Sévérité"]
        )
    
    # Filtrer les pertes
    filtered_losses = result.detected_losses
    
    if selected_category != "Toutes":
        filtered_losses = [l for l in filtered_losses if l.timwoods_category == selected_category]
    
    if selected_severity != "Toutes":
        filtered_losses = [l for l in filtered_losses if l.severity == selected_severity]
    
    # Trier
    if sort_by == "Coût (décroissant)":
        filtered_losses = sorted(filtered_losses, key=lambda x: x.estimated_cost_eur, reverse=True)
    elif sort_by == "Fréquence (décroissant)":
        filtered_losses = sorted(filtered_losses, key=lambda x: x.frequency, reverse=True)
    elif sort_by == "Sévérité":
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        filtered_losses = sorted(filtered_losses, key=lambda x: severity_order.get(x.severity, 4))
    
    st.markdown(f"**{len(filtered_losses)} perte(s) affichée(s)**")
    st.markdown("---")
    
    # Afficher les pertes
    for i, loss in enumerate(filtered_losses, 1):
        with st.expander(f"**{i}. {loss.title}** - {loss.timwoods_category} ({loss.severity.upper()})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Fréquence", loss.frequency)
            with col2:
                st.metric("Durée totale", f"{loss.total_duration_hours:.1f}h")
            with col3:
                st.metric("Coût estimé", f"{loss.estimated_cost_eur:,.0f} €")
            
            st.markdown("**Description :**")
            st.write(loss.description)
            
            if loss.affected_machines:
                st.markdown(f"**Machines concernées :** {', '.join(loss.affected_machines)}")
            
            if loss.affected_lines:
                st.markdown(f"**Lignes concernées :** {', '.join(loss.affected_lines)}")
            
            st.progress(loss.confidence_score)
            st.caption(f"Confiance de détection : {loss.confidence_score:.0%}")


def display_analysis_tab(result: AnalysisResult):
    """Affiche l'onglet Analyse des causes."""
    st.markdown("## 🧠 Analyse des causes racines")
    
    if not result.root_cause_analyses:
        st.info("Aucune analyse de causes racines disponible.")
        return
    
    for i, rca in enumerate(result.root_cause_analyses, 1):
        # Trouver la perte correspondante
        loss = next((l for l in result.detected_losses if l.loss_id == rca.loss_id), None)
        
        if loss:
            st.markdown(f"### {i}. {loss.title}")
            st.markdown(f"**Catégorie TIMWOODS** : {loss.timwoods_category}")
            
            # Afficher les 5 Pourquoi
            st.markdown("#### 🔄 Méthode des 5 Pourquoi")
            
            for cause in rca.causes:
                level = cause.get('level', 0)
                cause_text = cause.get('cause', '')
                indent = "  " * (level - 1)
                st.markdown(f"{indent}**Pourquoi {level} ?** → {cause_text}")
            
            st.markdown(f"**🎯 Cause racine identifiée :** {rca.root_cause}")
            
            # Facteurs contributifs
            if rca.contributing_factors:
                st.markdown("**Facteurs contributifs :**")
                for factor in rca.contributing_factors:
                    st.markdown(f"- {factor}")
            
            st.markdown("---")


def display_recommendations_tab(result: AnalysisResult):
    """Affiche l'onglet Recommandations."""
    st.markdown("## 💡 Recommandations d'amélioration")
    
    if not result.recommendations:
        st.info("Aucune recommandation disponible.")
        return
    
    # Afficher la matrice effort/impact
    st.plotly_chart(
        create_recommendations_priority_matrix(result.recommendations),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Grouper par priorité
    st.markdown("### 📋 Liste des recommandations")
    
    priority_labels = {1: "🔴 Priorité 1 (Haute)", 2: "🟠 Priorité 2", 
                      3: "🟡 Priorité 3", 4: "🟢 Priorité 4", 5: "⚪ Priorité 5 (Basse)"}
    
    for priority in [1, 2, 3, 4, 5]:
        priority_recs = [r for r in result.recommendations if r.priority == priority]
        
        if priority_recs:
            st.markdown(f"#### {priority_labels[priority]} ({len(priority_recs)} recommandation(s))")
            
            for rec in priority_recs:
                with st.expander(f"**{rec.title}** - {rec.responsible_department}"):
                    st.markdown(rec.description)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Gain estimé", f"{rec.estimated_gain_eur:,.0f} €")
                    with col2:
                        effort_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
                        st.metric("Effort", f"{effort_emoji.get(rec.implementation_effort, '')} {rec.implementation_effort}")
                    with col3:
                        st.metric("Timeline", f"{rec.timeline_weeks} semaines")
                    with col4:
                        st.metric("Priorité", rec.priority)


def display_statistics_tab(result: AnalysisResult):
    """Affiche l'onglet Statistiques."""
    st.markdown("## 📈 Statistiques détaillées")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_loss_severity_heatmap(result.detected_losses),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            create_cost_impact_chart(result.detected_losses),
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Statistiques résumées
    st.markdown("### 📊 Résumé statistique")
    
    stats = result.summary_stats
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Distribution TIMWOODS**")
        timwoods_dist = stats.get('timwoods_distribution', {})
        for category, count in sorted(timwoods_dist.items(), key=lambda x: x[1], reverse=True):
            st.write(f"{category}: {count}")
    
    with col2:
        st.markdown("**Distribution Sévérité**")
        severity_dist = stats.get('severity_distribution', {})
        for severity, count in sorted(severity_dist.items(), 
                                     key=lambda x: ['critical', 'high', 'medium', 'low'].index(x[0]) if x[0] in ['critical', 'high', 'medium', 'low'] else 4):
            st.write(f"{severity.capitalize()}: {count}")
    
    with col3:
        st.markdown("**Métriques clés**")
        st.write(f"Coût total: {stats.get('total_cost_eur', 0):,.0f} €")
        st.write(f"Gain potentiel: {stats.get('total_potential_gain_eur', 0):,.0f} €")
        st.write(f"ROI: {stats.get('roi_percentage', 0):.1f}%")
        st.write(f"Quick wins: {stats.get('quick_wins_count', 0)}")
    
    # Export JSON
    st.markdown("---")
    st.markdown("### 💾 Export des résultats")
    
    if st.button("📥 Télécharger le rapport JSON"):
        json_data = result.model_dump_json(indent=2)
        st.download_button(
            label="Télécharger JSON",
            data=json_data,
            file_name=f"lean_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def main():
    """Fonction principale de l'application."""
    init_session_state()
    
    # Titre principal
    st.markdown('<h1 class="main-title">🏭 Agent IA – Détection des Pertes Lean Invisibles</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    analyze_button, use_custom_data = sidebar()
    
    # Si bouton analyse cliqué
    if analyze_button:
        st.session_state.analysis_running = True
        
        with st.spinner("🔄 Chargement des données..."):
            data = load_data(use_custom_data)
        
        with st.spinner("🧠 Analyse en cours... Cela peut prendre quelques instants."):
            success = run_analysis(data)
        
        st.session_state.analysis_running = False
        
        if success:
            st.success("✅ Analyse terminée avec succès!")
            st.balloons()
    
    # Affichage des résultats
    if st.session_state.analysis_result is not None:
        result = st.session_state.analysis_result
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Vue d'ensemble",
            "🔍 Pertes détectées",
            "🧠 Analyse des causes",
            "💡 Recommandations",
            "📈 Statistiques"
        ])
        
        with tab1:
            display_overview_tab(result)
        
        with tab2:
            display_losses_tab(result)
        
        with tab3:
            display_analysis_tab(result)
        
        with tab4:
            display_recommendations_tab(result)
        
        with tab5:
            display_statistics_tab(result)
    
    else:
        # Message d'accueil
        st.markdown("""
        ## 👋 Bienvenue !
        
        Cette application utilise l'intelligence artificielle pour détecter les **pertes Lean invisibles** 
        dans vos processus de production.
        
        ### 🎯 Fonctionnalités
        
        - 🔍 **Détection automatique** des micro-arrêts et pertes cachées
        - 📊 **Classification TIMWOODS** intelligente
        - 🧠 **Analyse de causes racines** (méthode des 5 Pourquoi)
        - 💡 **Recommandations** d'amélioration priorisées
        - 📈 **Visualisations** interactives
        
        ### 🚀 Pour commencer
        
        1. Configurez votre clé API OpenAI dans le fichier `.env` (optionnel - mode heuristique disponible)
        2. Cliquez sur **"🚀 Lancer l'analyse"** dans la sidebar
        3. Explorez les résultats dans les différents onglets
        
        ---
        
        💡 **Astuce** : Sans clé API, l'application fonctionne en mode heuristique 
        avec des règles d'analyse basées sur des seuils statistiques.
        """)
        
        # Exemple de données
        with st.expander("📊 Aperçu des données synthétiques"):
            st.markdown("""
            Les données synthétiques incluent :
            - **500 logs de production** sur 30 jours
            - **5 machines** (CNC-01, CNC-02, PRESS-01, PRESS-02, ASSEMBLY-01)
            - **3 lignes** de production (L1, L2, L3)
            - **200 enregistrements qualité** (rebuts, retouches, etc.)
            - **80 rapports d'incidents**
            
            **Patterns intentionnels** :
            - CNC-01 : 3x plus de micro-arrêts (perte cachée)
            - Shift nuit : arrêts plus longs
            - PRESS-01 : ralentissements récurrents
            """)


if __name__ == "__main__":
    main()
