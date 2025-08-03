from dataclasses import dataclass
from phext.coordinate import Coordinate

@dataclass
class PositionedScroll:
    coord: Coordinate
    text: str
    
    def __init__(self, coord, text):
        self.coord = coord
        self.text = text