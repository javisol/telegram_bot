from dataclasses import dataclass

@dataclass
class Event:
    """Class for storing Events."""
    time: str
    summary: str
