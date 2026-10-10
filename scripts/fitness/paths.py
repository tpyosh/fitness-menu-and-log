"""Canonical repository paths shared by the command-line tools."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRESCRIPTIONS = ROOT / "data/menus/prescriptions.json"
TRIALS = ROOT / "data/menus/active-trials.json"
CURRENT_MENUS = ROOT / "data/menus/current-menus.md"
DESIGN_PHILOSOPHY = ROOT / "data/menus/design-philosophy.md"
SESSIONS_CSV = ROOT / "data/logs/structured/sessions.csv"
SESSIONS_YAML = ROOT / "data/logs/structured/sessions.yaml"
REVIEWS_DIR = ROOT / "data/logs/reviews"
REQUEST_STATE = REVIEWS_DIR / "review-request-state.json"
REVIEW_ASSESSMENT = REVIEWS_DIR / "current-assessment.md"
REVIEW_BACKLOG = REVIEWS_DIR / "backlog.md"
PROMPT_TEMPLATE = ROOT / "data/prompts/garmin-coach-review-request.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)
