"""
Tests pour le ParserAgent.
"""
import pytest
from src.agents.parser_agent import ParserAgent


def test_parser_fallback_mode():
    """Test le mode fallback heuristique du parser (sans API)."""
    parser = ParserAgent(llm=None)
    
    # Données de test
    test_data = """
    CNC-01:
      - Micro-arrêts : 45
      - Temps d'arrêt : 12.5h
    
    PRESS-01:
      - Micro-arrêts : 15
      - Temps d'arrêt : 6.0h
    
    Shift nuit : 25 événements, 8.5h d'arrêt
    
    Par type de défaut :
      rebut                    : 35
      retouche                 : 28
      sur_controle             : 18
    """
    
    losses = parser.parse(test_data)
    
    # Vérifier qu'on a des pertes détectées
    assert isinstance(losses, list)
    assert len(losses) > 0
    
    # Vérifier la structure des pertes
    for loss in losses:
        assert 'loss_id' in loss
        assert 'title' in loss
        assert 'description' in loss
        assert 'frequency' in loss
        assert 'total_duration_hours' in loss
        assert 'severity' in loss
        assert 'confidence_score' in loss


def test_parser_output_format():
    """Test le format de sortie du parser."""
    parser = ParserAgent(llm=None)
    
    test_data = """
    CNC-01:
      - Micro-arrêts : 55
      - Temps d'arrêt : 15.0h
    """
    
    losses = parser.parse(test_data)
    
    # Vérifier qu'on détecte bien une perte pour les micro-arrêts élevés
    assert len(losses) > 0
    
    first_loss = losses[0]
    
    # Vérifier les champs requis
    assert first_loss['frequency'] > 0
    assert first_loss['total_duration_hours'] > 0
    assert first_loss['confidence_score'] >= 0 and first_loss['confidence_score'] <= 1
    assert first_loss['severity'] in ['low', 'medium', 'high', 'critical']


def test_parser_no_losses():
    """Test le cas où aucune perte n'est détectée."""
    parser = ParserAgent(llm=None)
    
    # Données normales sans problème
    test_data = """
    Production normale.
    Aucun événement particulier.
    """
    
    losses = parser.parse(test_data)
    
    # Peut retourner une liste vide ou des pertes avec confiance faible
    assert isinstance(losses, list)
