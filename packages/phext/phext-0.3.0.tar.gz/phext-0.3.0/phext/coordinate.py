from dataclasses import dataclass
from functools import total_ordering

@total_ordering
@dataclass
class Coordinate:
    library: int
    shelf: int
    series: int
    collection: int
    volume: int
    book: int
    chapter: int
    section: int
    scroll: int

    @classmethod
    def from_string(ignored, coord_str: str):
        try:
            parts = coord_str.strip().split("/")
            if len(parts) != 3:
                raise ValueError("Coordinate must conform to Phext Standard Addressing")

            nums = []
            for part in parts:
                nums.extend(int(x) for x in part.split("."))

            if len(nums) != 9:
                raise ValueError("Coordinate must have exactly 9 numeric parts")

            if any(n < 1 or n > 999 for n in nums):
                raise ValueError("All coordinate values must be between 1 and 999")

            return Coordinate(nums[0], nums[1], nums[2], nums[3], nums[4], nums[5], nums[6], nums[7], nums[8])

        except Exception as e:
            raise ValueError(f"Invalid coordinate string: {coord_str} {e}") from e

    def libraryBreak(self):
        self.library += 1
        self.shelf = 1
        self.series = 1
        self.collection = 1
        self.volume = 1
        self.book = 1
        self.chapter = 1
        self.section = 1
        self.scroll = 1

    def shelfBreak(self):
        self.shelf += 1
        self.series = 1
        self.collection = 1
        self.volume = 1
        self.book = 1
        self.chapter = 1
        self.section = 1
        self.scroll = 1

    def seriesBreak(self):
        self.series += 1
        self.collection = 1
        self.volume = 1
        self.book = 1
        self.chapter = 1
        self.section = 1
        self.scroll = 1

    def collectionBreak(self):
        self.collection += 1
        self.volume = 1
        self.book = 1
        self.chapter = 1
        self.section = 1
        self.scroll = 1

    def volumeBreak(self):
        self.volume += 1
        self.book = 1
        self.chapter = 1
        self.section = 1
        self.scroll = 1

    def bookBreak(self):
        self.book += 1
        self.chapter = 1
        self.section = 1
        self.scroll = 1

    def chapterBreak(self):
        self.chapter += 1
        self.section = 1
        self.scroll = 1

    def sectionBreak(self):
        self.section += 1
        self.scroll = 1

    def scrollBreak(self):
        self.scroll += 1
    
    def __init__(self, lb, sf, sr, cn, vm, bk, ch, sn, sc):
        self.library = int(lb)
        self.shelf = int(sf)
        self.series = int(sr)
        self.collection = int(cn)
        self.volume = int(vm)
        self.book = int(bk)
        self.chapter = int(ch)
        self.section = int(sn)
        self.scroll = int(sc)

    def copy_coordinate(self, other):
        self.library = int(other.library)
        self.shelf = int(other.shelf)
        self.series = int(other.series)
        self.collection = int(other.collection)
        self.volume = int(other.volume)
        self.book = int(other.book)
        self.chapter = int(other.chapter)
        self.section = int(other.section)
        self.scroll = int(other.scroll)

    def __str__(self) -> str:
        return f"{self.library}.{self.shelf}.{self.series}/" \
               f"{self.collection}.{self.volume}.{self.book}/" \
               f"{self.chapter}.{self.section}.{self.scroll}"
    
    def urlencoded(self) -> str:
        return f"{self.library}.{self.shelf}.{self.series};" \
               f"{self.collection}.{self.volume}.{self.book};" \
               f"{self.chapter}.{self.section}.{self.scroll}"
    
    def __eq__(self, other):
        return isinstance(self, Coordinate) and isinstance(other, Coordinate) and self.library == other.library and self.shelf == other.shelf and self.series == other.series and self.collection == other.collection and self.volume == other.volume and self.book == other.book and self.chapter == other.chapter and self.section == other.section and self.scroll == other.scroll
    
    def __lt__(self, other):
        if not isinstance(other, Coordinate):
            return NotImplemented
        return self.as_tuple() < other.as_tuple()
    
    def as_tuple(self) -> tuple:
        return (
            self.library, self.shelf, self.series,
            self.collection, self.volume, self.book,
            self.chapter, self.section, self.scroll
        )

    def __hash__(self):
        return hash((
            self.library, self.shelf, self.series,
            self.collection, self.volume, self.book,
            self.chapter, self.section, self.scroll
        ))