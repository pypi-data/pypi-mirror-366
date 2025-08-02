from dataclasses import dataclass


@dataclass
class SlotCategory:
    used: int
    unused: int
    max: int
    disabled: int


@dataclass
class CharacterSlotOverview:
    character_name: str
    character_id: int
    manufacturing: SlotCategory
    reaction: SlotCategory
    research: SlotCategory
