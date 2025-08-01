from typing import Dict, List

from pydantic import BaseModel

from .common import MitreIdName


# models
class TechniquesByTactics(BaseModel):
    Dict[str, List[str]]


class AttacksCovergageStats(BaseModel):
    implemented_tactics: int
    implemented_techniques: int
    mitre_tactics: int = 14
    mitre_techniques: int
    tactics: Dict[str, int]


# Modèle représentant la réponse des stats pour le dashboard front
class DashboardStats(BaseModel):
    attacks_coverage: AttacksCovergageStats
    number_attacks: int
    number_recent_attacks: int
    number_scenarios: int
    number_recent_scenarios: int


class Subtechnique(BaseModel):
    id: str
    name: str
    parent_id: str
    tactics: List[MitreIdName]


class Technique(BaseModel):
    id: str
    name: str
    subtechniques: List[Subtechnique]
    tactics: List[MitreIdName]
