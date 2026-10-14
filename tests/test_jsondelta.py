import json
import pytest
from jsondelta import diff, main


def d(a, b, **kw):
    return list(diff(a, b, **kw))


def test_identical_key_order():
    assert d({"a": 1, "b": 2}, {"b": 2, "a": 1}) == []


def test_changed_added_removed():
    assert d({"a": 1, "b": 2}, {"a": 2, "c": 3}) == [("~", "a", 1, 2), ("-", "b", 2, None), ("+", "c", None, 3)]


def test_nested_path():
    assert d({"x": {"y": [1, 2]}}, {"x": {"y": [1, 3]}}) == [("~", "x.y[1]", 2, 3)]


def test_type_change_bool_int():
    assert d({"a": True}, {"a": 1}) == [("~", "a", True, 1)]


def test_list_length():
    assert d([1], [1, 2]) == [("+", "[1]", None, 2)]
    assert d([1, 2], [1]) == [("-", "[1]", 2, None)]


def test_unordered():
    assert d([1, 2, {"a": 1}], [{"a": 1}, 2, 1], unordered=True) == []
    assert d([1, 2], [2, 3], unordered=True) == [("-", "[0]", 1, None), ("+", "[]", None, 3)]


def test_ignore():
    assert d({"m": {"t": 1}, "a": 1}, {"m": {"t": 2}, "a": 1}, ignore={"m.t"}) == []


def test_root_scalar():
    assert d(1, 2) == [("~", "$", 1, 2)]


def write(tmp_path, name, obj):
    p = tmp_path / name
    p.write_text(obj if isinstance(obj, str) else json.dumps(obj))
    return str(p)


def test_exit_codes(tmp_path, capsys):
    a = write(tmp_path, "a.json", {"a": 1})
    assert main([a, a]) == 0
    b = write(tmp_path, "b.json", {"a": 2})
    assert main([a, b]) == 1
    assert "~ a: 1 -> 2" in capsys.readouterr().out


def test_bad_json_and_missing(tmp_path):
    a = write(tmp_path, "a.json", {"a": 1})
    bad = write(tmp_path, "bad.json", "{oops")
    with pytest.raises(SystemExit) as e:
        main([a, bad])
    assert "invalid JSON" in str(e.value)
    with pytest.raises(SystemExit) as e:
        main([a, str(tmp_path / "nope.json")])
    assert "cannot read" in str(e.value)


def test_json_output_and_quiet(tmp_path, capsys):
    a = write(tmp_path, "a.json", [1])
    b = write(tmp_path, "b.json", [2])
    assert main([a, b, "--json"]) == 1
    assert json.loads(capsys.readouterr().out)[0]["path"] == "[0]"
    assert main([a, b, "-q"]) == 1
    assert capsys.readouterr().out == ""
