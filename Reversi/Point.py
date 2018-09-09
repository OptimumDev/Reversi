#!/usr/bin/env python3


from math import sqrt
import copy
import re


class Point:

    STRING_PARSER = re.compile(r'Point\((?P<x>\d+), (?P<y>\d+)\)')

    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __copy__(self):
        return Point(self.x, self.y)

    def __str__(self):
        return 'Point({}, {})'.format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.__x += other.x
        self.__y += other.y
        return self

    def __deepcopy__(self, memodict={}):
        return Point(copy.deepcopy(self.__x), copy.deepcopy(self.__y))

    @staticmethod
    def from_string(point_string):
        coordinates = Point.STRING_PARSER.search(point_string)
        if coordinates is None or not coordinates['x'].isdecimal() or not coordinates['y'].isdecimal():
            raise ValueError
        return Point(int(coordinates['x']), int(coordinates['y']))

    def move(self, shift):
        self.__x += shift
        self.__y += shift
        return self

    def to_image_coordinates(self, image_size, shift):
        return Point((self.x + shift) * image_size, (self.y + shift) * image_size)

    def to_cell_coordinates(self, image_size, shift):
        return Point(self.x // image_size - shift, self.y // image_size - shift)

    def normalize(self):
        x = 0
        y = 0
        if self.__x != 0:
            x = self.__x // abs(self.__x)
        if self.__y != 0:
            y = self.__y // abs(self.__y)
        return Point(x, y)

    def to_tuple(self):
        return self.__x, self.__y

    def get_distance(self, other):
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    @staticmethod
    def get_directions():
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx != 0 or dy != 0:
                    yield Point(dx, dy)

    def get_nearby_points(self):
        for delta in Point.get_directions():
            yield self + delta
