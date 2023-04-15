from BaseClasses import Location, Region, Entrance, MultiWorld
from .Locations import Gothic1Location, location_table

def create_regions(player: int, multiworld: MultiWorld) -> list[Region]:
    menu = Region("Menu", player, multiworld)
    menu.exits = [Entrance(player, "New Game", menu)]
    regions = [menu]
    
    prev = menu.exits[0]
    for c in range(1, 7):
        chapter = Region(f"Chapter {c}", player, multiworld)
        chapter.exits = [Entrance(player, f"Beat Chapter {c}", chapter)]
        prev.connect(chapter)
        prev = chapter.exits[0]
        regions.append(chapter)

    # put all chests in chapter 1
    regions[1].locations = [Gothic1Location(player, loc.name, loc.code, regions[1]) for loc in location_table]

    # put sleeper event location in chapter 6
    regions[6].locations = [Gothic1Location(player, "Sleeper", None, regions[6])]
    regions[6].exits = []

    return regions