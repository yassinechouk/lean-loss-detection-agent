"""
Tests pour l'AnalyzerAgent.
"""
import pytest
from src.agents.analyzer_agent import AnalyzerAgent
from src.models.timwoods import TimwoodsCategory


def test_analyzer_fallback_mode():
    """Test le mode fallback heuristique de l'analyzer."""
    analyzer = AnalyzerAgent(llm=None)
    
    # Pertes de test
    test_losses = [
        {
            "loss_id": "LOSS_001",
            "title": "Micro-arrêts fréquents sur CNC-01",
            "description": "La machine présente des micro-arrêts répétitifs",
            "frequency": 45,
            "total_duration_hours": 12.5,
            "severity": "high"
        },
        {
            "loss_id": "LOSS_002",
            "title": "Taux de rebut élevé",
            "description": "Nombre de rebuts anormalement élevé",
            "frequency": 35,
            "total_duration_hours": 8.0,
            "severity": "high"
        }
    ]
    
    analyses = analyzer.analyze(test_losses)
    
    # Vérifications
    assert isinstance(analyses, list)
    assert len(analyses) == 2
    
    for analysis in analyses:
        assert 'loss_id' in analysis
        assert 'timwoods_category' in analysis
        assert 'justification' in analysis
        assert 'root_cause_analysis' in analysis
        assert 'estimated_cost_eur' in analysis
        assert 'severity' in analysis


def test_timwoods_classification():
    """Test la classification TIMWOODS."""
    analyzer = AnalyzerAgent(llm=None)
    
    # Test de pertes avec mots-clés spécifiques
    test_cases = [
        {
            "loss": {
                "loss_id": "L1",
                "title": "Micro-arrêts avec attente",
                "description": "Temps d'attente machine",
                "frequency": 20,
                "total_duration_hours": 5.0,
                "severity": "medium"
            },
            "expected_category": "Waiting"
        },
        {
            "loss": {
                "loss_id": "L2",
                "title": "Rebuts qualité",
                "description": "Défauts de production",
                "frequency": 30,
                "total_duration_hours": 7.0,
                "severity": "high"
            },
            "expected_category": "Defects"
        }
    ]
    
    for test_case in test_cases:
        analyses = analyzer.analyze([test_case["loss"]])
        assert len(analyses) == 1
        assert analyses[0]['timwoods_category'] == test_case["expected_category"]


def test_root_cause_analysis_structure():
    """Test la structure de l'analyse de causes racines."""
    analyzer = AnalyzerAgent(llm=None)
    
    test_loss = {
        "loss_id": "LOSS_TEST",
        "title": "Test loss",
        "description": "Test description",
        "frequency": 10,
        "total_duration_hours": 3.0,
        "severity": "medium"
    }
    
    analyses = analyzer.analyze([test_loss])
    
    assert len(analyses) == 1
    rca = analyses[0]['root_cause_analysis']
    
    # Vérifier la structure du 5 Pourquoi
    assert 'method' in rca
    assert rca['method'] == 'five_whys'
    assert 'causes' in rca
    assert isinstance(rca['causes'], list)
    assert len(rca['causes']) > 0
    assert 'root_cause' in rca
    assert 'contributing_factors' in rca


def test_cost_estimation():
    """Test l'estimation des coûts."""
    analyzer = AnalyzerAgent(llm=None)
    
    test_loss = {
        "loss_id": "LOSS_COST",
        "title": "Test cost estimation",
        "description": "Testing cost calculation",
        "frequency": 50,
        "total_duration_hours": 10.0,
        "severity": "high"
    }
    
    analyses = analyzer.analyze([test_loss])
    
    assert len(analyses) == 1
    assert analyses[0]['estimated_cost_eur'] > 0
    assert isinstance(analyses[0]['estimated_cost_eur'], (int, float))
