from __future__ import annotations
import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
from datetime import datetime
import re
import requests
from requests.adapters import HTTPAdapter, Retry
from dotenv import load_dotenv

load_dotenv()

# Environment configuration
URL = os.getenv("URL", "mts-prism.com")
PORT = int(os.getenv("PORT", "8082"))
TEAM_API_CODE = os.getenv("TEAM_API_CODE")

if not TEAM_API_CODE:
    raise RuntimeError("TEAM_API_CODE is missing. Put it in .env")

logger = logging.getLogger("prism")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(handler)

def _session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.4,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=["GET", "POST"],
    )
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.headers.update({"X-API-Code": TEAM_API_CODE})
    return s

def _url(path: str) -> str:
    return f"http://{URL}:{PORT}/{path.lstrip('/')}"

def send_get_request(path: str) -> Tuple[bool, str]:
    with _session() as s:
        r = s.get(_url(path), timeout=10)
    if r.status_code != 200:
        return False, f"GET {path} -> {r.status_code}: {r.text}"
    return True, r.text

def send_post_request(path: str, data: Any = None) -> Tuple[bool, str]:
    with _session() as s:
        r = s.post(_url(path), data=json.dumps(data), headers={"Content-Type":"application/json"}, timeout=15)
    if r.status_code != 200:
        return False, f"POST {path} -> {r.status_code}: {r.text}"
    return True, r.text

def get_context() -> Tuple[bool, str]:
    return send_get_request("/request")

def get_my_current_information() -> Tuple[bool, str]:
    return send_get_request("/info")

def normalize_date(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        pass
    clean = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)
    try:
        return datetime.strptime(clean, "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Unsupported date format: {date_str}")

@dataclass
class ParsedContext:
    name: str | None
    age: int | None
    gender: str | None
    budget: int | None
    salary: int | None
    start_date: str | None
    end_date: str | None

def context_to_tuple(context: str) -> ParsedContext:
    context_dict = json.loads(context)
    message = context_dict.get("message", "")

    name_match = re.match(r"([A-Z][a-z]+ [A-Z][a-z]+)", message)
    name = name_match.group(1) if name_match else None

    age_match = re.search(r"(\d+)(?:-?\s*)years?(?:-?\s*)old", message)
    age = int(age_match.group(1)) if age_match else None

    budget_match = re.search(r"budget of \$([\d,]+)", message)
    budget = int(budget_match.group(1).replace(",", "")) if budget_match else None

    pattern = r"((?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}(?:st|nd|rd|th)?,\s\d{4})|(\d{4}-\d{2}-\d{2})"
    matches = re.findall(pattern, message)
    dates = [d for tup in matches for d in tup if d]
    start_date = normalize_date(dates[0]) if len(dates) > 0 else None
    end_date = normalize_date(dates[1]) if len(dates) > 1 else None

    gender = None
    gmatch = re.search(r"\b(he|she|him|her)\b", message, re.IGNORECASE)
    if gmatch:
        pron = gmatch.group(0).lower()
        gender = "male" if pron in ("he","him") else ("female" if pron in ("she","her") else None)

    sal_match = re.search(r"(?i)(?:salary|income|pay|wage)[^\d]*(\d+)", message, re.IGNORECASE)
    salary = int(sal_match.group(1)) if sal_match else None

    parsed = ParsedContext(name, age, gender, budget, salary, start_date, end_date)
    logger.info("Parsed context: %s", parsed)
    return parsed

def send_portfolio(weighted_stocks: List[Tuple[str, int]]) -> Tuple[bool, str]:
    """
    weighted_stocks: [("AAPL", 3), ("MSFT", 2)]
    """
    payload = [{"ticker": t, "quantity": q} for t, q in weighted_stocks]
    return send_post_request("/submit", data=payload)
