from phext.coordinate import Coordinate
from phext.positionedScroll import PositionedScroll
from phext.range import Range
from phext.phext import Phext
from datetime import datetime
from copy import deepcopy
import pytest

# Upstream tests covered by this module:
# test_dead_reckoning
# test_line_break
# test_more_cowbell
# test_coordinate_based_insert
# test_coordinate_based_replace
# test_coordinate_based_remove
# test_range_based_replace
# test_next_scroll
# test_last_empty_scroll
# test_merge
# test_subtract
# test_normalize
# test_expand
# test_contract
# test_fs_read_write
# test_replace_create
# test_summary
# test_navmap
# test_textmap
# test_larger_coordinates
# test_phext_index
# test_scroll_manifest
# test_phext_soundex_v1
# test_insert_performance_2k_scrolls
# test_insert_performance_medium_scrolls
# test_hash_support
# test_subspace_filter

def test_dead_reckoning():
  test = "random text in 1.1.1/1.1.1/1.1.1 that we can skip past"
  test += Phext.LIBRARY_BREAK
  test += "everything in here is at 2.1.1/1.1.1/1.1.1"
  test += Phext.SCROLL_BREAK
  test += "and now we're at 2.1.1/1.1.1/1.1.2"
  test += Phext.SCROLL_BREAK
  test += "moving on up to 2.1.1/1.1.1/1.1.3"
  test += Phext.BOOK_BREAK
  test += "and now over to 2.1.1/1.1.2/1.1.1"
  test += Phext.SHELF_BREAK
  test += "woot, up to 2.2.1/1.1.1/1.1.1"
  test += Phext.LIBRARY_BREAK
  test += "here we are at 3.1.1/1.1.1.1.1"
  test += Phext.LIBRARY_BREAK # 4.1.1/1.1.1/1.1.1
  test += Phext.LIBRARY_BREAK # 5.1.1/1.1.1/1.1.1
  test += "getting closer to our target now 5.1.1/1.1.1/1.1.1"
  test += Phext.SHELF_BREAK # 5.2.1
  test += Phext.SHELF_BREAK # 5.3.1
  test += Phext.SHELF_BREAK # 5.4.1
  test += Phext.SHELF_BREAK # 5.5.1
  test += Phext.SERIES_BREAK # 5.5.2
  test += Phext.SERIES_BREAK # 5.5.3
  test += Phext.SERIES_BREAK # 5.5.4
  test += Phext.SERIES_BREAK # 5.5.5
  test += "here we go! 5.5.5/1.1.1/1.1.1"
  test += Phext.COLLECTION_BREAK # 5.5.5/2.1.1/1.1.1
  test += Phext.COLLECTION_BREAK # 5.5.5/3.1.1/1.1.1
  test += Phext.COLLECTION_BREAK # 5.5.5/4.1.1/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.1.2/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.1.3/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.1.4/1.1.1
  test += "this test appears at 5.5.5/4.1.4/1.1.1"
  test += Phext.VOLUME_BREAK # 5.5.5/4.2.1/1.1.1
  test += Phext.VOLUME_BREAK # 5.5.5/4.3.1/1.1.1
  test += Phext.VOLUME_BREAK # 5.5.5/4.4.1/1.1.1
  test += Phext.VOLUME_BREAK # 5.5.5/4.5.1/1.1.1
  test += Phext.VOLUME_BREAK # 5.5.5/4.6.1/1.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.1/2.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.1/3.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.1/4.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.1/5.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.2/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.3/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.4/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.5/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.6/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.7/1.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/2.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/3.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/4.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/5.1.1
  test += Phext.SCROLL_BREAK # 5.5.5/4.6.7/5.1.2
  test += Phext.SCROLL_BREAK # 5.5.5/4.6.7/5.1.3
  test += Phext.SCROLL_BREAK # 5.5.5/4.6.7/5.1.4
  test += Phext.SCROLL_BREAK # 5.5.5/4.6.7/5.1.5
  test += Phext.SCROLL_BREAK # 5.5.5/4.6.7/5.1.6
  test += "here's a test at 5.5.5/4.6.7/5.1.6"
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/5.1.7
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/6.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/7.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/8.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/9.1.1
  test += Phext.SECTION_BREAK # 5.5.5/4.6.7/9.2.1
  test += Phext.SECTION_BREAK # 5.5.5/4.6.7/9.3.1
  test += Phext.SECTION_BREAK # 5.5.5/4.6.7/9.4.1
  test += Phext.SECTION_BREAK # 5.5.5/4.6.7/9.5.1
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.2
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.3
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.4
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.5
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.6
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.7
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.8
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.9
  test += "Expected Test Pattern Alpha Whisky Tango Foxtrot"
  coord = Coordinate.from_string("5.5.5/4.6.7/9.5.9")

  phext = Phext()
  result = phext.fetch(test, coord)
  assert result == "Expected Test Pattern Alpha Whisky Tango Foxtrot"

  coord2 = Coordinate.from_string("5.5.5/4.6.7/5.1.6")
  result2 = phext.fetch(test, coord2)
  assert result2 == "here's a test at 5.5.5/4.6.7/5.1.6"

def test_line_break():
  assert Phext.LINE_BREAK == '\n'

def test_more_cowbell():
  assert Phext.MORE_COWBELL == '\x07'

def test_coordinate_based_insert():
  phext = Phext()
  doc = "aaa\x01bbb\x17ccc"
  root = phext.defaultCoordinate()

  test1 = phext.phokenize(doc)
  precheck = [
    PositionedScroll(Coordinate(1,1,1, 1,1,1, 1,1,1), "aaa"),
    PositionedScroll(Coordinate(2,1,1, 1,1,1, 1,1,1), "bbb"),
    PositionedScroll(Coordinate(2,1,1, 1,1,1, 1,1,2), "ccc")
  ]
  assert test1 == precheck
  test2 = phext.dephokenize(test1)
  assert test2 == doc

  coord1 = Coordinate.from_string("2.1.1/1.1.1/1.1.3")
  update1 = phext.insert(doc, coord1, "ddd")
  assert update1 == "aaa\x01bbb\x17ccc\x17ddd"

  # append 'eee' after 'ddd'
  coord2 = Coordinate.from_string("2.1.1/1.1.1/1.1.4")
  update2 = phext.insert(update1, coord2, "eee")
  assert update2 == "aaa\x01bbb\x17ccc\x17ddd\x17eee"

  # append 'fff' after 'eee'
  coord3 = Coordinate.from_string("2.1.1/1.1.1/1.2.1")
  update3 = phext.insert(update2, coord3, "fff")
  assert update3 == "aaa\x01bbb\x17ccc\x17ddd\x17eee\x18fff"

  # append 'ggg' after 'fff'
  coord4 = Coordinate.from_string("2.1.1/1.1.1/1.2.2")
  update4 = phext.insert(update3, coord4, "ggg")
  assert update4 == "aaa\x01bbb\x17ccc\x17ddd\x17eee\x18fff\x17ggg"

  # append 'hhh' after 'ggg'
  coord5 = Coordinate.from_string("2.1.1/1.1.1/2.1.1")
  update5 = phext.insert(update4, coord5, "hhh")
  assert update5 == "aaa\x01bbb\x17ccc\x17ddd\x17eee\x18fff\x17ggg\x19hhh"

  # append 'iii' after 'eee'
  coord6 = Coordinate.from_string("2.1.1/1.1.1/1.1.5")
  update6 = phext.insert(update5, coord6, "iii")
  assert update6 == "aaa\x01bbb\x17ccc\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh"

  # extend 1.1.1/1.1.1/1.1.1 with '---AAA'
  update7 = phext.insert(update6, root, "---AAA")
  assert update7 == "aaa---AAA\x01bbb\x17ccc\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.1.1 with '---BBB'
  coord8 = Coordinate.from_string("2.1.1/1.1.1/1.1.1")
  update8 = phext.insert(update7, coord8, "---BBB")
  assert update8 == "aaa---AAA\x01bbb---BBB\x17ccc\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.1.2 with '---CCC'
  coord9 = Coordinate.from_string("2.1.1/1.1.1/1.1.2")
  update9 = phext.insert(update8, coord9, "---CCC")
  assert update9 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.1.3 with '---DDD'
  coord10 = Coordinate.from_string("2.1.1/1.1.1/1.1.3")
  update10 = phext.insert(update9, coord10, "---DDD")
  assert update10 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee\x17iii\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.1.4 with '---EEE'
  coord11 = Coordinate.from_string("2.1.1/1.1.1/1.1.4")
  update11 = phext.insert(update10, coord11, "---EEE")
  assert update11 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.1.5 with '---III'
  coord12 = Coordinate.from_string("2.1.1/1.1.1/1.1.5")
  update12 = phext.insert(update11, coord12, "---III")
  assert update12 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.2.1 with '---FFF'
  coord13 = Coordinate.from_string("2.1.1/1.1.1/1.2.1")
  update13 = phext.insert(update12, coord13, "---FFF")
  assert update13 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.2.2 with '---GGG'
  coord14 = Coordinate.from_string("2.1.1/1.1.1/1.2.2")
  update14 = phext.insert(update13, coord14, "---GGG")
  assert update14 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh"

  # extend 2.1.1/1.1.1/2.1.1 with '---HHH'
  coord15 = Coordinate.from_string("2.1.1/1.1.1/2.1.1")
  update15 = phext.insert(update14, coord15, "---HHH")
  assert update15 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH"

  # insert 'jjj' at 2.1.1/1.1.2/1.1.1
  coord16 = Coordinate.from_string("2.1.1/1.1.2/1.1.1")
  update16 = phext.insert(update15, coord16, "jjj")
  assert update16 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj"

  # insert 'kkk' at 2.1.1/1.2.1/1.1.1
  coord17 = Coordinate.from_string("2.1.1/1.2.1/1.1.1")
  update17 = phext.insert(update16, coord17, "kkk")
  assert update17 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk"

  # insert 'lll' at 2.1.1/2.1.1/1.1.1
  coord18 = Coordinate.from_string("2.1.1/2.1.1/1.1.1")
  update18 = phext.insert(update17, coord18, "lll")
  assert update18 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll"

  # insert 'mmm' at 2.1.2/1.1.1/1.1.1
  coord19 = Coordinate.from_string("2.1.2/1.1.1/1.1.1")
  update19 = phext.insert(update18, coord19, "mmm")
  assert update19 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll\x1Emmm"

  # insert 'nnn' at 2.2.1/1.1.1/1.1.1
  coord20 = Coordinate.from_string("2.2.1/1.1.1/1.1.1")
  update20 = phext.insert(update19, coord20, "nnn")
  assert update20 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll\x1Emmm\x1Fnnn"

  # insert 'ooo' at 3.1.1/1.1.1/1.1.1
  coord21 = Coordinate.from_string("3.1.1/1.1.1/1.1.1")
  update21 = phext.insert(update20, coord21, "ooo")
  assert update21 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll\x1Emmm\x1Fnnn\x01ooo"

def test_coordinate_based_replace():
  phext = Phext()

  # replace 'AAA' with 'aaa'
  coord0 = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  update0 = phext.replace("AAA\x17bbb\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj", coord0, "aaa")
  assert update0 == "aaa\x17bbb\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'bbb' with '222'
  coord1 = Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  update1 = phext.replace(update0, coord1, "222")
  assert update1 == "aaa\x17222\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ccc' with '3-'
  coord2 = Coordinate.from_string("1.1.1/1.1.1/1.2.1")
  update2 = phext.replace(update1, coord2, "3-")
  assert update2 == "aaa\x17222\x183-\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ddd' with 'delta'
  coord3 = Coordinate.from_string("1.1.1/1.1.1/2.1.1")
  update3 = phext.replace(update2, coord3, "delta")
  assert update3 == "aaa\x17222\x183-\x19delta\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'eee' with 'a bridge just close enough'
  coord4 = Coordinate.from_string("1.1.1/1.1.2/1.1.1")
  update4 = phext.replace(update3, coord4, "a bridge just close enough")
  assert update4 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'fff' with 'nifty'
  coord5 = Coordinate.from_string("1.1.1/1.2.1/1.1.1")
  update5 = phext.replace(update4, coord5, "nifty")
  assert update5 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cnifty\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ggg' with 'G8'
  coord6 = Coordinate.from_string("1.1.1/2.1.1/1.1.1")
  update6 = phext.replace(update5, coord6, "G8")
  assert update6 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cnifty\x1DG8\x1Ehhh\x1Fiii\x01jjj"

  # replace 'hhh' with 'Hello World'
  coord7 = Coordinate.from_string("1.1.2/1.1.1/1.1.1")
  update7 = phext.replace(update6, coord7, "Hello World")
  assert update7 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cnifty\x1DG8\x1EHello World\x1Fiii\x01jjj"

  # replace 'iii' with '_o_'
  coord8 = Coordinate.from_string("1.2.1/1.1.1/1.1.1")
  update8 = phext.replace(update7, coord8, "_o_")
  assert update8 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cnifty\x1DG8\x1EHello World\x1F_o_\x01jjj"

  # replace 'jjj' with '/win'
  coord9 = Coordinate.from_string("2.1.1/1.1.1/1.1.1")
  update9 = phext.replace(update8, coord9, "/win")
  assert update9 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cnifty\x1DG8\x1EHello World\x1F_o_\x01/win"

  # the api editor has trouble with this input...
  coord_r0a = Coordinate.from_string("2.1.1/1.1.1/1.1.5")
  update_r0a = phext.replace("hello world\x17scroll two", coord_r0a, "2.1.1-1.1.1-1.1.5")
  assert update_r0a == "hello world\x17scroll two\x01\x17\x17\x17\x172.1.1-1.1.1-1.1.5"

  # regression from api testing
  # unit tests don't hit the failure I'm seeing through rocket...hmm - seems to be related to using library breaks
  coord_r1a = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  update_r1a = phext.replace("", coord_r1a, "aaa")
  assert update_r1a == "aaa"

  coord_r1b = Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  update_r1b = phext.replace(update_r1a, coord_r1b, "bbb")
  assert update_r1b == "aaa\x17bbb"

  coord_r1c = Coordinate.from_string("1.2.3/4.5.6/7.8.9")
  update_r1c = phext.replace(update_r1b, coord_r1c, "ccc")
  assert update_r1c == "aaa\x17bbb\x1F\x1E\x1E\x1D\x1D\x1D\x1C\x1C\x1C\x1C\x1A\x1A\x1A\x1A\x1A\x19\x19\x19\x19\x19\x19\x18\x18\x18\x18\x18\x18\x18\x17\x17\x17\x17\x17\x17\x17\x17ccc"

  coord_r1d = Coordinate.from_string("1.4.4/2.8.8/4.16.16")
  update_r1d = phext.replace(update_r1c, coord_r1d, "ddd")
  assert update_r1d == "aaa\x17bbb\x1F\x1E\x1E\x1D\x1D\x1D\x1C\x1C\x1C\x1C\x1A\x1A\x1A\x1A\x1A\x19\x19\x19\x19\x19\x19\x18\x18\x18\x18\x18\x18\x18\x17\x17\x17\x17\x17\x17\x17\x17ccc\x1F\x1F\x1E\x1E\x1E\x1D\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x19\x19\x19\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17ddd"

  coord_regression_1 = Coordinate.from_string("11.12.13/14.15.16/17.18.19")
  update_regression_1 = phext.replace(update_r1d, coord_regression_1, "eee")
  assert update_regression_1 == "aaa\x17bbb\x1F\x1E\x1E\x1D\x1D\x1D\x1C\x1C\x1C\x1C\x1A\x1A\x1A\x1A\x1A\x19\x19\x19\x19\x19\x19\x18\x18\x18\x18\x18\x18\x18\x17\x17\x17\x17\x17\x17\x17\x17ccc\x1F\x1F\x1E\x1E\x1E\x1D\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x19\x19\x19\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17ddd" + \
  "\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01" + \
  "\x1F\x1F\x1F\x1F\x1F\x1F\x1F\x1F\x1F\x1F\x1F" + \
  "\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x1E" + \
  "\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D" + \
  "\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C" + \
  "\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A" + \
  "\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19" + \
  "\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18" + \
  "\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17" + \
  "eee"

  # finally found the bugger!
  coord_regression_2 = Coordinate.from_string("1.1.1/1.1.2/1.1.2")
  regression_2_baseline = "1.1.11.1.21.1.31.1.41.2.11.2.21.2.31.2.4" + \
    "2.1.13.1.14.1.12/1.1.12/1.1.32.1/1.1.12.1.1/1.1.12/1.1.1/1.1.12.1/1.1.1/1.1.12.1.1/1.1.1/1.1.1"
  update_regression_2 = phext.replace(regression_2_baseline, coord_regression_2, "new content")
  assert update_regression_2, "1.1.1\x171.1.2\x171.1.3\x171.1.4\x181.2.1\x171.2.2\x171.2.3\x171.2.4\x192.1.1\x193.1.1\x194.1.1\x1a2/1.1.1\x17new content\x172/1.1.3\x1c2.1/1.1.1\x1d2.1.1/1.1.1\x1e2/1.1.1/1.1.1\x1f2.1/1.1.1/1.1.1\x012.1.1/1.1.1/1.1.1"

def test_coordinate_based_remove():
  phext = Phext()

  # replace 'aaa' with ''
  coord1 = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  update1 = phext.remove("aaa\x17bbb\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj", coord1)
  assert update1 == "\x17bbb\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'bbb' with ''
  coord2 = Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  update2 = phext.remove(update1, coord2)
  assert update2 == "\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ccc' with ''
  coord3 = Coordinate.from_string("1.1.1/1.1.1/1.2.1")
  update3 = phext.remove(update2, coord3)
  assert update3 == "\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ddd' with ''
  coord4 = Coordinate.from_string("1.1.1/1.1.1/2.1.1")
  update4 = phext.remove(update3, coord4)
  assert update4 == "\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'eee' with ''
  coord5 = Coordinate.from_string("1.1.1/1.1.2/1.1.1")
  update5 = phext.remove(update4, coord5)
  assert update5 == "\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'fff' with ''
  coord6 = Coordinate.from_string("1.1.1/1.2.1/1.1.1")
  update6 = phext.remove(update5, coord6)
  assert update6 == "\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ggg' with ''
  coord7 = Coordinate.from_string("1.1.1/2.1.1/1.1.1")
  update7 = phext.remove(update6, coord7)
  assert update7 == "\x1Ehhh\x1Fiii\x01jjj"

  # replace 'hhh' with ''
  coord8 = Coordinate.from_string("1.1.2/1.1.1/1.1.1")
  update8 = phext.remove(update7, coord8)
  assert update8 == "\x1Fiii\x01jjj"

  # replace 'iii' with ''
  coord9 = Coordinate.from_string("1.2.1/1.1.1/1.1.1")
  update9 = phext.remove(update8, coord9)
  assert update9 == "\x01jjj"

  # replace 'jjj' with ''
  coord10 = Coordinate.from_string("2.1.1/1.1.1/1.1.1")
  update10 = phext.remove(update9, coord10)
  assert update10 == ""

def test_range_based_replace():
  phext = Phext()

  doc1 = "Before\x19text to be replaced\x1Calso this\x1Dand this\x17After"
  range1 = Range(Coordinate.from_string("1.1.1/1.1.1/2.1.1"),
                 Coordinate.from_string("1.1.1/2.1.1/1.1.1"))
  update1 = phext.range_replace(doc1, range1, "")
  assert update1 == "Before\x1d\x17After"

  doc2 = "Before\x01Library two\x01Library three\x01Library four"
  range2 = Range(Coordinate.from_string("2.1.1/1.1.1/1.1.1"),
                 Coordinate.from_string("3.1.1/1.1.1/1.1.1"))

  update2 = phext.range_replace(doc2, range2, "")
  assert update2 == "Before\x01\x01\x01Library four"

# note: next_scroll for python just returns the next two frames
def test_next_scroll():
  phext = Phext()
  doc1 = "3A\x17B2\x18C1"
  root = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  temp = phext.next_scroll(doc1, root)
  assert temp[0].coord == root
  assert temp[0].text == "3A"
  assert temp[1].coord == Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  assert temp[1].text == "B2"

def test_last_empty_scroll():
  # a regression discovered from SQ - see https://github.com/wbic16/SQ
  phext = Phext()
  doc1 = "hello\x17world\x17"
  target1 = Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  parts1 = phext.get_subspace_coordinates(doc1, target1)
  assert parts1.start == 6
  assert parts1.end == 11
  assert parts1.best == target1

  test1 = phext.fetch(doc1, target1)
  assert test1 == "world"

def test_merge():
  phext = Phext()
  doc_1a = "3A\x17B2"
  doc_1b = "4C\x17D1"
  update_1 = phext.merge(doc_1a, doc_1b)
  assert update_1 == "3A4C\x17B2D1"

  doc_2a = "Hello \x17I've come to talk"
  doc_2b = "Darkness, my old friend.\x17 with you again."
  update_2 = phext.merge(doc_2a, doc_2b)
  assert update_2 == "Hello Darkness, my old friend.\x17I've come to talk with you again."

  doc_3a = "One\x17Two\x18Three\x19Four"
  doc_3b = "1\x172\x183\x194"
  update_3 = phext.merge(doc_3a, doc_3b)
  assert update_3 == "One1\x17Two2\x18Three3\x19Four4"

  doc_4a = "\x1A\x1C\x1D\x1E\x1F\x01stuff here"
  doc_4b = "\x1A\x1C\x1D\x1Eprecursor here\x1F\x01and more"
  update_4 = phext.merge(doc_4a, doc_4b)
  assert update_4 == "\x1Eprecursor here\x01stuff hereand more"

  doc_5a = "\x01\x01 Library at 3.1.1/1.1.1/1.1.1 \x1F Shelf at 3.2.1/1.1.1/1.1.1"
  doc_5b = "\x01\x01\x01 Library 4.1.1/1.1.1/1.1.1 \x1E Series at 4.1.2/1.1.1/1.1.1"
  update_5 = phext.merge(doc_5a, doc_5b)
  sample = phext.phokenize(update_5)
  for item in sample:
    print(str(item.coord) + ": " + item.text)
  assert update_5 == "\x01\x01 Library at 3.1.1/1.1.1/1.1.1 \x1F Shelf at 3.2.1/1.1.1/1.1.1\x01 Library 4.1.1/1.1.1/1.1.1 \x1E Series at 4.1.2/1.1.1/1.1.1"

  doc_6a = "\x1D Collection at 1.1.1/2.1.1/1.1.1\x1C Volume at 1.1.1/2.2.1/1.1.1"
  doc_6b = "\x1D\x1D Collection at 1.1.1/3.1.1/1.1.1\x1C Volume at 1.1.1/3.2.1/1.1.1"
  update_6 = phext.merge(doc_6a, doc_6b)
  assert update_6 == "\x1D Collection at 1.1.1/2.1.1/1.1.1\x1C Volume at 1.1.1/2.2.1/1.1.1\x1D Collection at 1.1.1/3.1.1/1.1.1\x1C Volume at 1.1.1/3.2.1/1.1.1"

  doc_7a = "\x1ABook #2 Part 1\x1ABook #3 Part 1"
  doc_7b = "\x1A + Part II\x1A + Part Deux"
  update_7 = phext.merge(doc_7a, doc_7b)
  assert update_7 == "\x1ABook #2 Part 1 + Part II\x1ABook #3 Part 1 + Part Deux"

  doc8a = "AA\x01BB\x01CC"
  doc8b = "__\x01__\x01__"
  update8 = phext.merge(doc8a, doc8b)
  assert update8 == "AA__\x01BB__\x01CC__"

def test_subtract():
  phext = Phext()
  doc1a = "Here's scroll one.\x17Scroll two."
  doc1b = "Just content at the first scroll"
  update1 = phext.subtract(doc1a, doc1b)
  assert update1 == "\x17Scroll two."

def test_normalize():
  phext = Phext()
  doc1 = "\x17Scroll two\x18\x18\x18\x18"
  update1 = phext.normalize(doc1)
  assert update1 == "\x17Scroll two"

def test_expand():
  phext = Phext()
  doc1 = "nothing but line breaks\x0Ato test expansion to scrolls\x0Aline 3"
  update1 = phext.expand(doc1)
  assert update1 == "nothing but line breaks\x17to test expansion to scrolls\x17line 3"

  update2 = phext.expand(update1)
  assert update2 == "nothing but line breaks\x18to test expansion to scrolls\x18line 3"

  update3 = phext.expand(update2)
  assert update3 == "nothing but line breaks\x19to test expansion to scrolls\x19line 3"

  update4 = phext.expand(update3)
  assert update4 == "nothing but line breaks\x1Ato test expansion to scrolls\x1Aline 3"

  update5 = phext.expand(update4)
  assert update5 == "nothing but line breaks\x1Cto test expansion to scrolls\x1Cline 3"

  update6 = phext.expand(update5)
  assert update6 == "nothing but line breaks\x1Dto test expansion to scrolls\x1Dline 3"

  update7 = phext.expand(update6)
  assert update7 == "nothing but line breaks\x1Eto test expansion to scrolls\x1Eline 3"

  update8 = phext.expand(update7)
  assert update8 == "nothing but line breaks\x1Fto test expansion to scrolls\x1Fline 3"

  update9 = phext.expand(update8)
  assert update9 == "nothing but line breaks\x01to test expansion to scrolls\x01line 3"

  update10 = phext.expand(update9)
  assert update10 == "nothing but line breaks\x01to test expansion to scrolls\x01line 3"

def test_contract():
  phext = Phext()
  doc1 = "A more complex example than expand\x01----\x1F++++\x1E____\x1Doooo\x1C====\x1Azzzz\x19gggg\x18....\x17qqqq"
  update1 = phext.contract(doc1)
  assert update1 == "A more complex example than expand\x1F----\x1E++++\x1D____\x1Coooo\x1A====\x19zzzz\x18gggg\x17....\x0Aqqqq"

  update2 = phext.contract(update1)
  assert update2 == "A more complex example than expand\x1E----\x1D++++\x1C____\x1Aoooo\x19====\x18zzzz\x17gggg\x0A....\x0Aqqqq"

def test_fs_read_write():
  phext = Phext()

  initial = "a simple phext doc with three scrolls\x17we just want to verify\x17that all of our breaks are making it through python's fs layer.\x18section 2\x19chapter 2\x1Abook 2\x1Cvolume 2\x1Dcollection 2\x1Eseries 2\x1Fshelf 2\x01library 2"
  filename = "unit-test.phext"
  with open(filename, "w", encoding="utf-8") as file:
    file.write(initial)
  with open(filename, "r", encoding="utf-8") as file:
    verify = file.read()

  assert verify == initial
  coordinate = Coordinate.from_string("2.1.1/1.1.1/1.1.1")
  message = phext.replace(verify, coordinate, "still lib 2")
  assert message == "a simple phext doc with three scrolls\x17we just want to verify\x17that all of our breaks are making it through python's fs layer.\x18section 2\x19chapter 2\x1Abook 2\x1Cvolume 2\x1Dcollection 2\x1Eseries 2\x1Fshelf 2\x01still lib 2"

def test_replace_create():
  phext = Phext()
  initial = "A\x17B\x17C\x18D\x19E\x1AF\x1CG\x1DH\x1EI\x1FJ\x01K"
  coordinate = Coordinate.from_string("3.1.1/1.1.1/1.1.1")
  message = phext.replace(initial, coordinate, "L")
  assert message == "A\x17B\x17C\x18D\x19E\x1AF\x1CG\x1DH\x1EI\x1FJ\x01K\x01L"

def test_summary():
  phext = Phext()
  doc1 = "A short phext\nSecond line\x17second scroll.............................";
  update1 = phext.create_summary(doc1);
  assert update1 == "A short phext..."

  doc2 = "very terse";
  update2 = phext.create_summary(doc2);
  assert update2 == "very terse"

def test_navmap():
  phext = Phext()
  example = "Just a couple of scrolls.\x17Second scroll\x17Third scroll"
  result = phext.navmap("http://127.0.0.1/api/v1/index/", example)
  assert result == "<ul>\n<li><a href=\"http://127.0.0.1/api/v1/index/1.1.1;1.1.1;1.1.1\">1.1.1/1.1.1/1.1.1 Just a couple of scrolls.</a></li>\n<li><a href=\"http://127.0.0.1/api/v1/index/1.1.1;1.1.1;1.1.2\">1.1.1/1.1.1/1.1.2 Second scroll</a></li>\n<li><a href=\"http://127.0.0.1/api/v1/index/1.1.1;1.1.1;1.1.3\">1.1.1/1.1.1/1.1.3 Third scroll</a></li>\n</ul>\n"

def test_textmap():
  phext = Phext()
  example = "Just a couple of scrolls.\x17Second scroll\x17Third scroll"
  result = phext.textmap(example)
  assert result == "* 1.1.1/1.1.1/1.1.1: Just a couple of scrolls.\n* 1.1.1/1.1.1/1.1.2: Second scroll\n* 1.1.1/1.1.1/1.1.3: Third scroll\n"

def test_larger_coordinates():
  phext = Phext()
  coord = Coordinate.from_string("111.222.333/444.555.666/777.888.999")
  result = phext.insert("", coord, "Hello World")
  map = phext.textmap(result)
  assert len(result) == 4997
  assert map == "* 111.222.333/444.555.666/777.888.999: Hello World\n"

def test_phext_index():
  phext = Phext()
  example = "first scroll\x17second scroll\x18second section\x19second chapter\x1Abook 2\x1Cvolume 2\x1Dcollection 2\x1Eseries 2\x1Fshelf 2\x01library 2"
  result = phext.index(example)
  assert result == "0\x1713\x1827\x1942\x1a57\x1c64\x1d73\x1e86\x1f95\x01103"

  coord1 = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  test1 = phext.offset(example, coord1)
  assert test1 == 0

  coord2 = Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  test2 = phext.offset(example, coord2)
  assert test2 == 13

  coord3 = Coordinate.from_string("1.1.1/1.1.1/1.2.1")
  test3 = phext.offset(example, coord3)
  assert test3 == 27

  coord4 = Coordinate.from_string("1.1.1/1.1.1/2.1.1")
  test4 = phext.offset(example, coord4)
  assert test4 == 42

  coord5 = Coordinate.from_string("1.1.1/1.1.2/1.1.1")
  test5 = phext.offset(example, coord5)
  assert test5 == 57

  coord6 = Coordinate.from_string("1.1.1/1.2.1/1.1.1")
  test6 = phext.offset(example, coord6)
  assert test6 == 64

  coord7 = Coordinate.from_string("1.1.1/2.1.1/1.1.1")
  test7 = phext.offset(example, coord7)
  assert test7 == 73

  coord8 = Coordinate.from_string("1.1.2/1.1.1/1.1.1")
  test8 = phext.offset(example, coord8)
  assert test8 == 86

  coord9 = Coordinate.from_string("1.2.1/1.1.1/1.1.1")
  test9 = phext.offset(example, coord9)
  assert test9 == 95

  coord9 = Coordinate.from_string("2.1.1/1.1.1/1.1.1")
  test9 = phext.offset(example, coord9)
  assert test9 == 103

  coord_invalid = Coordinate.from_string("2.1.1/1.1.1/1.2.1")
  test_invalid = phext.offset(example, coord_invalid)
  assert test_invalid == 103

  assert len(example) == 112

def test_scroll_manifest():
  phext = Phext()
  example = "first scroll\x17second scroll\x18second section\x19second chapter\x1Abook 2\x1Cvolume 2\x1Dcollection 2\x1Eseries 2\x1Fshelf 2\x01library 2";
  result = phext.manifest(example);

  scroll0 = "00000000000000000000"
  hash0 = phext.checksum(scroll0)
  assert hash0, "7e79edd92a62a048e1cd24ffab542e34"

  scroll1 = "first scroll"
  hash1 = phext.checksum(scroll1)
  assert hash1, "ba9d944e4967e29d48bae69ac2999699"

  scroll2 = "second scroll"
  hash2 = phext.checksum(scroll2)
  assert hash2, "2fe1b2040314ac66f132dd3b4926157c"

  scroll3 = "second section"
  hash3 = phext.checksum(scroll3)
  assert hash3, "fddb6916753b6f4e0b5281469134778b"

  scroll4 = "second chapter"
  hash4 = phext.checksum(scroll4)
  assert hash4, "16ab5b1a0a997db95ec215a3bf2c57b3"

  scroll5 = "book 2"
  hash5 = phext.checksum(scroll5)
  assert hash5, "0f20f79bf36f63e8fba25cc6765e2d0d"

  scroll6 = "volume 2"
  hash6 = phext.checksum(scroll6)
  assert hash6, "7ead0c6fef43adb446fe3bda6fb0adc7"

  scroll7 = "collection 2"
  hash7 = phext.checksum(scroll7)
  assert hash7, "78c12298931c6edede92962137a9280a"

  scroll8 = "series 2"
  hash8 = phext.checksum(scroll8)
  assert hash8, "0f35100c84df601a490b7b63d7e8c0a8"

  scroll9 = "shelf 2"
  hash9 = phext.checksum(scroll9)
  assert hash9, "3bbf7e67cb33d613a906bc5a3cbefd95"

  scroll10 = "library 2"
  hash10 = phext.checksum(scroll10)
  assert hash10, "2e7fdd387196a8a2706ccb9ad6792bc3"

  expected = f"{hash1}\x17{hash2}\x18{hash3}\x19{hash4}\x1A{hash5}\x1C{hash6}\x1D{hash7}\x1E{hash8}\x1F{hash9}\x01{hash10}"
  assert result, expected

def test_phext_soundex_v1():
  phext = Phext()
  sample = "it was the best of scrolls\x17it was the worst of scrolls\x17aaa\x17bbb\x17ccc\x17ddd\x17eee\x17fff\x17ggg\x17hhh\x17iii\x17jjj\x17kkk\x17lll\x18mmm\x18nnn\x18ooo\x18ppp\x19qqq\x19rrr\x19sss\x19ttt\x1auuu\x1avvv\x1awww\x1axxx\x1ayyy\x1azzz"
  result = phext.soundex_v1(sample)
  assert result == "36\x1741\x171\x174\x177\x1710\x171\x174\x177\x171\x171\x177\x177\x1713\x1816\x1816\x181\x184\x197\x1919\x197\x1910\x1a1\x1a4\x1a1\x1a7\x1a1\x1a7"

def test_insert_performance_2k_scrolls():
  phext = Phext()
  doc1 = "the quick brown fox jumped over the lazy dog";
  next = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  result = []

  start = datetime.now()
  x = 0
  while x < 2000:
    x += 1
    if next.scroll > 32:
      next.sectionBreak()
    if next.section > 32:
      next.chapterBreak()
    if next.chapter > 32:
      next.bookBreak()
    ith = PositionedScroll(deepcopy(next), doc1)
    result.append(ith)
    next.scrollBreak()

  result = phext.dephokenize(result)
  end = datetime.now()
  duration = end - start
  elapsed_ms = int((duration).total_seconds() * 1000)
  print("Performance-2K: " + str(elapsed_ms))

  # require at most 2.5ms per scroll on an i9-13900HX
  assert elapsed_ms < 5000

  expected = Coordinate.from_string("1.1.1/1.1.1/2.31.17")
  assert next == expected

  expected_doc1_length = 44
  assert len(doc1) == expected_doc1_length
  phext_tokens = 0
  scroll_breaks = 0
  section_breaks = 0
  chapter_breaks = 0
  for byte in result:
    if phext.isPhextBreak(byte):
      phext_tokens += 1
    if byte == phext.SCROLL_BREAK:
      scroll_breaks += 1
    if byte == phext.SECTION_BREAK:
      section_breaks += 1
    if byte == phext.CHAPTER_BREAK:
      chapter_breaks += 1

  expected_tokens = 1999
  assert phext_tokens == expected_tokens
  assert scroll_breaks == 1937
  assert section_breaks == 61
  assert chapter_breaks == 1

  expected_length = 2000 * expected_doc1_length + expected_tokens
  assert len(result) == expected_length

# TODO: might have perf regressions - not sure yet
#def test_insert_performance_medium_scrolls():
#  phext = Phext()
#  doc_template = "the quick brown fox jumped over the lazy dog\n"
#  doc1 = ""
#  doc1 = doc_template * 1000
#  
#  next = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
#  result: dict[int, str] = {}
#  x = 0
#  while x < 25:
#    result[x] = ""
#    x += 1
#
#  start = datetime.now()
#  x = 0
#  while x < 25:
#    x += 1
#    if next.scroll > 5:
#      next.sectionBreak()
#    if next.section > 5:
#      next.sectionBreak()
#    if next.chapter > 5:
#      next.chapterBreak()
#    result[x] = phext.insert(result[x-1], next, doc1)
#    next.scrollBreak()
#
#  end = datetime.now()
#  duration = end - start
#  elapsed_ms = int((duration).total_seconds() * 1000)
#  print("Performance-Medium: " + str(elapsed_ms))
#
#  assert elapsed_ms < 1000
#
#  expected = Coordinate.from_string("1.1.1/1.1.1/1.5.6")
#  assert next == expected
#
#  expected_doc1_length = 45000 # counting line breaks
#  assert len(result) == expected_doc1_length
#
#  # 2000 scrolls should be separated by 1999 delimiters
#  phext_tokens = 0
#  line_breaks = 0
#  scroll_breaks = 0
#  section_breaks = 0
#  chapter_breaks = 0
#
#  for byte in result:
#    if phext.isPhextBreak(byte):
#      phext_tokens += 1
#    if byte == phext.LINE_BREAK:
#      line_breaks += 1
#    if byte == phext.SCROLL_BREAK:
#      scroll_breaks += 1
#    if byte == phext.SECTION_BREAK:
#      section_breaks += 1
#    if byte == phext.CHAPTER_BREAK:
#      chapter_breaks += 1
#  expected_tokens = 25024
#  assert phext_tokens == expected_tokens
#
#  assert line_breaks == 25000
#  assert scroll_breaks == 20
#  assert section_breaks == 4
#  assert chapter_breaks == 0
#
#  # doc1 * 1000 + delimiter count
#  expected_length = 25 * (expected_doc1_length-1000) + expected_tokens
#  assert len(result) == expected_length
#  
#  assert False

def test_hash_support():
  phext = Phext()
  stuff = phext.explode("hello world\x17\x17\x17scroll 4\x01Library 2")
  scroll1_address = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  scroll2_address = Coordinate.from_string("1.1.1/1.1.1/1.1.4")
  scroll3_address = Coordinate.from_string("2.1.1/1.1.1/1.1.1")
  assert stuff[scroll1_address] == "hello world"
  assert stuff[scroll2_address] == "scroll 4"
  assert stuff[scroll3_address] == "Library 2"

  scroll4_address = Coordinate.from_string("2.3.4/5.6.7/8.9.1")
  stuff[scroll4_address] = "random insertion"

  serialized = phext.implode(stuff)
  assert serialized == "hello world\x17\x17\x17scroll 4\x01Library 2\x1f\x1f\x1e\x1e\x1e\x1d\x1d\x1d\x1d\x1c\x1c\x1c\x1c\x1c\x1a\x1a\x1a\x1a\x1a\x1a\x19\x19\x19\x19\x19\x19\x19\x18\x18\x18\x18\x18\x18\x18\x18random insertion"

# TODO: not implemented upstream either
#def test_subspace_filter():
  # filtering in subspace happens in bands
  # we split the phext into 36 regions
  # each region can be further sub-divided into 32 segments
  # where your scrolls fall into this map determines if they
  # are selected. subspace filtering happens in bitspace.
  # we have 6 bits per region to work with:
  # 0-25:  ABCDEFGHIJKLMNOPQRSTUVWXYZ
  # 26-51: abcdefghijklmnopqrstuvwxyz
  # 52-63: 0123456789+/
  # 
  # 
  # 
  # Collectors (0-15)
  #             A   B   C   D   E   F   G   H
  # First n%:   1   2   4   8  16  32  64 100  [8]
  # Last n%:  100  50  25  12   6   3   2   1  [8]
  #             I   J   K   L   M   N   O   P
  # 
  # Harmonics (16-31)
  #             Q   R   S   T   U   V   W   X
  # Primes 1:   2   3   5   7  11  13  17  19  [8]
  # Primes 2:  23  29  31  37  41  43  47  53  [8]
  #             Y   Z   a   b   c   d   e   f
  # 
  # Scroll Size (32-47)
  #                 g     h   i   j   k   l   m    n
  # Smaller Than:  1K    2K  4K  8K 16K 32K 64K 128K [8]
  # Larger Than:   128K 64K 32K 16K  8K  4K  2K   1K [8]
  #                 o     p   q   r   s   t   u    v
  # 
  # Reserved (48-63)
  #                 w   x   y   z   0   1   2   3
  # TBD                                              [8]
  # TBD                                              [8]
  #                 4   5   6   7   8   9   +   /
  # 
  # 36 characters in base64
  # 
  # TODO: create a suite of test filters and verify they select
  # properly

# TODO: not implemented upstream either
#def test_macrophext():
  # maybe add \x02 and \x03 support for very large phexts...?
  # assert False

def test_phext_breaks():
  phext = Phext()
  assert phext.isPhextBreak("\n")
  assert phext.isPhextBreak("\x01")
  assert phext.isPhextBreak("\x17")
  assert phext.isPhextBreak("\x18")
  assert phext.isPhextBreak("\x19")
  assert phext.isPhextBreak("\x1a")
  assert phext.isPhextBreak("\x1c")
  assert phext.isPhextBreak("\x1d")
  assert phext.isPhextBreak("\x1e")
  assert phext.isPhextBreak("\x1f")
  assert phext.isPhextBreak(phext.LINE_BREAK)
  assert phext.isPhextBreak(phext.LIBRARY_BREAK)
  assert phext.isPhextBreak(phext.SHELF_BREAK)
  assert phext.isPhextBreak(phext.SERIES_BREAK)
  assert phext.isPhextBreak(phext.COLLECTION_BREAK)
  assert phext.isPhextBreak(phext.VOLUME_BREAK)
  assert phext.isPhextBreak(phext.BOOK_BREAK)
  assert phext.isPhextBreak(phext.CHAPTER_BREAK)
  assert phext.isPhextBreak(phext.SECTION_BREAK)
  assert phext.isPhextBreak(phext.SCROLL_BREAK)

def test_normalize():
  phext = Phext()
  doc1 = "\x17Scroll two\x18\x18\x18\x18"
  update1 = phext.normalize(doc1)
  assert update1 == "\x17Scroll two"