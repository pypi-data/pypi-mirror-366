# SQLite-based key-value storage

--------------------------------

## TOC

1. [Abstract](#1-abstract)  
2. [Get Started](#2-get-started)  
  2.1 [Install the Package](#21-install-the-package)  
  2.2 [SQLiteKVDB Implementation Details](#22-sqlitekvdb-implementation-details)  
  2.3 [SQLiteKVDB Use Case Example](#23-sqlitekvdb-use-case-example)
  

## 1. Abstract

--------------
  The package provides an implementation of SQLite-based key-value storage with dict-like interface.
Storage can save values of any type supported by Python. Yet you must choose proper serialization method, corresponding
planned use case before creating storage. Keys are to be strings.

  Storage instances can hold identity (name and version) of an application (DB controller) which created it. It might be
useful to have a possibility to verify these data when loading saved DB instances to avoid data misinterpretation or 
corruption.

[[TOC]](#toc "Back to Table Of Content")


## 2. Get Started

-----------------

### 2.1 Install the Package

-------------------------------------
  You install the `sqlite-kvdb` package like any other regular Python package:

```terminal
pip install sqlite-kvdb
```

[[TOC]](#toc "Table Of Content")


### 2.2 SQLiteKVDB Implementation details

-----------------------------------------
  Please keep in mind a few points about SQLiteKVDB implementation:

  * SQLiteKVDB objects do not do any internal data caching.  
    Data is directly fetched from the underlying SQLite database at the access time.
    
    
  * SQLiteKVDB objects use the `auto_commit` parameter to control when data modifications are actually stored to 
    underlying SQLite database. It's set at SQLiteKVDB object instantiation time and defaults to `True`.
    
    If the `auto_commit` is `True` changes immediately saved to the underlying database at the moment of assigning 
    a `value` to a `key`. 
    
    If the `auto_commit` is `False` changes are internally cached by the SQLite engine (within a WRITE TRANSACTION 
    scope) until the `SQLiteKVDB.commit()` method is called. 
    This mode is useful when multiple values to be assigned at once.

    **NOTE.** The SQLiteKVDB does not explicitly control transaction behaviour of the SQLite engine. That means it
    remains in the default implicit transaction management DEFFERED mode [1][2]. I.e. SQLiteKVDB.auto_commit=True 
    basically means that SQLiteKVDB implicitly calls SQLiteKVDB.commit() under the hood for each value assignment
    operation.
    
    
  * in case when a `value` is a complex object direct assignment to its attributes won't be auto-propagated to 
    underlying SQLite database. You have to instantiate a copy of such a `value`, modify attributes as appropriate, and 
    then assign it back to the same `key` it was initially assigned to.
    
    Please check the example below:

    ```python
    from pydantic import BaseModel
    
    from sqlite_construct import DBReference, DB_SCHEME
    from sqlite_kvdb import SQLiteKVDB
    
    class ComplexObject(BaseModel):
        attr1: str
    
    kvdb = SQLiteKVDB(db_ref=DBReference(scheme=DB_SCHEME.SQLITE3, path=":memory:"), auto_commit=True)
    
    object1 = ComplexObject(attr1="1")
    kvdb["key1"] = object1  
    print(list(kvdb.items()))  # Would print "[('key1', ComplexObject(attr1='1'))]"
    
    object1.attr1 = "2"         # This won't work
    kvdb["key1"].attr1 = "3"    # This won't work either
    print(list(kvdb.items()))   # Sill would print "[('key1', ComplexObject(attr1='1'))]"
    
    db_object1 = kvdb["key1"]
    db_object1.attr1 = "4"
    kvdb["key1"] = db_object1
    print(list(kvdb.items()))  # Would print "[('key1', ComplexObject(attr1='4'))]" 
    ```

>**_Reference:_**  
[1] [(sqlite3) Transaction control](https://docs.python.org/3.11/library/sqlite3.html#transaction-control)  
[2] [(SQLite) Transactions](https://www.sqlite.org/lang_transaction.html#transactions)  

[[TOC]](#toc "Table Of Content")


### 2.3 SQLiteKVDB Use Case Example

-----------------------------------

```python
from datetime import datetime, timedelta, timezone
from enum import Enum
from time import sleep

from pydantic import BaseModel

from sqlite_construct import DBReference, DB_SCHEME
from sqlite_kvdb import SQLiteKVDB, SQLiteKVDBError


class Sex(Enum):
    MALE = "male"
    FEMALE = "female"


class AbilityType(Enum):
    BASIC = "basic"
    EXTRA = "extra"


class Ability(BaseModel):
    type: AbilityType
    active: bool = False
    grade: int = 0


class CharacterState(BaseModel):
    abilities: dict[str, Ability]
    level: int
    lives: int
    health: int


class Character(BaseModel):
    name: str
    sex: Sex
    state: CharacterState


class PlayerState(BaseModel):
    last_login: datetime
    last_ingame_period: timedelta
    character: Character


class Mission(BaseModel):
    name: str
    progress: int


state_player_init = PlayerState(
    last_login=datetime.now(timezone.utc),
    last_ingame_period=timedelta(),
    character=Character(
        name="wizard",
        sex=Sex.MALE,
        state=CharacterState(
            abilities=dict(
                strength=Ability(type=AbilityType.BASIC, active=True, grade=2),
                speed=Ability(type=AbilityType.BASIC, active=True, grade=2),
                witchcraft=Ability(type=AbilityType.BASIC, active=True, grade=10),
                range=Ability(type=AbilityType.BASIC, active=True, grade=2),
            ),
            level=1,
            lives=5,
            health=100,
        )
    )
)

# Initialize state object
try:
    state = SQLiteKVDB(
        db_ref=DBReference(scheme=DB_SCHEME.SQLITE3, path="adventure-state.sqlite3"),
        auto_commit=False,
        app_codename="adventure",
        app_version="1.2.3"
    )

    state["player"] = state_player_init
    state["mission"] = Mission(name="TakeoverTheWorld", progress=0)
    state["location"] = "Midland"

    state.commit()
except SQLiteKVDBError as e:
    raise RuntimeError(f"Save state: {e.__class__.__name__}: {e}") from e

# Few hours later ...
# Gain new abilities
state_player = state["player"]
state_player.character.state.abilities["prediction"] = Ability(
    type=AbilityType.EXTRA, active=False, grade=1
)
state_player.character.state.abilities["flight"] = Ability(
    type=AbilityType.EXTRA, active=False, grade=1
)
state["player"] = state_player
state.commit()

sleep(5)
# Few hours later ...
# Exit game
try:
    state_player = state["player"]
    state_player.last_ingame_period = datetime.now(timezone.utc) - state["player"].last_login
    state_player.character.state.level = 2
    state_player.character.state.lives = 4
    state_player.character.state.health = 80
    state_player.character.state.abilities["range"] = 5
    state_player.character.state.abilities["prediction"].active = True
    state["player"] = state_player

    state_mission = state["mission"]
    state_mission.progress = 14
    state["mission"] = state_mission

    state["location"] = "Highland"

    state.close()   # Commits all pending transactions
except SQLiteKVDBError as e:
    raise RuntimeError(f"Save state: {e.__class__.__name__}: {e}") from e

sleep(5)
# Few hours later ...
# Back to the game
try:
    state = SQLiteKVDB(
        db_ref=DBReference(scheme=DB_SCHEME.SQLITE3, path="adventure-state.sqlite3"),
        auto_commit=False,
        app_codename="adventure",
        app_version="1.2.3"
    )

    state["player"].last_login = datetime.now(timezone.utc)
    state.commit()
except SQLiteKVDBError as e:
    raise RuntimeError(f"Load state: {e.__class__.__name__}: {e}") from e

# Exit game ...
# Assign actual state values here
state.close()
```

[[TOC]](#toc "Table Of Content")
