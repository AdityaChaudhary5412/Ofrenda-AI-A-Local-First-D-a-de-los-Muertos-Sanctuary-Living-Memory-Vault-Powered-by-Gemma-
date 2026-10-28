"""
Ofrenda AI - Data Models for Digital Altars, Ancestral Memories, and Offerings
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional

@dataclass
class Offering:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    category: str = "food"  # cempasuchil, candle, food, drink, personal, incense, salt, water
    tier: str = "tierra"    # cielo (top), tierra (middle), inframundo (base)
    description: str = ""
    icon: str = "🕯️"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Offering':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Memory:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    story: str = ""
    era_or_year: str = ""
    tags: List[str] = field(default_factory=list)
    recorded_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Ancestor:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    relationship: str = ""
    birth_year: Optional[int] = None
    passing_year: Optional[int] = None
    bio: str = ""
    favorite_foods: List[str] = field(default_factory=list)
    favorite_songs: List[str] = field(default_factory=list)
    sayings_and_advice: List[str] = field(default_factory=list)
    photo_url: str = ""
    memories: List[Memory] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['memories'] = [m.to_dict() if isinstance(m, Memory) else m for m in self.memories]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ancestor':
        memories_data = data.pop('memories', [])
        ancestor = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        ancestor.memories = [
            Memory.from_dict(m) if isinstance(m, dict) else m
            for m in memories_data
        ]
        return ancestor


@dataclass
class Altar:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = "Ofrenda de la Familia"
    family_name: str = "Familia"
    dedication_text: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    candles_lit: bool = True
    cempasuchil_path_active: bool = True
    ancestors: List[Ancestor] = field(default_factory=list)
    offerings: List[Offering] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['ancestors'] = [a.to_dict() if isinstance(a, Ancestor) else a for a in self.ancestors]
        d['offerings'] = [o.to_dict() if isinstance(o, Offering) else o for o in self.offerings]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Altar':
        ancestors_data = data.pop('ancestors', [])
        offerings_data = data.pop('offerings', [])
        altar = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        altar.ancestors = [
            Ancestor.from_dict(a) if isinstance(a, dict) else a
            for a in ancestors_data
        ]
        altar.offerings = [
            Offering.from_dict(o) if isinstance(o, dict) else o
            for o in offerings_data
        ]
        return altar

    def add_ancestor(self, ancestor: Ancestor) -> None:
        self.ancestors.append(ancestor)

    def add_offering(self, offering: Offering) -> None:
        self.offerings.append(offering)

    def get_offerings_by_tier(self) -> Dict[str, List[Offering]]:
        return {
            "cielo": [o for o in self.offerings if o.tier == "cielo"],
            "tierra": [o for o in self.offerings if o.tier == "tierra"],
            "inframundo": [o for o in self.offerings if o.tier == "inframundo"],
        }
