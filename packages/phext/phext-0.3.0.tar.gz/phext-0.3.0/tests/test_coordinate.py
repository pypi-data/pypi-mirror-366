from phext.coordinate import Coordinate
import pytest

# Upstream tests covered by this module:
# test_coordinate_parsing
# test_to_urlencoded
# test_coordinates_invalid
# test_coordinates_valid
# test_url_encoding

# notes
# Apparently there aren't any test methods in phext-rs for break methods?

# expected valid conditions

def test_valid_home_coordinate():
    coord = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
    assert coord.library == 1
    assert coord.shelf == 1
    assert coord.series == 1
    assert coord.collection == 1
    assert coord.volume == 1
    assert coord.book == 1
    assert coord.chapter == 1
    assert coord.section == 1
    assert coord.scroll == 1

def test_independent_coordinates():
    coord = Coordinate.from_string("1.2.3/4.5.6/7.8.9")
    assert coord.library == 1
    assert coord.shelf == 2
    assert coord.series == 3
    assert coord.collection == 4
    assert coord.volume == 5
    assert coord.book == 6
    assert coord.chapter == 7
    assert coord.section == 8
    assert coord.scroll == 9

def test_large_coordinates():
    coord = Coordinate.from_string("999.998.997/996.995.994/993.992.991")
    assert coord.library == 999
    assert coord.shelf == 998
    assert coord.series == 997
    assert coord.collection == 996
    assert coord.volume == 995
    assert coord.book == 994
    assert coord.chapter == 993
    assert coord.section == 992
    assert coord.scroll == 991

def test_whitespace_support():
   coord = Coordinate.from_string("   9.8.7/6.5.4/3.2.1   ")
   assert coord.library == 9
   assert coord.shelf == 8
   assert coord.series == 7
   assert coord.collection == 6
   assert coord.volume == 5
   assert coord.book == 4
   assert coord.chapter == 3
   assert coord.section == 2
   assert coord.scroll == 1

def test_internal_whitespace_support():
   coord = Coordinate.from_string("91.82.73 / 64.55.46 / 37.28.19")
   assert coord.library == 91
   assert coord.shelf == 82
   assert coord.series == 73
   assert coord.collection == 64
   assert coord.volume == 55
   assert coord.book == 46
   assert coord.chapter == 37
   assert coord.section == 28
   assert coord.scroll == 19

def test_to_urlencoded():
   coord = Coordinate(98, 76, 54, 32, 10, 1, 23, 45, 67)
   assert coord.urlencoded() == "98.76.54;32.10.1;23.45.67"

def test_library_break():
   coord = Coordinate(98, 76, 54, 32, 10, 1, 23, 45, 67)
   coord.libraryBreak()
   expected = Coordinate(99,1,1, 1,1,1, 1,1,1)
   assert coord == expected

def test_shelf_break():
   coord = Coordinate(98, 76, 54, 32, 10, 1, 23, 45, 67)
   coord.shelfBreak()
   expected = Coordinate(98,77,1, 1,1,1, 1,1,1)
   assert coord == expected

def test_series_break():
   coord = Coordinate(98, 76, 54, 32, 10, 1, 23, 45, 67)
   coord.seriesBreak()
   expected = Coordinate(98,76,55, 1,1,1, 1,1,1)
   assert coord == expected

def test_collection_break():
   coord = Coordinate(98, 76, 54, 32, 10, 1, 23, 45, 67)
   coord.collectionBreak()
   expected = Coordinate(98,76,54, 33,1,1, 1,1,1)
   assert coord == expected

def test_volume_break():
   coord = Coordinate(98, 76, 54, 32, 10, 1, 23, 45, 67)
   coord.volumeBreak()
   expected = Coordinate(98,76,54, 32,11,1, 1,1,1)
   assert coord == expected

def test_book_break():
   coord = Coordinate(98, 76, 54, 32, 10, 1, 23, 45, 67)
   coord.bookBreak()
   expected = Coordinate(98,76,54, 32,10,2, 1,1,1)
   assert coord == expected

def test_chapter_break():
   coord = Coordinate(98, 76, 54, 32, 10, 1, 23, 45, 67)
   coord.chapterBreak()
   expected = Coordinate(98,76,54, 32,10,1, 24,1,1)
   assert coord == expected

def test_section_break():
   coord = Coordinate(98, 76, 54, 32, 10, 1, 23, 45, 67)
   coord.sectionBreak()
   expected = Coordinate(98,76,54, 32,10,1, 23,46,1)
   assert coord == expected

def test_scroll_break():
   coord = Coordinate(98, 76, 54, 32, 10, 1, 23, 45, 67)
   coord.scrollBreak()
   expected = Coordinate(98,76,54, 32,10,1, 23,45,68)
   assert coord == expected

# invalid conditions

def test_no_input():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("")

def test_too_large_coordinates():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("1000.1001.1002/1003.1004.1005/1006.1007.1008")

def test_negative_coordinates():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("-1.-2.-3/-4.-5.-6/-7.-8.-9")

def test_malformed_coordinates():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("1.2.3/4.5")

def test_null_coordinates():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("0.0.0/0.0.0/0.0.0")

def test_null_library():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("0.1.1/1.1.1/1.1.1")

def test_null_shelf():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("1.0.1/1.1.1/1.1.1")

def test_null_series():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("1.1.0/1.1.1/1.1.1")

def test_null_collection():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("1.1.1/0.1.1/1.1.1")

def test_null_volume():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("1.1.1/1.0.1/1.1.1")

def test_null_book():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("1.1.1/1.1.0/1.1.1")

def test_null_chapter():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("1.1.1/1.1.1/0.1.1")

def test_null_section():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("1.1.1/1.1.1/1.0.1")

def test_null_scroll():
    with pytest.raises(ValueError):
      coord = Coordinate.from_string("1.1.1/1.1.1/1.1.0")
