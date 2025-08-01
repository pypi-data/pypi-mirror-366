# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

from mantis_dataset_model.dataset_model import WorkerMitreData
from pydantic import BaseModel


class Worker(BaseModel):
    id: str
    name: str
    title: str
    title_fr: str
    description: str
    cve: List[Dict[str, str]]
    version: str
    side_effects: str
    topics: str
    repeatable: bool
    mitre_data: WorkerMitreData
    attack_mode: str


class UserActivity(BaseModel):
    id: int
    duration: float
    mitre_data: WorkerMitreData
    parameters: str
    title: str
    description: str
    task_id: str


class CustomAttack(BaseModel):
    id: int
    uid: str
    mitre_tag: str
    title: str
    status: str
    description: str
    command: str
    output: str


class Attack(BaseModel):
    id: str
    source_ids: List[str]
    worker: Optional[Worker] = None
    user_activity: Optional[UserActivity] = None
    custom_attack: Optional[CustomAttack] = None
    status: str
    started_date: datetime
    last_update: datetime
    target_nodes: List[str]
    output: List[str]
    infrastructure: List[str]
