from lentezinha import update

from common_fixtures import user_01, user_02


def test_set_attribute_within_nested_dicts(user_01):
    update(user_01, "user.profile.age", 40)
    assert user_01["user"]["profile"]["age"] == 40


def test_set_list_element_at_the_end_of_chain(user_01):
    update(user_01, "user.emails.1", "alice@proton.me")
    assert user_01["user"]["emails"][1] == "alice@proton.me"


def test_set_attribute_apply(user_01):
    update(user_01, "user.profile.age", lambda a: a + 5)
    assert user_01["user"]["profile"]["age"] == 35


def test_set_returns_updated_value(user_01):
    assert update(user_01, "user.profile.age", lambda a: a + 5) == 35


def test_set_list_element_in_nested_pydantic_classes(user_02):
    update(user_02, "emails.1", "alice@hotmail.com")
    assert user_02.emails[1] == "alice@hotmail.com"
