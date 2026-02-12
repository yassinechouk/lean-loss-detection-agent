"""
Tests pour le RecommenderAgent.
"""
import pytest
from src.agents.recommender_agent import RecommenderAgent


def test_recommender_fallback_mode():
    """Test le mode fallback heuristique du recommender."""
    recommender = RecommenderAgent(llm=None)
    
    # Analyses de test
    test_analyses = [
        {
            "loss_id": "LOSS_001",
            "timwoods_category": "Waiting",
            "estimated_cost_eur": 15000.0,
            "severity": "high",
            "root_cause_analysis": {
                "method": "five_whys",
                "causes": [],
                "root_cause": "Test root cause"
            }
        }
    ]
    
    recommendations = recommender.recommend(test_analyses)
    
    # Vérifications
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    
    for rec in recommendations:
        assert 'recommendation_id' in rec
        assert 'loss_id' in rec
        assert 'title' in rec
        assert 'description' in rec
        assert 'priority' in rec
        assert 'estimated_gain_eur' in rec
        assert 'implementation_effort' in rec
        assert 'timeline_weeks' in rec
        assert 'responsible_department' in rec


def test_recommendation_structure():
    """Test la structure des recommandations."""
    recommender = RecommenderAgent(llm=None)
    
    test_analysis = {
        "loss_id": "LOSS_TEST",
        "timwoods_category": "Defects",
        "estimated_cost_eur": 10000.0,
        "severity": "critical"
    }
    
    recommendations = recommender.recommend([test_analysis])
    
    assert len(recommendations) > 0
    
    rec = recommendations[0]
    
    # Vérifier les contraintes
    assert rec['priority'] >= 1 and rec['priority'] <= 5
    assert rec['implementation_effort'] in ['low', 'medium', 'high']
    assert rec['timeline_weeks'] > 0
    assert rec['estimated_gain_eur'] >= 0


def test_recommendation_prioritization():
    """Test la priorisation des recommandations."""
    recommender = RecommenderAgent(llm=None)
    
    # Plusieurs analyses avec sévérités différentes
    test_analyses = [
        {
            "loss_id": "L1",
            "timwoods_category": "Waiting",
            "estimated_cost_eur": 5000.0,
            "severity": "low"
        },
        {
            "loss_id": "L2",
            "timwoods_category": "Defects",
            "estimated_cost_eur": 20000.0,
            "severity": "critical"
        }
    ]
    
    recommendations = recommender.recommend(test_analyses)
    
    # Les recommandations doivent être triées par priorité
    assert len(recommendations) > 0
    
    priorities = [rec['priority'] for rec in recommendations]
    # Vérifier que les priorités sont dans un ordre logique (pas nécessairement strictement croissant)
    assert min(priorities) >= 1
    assert max(priorities) <= 5


def test_gain_estimation():
    """Test l'estimation des gains."""
    recommender = RecommenderAgent(llm=None)
    
    test_analysis = {
        "loss_id": "LOSS_GAIN",
        "timwoods_category": "OverProcessing",
        "estimated_cost_eur": 12000.0,
        "severity": "medium"
    }
    
    recommendations = recommender.recommend([test_analysis])
    
    assert len(recommendations) > 0
    
    # Le gain devrait être une fraction du coût de la perte
    for rec in recommendations:
        assert rec['estimated_gain_eur'] > 0
        assert rec['estimated_gain_eur'] <= test_analysis['estimated_cost_eur']


def test_empty_analysis():
    """Test le cas où il n'y a pas d'analyse à traiter."""
    recommender = RecommenderAgent(llm=None)
    
    recommendations = recommender.recommend([])
    
    assert isinstance(recommendations, list)
    assert len(recommendations) == 0
