import pytest

from src.routix.dynamic_data_object import DynamicDataObject


def test_non_dict_initialization_raises_type_error():
    with pytest.raises(
        TypeError, match="DynamicDataObject must be initialized with a dictionary"
    ):
        DynamicDataObject(["not", "a", "dict"])
    with pytest.raises(
        TypeError, match="DynamicDataObject must be initialized with a dictionary"
    ):
        DynamicDataObject("not a dict")
    with pytest.raises(
        TypeError, match="DynamicDataObject must be initialized with a dictionary"
    ):
        DynamicDataObject(123)
    with pytest.raises(
        TypeError, match="DynamicDataObject must be initialized with a dictionary"
    ):
        DynamicDataObject(None)


def test_dynamic_attribute_assignment():
    obj = {"name": "John", "age": 30}
    data = DynamicDataObject(obj)
    assert data.name == "John"
    assert data.age == 30


def test_invalid_key_raises_error():
    with pytest.raises(
        ValueError, match="Invalid key: 123. Keys must be valid string identifiers."
    ):
        DynamicDataObject({123: "value"})


def test_reserved_key_raises_error():
    with pytest.raises(
        ValueError,
        match="Key '__init__' is reserved and cannot be used as an attribute.",
    ):
        DynamicDataObject({"__init__": "value"})


def test_nested_dict_conversion():
    obj = {"a": 1, "b": {"ba": 2, "bb": 3}}
    data = DynamicDataObject.from_obj(obj)
    assert data.a == 1
    assert isinstance(data.b, DynamicDataObject)
    assert data.b.ba == 2
    assert data.b.bb == 3


def test_list_of_dict_conversion():
    obj = [{"id": 1, "value": "a"}, {"id": 2, "value": "b"}]
    data = DynamicDataObject.from_obj(obj)
    assert isinstance(data, list)
    assert len(data) == 2
    assert isinstance(data[0], DynamicDataObject)
    assert data[0].id == 1
    assert data[0].value == "a"
    assert isinstance(data[1], DynamicDataObject)
    assert data[1].id == 2
    assert data[1].value == "b"


def test_to_obj_conversion():
    obj = {"name": "John", "details": {"age": 30, "skills": ["Python", "JSON"]}}
    data = DynamicDataObject.from_obj(obj)
    plain_obj = data.to_obj()
    assert plain_obj == obj


def test_json_serialization(tmp_path):
    obj = {"name": "John", "age": 30}
    data = DynamicDataObject(obj)
    file_path = tmp_path / "test.json"
    data.to_json(file_path)
    loaded_data = DynamicDataObject.from_json(file_path)
    assert loaded_data.name == "John"
    assert loaded_data.age == 30


def test_yaml_serialization(tmp_path):
    import yaml

    obj = {"name": "Alice", "skills": ["Python", "ML"]}
    data = DynamicDataObject(obj)
    file_path = tmp_path / "test.yaml"
    data.to_yaml(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f)
    assert loaded["name"] == "Alice"
    assert loaded["skills"] == ["Python", "ML"]


def test_bytes_type_raises():
    with pytest.raises(TypeError, match="bytes type is not supported"):
        DynamicDataObject.from_obj(b"abc")


def test_roundtrip_nested_list_dict():
    obj = {"items": [{"a": 1}, {"b": 2}]}
    data = DynamicDataObject.from_obj(obj)
    assert isinstance(data.items, list)
    assert data.items[0].a == 1
    assert data.items[1].b == 2
    assert data.to_obj() == obj


def test_equality_and_repr():
    obj1 = {"x": 1, "y": {"z": 2}}
    obj2 = {"x": 1, "y": {"z": 2}}
    d1 = DynamicDataObject.from_obj(obj1)
    d2 = DynamicDataObject.from_obj(obj2)
    assert d1.to_obj() == d2.to_obj()
    assert "DynamicDataObject" in repr(d1)
