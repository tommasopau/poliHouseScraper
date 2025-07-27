from datetime import datetime, date
import json
from typing import Dict, Any


def normalize_tenant_preference(value: str) -> str:
    """
    Normalizza il campo tenant_preference.
    Restituisce solo 'ragazzo', 'ragazza' o 'indifferente'.
    Se il valore non è chiaro o contiene più opzioni, restituisce 'indifferente'.
    """
    if not value or not isinstance(value, str):
        return "indifferente"
    value = value.lower().replace("/", ",").replace("|", ",")
    valid = {"ragazzo", "ragazza", "indifferente"}
    for part in value.split(","):
        part = part.strip()
        if part in valid:
            return part
    return "indifferente"


def parse_date(date_str: str) -> date | None:
    """
    Parse a date string in 'YY-MM-DD' or 'YYYY-MM-DD' format to a date object.
    """
    if not date_str:
        return None
    for fmt in ("%y-%m-%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def parse_llm_response(response: str) -> Dict[str, Any]:
    """
    Parse LLM response to JSON.
    Cleans markdown and extracts JSON object.
    """
    try:
        cleaned = response.strip()
        if "```" in cleaned:
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            cleaned = cleaned[start:end]
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {}
