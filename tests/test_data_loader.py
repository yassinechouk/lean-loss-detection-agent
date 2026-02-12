"""
Tests pour le DataLoader.
"""
import pytest
import csv
from pathlib import Path
from datetime import datetime
from src.data.loader import DataLoader
from src.models.schemas import ProductionLog, QualityRecord, IncidentReport


@pytest.fixture
def temp_data_dir(tmp_path):
    """Crée un répertoire temporaire avec des fichiers CSV de test."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    
    # Créer un fichier de logs de production
    production_file = data_dir / "production_logs.csv"
    with open(production_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'timestamp', 'machine_id', 'event_type', 'duration_minutes',
            'description', 'line_id', 'operator_id', 'shift'
        ])
        writer.writeheader()
        writer.writerow({
            'timestamp': '2024-01-15T10:30:00',
            'machine_id': 'CNC-01',
            'event_type': 'micro_arret',
            'duration_minutes': '3.5',
            'description': 'Test event',
            'line_id': 'L1',
            'operator_id': 'OP001',
            'shift': 'matin'
        })
    
    # Créer un fichier de quality records
    quality_file = data_dir / "quality_records.csv"
    with open(quality_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'timestamp', 'product_id', 'defect_type', 'quantity',
            'severity', 'description', 'machine_id', 'line_id'
        ])
        writer.writeheader()
        writer.writerow({
            'timestamp': '2024-01-15T11:00:00',
            'product_id': 'PROD1234',
            'defect_type': 'rebut',
            'quantity': '5',
            'severity': 'high',
            'description': 'Test defect',
            'machine_id': 'CNC-01',
            'line_id': 'L1'
        })
    
    # Créer un fichier d'incident reports
    incident_file = data_dir / "incident_reports.csv"
    with open(incident_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'timestamp', 'incident_id', 'category', 'description',
            'impact_level', 'resolution_time_hours', 'root_cause',
            'machine_id', 'line_id'
        ])
        writer.writeheader()
        writer.writerow({
            'timestamp': '2024-01-15T12:00:00',
            'incident_id': 'INC0001',
            'category': 'panne_mecanique',
            'description': 'Test incident',
            'impact_level': '3',
            'resolution_time_hours': '2.5',
            'root_cause': 'Test cause',
            'machine_id': 'CNC-01',
            'line_id': 'L1'
        })
    
    return str(data_dir)


def test_load_production_logs(temp_data_dir):
    """Test le chargement des logs de production."""
    loader = DataLoader(temp_data_dir)
    logs = loader.load_production_logs()
    
    assert len(logs) == 1
    assert isinstance(logs[0], ProductionLog)
    assert logs[0].machine_id == 'CNC-01'
    assert logs[0].event_type == 'micro_arret'
    assert logs[0].duration_minutes == 3.5


def test_load_quality_records(temp_data_dir):
    """Test le chargement des enregistrements qualité."""
    loader = DataLoader(temp_data_dir)
    records = loader.load_quality_records()
    
    assert len(records) == 1
    assert isinstance(records[0], QualityRecord)
    assert records[0].product_id == 'PROD1234'
    assert records[0].defect_type == 'rebut'
    assert records[0].quantity == 5


def test_load_incident_reports(temp_data_dir):
    """Test le chargement des rapports d'incidents."""
    loader = DataLoader(temp_data_dir)
    reports = loader.load_incident_reports()
    
    assert len(reports) == 1
    assert isinstance(reports[0], IncidentReport)
    assert reports[0].incident_id == 'INC0001'
    assert reports[0].category == 'panne_mecanique'
    assert reports[0].impact_level == 3


def test_load_all(temp_data_dir):
    """Test le chargement de toutes les données."""
    loader = DataLoader(temp_data_dir)
    data = loader.load_all()
    
    assert 'production_logs' in data
    assert 'quality_records' in data
    assert 'incident_reports' in data
    assert len(data['production_logs']) == 1
    assert len(data['quality_records']) == 1
    assert len(data['incident_reports']) == 1


def test_load_missing_file():
    """Test la gestion d'erreur quand un fichier est manquant."""
    with pytest.raises(FileNotFoundError):
        loader = DataLoader("nonexistent_dir")
