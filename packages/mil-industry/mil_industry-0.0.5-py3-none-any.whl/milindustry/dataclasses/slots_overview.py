from dataclasses import dataclass
from datetime import datetime

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
    as_of: datetime
