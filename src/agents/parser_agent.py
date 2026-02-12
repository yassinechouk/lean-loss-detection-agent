"""
Agent Parser pour l'extraction des pertes cachées à partir des données de production.
Supporte le mode LLM (OpenAI) et le mode fallback heuristique.
"""
import json
import uuid
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter

from src.utils.config import get_settings
from src.prompts.templates import PARSER_SYSTEM_PROMPT, PARSER_HUMAN_TEMPLATE


class ParserAgent:
    """Agent d'extraction des pertes cachées."""
    
    def __init__(self, llm=None):
        """
        Initialise l'agent parser.
        
        Args:
            llm: Instance LLM optionnelle (ChatOpenAI). Si None, utilise la config.
        """
        self.settings = get_settings()
        self.llm = llm
        self.chain = None
        
        # Si une clé API est configurée et pas de LLM fourni, créer un LLM
        if self.llm is None and self.settings.is_api_configured():
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model=self.settings.llm_model,
                    temperature=self.settings.llm_temperature,
                    api_key=self.settings.openai_api_key
                )
                self._create_chain()
            except Exception as e:
                print(f"⚠️  Impossible d'initialiser le LLM : {e}")
                print("   → Mode fallback heuristique activé")
                self.llm = None
    
    def _create_chain(self):
        """Crée la chaîne LangChain pour l'analyse."""
        if self.llm is None:
            return
        
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import JsonOutputParser
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", PARSER_SYSTEM_PROMPT),
                ("human", PARSER_HUMAN_TEMPLATE)
            ])
            
            self.chain = prompt | self.llm | JsonOutputParser()
        except Exception as e:
            print(f"⚠️  Erreur lors de la création de la chaîne : {e}")
            self.llm = None
            self.chain = None
    
    def parse(self, production_data: str) -> List[Dict[str, Any]]:
        """
        Analyse les données de production et retourne les pertes détectées.
        
        Args:
            production_data: Données de production formatées en texte
            
        Returns:
            Liste de dictionnaires représentant les pertes détectées
        """
        # Mode LLM si disponible
        if self.chain is not None:
            try:
                result = self.chain.invoke({"production_data": production_data})
                losses = result.get("detected_losses", [])
                print(f"✅ Mode LLM : {len(losses)} pertes détectées")
                return losses
            except Exception as e:
                print(f"⚠️  Erreur LLM : {e}")
                print("   → Basculement vers mode heuristique")
        
        # Mode fallback heuristique
        return self._heuristic_parse(production_data)
    
    def _heuristic_parse(self, production_data: str) -> List[Dict[str, Any]]:
        """
        Mode fallback : analyse heuristique basée sur des règles simples.
        
        Args:
            production_data: Données de production formatées
            
        Returns:
            Liste de pertes détectées
        """
        print("🔧 Mode heuristique activé (sans API)")
        
        detected_losses = []
        
        # Extraire les informations du texte
        lines = production_data.split('\n')
        
        # Règle 1: Détecter les micro-arrêts excessifs par machine
        micro_arret_pattern = {}
        arret_pattern = {}
        downtime_by_machine = defaultdict(float)
        
        for line in lines:
            if "Micro-arrêts :" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    try:
                        count = int(parts[1].strip())
                        # Chercher le nom de la machine dans les lignes précédentes
                        machine_name = self._extract_machine_name_from_context(lines, line)
                        if machine_name:
                            micro_arret_pattern[machine_name] = count
                    except:
                        pass
            
            if "Temps d'arrêt :" in line and "h" in line:
                try:
                    machine_name = self._extract_machine_name_from_context(lines, line)
                    hours_str = line.split(":")[1].strip().replace("h", "")
                    hours = float(hours_str)
                    if machine_name:
                        downtime_by_machine[machine_name] = hours
                except:
                    pass
        
        # Générer des pertes pour micro-arrêts excessifs (> 30)
        for machine, count in micro_arret_pattern.items():
            if count > 30:
                loss_id = f"LOSS_{str(uuid.uuid4())[:8]}"
                detected_losses.append({
                    "loss_id": loss_id,
                    "title": f"Micro-arrêts fréquents sur {machine}",
                    "description": f"La machine {machine} présente {count} micro-arrêts sur la période, "
                                 f"ce qui indique un problème récurrent nécessitant investigation. "
                                 f"Ces arrêts courts mais répétés génèrent des pertes de temps d'attente.",
                    "frequency": count,
                    "total_duration_hours": count * 0.05,  # Estimation : ~3min par micro-arrêt
                    "affected_machines": [machine],
                    "affected_lines": [self._guess_line_from_machine(machine)],
                    "pattern": f"Micro-arrêts répétitifs ({count} occurrences)",
                    "severity": "high" if count > 50 else "medium",
                    "confidence_score": 0.75
                })
        
        # Règle 2: Temps d'arrêt élevé (> 8h sur la période)
        for machine, hours in downtime_by_machine.items():
            if hours > 8.0:
                loss_id = f"LOSS_{str(uuid.uuid4())[:8]}"
                detected_losses.append({
                    "loss_id": loss_id,
                    "title": f"Temps d'arrêt élevé sur {machine}",
                    "description": f"La machine {machine} cumule {hours:.1f} heures d'arrêt sur la période. "
                                 f"Cela représente une perte de disponibilité significative qui impacte la production.",
                    "frequency": 1,  # Perte globale
                    "total_duration_hours": hours,
                    "affected_machines": [machine],
                    "affected_lines": [self._guess_line_from_machine(machine)],
                    "pattern": f"Cumul d'arrêts important ({hours:.1f}h)",
                    "severity": "critical" if hours > 15 else "high",
                    "confidence_score": 0.85
                })
        
        # Règle 3: Shift problématique (nuit)
        if "nuit" in production_data.lower() and ("arrêt" in production_data.lower() or "h d'arrêt" in production_data.lower()):
            # Chercher les statistiques par shift
            for i, line in enumerate(lines):
                if "nuit" in line.lower() and "h d'arrêt" in line.lower():
                    try:
                        # Extraire les heures d'arrêt
                        parts = line.split(":")
                        if len(parts) >= 2:
                            hours_part = parts[-1].strip().split("h")[0].strip()
                            hours = float(hours_part.split()[-1])
                            
                            if hours > 5.0:  # Seuil pour shift nuit
                                loss_id = f"LOSS_{str(uuid.uuid4())[:8]}"
                                detected_losses.append({
                                    "loss_id": loss_id,
                                    "title": "Problèmes récurrents shift de nuit",
                                    "description": f"Le shift de nuit présente un temps d'arrêt anormal ({hours:.1f}h). "
                                                 f"Cela peut indiquer un manque de supervision, des problèmes de compétences "
                                                 f"ou des conditions de travail défavorables.",
                                    "frequency": 1,
                                    "total_duration_hours": hours,
                                    "affected_machines": [],
                                    "affected_lines": [],
                                    "pattern": "Arrêts plus longs en shift nuit",
                                    "severity": "medium",
                                    "confidence_score": 0.70
                                })
                                break
                    except:
                        pass
        
        # Règle 4: Défauts qualité (rebuts)
        if "rebut" in production_data.lower():
            for line in lines:
                if "rebut" in line.lower() and ":" in line:
                    try:
                        count = int(line.split(":")[-1].strip())
                        if count > 30:  # Seuil de rebuts
                            loss_id = f"LOSS_{str(uuid.uuid4())[:8]}"
                            detected_losses.append({
                                "loss_id": loss_id,
                                "title": "Taux de rebut élevé",
                                "description": f"Le nombre de rebuts ({count} pièces) est anormalement élevé. "
                                             f"Cela indique des problèmes de qualité process ou de conformité matière "
                                             f"qui génèrent des pertes financières directes.",
                                "frequency": count,
                                "total_duration_hours": count * 0.5,  # Estimation du temps perdu
                                "affected_machines": [],
                                "affected_lines": [],
                                "pattern": "Rebuts répétés",
                                "severity": "high",
                                "confidence_score": 0.80
                            })
                            break
                    except:
                        pass
        
        # Règle 5: Sur-contrôle
        if "sur_controle" in production_data.lower():
            for line in lines:
                if "sur_controle" in line.lower() and ":" in line:
                    try:
                        count = int(line.split(":")[-1].strip())
                        if count > 15:  # Seuil de sur-contrôle
                            loss_id = f"LOSS_{str(uuid.uuid4())[:8]}"
                            detected_losses.append({
                                "loss_id": loss_id,
                                "title": "Sur-contrôle qualité",
                                "description": f"Des contrôles qualité excessifs ({count} occurrences) sont effectués. "
                                             f"Ces contrôles peuvent être redondants ou dépasser les exigences, "
                                             f"générant du temps perdu sans valeur ajoutée.",
                                "frequency": count,
                                "total_duration_hours": count * 0.25,  # Estimation : 15min par contrôle
                                "affected_machines": [],
                                "affected_lines": [],
                                "pattern": "Contrôles redondants",
                                "severity": "medium",
                                "confidence_score": 0.65
                            })
                            break
                    except:
                        pass
        
        print(f"✅ Mode heuristique : {len(detected_losses)} pertes détectées")
        return detected_losses
    
    def _extract_machine_name_from_context(self, lines: List[str], current_line: str) -> Optional[str]:
        """Extrait le nom de machine du contexte."""
        idx = lines.index(current_line) if current_line in lines else -1
        if idx > 0:
            # Chercher dans les lignes précédentes
            for i in range(max(0, idx - 5), idx):
                line = lines[i]
                # Chercher un pattern de machine (ex: CNC-01, PRESS-01, etc.)
                for machine in ["CNC-01", "CNC-02", "PRESS-01", "PRESS-02", "ASSEMBLY-01"]:
                    if machine in line:
                        return machine
        return None
    
    def _guess_line_from_machine(self, machine_id: str) -> str:
        """Devine la ligne de production à partir du nom de machine."""
        if "CNC" in machine_id:
            return "L1"
        elif "PRESS" in machine_id:
            return "L2"
        else:
            return "L3"
