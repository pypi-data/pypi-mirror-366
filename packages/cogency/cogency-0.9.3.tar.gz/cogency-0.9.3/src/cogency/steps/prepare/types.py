"""Prepareed data types - cleaned queries with context and memory integration."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Prepareed:
    memory: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    memory_type: Optional[str] = None
    mode: Optional[str] = None
    selected_tools: List[str] = field(default_factory=list)
    reasoning: Optional[str] = None
