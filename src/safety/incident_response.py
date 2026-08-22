"""Deterministic, source-linked next-step guidance for personal crime reports."""

from dataclasses import dataclass
import re


EMERGENCY_URL = "https://112.gov.in/"
CYBERCRIME_URL = "https://cybercrime.gov.in/"
NALSA_URL = "https://nalsa.gov.in/promoting-inclusive-legal-system/"


@dataclass(frozen=True)
class IncidentGuide:
    title: str
    urgency_notice: str | None
    steps: tuple[str, ...]
    resources: tuple[tuple[str, str], ...]


PERSONAL_PATTERNS = (
    r"\bhappened to me\b",
    r"\bwhat (?:should|can) i do\b",
    r"\bwhat do i do\b",
    r"\bhelp me\b",
    r"\bi (?:was|am|have been|got|lost|received|paid|sent)\b",
    r"\bmy (?:account|card|phone|money|wallet|child|daughter|son|home|house|car)\b",
    r"\b(?:someone|they|he|she) (?:threatened|attacked|hurt|scammed|harassed) me\b",
)

CRIME_PATTERN = re.compile(
    r"\b(assault|attack|rape|sexual|harass|stalk|threat|violence|kidnap|abduct|"
    r"robbed|theft|stole|fraud|scam|cyber|hack|hacked|blackmail|extort|"
    r"domestic violence|abuse|missing|injur|hurt)\w*\b",
    re.IGNORECASE,
)
CYBER_PATTERN = re.compile(
    r"\b(cyber|online|upi|bank|account|card|otp|phishing|scam|fraud|wallet|"
    r"transaction|payment|hacked|hack)\w*\b",
    re.IGNORECASE,
)
IMMEDIATE_DANGER_PATTERN = re.compile(
    r"\b(now|right now|immediate|danger|unsafe|threat|attack|weapon|bleeding|"
    r"kidnap|abduct|violence|hurt|injur)\w*\b",
    re.IGNORECASE,
)


def get_incident_guide(query: str) -> IncidentGuide | None:
    """Return help guidance only for a likely personal request, not abstract law queries."""
    normalized_query = " ".join(query.lower().split())
    is_personal_request = any(
        re.search(pattern, normalized_query) for pattern in PERSONAL_PATTERNS
    )
    if not is_personal_request or not CRIME_PATTERN.search(normalized_query):
        return None

    urgency_notice = None
    if IMMEDIATE_DANGER_PATTERN.search(normalized_query):
        urgency_notice = (
            "If you or someone else is in immediate danger, call 112 now or move "
            "to a safer place if you can do so safely."
        )

    if CYBER_PATTERN.search(normalized_query):
        return IncidentGuide(
            title="What you can do now — suspected cyber or financial fraud",
            urgency_notice=urgency_notice,
            steps=(
                "If money was sent or an account was accessed, call 1930 immediately.",
                "Contact your bank, card issuer, UPI app, or payment provider using its official support channel and ask it to secure the affected account.",
                "Preserve transaction IDs, screenshots, phone numbers, URLs, emails, and chat messages. Do not delete or alter the originals.",
                "Submit a report on the National Cyber Crime Reporting Portal and record the acknowledgement or complaint number.",
                "For ongoing threats, harassment, or immediate safety concerns, contact emergency services or local police.",
            ),
            resources=(
                ("Call 1930 — Cyber Crime Helpline", "tel:1930"),
                ("National Cyber Crime Reporting Portal", CYBERCRIME_URL),
                ("Emergency assistance — 112", EMERGENCY_URL),
                ("Free legal-aid information — NALSA 15100", NALSA_URL),
            ),
        )

    return IncidentGuide(
        title="What you can do now — support after an incident",
        urgency_notice=urgency_notice,
        steps=(
            "Prioritise your immediate safety. If there is an immediate threat, call 112; seek urgent medical care for injuries or other urgent health needs.",
            "Move to a safer place and contact a trusted person if that is safe for you.",
            "Preserve relevant evidence such as messages, call logs, photos, documents, CCTV details, or witness contacts. Avoid editing or deleting the originals.",
            "Write down what happened while it is fresh: dates, times, locations, people involved, and any identifying details.",
            "Contact local police or the relevant authority to ask about reporting the incident and retain any acknowledgement or reference number you receive.",
            "If you need legal support, contact a Legal Services Authority or the NALSA helpline to ask about available assistance.",
        ),
        resources=(
            ("Emergency assistance — call 112", "tel:112"),
            ("112 India Emergency Response Support System", EMERGENCY_URL),
            ("Free legal-aid information — NALSA 15100", NALSA_URL),
        ),
    )
