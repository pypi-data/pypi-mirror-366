import pytest
import json
import os
from pathlib import Path
from wixok.jsonfile import JSONFile


def test_load_valid_list(tmp_path):
    file = tmp_path / "data.json"
    json_data = [1, 2, 3]
    file.write_text(json.dumps(json_data), encoding="utf-8")
    assert JSONFile.load(file) == json_data


def test_load_invalid_json(tmp_path):
    file = tmp_path / "broken.json"
    file.write_text("{ not json }", encoding="utf-8")
    assert JSONFile.load(file) == []


def test_load_non_list_json(tmp_path, capsys):
    JSONFile.debug = True
    file = tmp_path / "dict.json"
    file.write_text(json.dumps({"a": 1}), encoding="utf-8")
    result = JSONFile.load(file)
    assert result == [{"a": 1}]
    JSONFile.debug = False


def test_load_missing_file(tmp_path):
    file = tmp_path / "missing.json"
    assert JSONFile.load(file) == []


def test_load_permission_error(tmp_path):
    file = tmp_path / "restricted.json"
    file.write_text(json.dumps([1, 2, 3]))
    file.chmod(0o000)
    try:
        assert JSONFile.load(file) == []
    finally:
        file.chmod(0o644)


# === APPEND TESTS ===

def test_append_scalar_to_list(tmp_path):
    file = tmp_path / "list.json"
    file.write_text(json.dumps([1, 2]))
    assert JSONFile.append(file, 3) is True
    assert json.loads(file.read_text()) == [1, 2, 3]


def test_append_list_to_list(tmp_path):
    file = tmp_path / "list.json"
    file.write_text(json.dumps([1]))
    assert JSONFile.append(file, [2, 3]) is True
    assert json.loads(file.read_text()) == [1, 2, 3]


def test_append_dict_to_list(tmp_path):
    file = tmp_path / "list.json"
    file.write_text(json.dumps([1, 2]))
    result = JSONFile.append(file, {"key": "value"})
    assert result is True
    assert json.loads(file.read_text()) == [1, 2, {"key": "value"}]


def test_append_dict_to_dict(tmp_path):
    file = tmp_path / "dict.json"
    file.write_text(json.dumps({"a": 1}))
    result = JSONFile.append(file, {"b": 2})
    assert result is True
    assert json.loads(file.read_text()) == {"a": 1, "b": 2}


def test_append_list_to_dict(tmp_path, capsys):
    JSONFile.debug = True
    file = tmp_path / "dict.json"
    file.write_text(json.dumps({"x": 1}))
    result = JSONFile.append(file, [2, 3])
    assert result is False
    captured = capsys.readouterr()
    assert "Cannot append non-dict data" in captured.out
    JSONFile.debug = False


def test_append_invalid_to_dict(tmp_path, capsys):
    JSONFile.debug = True
    file = tmp_path / "dict.json"
    file.write_text(json.dumps({"x": 1}))
    assert JSONFile.append(file, ["invalid"]) is False
    captured = capsys.readouterr()
    assert "Cannot append non-dict data" in captured.out
    JSONFile.debug = False


def test_append_unsupported_structure(tmp_path, capsys):
    JSONFile.debug = True
    file = tmp_path / "string.json"
    file.write_text(json.dumps("not a list or dict"))
    assert JSONFile.append(file, {"a": 1}) is False
    captured = capsys.readouterr()
    assert "Unsupported JSON structure" in captured.out
    JSONFile.debug = False


def test_append_invalid_json(tmp_path):
    file = tmp_path / "broken.json"
    file.write_text("{ invalid json }")
    assert JSONFile.append(file, {"a": 1}) is False


def test_append_permission_error(tmp_path):
    file = tmp_path / "list.json"
    file.write_text(json.dumps([1]))
    file.chmod(0o000)
    try:
        assert JSONFile.append(file, 2) is False
    finally:
        file.chmod(0o644)


# === SAVE TESTS ===

def test_save_valid_data(tmp_path):
    file = tmp_path / "save.json"
    data = {"a": [1, 2]}
    assert JSONFile.save(file, data) is True
    assert json.loads(file.read_text()) == data


def test_save_invalid_type(tmp_path, capsys):
    JSONFile.debug = True
    file = tmp_path / "save.json"
    class Unserializable: pass
    assert JSONFile.save(file, Unserializable()) is False
    captured = capsys.readouterr()
    assert "not JSON serializable" in captured.out
    JSONFile.debug = False


def test_save_permission_error(tmp_path):
    file = tmp_path / "save.json"
    file.write_text(json.dumps([1]))
    file.chmod(0o000)
    try:
        assert JSONFile.save(file, [2]) is False
    finally:
        file.chmod(0o644)


def test_save_is_directory(tmp_path):
    assert JSONFile.save(tmp_path, {"x": 1}) is False
