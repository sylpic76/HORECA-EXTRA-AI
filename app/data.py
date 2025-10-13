"""Sample in-memory data for the HORECA Extra AI application."""
from __future__ import annotations

from datetime import date
from typing import Dict, List, TypedDict


class Shift(TypedDict):
    label: str
    start: str
    end: str


class Job(TypedDict):
    id: str
    title: str
    location: str
    venue_name: str
    start_date: date
    end_date: date
    shifts: List[Shift]
    requirements: List[str]


class Candidate(TypedDict):
    id: str
    name: str
    locations: List[str]
    skills: List[str]
    availability: List[Dict[str, date]]  # each dict has start and end keys
    preferred_shifts: List[str]


jobs: List[Job] = [
    {
        "id": "job-1",
        "title": "Serveur soirée cocktail",
        "location": "Paris",
        "venue_name": "Le Toit de Paris",
        "start_date": date(2024, 7, 12),
        "end_date": date(2024, 7, 12),
        "shifts": [
            {"label": "Soir", "start": "18:00", "end": "23:30"},
        ],
        "requirements": ["service en salle", "anglais"],
    },
    {
        "id": "job-2",
        "title": "Chef de partie brunch",
        "location": "Lyon",
        "venue_name": "Café Bellecour",
        "start_date": date(2024, 7, 14),
        "end_date": date(2024, 7, 15),
        "shifts": [
            {"label": "Matin", "start": "07:00", "end": "13:00"},
        ],
        "requirements": ["cuisine", "gestion du chaud"],
    },
    {
        "id": "job-3",
        "title": "Barman événement privé",
        "location": "Marseille",
        "venue_name": "Villa du Pharo",
        "start_date": date(2024, 7, 18),
        "end_date": date(2024, 7, 18),
        "shifts": [
            {"label": "Soir", "start": "17:00", "end": "01:00"},
        ],
        "requirements": ["cocktails", "service rapide"],
    },
]


candidates: List[Candidate] = [
    {
        "id": "cand-1",
        "name": "Lina",
        "locations": ["Paris", "Versailles"],
        "skills": ["service en salle", "anglais", "encaissement"],
        "availability": [
            {"start": date(2024, 7, 10), "end": date(2024, 7, 20)}
        ],
        "preferred_shifts": ["Jour", "Soir"],
    },
    {
        "id": "cand-2",
        "name": "Hugo",
        "locations": ["Lyon"],
        "skills": ["cuisine", "gestion du chaud", "dressage"],
        "availability": [
            {"start": date(2024, 7, 12), "end": date(2024, 7, 16)}
        ],
        "preferred_shifts": ["Matin"],
    },
    {
        "id": "cand-3",
        "name": "Aya",
        "locations": ["Marseille", "Aix-en-Provence"],
        "skills": ["cocktails", "service rapide", "anglais"],
        "availability": [
            {"start": date(2024, 7, 18), "end": date(2024, 7, 22)}
        ],
        "preferred_shifts": ["Soir"],
    },
]
