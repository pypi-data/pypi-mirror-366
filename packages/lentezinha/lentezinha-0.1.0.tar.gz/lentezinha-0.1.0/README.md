# Lentezinha

Tiny Lens for Python: a single 30 KiB module to improve readability. "Lentezinha" means "little lens" in Brazilian Portuguese.

## Motivation

I don't like to do this: `user.get("profile", {}).get("age"))`, where `user` is a nested dictionary. I'd rather say `user.get("profile.age")`.

## Usage

```python
user = {"name": "Ana", "profile": {"age": 20}}

from lentezinha import read
read(user, "profile.age")  # == 20

from lentezinha import update
update(user, "profile.age", lambda a: a + 1)  # Updates age to 21
```

You can use a `Lens` instance if you plan to access nested attributes many times:

```python
from lentezinha import Lens
age = Lens("profile.age")

print(age.get(user))  # == 20

age.set(user, 27)  # == 27

age.set(user, lambda a: a + 1)  # == 28
```

It also works with Pydantic:

```python
from pydantic import BaseModel

class Profile(BaseModel):
    age: int

class User(BaseModel):
    profile: Profile

user = User(profile=Profile(age=20))

age.get(user)  # == 20
age.set(user, 27)  # == 27
```

## Installation

```shell
pip install lentezinha
```

## TODO

- Compose lenses
