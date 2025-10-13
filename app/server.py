"""Flask server powering the HORECA Extra AI demo application."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template, request

from .data import Job, Candidate, candidates, jobs
from .matching import MatchResult, evaluate_candidate_for_job, suggest_candidates

app = Flask(__name__)


def serialize_job(job: Job) -> Dict[str, Any]:
    return {
        "id": job["id"],
        "title": job["title"],
        "location": job["location"],
        "venue_name": job["venue_name"],
        "start_date": job["start_date"].isoformat(),
        "end_date": job["end_date"].isoformat(),
        "shifts": job["shifts"],
        "requirements": job["requirements"],
    }


def serialize_candidate(candidate: Candidate) -> Dict[str, Any]:
    return {
        "id": candidate["id"],
        "name": candidate["name"],
        "locations": candidate["locations"],
        "skills": candidate["skills"],
        "availability": [
            {"start": period["start"].isoformat(), "end": period["end"].isoformat()}
            for period in candidate["availability"]
        ],
        "preferred_shifts": candidate["preferred_shifts"],
    }


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/jobs", methods=["GET"])
def list_jobs() -> Any:
    location = request.args.get("location")
    start = _parse_date(request.args.get("start"))
    end = _parse_date(request.args.get("end"))

    filtered: List[Job] = jobs
    if location:
        filtered = [job for job in filtered if job["location"].lower() == location.lower()]
    if start:
        filtered = [job for job in filtered if job["end_date"] >= start]
    if end:
        filtered = [job for job in filtered if job["start_date"] <= end]

    return jsonify([serialize_job(job) for job in filtered])


@app.route("/api/jobs", methods=["POST"])
def create_job() -> Any:
    payload: Dict[str, Any] = request.get_json(force=True)
    new_job: Job = {
        "id": payload.get("id") or f"job-{len(jobs) + 1}",
        "title": payload["title"],
        "location": payload["location"],
        "venue_name": payload.get("venue_name", "Établissement"),
        "start_date": _parse_date(payload["start_date"]),
        "end_date": _parse_date(payload["end_date"]),
        "shifts": payload.get("shifts", []),
        "requirements": payload.get("requirements", []),
    }
    if new_job["start_date"] is None or new_job["end_date"] is None:
        return jsonify({"error": "start_date et end_date sont obligatoires"}), 400

    jobs.append(new_job)
    return jsonify(serialize_job(new_job)), 201


@app.route("/api/candidates", methods=["GET"])
def list_candidates() -> Any:
    return jsonify([serialize_candidate(candidate) for candidate in candidates])


def _load_job(job_id: str) -> Optional[Job]:
    for job in jobs:
        if job["id"] == job_id:
            return job
    return None


def _load_candidate(candidate_id: str) -> Optional[Candidate]:
    for candidate in candidates:
        if candidate["id"] == candidate_id:
            return candidate
    return None


@app.route("/api/assistant/candidate", methods=["POST"])
def candidate_assistant() -> Any:
    payload: Dict[str, Any] = request.get_json(force=True)
    job_id = payload.get("job_id")
    job = _load_job(job_id)
    if not job:
        return jsonify({"error": "Mission introuvable"}), 404

    candidate_payload = {
        "id": "temp",
        "name": payload.get("name", "Candidat"),
        "locations": payload.get("locations", []),
        "skills": payload.get("skills", []),
        "availability": [
            {
                "start": _parse_date(payload.get("availability_start")) or job["start_date"],
                "end": _parse_date(payload.get("availability_end")) or job["end_date"],
            }
        ],
        "preferred_shifts": payload.get("preferred_shifts", []),
    }

    match = evaluate_candidate_for_job(candidate_payload, job)
    return jsonify({
        "match": match.is_match,
        "score": match.score,
        "messages": match.messages,
    })


@app.route("/api/assistant/employer", methods=["POST"])
def employer_assistant() -> Any:
    payload: Dict[str, Any] = request.get_json(force=True)
    job_id = payload.get("job_id")
    job = _load_job(job_id)
    if not job:
        return jsonify({"error": "Mission introuvable"}), 404

    candidate_id = payload.get("candidate_id")
    response: Dict[str, Any] = {"job": serialize_job(job)}

    if candidate_id:
        candidate = _load_candidate(candidate_id)
        if not candidate:
            return jsonify({"error": "Candidat introuvable"}), 404
        match = evaluate_candidate_for_job(candidate, job)
        response["candidate"] = serialize_candidate(candidate)
        response["match"] = {
            "is_match": match.is_match,
            "score": match.score,
            "messages": match.messages,
        }

    suggestions = [
        {
            "candidate": serialize_candidate(candidate),
            "match": {
                "is_match": match.is_match,
                "score": match.score,
                "messages": match.messages,
            },
        }
        for candidate, match in suggest_candidates(job, candidates)
    ]
    response["suggestions"] = suggestions[:3]
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
