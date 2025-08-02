import pytest

from mbls.cpsat.obj_value_bound_store import ObjValueBoundStore


@pytest.fixture
def store():
    return ObjValueBoundStore()


def test_add_and_get_obj_value(store: ObjValueBoundStore):
    # If not specified, is_maximize=False.
    store.add_obj_value(0.0, 10.0)
    store.add_obj_value(1.0, 9.0)
    assert store.obj_value_series.items() == [(0.0, 10.0), (1.0, 9.0)]


def test_add_and_get_obj_bound(store: ObjValueBoundStore):
    # If not specified, is_maximize=False.
    store.add_obj_bound(0.0, 8.0)
    store.add_obj_bound(1.0, 9.0)
    assert store.obj_bound_series.items() == [(0.0, 8.0), (1.0, 9.0)]


def test_add_last_timestamp_note(store: ObjValueBoundStore):
    store.add_obj_value(1.0, 10.0)
    store.add_obj_bound(0.0, 8.0)
    store.add_last_timestamp_note(
        "TheLastNote", obj_value_is_valid=True, obj_bound_is_valid=True
    )
    obj_value_timestamp_note_map = store.obj_value_series.timestamp_note_map
    obj_bound_timestamp_note_map = store.obj_bound_series.timestamp_note_map
    assert obj_value_timestamp_note_map[1.0] == "TheLastNote"
    # Although the last bound is at 0.0,
    # the note is added to the last timestamp of the bound series
    assert obj_bound_timestamp_note_map[1.0] == "TheLastNote"


def test_to_dict_and_from_dict(store: ObjValueBoundStore):
    store.add_obj_value(0.0, 10.0)
    store.add_obj_bound(0.0, 8.0)
    d = store.to_dict()
    loaded = ObjValueBoundStore.from_dict(d)
    assert loaded.obj_value_series.items() == [(0.0, 10.0)]
    assert loaded.obj_bound_series.items() == [(0.0, 8.0)]
