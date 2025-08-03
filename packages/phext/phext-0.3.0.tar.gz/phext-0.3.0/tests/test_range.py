from phext.range import Range
from phext.coordinate import Coordinate
import pytest

def test_range_exists():
  a = Coordinate(1,1,1, 1,1,1, 1,1,1)
  b = Coordinate.from_string("2.2.2/2.2.2/2.2.2")
  test = Range(a, b)

  assert test.start == a
  assert test.end == b