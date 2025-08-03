from phext.coordinate import Coordinate
from phext.positionedScroll import PositionedScroll
from phext.phext import Phext
import pytest

# Upstream tests covered by this module:
# test_scrolls, test_sections, test_chapters
# test_books, test_volumes, test_collections
# test_series, test_shelves, test_libraries
# test_realistic_parse

def test_scroll_interface():
  coord = Coordinate.from_string("1.2.3/4.5.6/7.8.9")
  text = "Hello World"
  ps = PositionedScroll(coord, text)
  assert ps.coord == coord
  assert ps.text == text

def test_positioned_scrolls():
  coord1 = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  coord2 = Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  coord3 = Coordinate.from_string("1.1.1/1.1.1/1.1.3")
  text1 = "Scroll #1"
  text2 = "Scroll #2"
  text3 = "Scroll #3"
  data = [
     PositionedScroll(coord1, text1),
     PositionedScroll(coord2, text2),
     PositionedScroll(coord3, text3)
  ]
  assert data[0].coord == coord1
  assert data[1].coord == coord2
  assert data[2].coord == coord3
  assert data[0].text == text1
  assert data[1].text == text2
  assert data[2].text == text3

# also known as test_realistic_parse
def test_phokenize():
  example = "here's some text at 6.13.4/2.11.4/2.20.3this is the next scroll and won't be picked"
  phext = Phext()
  parsed = phext.phokenize(example)
  scroll1 = Coordinate(6,13,4, 2,11,4, 2,20,3)
  text1 = "here's some text at 6.13.4/2.11.4/2.20.3"
  scroll2 = Coordinate(6,13,4, 2,11,4, 2,20,4)
  text2 = "this is the next scroll and won't be picked"
  expected = [
    PositionedScroll(scroll1, text1),
    PositionedScroll(scroll2, text2)
  ]
  assert parsed == expected
