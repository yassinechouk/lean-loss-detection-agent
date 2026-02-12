"""
Chargeur de données de production avec validation Pydantic.
"""
import csv
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from src.models.schemas import ProductionLog, QualityRecord, IncidentReport


class DataLoader:
    """Chargeur de données industrielles avec validation."""
    
    def __init__(self, data_dir: str = "data/synthetic"):
        """
        Initialise le chargeur de données.
        
        Args:
            data_dir: Répertoire contenant les fichiers CSV
        """
        self.data_dir = Path(data_dir)
        
        if not self.data_dir.exists():
            raise FileNotFoundError(
                f"Le répertoire de données n'existe pas : {self.data_dir.absolute()}"
            )
    
    def load_production_logs(self, filename: str = "production_logs.csv") -> List[ProductionLog]:
        """
        Charge et valide les logs de production.
        
        Args:
            filename: Nom du fichier CSV
            
        Returns:
            Liste de ProductionLog validés
            
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si les données sont invalides
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(
                f"Fichier introuvable : {filepath.absolute()}\n"
                f"Assurez-vous d'avoir généré les données synthétiques avec : "
                f"python -m src.data.synthetic_generator"
            )
        
        logs = []
        errors = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                try:
                    # Conversion du timestamp
                    row['timestamp'] = datetime.fromisoformat(row['timestamp'])
                    row['duration_minutes'] = float(row['duration_minutes'])
                    
                    log = ProductionLog.model_validate(row)
                    logs.append(log)
                except Exception as e:
                    errors.append(f"Ligne {i}: {str(e)}")
        
        if errors:
            print(f"⚠️  {len(errors)} erreur(s) de validation détectée(s):")
            for error in errors[:5]:  # Afficher les 5 premières erreurs
                print(f"   {error}")
            if len(errors) > 5:
                print(f"   ... et {len(errors) - 5} autres erreurs")
        
        print(f"✅ {len(logs)} logs de production chargés depuis {filename}")
        return logs
    
    def load_quality_records(self, filename: str = "quality_records.csv") -> List[QualityRecord]:
        """
        Charge et valide les enregistrements qualité.
        
        Args:
            filename: Nom du fichier CSV
            
        Returns:
            Liste de QualityRecord validés
            
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Fichier introuvable : {filepath.absolute()}")
        
        records = []
        errors = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                try:
                    row['timestamp'] = datetime.fromisoformat(row['timestamp'])
                    row['quantity'] = int(row['quantity'])
                    
                    record = QualityRecord.model_validate(row)
                    records.append(record)
                except Exception as e:
                    errors.append(f"Ligne {i}: {str(e)}")
        
        if errors:
            print(f"⚠️  {len(errors)} erreur(s) de validation détectée(s):")
            for error in errors[:5]:
                print(f"   {error}")
        
        print(f"✅ {len(records)} enregistrements qualité chargés depuis {filename}")
        return records
    
    def load_incident_reports(self, filename: str = "incident_reports.csv") -> List[IncidentReport]:
        """
        Charge et valide les rapports d'incidents.
        
        Args:
            filename: Nom du fichier CSV
            
        Returns:
            Liste de IncidentReport validés
            
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Fichier introuvable : {filepath.absolute()}")
        
        reports = []
        errors = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                try:
                    row['timestamp'] = datetime.fromisoformat(row['timestamp'])
                    row['impact_level'] = int(row['impact_level'])
                    row['resolution_time_hours'] = float(row['resolution_time_hours'])
                    
                    report = IncidentReport.model_validate(row)
                    reports.append(report)
                except Exception as e:
                    errors.append(f"Ligne {i}: {str(e)}")
        
        if errors:
            print(f"⚠️  {len(errors)} erreur(s) de validation détectée(s):")
            for error in errors[:5]:
                print(f"   {error}")
        
        print(f"✅ {len(reports)} rapports d'incidents chargés depuis {filename}")
        return reports
    
    def load_all(self) -> dict:
        """
        Charge toutes les données disponibles.
        
        Returns:
            Dictionnaire contenant les trois types de données
            
        Raises:
            FileNotFoundError: Si un fichier requis n'existe pas
        """
        print(f"\n📂 Chargement des données depuis : {self.data_dir.absolute()}\n")
        
        try:
            production_logs = self.load_production_logs()
            quality_records = self.load_quality_records()
            incident_reports = self.load_incident_reports()
            
            print(f"\n✨ Chargement terminé avec succès!")
            
            return {
                "production_logs": production_logs,
                "quality_records": quality_records,
                "incident_reports": incident_reports
            }
        except FileNotFoundError as e:
            print(f"\n❌ Erreur de chargement : {str(e)}")
            raise
