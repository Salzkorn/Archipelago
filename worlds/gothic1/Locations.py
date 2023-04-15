from BaseClasses import Location, MultiWorld
from typing import NamedTuple, Callable
import yaml

GOTHIC_LOCATION_OFFSET = 5353500

class Gothic1Location(Location):
    game: str = "Gothic 1"

    def __init__(self, player: int, name = "", code = None, parent = None):
        super(Gothic1Location, self).__init__(player, name, code, parent)
        self.event = code is None

class LocationData(NamedTuple):
    type: str
    name: str
    code: int
    rule: Callable = lambda state: True

location_table = tuple(LocationData("Chests", f"Chest {code + 1}", code + GOTHIC_LOCATION_OFFSET) for code in range(50))

location_name_groups = {}
for loc in location_table:
    location_name_groups.setdefault(loc.type, []).append(loc.name)