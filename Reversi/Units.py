#!/usr/bin/env python3


from PyQt5.QtGui import QImage
import copy


class Unit:

    def __init__(self, coordinates, image):
        self._coordinates = coordinates
        self._image = image

    @property
    def coordinates(self):
        return self._coordinates

    @property
    def image(self):
        return self._image


class Cell(Unit):

    NORMAL = QImage('images/Cell.png')
    HIGHLIGHTED = QImage('images/HighlightedCell.png')

    def __init__(self, coordinates):
        super().__init__(coordinates, self.NORMAL)

    def highlight(self):
        self._image = self.HIGHLIGHTED

    def normalize(self):
        self._image = self.NORMAL

    def __deepcopy__(self, memodict={}):
        cell_copy = Cell(copy.deepcopy(self._coordinates))
        cell_copy._image = self._image
        return cell_copy


class Checker(Unit):

    WHITE = QImage('images/WhiteChecker.png')
    BLACK = QImage('images/BlackChecker.png')

    def __init__(self, coordinates, is_white):
        super().__init__(coordinates, self.WHITE if is_white else self.BLACK)
        self.__is_white = is_white

    @property
    def is_white(self):
        return self.__is_white

    def change_color(self):
        self._image = self.BLACK if self.__is_white else self.WHITE
        self.__is_white = not self.__is_white

    def __deepcopy__(self, memodict={}):
        return Checker(copy.deepcopy(self._coordinates), copy.deepcopy(self.__is_white))

    def __eq__(self, other):
        return self.coordinates == other.coordinates and self.is_white == other.is_white

    def __str__(self):
        color = 'White' if self.is_white else 'Black'
        return f'Checker({self.coordinates.x}, {self.coordinates.y}, {color})'
