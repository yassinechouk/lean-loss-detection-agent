"""
Prétraitement et agrégation des données pour l'analyse LLM.
"""
from typing import List, Dict, Any
from collections import defaultdict, Counter
from datetime import datetime
from src.models.schemas import ProductionLog, QualityRecord, IncidentReport


class DataPreprocessor:
    """Préprocesseur de données industrielles pour l'analyse."""
    
    def compute_statistics(self, production_logs: List[ProductionLog]) -> Dict[str, Any]:
        """
        Calcule des statistiques agrégées sur les logs de production.
        
        Args:
            production_logs: Liste des logs de production
            
        Returns:
            Dictionnaire de statistiques
        """
        if not production_logs:
            return {}
        
        stats = {
            "total_logs": len(production_logs),
            "by_event_type": defaultdict(int),
            "by_machine": defaultdict(lambda: {
                "total_events": 0,
                "total_downtime_hours": 0,
                "micro_arrets_count": 0,
                "arrets_count": 0,
                "ralentissements_count": 0
            }),
            "by_shift": defaultdict(lambda: {"count": 0, "total_downtime_hours": 0}),
            "by_line": defaultdict(lambda: {"count": 0, "total_downtime_hours": 0})
        }
        
        total_downtime_minutes = 0
        micro_arret_count = 0
        arret_count = 0
        
        for log in production_logs:
            # Comptage par type
            stats["by_event_type"][log.event_type] += 1
            
            # Statistiques par machine
            machine_stats = stats["by_machine"][log.machine_id]
            machine_stats["total_events"] += 1
            
            if log.event_type != "normal":
                machine_stats["total_downtime_hours"] += log.duration_minutes / 60
                total_downtime_minutes += log.duration_minutes
            
            if log.event_type == "micro_arret":
                machine_stats["micro_arrets_count"] += 1
                micro_arret_count += 1
            elif log.event_type == "arret":
                machine_stats["arrets_count"] += 1
                arret_count += 1
            elif log.event_type == "ralentissement":
                machine_stats["ralentissements_count"] += 1
            
            # Par shift
            if log.event_type != "normal":
                stats["by_shift"][log.shift]["count"] += 1
                stats["by_shift"][log.shift]["total_downtime_hours"] += log.duration_minutes / 60
            
            # Par ligne
            if log.event_type != "normal":
                stats["by_line"][log.line_id]["count"] += 1
                stats["by_line"][log.line_id]["total_downtime_hours"] += log.duration_minutes / 60
        
        # Calculs globaux
        stats["total_downtime_hours"] = total_downtime_minutes / 60
        stats["micro_arret_count"] = micro_arret_count
        stats["arret_count"] = arret_count
        
        # MTBF approximatif (Mean Time Between Failures)
        if arret_count > 0:
            # Supposons une période de 30 jours
            stats["approx_mtbf_hours"] = (30 * 24) / arret_count
        
        return dict(stats)
    
    def detect_patterns(
        self, 
        production_logs: List[ProductionLog], 
        quality_records: List[QualityRecord]
    ) -> List[str]:
        """
        Détecte des patterns simples dans les données.
        
        Args:
            production_logs: Logs de production
            quality_records: Enregistrements qualité
            
        Returns:
            Liste de patterns identifiés (descriptions textuelles)
        """
        patterns = []
        
        # Pattern 1: Machines avec taux élevé de micro-arrêts
        micro_arrets_by_machine = defaultdict(int)
        for log in production_logs:
            if log.event_type == "micro_arret":
                micro_arrets_by_machine[log.machine_id] += 1
        
        avg_micro_arrets = sum(micro_arrets_by_machine.values()) / max(len(micro_arrets_by_machine), 1)
        for machine, count in micro_arrets_by_machine.items():
            if count > avg_micro_arrets * 1.5:
                patterns.append(
                    f"⚠️  Machine {machine} : taux de micro-arrêts élevé ({count} occurrences, "
                    f"soit {count/avg_micro_arrets:.1f}x la moyenne)"
                )
        
        # Pattern 2: Shifts problématiques
        downtime_by_shift = defaultdict(float)
        for log in production_logs:
            if log.event_type in ["arret", "micro_arret"]:
                downtime_by_shift[log.shift] += log.duration_minutes
        
        if downtime_by_shift:
            avg_downtime = sum(downtime_by_shift.values()) / len(downtime_by_shift)
            for shift, downtime in downtime_by_shift.items():
                if downtime > avg_downtime * 1.3:
                    patterns.append(
                        f"🌙 Shift {shift} : temps d'arrêt supérieur ({downtime/60:.1f}h vs moyenne {avg_downtime/60:.1f}h)"
                    )
        
        # Pattern 3: Corrélation machines/défauts qualité
        defects_by_machine = defaultdict(int)
        for record in quality_records:
            if record.defect_type in ["rebut", "non_conformite"]:
                defects_by_machine[record.machine_id] += record.quantity
        
        if defects_by_machine:
            avg_defects = sum(defects_by_machine.values()) / len(defects_by_machine)
            for machine, count in defects_by_machine.items():
                if count > avg_defects * 1.5:
                    patterns.append(
                        f"❌ Machine {machine} : taux de défauts élevé ({count} pièces rebutées/NC)"
                    )
        
        # Pattern 4: Description des événements récurrents
        description_counter = Counter()
        for log in production_logs:
            if log.event_type in ["micro_arret", "arret"]:
                description_counter[log.description] += 1
        
        for description, count in description_counter.most_common(5):
            if count >= 10:
                patterns.append(
                    f"🔁 Événement récurrent : '{description}' ({count} occurrences)"
                )
        
        return patterns
    
    def prepare_for_analysis(
        self, 
        production_logs: List[ProductionLog],
        quality_records: List[QualityRecord],
        incident_reports: List[IncidentReport]
    ) -> str:
        """
        Prépare un résumé textuel structuré pour l'analyse LLM.
        
        Args:
            production_logs: Logs de production
            quality_records: Enregistrements qualité
            incident_reports: Rapports d'incidents
            
        Returns:
            Texte structuré prêt pour l'analyse
        """
        # Calculer les statistiques
        stats = self.compute_statistics(production_logs)
        patterns = self.detect_patterns(production_logs, quality_records)
        
        # Construction du résumé
        summary = []
        summary.append("=" * 80)
        summary.append("RÉSUMÉ DES DONNÉES DE PRODUCTION - ANALYSE LEAN")
        summary.append("=" * 80)
        summary.append("")
        
        # Section 1: Vue d'ensemble
        summary.append("📊 VUE D'ENSEMBLE")
        summary.append("-" * 80)
        summary.append(f"Période analysée : ~30 jours")
        summary.append(f"Total d'événements : {stats.get('total_logs', 0)}")
        summary.append(f"Temps d'arrêt total : {stats.get('total_downtime_hours', 0):.1f} heures")
        summary.append(f"Enregistrements qualité : {len(quality_records)}")
        summary.append(f"Incidents rapportés : {len(incident_reports)}")
        summary.append("")
        
        # Section 2: Répartition des événements
        summary.append("📈 RÉPARTITION DES ÉVÉNEMENTS")
        summary.append("-" * 80)
        event_types = stats.get('by_event_type', {})
        for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_logs'] * 100) if stats['total_logs'] > 0 else 0
            summary.append(f"  {event_type.upper():20s} : {count:4d} ({percentage:5.1f}%)")
        summary.append("")
        
        # Section 3: Analyse par machine
        summary.append("🔧 ANALYSE PAR MACHINE")
        summary.append("-" * 80)
        by_machine = stats.get('by_machine', {})
        for machine_id, machine_stats in sorted(by_machine.items()):
            summary.append(f"\n{machine_id}:")
            summary.append(f"  - Événements totaux : {machine_stats['total_events']}")
            summary.append(f"  - Temps d'arrêt : {machine_stats['total_downtime_hours']:.1f}h")
            summary.append(f"  - Micro-arrêts : {machine_stats['micro_arrets_count']}")
            summary.append(f"  - Arrêts : {machine_stats['arrets_count']}")
            summary.append(f"  - Ralentissements : {machine_stats['ralentissements_count']}")
        summary.append("")
        
        # Section 4: Analyse par shift
        summary.append("🕐 ANALYSE PAR SHIFT")
        summary.append("-" * 80)
        by_shift = stats.get('by_shift', {})
        for shift, shift_stats in sorted(by_shift.items()):
            summary.append(f"  {shift.capitalize():15s} : {shift_stats['count']} événements, "
                         f"{shift_stats['total_downtime_hours']:.1f}h d'arrêt")
        summary.append("")
        
        # Section 5: Patterns détectés
        if patterns:
            summary.append("🔍 PATTERNS DÉTECTÉS")
            summary.append("-" * 80)
            for pattern in patterns:
                summary.append(f"  {pattern}")
            summary.append("")
        
        # Section 6: Échantillon de données qualité
        summary.append("📋 DONNÉES QUALITÉ (échantillon)")
        summary.append("-" * 80)
        defect_type_count = Counter([r.defect_type for r in quality_records])
        severity_count = Counter([r.severity for r in quality_records])
        
        summary.append(f"Par type de défaut :")
        for defect_type, count in defect_type_count.most_common():
            summary.append(f"  {defect_type:20s} : {count}")
        
        summary.append(f"\nPar sévérité :")
        for severity, count in severity_count.most_common():
            summary.append(f"  {severity:20s} : {count}")
        summary.append("")
        
        # Section 7: Échantillon d'incidents
        summary.append("🚨 INCIDENTS (échantillon)")
        summary.append("-" * 80)
        incident_category_count = Counter([i.category for i in incident_reports])
        for category, count in incident_category_count.most_common():
            summary.append(f"  {category:25s} : {count}")
        summary.append("")
        
        # Section 8: Échantillon de logs détaillés
        summary.append("📝 ÉCHANTILLON DE LOGS DÉTAILLÉS")
        summary.append("-" * 80)
        
        # Top 10 événements problématiques
        problem_logs = [log for log in production_logs if log.event_type in ["arret", "micro_arret"]]
        problem_logs.sort(key=lambda x: x.duration_minutes, reverse=True)
        
        for log in problem_logs[:10]:
            summary.append(f"  [{log.timestamp.strftime('%Y-%m-%d %H:%M')}] "
                         f"{log.machine_id} | {log.event_type.upper()} | "
                         f"{log.duration_minutes:.1f}min | {log.description}")
        
        summary.append("")
        summary.append("=" * 80)
        
        return "\n".join(summary)
