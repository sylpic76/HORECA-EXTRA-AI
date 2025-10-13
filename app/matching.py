"""Rule-based assistants for candidates and employers."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, List, Tuple

from .data import Job, Candidate


def _date_range_overlap(
    job_start: date, job_end: date, availability_start: date, availability_end: date
) -> bool:
    return availability_start <= job_end and availability_end >= job_start


@dataclass
class MatchResult:
    is_match: bool
    score: float
    messages: List[str]


def evaluate_candidate_for_job(candidate: Candidate, job: Job) -> MatchResult:
    """Assess how well a candidate fits a job."""
    messages: List[str] = []
    score = 0.0

    if job["location"] in candidate["locations"]:
        messages.append("✅ Localisation compatible")
        score += 0.3
    else:
        messages.append(
            f"❌ Le job est à {job['location']} et {candidate['name']} intervient sur {', '.join(candidate['locations'])}."
        )

    availability_ok = any(
        _date_range_overlap(
            job["start_date"], job["end_date"], availability["start"], availability["end"]
        )
        for availability in candidate["availability"]
    )
    if availability_ok:
        messages.append("✅ Disponibilités compatibles")
        score += 0.3
    else:
        messages.append("❌ Le planning du candidat ne couvre pas les dates demandées")

    required_skills = set(job["requirements"])
    candidate_skills = set(skill.lower() for skill in candidate["skills"])
    matched_skills = [skill for skill in required_skills if skill.lower() in candidate_skills]
    if matched_skills:
        messages.append(
            "✅ Compétences clés : " + ", ".join(sorted(matched_skills))
        )
        score += 0.3 * len(matched_skills) / max(len(required_skills), 1)
    else:
        messages.append(
            "❌ Compétences requises manquantes : "
            + ", ".join(sorted(required_skills - set(matched_skills)))
        )

    preferred_shift_labels = set(shift.lower() for shift in candidate["preferred_shifts"])
    job_shift_labels = {shift["label"].lower() for shift in job["shifts"]}
    if preferred_shift_labels & job_shift_labels:
        messages.append("✅ Les horaires conviennent au candidat")
        score += 0.1
    else:
        messages.append("ℹ️ Les horaires sont à confirmer avec le candidat")

    is_match = score >= 0.5 and availability_ok
    if is_match:
        messages.insert(0, "🤝 Ce candidat est un excellent profil pour cette mission.")
    else:
        messages.insert(0, "⚠️ Des points restent à valider avant de confirmer la mission.")

    return MatchResult(is_match=is_match, score=round(score, 2), messages=messages)


def suggest_candidates(
    job: Job, candidates: Iterable[Candidate], min_score: float = 0.5
) -> List[Tuple[Candidate, MatchResult]]:
    """Return the best candidates for a job."""
    results = []
    for candidate in candidates:
        match = evaluate_candidate_for_job(candidate, job)
        if match.score >= min_score:
            results.append((candidate, match))
    return sorted(results, key=lambda item: item[1].score, reverse=True)
