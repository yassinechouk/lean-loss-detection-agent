"""
Générateur de données synthétiques réalistes pour démonstration et tests.
Exécutable en tant que module : python -m src.data.synthetic_generator
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple


class SyntheticDataGenerator:
    """Générateur de données synthétiques réalistes."""
    
    def __init__(self, output_dir: str = "data/synthetic"):
        """
        Initialise le générateur.
        
        Args:
            output_dir: Répertoire de sortie pour les fichiers CSV
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration des machines et lignes
        self.machines = ["CNC-01", "CNC-02", "PRESS-01", "PRESS-02", "ASSEMBLY-01"]
        self.lines = ["L1", "L2", "L3"]
        self.shifts = ["matin", "apres-midi", "nuit"]
        
        # Descriptions réalistes d'événements
        self.event_descriptions = {
            "micro_arret": [
                "Bourrage convoyeur",
                "Capteur position défaillant",
                "Ajustement outil mineur",
                "Attente pièce suivante",
                "Vérification qualité rapide",
                "Nettoyage zone de travail",
                "Changement outil cassé",
                "Réglage paramètre machine"
            ],
            "arret": [
                "Changement de série",
                "Attente approvisionnement matière",
                "Maintenance corrective",
                "Panne électrique",
                "Défaillance vérin pneumatique",
                "Problème logiciel automate",
                "Changement outillage complet",
                "Attente validation qualité",
                "Formation nouvel opérateur",
                "Réglage après dérive dimensionnelle"
            ],
            "ralentissement": [
                "Cadence réduite usure outil",
                "Refroidissement insuffisant",
                "Pression hydraulique faible",
                "Matière première non conforme",
                "Opérateur en formation",
                "Encrassement filtre",
                "Vibrations anormales",
                "Température ambiante élevée"
            ],
            "normal": [
                "Production normale",
                "Cycle standard",
                "Fonctionnement optimal",
                "Production conforme"
            ]
        }
        
        self.defect_descriptions = {
            "rebut": [
                "Dimension hors tolérance",
                "Rayure surface critique",
                "Fissure détectée",
                "Contamination matière",
                "Bavure excessive",
                "Défaut d'aspect majeur"
            ],
            "retouche": [
                "Ébavurage nécessaire",
                "Reprise usinage",
                "Ajustement dimensionnel",
                "Polissage surface",
                "Retouche peinture"
            ],
            "sur_controle": [
                "Contrôle 100% lot suspect",
                "Vérification dimensionnelle renforcée",
                "Contrôle redondant qualité",
                "Inspection visuelle complète"
            ],
            "non_conformite": [
                "Déviation procédure assemblage",
                "Paramètre machine hors plage",
                "Documentation manquante",
                "Traçabilité incomplète"
            ]
        }
        
        self.incident_categories = {
            "panne_mecanique": [
                "Rupture courroie transmission",
                "Défaillance roulement broche",
                "Casse outil usinage",
                "Fuite huile hydraulique",
                "Usure excessive glissières"
            ],
            "panne_electrique": [
                "Disjonction circuit commande",
                "Défaut variateur vitesse",
                "Capteur en court-circuit",
                "Problème carte électronique",
                "Surchauffe moteur"
            ],
            "defaut_qualite": [
                "Lot non-conforme détecté",
                "Dérive dimensionnelle progressive",
                "Contamination process",
                "Défaut répétitif sur série",
                "Non-conformité client"
            ],
            "probleme_logistique": [
                "Rupture stock matière première",
                "Retard livraison composant",
                "Erreur référence fourniture",
                "Sur-stock encombrant",
                "Mauvais routage pièces"
            ],
            "erreur_operateur": [
                "Erreur réglage paramètres",
                "Oubli opération",
                "Mauvais montage outil",
                "Non-respect procédure",
                "Confusion références produits"
            ]
        }
    
    def generate_production_logs(self, num_days: int = 30, num_logs: int = 500) -> List[dict]:
        """
        Génère des logs de production avec patterns intentionnels.
        
        Args:
            num_days: Nombre de jours à couvrir
            num_logs: Nombre total de logs à générer
            
        Returns:
            Liste de dictionnaires représentant les logs
        """
        logs = []
        start_date = datetime.now() - timedelta(days=num_days)
        
        for _ in range(num_logs):
            # Date aléatoire sur la période
            day_offset = random.randint(0, num_days - 1)
            hour = random.randint(6, 22)
            minute = random.randint(0, 59)
            timestamp = start_date + timedelta(days=day_offset, hours=hour, minutes=minute)
            
            # Déterminer le shift
            if 6 <= hour < 14:
                shift = "matin"
            elif 14 <= hour < 22:
                shift = "apres-midi"
            else:
                shift = "nuit"
            
            # Sélection machine avec biais intentionnel
            if random.random() < 0.4:  # 40% sur CNC-01 (machine problématique)
                machine_id = "CNC-01"
            else:
                machine_id = random.choice(self.machines)
            
            # Type d'événement avec distribution réaliste
            rand = random.random()
            if rand < 0.70:
                event_type = "normal"
                duration = random.uniform(15, 60)
            elif rand < 0.85:
                event_type = "micro_arret"
                duration = random.uniform(1, 5)
                # CNC-01 a 3x plus de micro-arrêts
                if machine_id == "CNC-01" and random.random() < 0.7:
                    pass  # Garder le micro_arret
            elif rand < 0.95:
                event_type = "arret"
                duration = random.uniform(5, 120)
                # Les nuits ont plus d'arrêts
                if shift == "nuit":
                    duration *= 1.5
            else:
                event_type = "ralentissement"
                duration = random.uniform(30, 180)
                # PRESS-01 a plus de ralentissements
                if machine_id == "PRESS-01" and random.random() < 0.6:
                    duration *= 1.3
            
            # Assignation ligne
            if machine_id in ["CNC-01", "CNC-02"]:
                line_id = "L1"
            elif machine_id in ["PRESS-01", "PRESS-02"]:
                line_id = "L2"
            else:
                line_id = "L3"
            
            log = {
                "timestamp": timestamp.isoformat(),
                "machine_id": machine_id,
                "event_type": event_type,
                "duration_minutes": round(duration, 2),
                "description": random.choice(self.event_descriptions[event_type]),
                "line_id": line_id,
                "operator_id": f"OP{random.randint(1, 15):03d}",
                "shift": shift
            }
            logs.append(log)
        
        # Trier par timestamp
        logs.sort(key=lambda x: x["timestamp"])
        return logs
    
    def generate_quality_records(self, num_records: int = 200) -> List[dict]:
        """
        Génère des enregistrements qualité avec corrélations.
        
        Args:
            num_records: Nombre d'enregistrements à générer
            
        Returns:
            Liste de dictionnaires représentant les enregistrements qualité
        """
        records = []
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(num_records):
            day_offset = random.randint(0, 29)
            hour = random.randint(6, 22)
            timestamp = start_date + timedelta(days=day_offset, hours=hour, minutes=random.randint(0, 59))
            
            # Type de défaut avec distribution
            rand = random.random()
            if rand < 0.40:
                defect_type = "rebut"
            elif rand < 0.75:
                defect_type = "retouche"
            elif rand < 0.90:
                defect_type = "sur_controle"
            else:
                defect_type = "non_conformite"
            
            # Sévérité distribuée
            sev_rand = random.random()
            if sev_rand < 0.30:
                severity = "low"
            elif sev_rand < 0.70:
                severity = "medium"
            elif sev_rand < 0.90:
                severity = "high"
            else:
                severity = "critical"
            
            # Machine avec biais (CNC-01 génère plus de rebuts)
            if defect_type == "rebut" and random.random() < 0.5:
                machine_id = "CNC-01"
            else:
                machine_id = random.choice(self.machines)
            
            # Ligne associée
            if machine_id in ["CNC-01", "CNC-02"]:
                line_id = "L1"
            elif machine_id in ["PRESS-01", "PRESS-02"]:
                line_id = "L2"
            else:
                line_id = "L3"
            
            record = {
                "timestamp": timestamp.isoformat(),
                "product_id": f"PROD{random.randint(1000, 9999)}",
                "defect_type": defect_type,
                "quantity": random.randint(1, 20),
                "severity": severity,
                "description": random.choice(self.defect_descriptions[defect_type]),
                "machine_id": machine_id,
                "line_id": line_id
            }
            records.append(record)
        
        records.sort(key=lambda x: x["timestamp"])
        return records
    
    def generate_incident_reports(self, num_incidents: int = 80) -> List[dict]:
        """
        Génère des rapports d'incidents.
        
        Args:
            num_incidents: Nombre d'incidents à générer
            
        Returns:
            Liste de dictionnaires représentant les incidents
        """
        incidents = []
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(num_incidents):
            day_offset = random.randint(0, 29)
            hour = random.randint(6, 22)
            timestamp = start_date + timedelta(days=day_offset, hours=hour, minutes=random.randint(0, 59))
            
            category = random.choice(list(self.incident_categories.keys()))
            impact_level = random.choices([1, 2, 3, 4, 5], weights=[0.15, 0.25, 0.35, 0.20, 0.05])[0]
            
            # Temps de résolution selon impact
            if impact_level <= 2:
                resolution_time = random.uniform(0.5, 4)
            elif impact_level == 3:
                resolution_time = random.uniform(2, 12)
            elif impact_level == 4:
                resolution_time = random.uniform(8, 24)
            else:
                resolution_time = random.uniform(24, 48)
            
            machine_id = random.choice(self.machines)
            if machine_id in ["CNC-01", "CNC-02"]:
                line_id = "L1"
            elif machine_id in ["PRESS-01", "PRESS-02"]:
                line_id = "L2"
            else:
                line_id = "L3"
            
            description = random.choice(self.incident_categories[category])
            
            # Génération d'une cause racine réaliste
            root_causes = {
                "panne_mecanique": [
                    "Manque de lubrification",
                    "Usure normale en fin de vie",
                    "Surcharge mécanique",
                    "Défaut de conception"
                ],
                "panne_electrique": [
                    "Vieillissement composants",
                    "Surtension réseau",
                    "Problème câblage",
                    "Humidité excessive"
                ],
                "defaut_qualite": [
                    "Dérive paramètres process",
                    "Matière première non-conforme",
                    "Usure outil de coupe",
                    "Erreur opérateur"
                ],
                "probleme_logistique": [
                    "Mauvaise planification",
                    "Défaillance fournisseur",
                    "Erreur système informatique",
                    "Communication insuffisante"
                ],
                "erreur_operateur": [
                    "Formation insuffisante",
                    "Procédure peu claire",
                    "Fatigue fin de shift",
                    "Distraction momentanée"
                ]
            }
            
            incident = {
                "timestamp": timestamp.isoformat(),
                "incident_id": f"INC{i+1:04d}",
                "category": category,
                "description": description,
                "impact_level": impact_level,
                "resolution_time_hours": round(resolution_time, 1),
                "root_cause": random.choice(root_causes[category]),
                "machine_id": machine_id,
                "line_id": line_id
            }
            incidents.append(incident)
        
        incidents.sort(key=lambda x: x["timestamp"])
        return incidents
    
    def save_to_csv(self, data: List[dict], filename: str):
        """
        Sauvegarde les données dans un fichier CSV.
        
        Args:
            data: Liste de dictionnaires à sauvegarder
            filename: Nom du fichier (avec extension .csv)
        """
        if not data:
            print(f"⚠️  Aucune donnée à sauvegarder pour {filename}")
            return
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        print(f"✅ {filename} généré : {len(data)} enregistrements")
    
    def generate_all(self):
        """Génère tous les fichiers de données synthétiques."""
        print("🏭 Génération des données synthétiques...")
        print(f"📁 Répertoire de sortie : {self.output_dir.absolute()}\n")
        
        # Production logs
        production_logs = self.generate_production_logs(num_days=30, num_logs=500)
        self.save_to_csv(production_logs, "production_logs.csv")
        
        # Quality records
        quality_records = self.generate_quality_records(num_records=200)
        self.save_to_csv(quality_records, "quality_records.csv")
        
        # Incident reports
        incident_reports = self.generate_incident_reports(num_incidents=80)
        self.save_to_csv(incident_reports, "incident_reports.csv")
        
        print("\n✨ Génération terminée avec succès!")
        print(f"\n📊 Résumé des données générées :")
        print(f"   - Logs de production : {len(production_logs)} entrées sur 30 jours")
        print(f"   - Enregistrements qualité : {len(quality_records)} entrées")
        print(f"   - Rapports d'incidents : {len(incident_reports)} entrées")
        print(f"\n💡 Patterns intentionnels intégrés :")
        print(f"   - CNC-01 : 3x plus de micro-arrêts (pattern caché)")
        print(f"   - Shift nuit : arrêts plus longs")
        print(f"   - PRESS-01 : ralentissements récurrents")
        print(f"   - CNC-01 : génère plus de rebuts qualité")


def main():
    """Point d'entrée principal du générateur."""
    generator = SyntheticDataGenerator()
    generator.generate_all()


if __name__ == "__main__":
    main()
