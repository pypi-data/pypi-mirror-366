from dataclasses import dataclass
from phext.coordinate import Coordinate

@dataclass
class Range:
  start: Coordinate
  end: Coordinate