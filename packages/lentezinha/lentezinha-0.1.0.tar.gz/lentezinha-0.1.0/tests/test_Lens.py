from common_fixtures import user_01, user_02, user_03
from lentezinha import Lens


def test_get_attribute_from_nested_dicts(user_01):
    age = Lens("user.profile.age")
    assert age.get(user_01) == 30

    name = Lens("user.profile.name")
    assert name.get(user_01) == "Alice"


def test_get_last_attribute_is_list_index(user_01):
    email = Lens("user.emails.0")
    assert email.get(user_01) == "alice@gmail.com"


def test_get_attribute_within_nested_pydantic_clases(user_02):
    age = Lens("profile.age")
    assert age.get(user_02) == 30


def test_get_with_separator(user_03):
    age = Lens("user:user.profiles:age", separator=":")
    assert age.get(user_03) == 30

    email = Lens("user:user emails:1", separator=":")
    assert email.get(user_03) == "alice@hotmail.com"


def test_set_attribute_within_nested_dicts(user_01):
    age = Lens("user.profile.age")
    age.set(user_01, 40)
    assert user_01["user"]["profile"]["age"] == 40


def test_set_list_element_at_the_end_of_chain(user_01):
    email = Lens("user.emails.1")
    email.set(user_01, "alice@proton.me")
    assert user_01["user"]["emails"][1] == "alice@proton.me"


def test_set_attribute_apply(user_01):
    age = Lens("user.profile.age")
    age.set(user_01, lambda a: a + 5)
    assert user_01["user"]["profile"]["age"] == 35


def test_set_returns_updated_value(user_01):
    age = Lens("user.profile.age")
    assert age.set(user_01, lambda a: a + 5) == 35


def test_set_list_element_in_nested_pydantic_classes(user_02):
    email = Lens("emails.1")
    email.set(user_02, "alice@hotmail.com")
    assert user_02.emails[1] == "alice@hotmail.com"
