from common_fixtures import user_01, user_02, user_03
from lentezinha import read


def test_get_attribute_from_nested_dicts(user_01):
    assert read(user_01, "user.profile.age") == 30
    assert read(user_01, "user.profile.name") == "Alice"


def test_get_last_attribute_is_list_index(user_01):
    assert read(user_01, "user.emails.0") == "alice@gmail.com"


def test_get_attribute_within_nested_pydantic_clases(user_02):
    assert read(user_02, "profile.age") == 30


def test_get_with_separator(user_03):
    assert read(user_03, "user:user.profiles:age", separator=":") == 30
    assert read(user_03, "user:user emails:1", separator=":") == "alice@hotmail.com"
