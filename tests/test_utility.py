import pytest
from app.utility.helpers import normalize_tenant_preference, parse_date, parse_llm_response


def test_normalize_tenant_preference():
    assert normalize_tenant_preference("ragazzo") == "ragazzo"
    assert normalize_tenant_preference("ragazza") == "ragazza"
    assert normalize_tenant_preference("indifferente") == "indifferente"
    assert normalize_tenant_preference("ragazzo/ragazza") == "ragazzo"
    assert normalize_tenant_preference("") == "indifferente"
    assert normalize_tenant_preference(None) == "indifferente"
    assert normalize_tenant_preference("RAGAZZA") == "ragazza"
    assert normalize_tenant_preference("ragazzo|ragazza") == "ragazzo"
    assert normalize_tenant_preference("unknown") == "indifferente"
    assert normalize_tenant_preference("ragazzo,ragazza") == "ragazzo"
    assert normalize_tenant_preference("ragazzo, ragazza") == "ragazzo"
    assert normalize_tenant_preference("ragazzo/indifferente") == "ragazzo"


def test_parse_date_valid():
    assert parse_date("24-07-27").year == 2024
    assert parse_date("2025-07-27").year == 2025


def test_parse_date_invalid():
    assert parse_date("") is None
    assert parse_date("not-a-date") is None
    assert parse_date("2025/07/27") is None


def test_parse_llm_response_valid_json():
    json_str = '{"price": 500, "location": "Milano"}'
    result = parse_llm_response(json_str)
    assert result["price"] == 500
    assert result["location"] == "Milano"


def test_parse_llm_response_with_markdown():
    md_json = "```json\n{\"price\": 600, \"location\": \"Bovisa\"}\n```"
    result = parse_llm_response(md_json)
    assert result["price"] == 600
    assert result["location"] == "Bovisa"


def test_parse_llm_response_invalid_json():
    bad_json = "not a json"
    result = parse_llm_response(bad_json)
    assert result == {}
