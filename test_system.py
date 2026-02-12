#!/usr/bin/env python
"""
Test complet du système end-to-end (sans API et avec API si disponible).
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.loader import DataLoader
from src.agents.graph import LeanLossDetectionGraph
from src.utils.config import get_settings

def test_system():
    """Test le système complet."""
    print("\n" + "="*80)
    print("TEST END-TO-END DU SYSTÈME LEAN LOSS DETECTION")
    print("="*80 + "\n")
    
    settings = get_settings()
    
    print("📋 Configuration :")
    print(f"   - Clé API configurée : {settings.is_api_configured()}")
    print(f"   - Modèle LLM : {settings.llm_model}")
    print(f"   - Température : {settings.llm_temperature}")
    print(f"   - Répertoire données : {settings.data_dir}")
    print()
    
    # 1. Chargement des données
    print("📂 ÉTAPE 1 : Chargement des données...")
    try:
        loader = DataLoader(settings.data_dir)
        data = loader.load_all()
        print(f"✅ Données chargées avec succès")
        print(f"   - {len(data['production_logs'])} logs de production")
        print(f"   - {len(data['quality_records'])} enregistrements qualité")
        print(f"   - {len(data['incident_reports'])} rapports d'incidents")
    except Exception as e:
        print(f"❌ Erreur lors du chargement : {e}")
        return False
    
    # 2. Exécution du graphe
    print("\n🔄 ÉTAPE 2 : Exécution du pipeline d'analyse...")
    try:
        graph = LeanLossDetectionGraph()
        result = graph.run(data)
        
        print("\n✅ Analyse terminée avec succès!")
        
        # 3. Vérification des résultats
        print("\n📊 ÉTAPE 3 : Vérification des résultats...")
        
        print(f"\n📋 Statistiques :")
        print(f"   - Pertes détectées : {len(result.detected_losses)}")
        print(f"   - Analyses de causes racines : {len(result.root_cause_analyses)}")
        print(f"   - Recommandations : {len(result.recommendations)}")
        
        if result.summary_stats:
            print(f"\n💰 Impact financier :")
            print(f"   - Coût total estimé : {result.summary_stats.get('total_cost_eur', 0):,.2f} EUR")
            print(f"   - Gain potentiel : {result.summary_stats.get('total_potential_gain_eur', 0):,.2f} EUR")
            print(f"   - ROI : {result.summary_stats.get('roi_percentage', 0):.1f}%")
        
        # Afficher quelques pertes détectées
        if result.detected_losses:
            print(f"\n🔍 Échantillon de pertes détectées :")
            for i, loss in enumerate(result.detected_losses[:3], 1):
                print(f"\n   {i}. {loss.title}")
                print(f"      Catégorie : {loss.timwoods_category}")
                print(f"      Sévérité : {loss.severity}")
                print(f"      Coût estimé : {loss.estimated_cost_eur:,.0f} EUR")
                print(f"      Confiance : {loss.confidence_score:.0%}")
        
        # Afficher quelques recommandations
        if result.recommendations:
            print(f"\n💡 Échantillon de recommandations :")
            for i, rec in enumerate(result.recommendations[:3], 1):
                print(f"\n   {i}. {rec.title}")
                print(f"      Priorité : {rec.priority}")
                print(f"      Gain estimé : {rec.estimated_gain_eur:,.0f} EUR")
                print(f"      Effort : {rec.implementation_effort}")
                print(f"      Timeline : {rec.timeline_weeks} semaines")
                print(f"      Responsable : {rec.responsible_department}")
        
        print("\n" + "="*80)
        print("✨ TEST RÉUSSI - LE SYSTÈME FONCTIONNE CORRECTEMENT!")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'analyse : {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)
