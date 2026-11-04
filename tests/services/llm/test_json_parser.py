import pytest

from junta_medica.exceptions import InvalidResponseError
from junta_medica.services.llm.json_parser import parse_json


def test_simple_json():
    assert parse_json('{"a": 1}') == {"a": 1}


def test_removes_markdown_fence():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_invalid_text_raises_error():
    with pytest.raises(InvalidResponseError):
        parse_json("esto no es json")


def test_list_is_not_accepted():
    with pytest.raises(InvalidResponseError):
        parse_json("[1, 2, 3]")


def test_removes_thinking_block():
    assert parse_json('<think>analizo el caso...</think>\n{"a": 1}') == {"a": 1}


def test_extracts_object_surrounded_by_text():
    assert parse_json('Aquí está la respuesta: {"a": {"b": 2}} Espero que ayude.') == {"a": {"b": 2}}
