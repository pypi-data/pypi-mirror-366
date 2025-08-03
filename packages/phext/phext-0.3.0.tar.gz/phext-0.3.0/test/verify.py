import phext
from phext.coordinate import Coordinate
from phext.range import Range
from phext.phext import Phext
coord = Coordinate.from_string("1.2.3/4.5.6/7.8.9")
phext = Phext()
buffer = phext.update("", coord, "Hello World")
print(buffer)
