#!/usr/bin/env python3


import copy
from Point import Point
from Units import Cell, Checker


class Game:
    WHITE = 'White'
    BLACK = 'Black'
    YOU = 'You'
    BOT = 'Bot'
    PLAYER = 'Player'
    BOT_DIFFICULTIES = ['Easy', 'Normal', 'Hard']
    HARD_BOT_INTELLIGENCE = 2

    def __init__(self, *args):
        if len(args) < 2:
            raise ValueError
        is_new_game = args[0]
        if is_new_game:
            if len(args) != 5:
                raise ValueError
        if is_new_game:
            self.__size = args[1]

            self.__white_turn = False
            self.__bot_active = args[2]

            self.BOT_IS_WHITE = args[3]
            self.PLAYER_IS_WHITE = not self.BOT_IS_WHITE
            self.BOT_DIFFICULTY = args[4]

            self.__occupied_coordinates = []
            self.__game_map = self.get_map()

            self.__colored_checkers = {self.WHITE: [], self.BLACK: []}
            self.__checkers = self.get_starting_checkers()
        else:
            load_data = self.load(args[1])

            self.__bot_active = load_data[0]

            self.BOT_DIFFICULTY = load_data[1]
            self.__size = load_data[2]

            self.__white_turn = load_data[3]
            self.PLAYER_IS_WHITE = load_data[3]
            self.BOT_IS_WHITE = not self.PLAYER_IS_WHITE

            self.__occupied_coordinates = []
            self.__game_map = self.get_map()

            self.__colored_checkers = {self.WHITE: [], self.BLACK: []}
            self.__checkers = {}
            for white_checker in load_data[4]:
                self.__colored_checkers[self.WHITE].append(white_checker)
                self.__checkers[white_checker.coordinates.to_tuple()] = white_checker
                self.__occupied_coordinates.append(white_checker.coordinates)
            for black_checker in load_data[5]:
                self.__colored_checkers[self.BLACK].append(black_checker)
                self.__checkers[black_checker.coordinates.to_tuple()] = black_checker
                self.__occupied_coordinates.append(black_checker.coordinates)

        self.__score = {self.WHITE: 0, self.BLACK: 0}
        self.update_score()

        self.__bots = [self.easy_bot_turn, self.normal_bot_turn, self.hard_bot_turn]

    def load(self, file_name):
        load_data = []
        with open(file_name, 'r') as file:
            data = file.read().splitlines()
        if data[0] == 'pvp':
            load_data.append(False)
            load_data.append(0)
        else:
            load_data.append(True)
            load_data.append(int(data[0][-1]))
        load_data.append(int(data[1]))
        load_data.append(data[2] == self.WHITE)
        white_checkers = []
        i = 3
        while len(data[i]) > 0:
            coordinates = data[i].split(' ')
            white_checkers.append(Checker(Point(int(coordinates[0]), int(coordinates[1])), True))
            i += 1
        i += 1
        load_data.append(white_checkers)
        black_checkers = []
        while i < len(data) and len(data[i]) > 0:
            coordinates = data[i].split(' ')
            black_checkers.append(Checker(Point(int(coordinates[0]), int(coordinates[1])), False))
            i += 1
        load_data.append(black_checkers)
        return load_data

    @property
    def bot_active(self):
        return self.__bot_active

    @property
    def is_white_turn(self):
        return self.__white_turn

    @property
    def score(self):
        return self.__score

    @property
    def size(self):
        return self.__size

    @property
    def game_map(self):
        return self.__game_map

    @property
    def checkers(self):
        return self.__checkers.values()

    @property
    def occupied_coordinates(self):
        return self.__occupied_coordinates

    @property
    def is_finished(self):
        return len(self.__checkers) == len(self.__game_map)

    def get_save(self):
        mode = 'pve' + str(self.BOT_DIFFICULTY) if self.__bot_active else 'pvp'
        size = str(self.__size)
        current_turn = self.WHITE if self.__white_turn else self.BLACK
        white_checkers = ''
        for checker in self.__colored_checkers[self.WHITE]:
            coordinates = checker.coordinates
            white_checkers += '{} {}\n'.format(coordinates.x, coordinates.y)
        black_checkers = ''
        for checker in self.__colored_checkers[self.BLACK]:
            coordinates = checker.coordinates
            black_checkers += '{} {}\n'.format(coordinates.x, coordinates.y)
        return '{}\n{}\n{}\n{}\n{}'.format(mode, size, current_turn, white_checkers, black_checkers)

    def is_inside_field(self, coordinates):
        return 0 <= coordinates.x < self.__size and 0 <= coordinates.y < self.__size

    def get_map(self):
        return [Cell(Point(x, y)) for x in range(self.__size) for y in range(self.__size)]

    def get_starting_checkers(self):
        middle = self.__size // 2
        checkers_dict = {}
        checkers = [Checker(Point(middle - 1, middle - 1), True),
                    Checker(Point(middle, middle - 1), False),
                    Checker(Point(middle - 1, middle), False),
                    Checker(Point(middle, middle), True)]
        for checker in checkers:
            checkers_dict[checker.coordinates.to_tuple()] = checker
            self.__occupied_coordinates.append(checker.coordinates)
            if checker.is_white:
                self.__colored_checkers[self.WHITE].append(checker)
            else:
                self.__colored_checkers[self.BLACK].append(checker)
        return checkers_dict

    def check_turn(self, coordinates, color=None):
        if color is None:
            color = self.is_white_turn
        return len(self.get_enemies_around(Checker(coordinates, color))) > 0

    def pass_turn(self):
        self.__white_turn = not self.__white_turn

    def make_turn(self, coordinates):
        self.add_checker(coordinates, self.is_white_turn)
        self.pass_turn()

    def bot_turn(self):
        return self.__bots[self.BOT_DIFFICULTY]()

    def easy_bot_turn(self):
        for cell in self.__game_map:
            if cell.coordinates not in self.__occupied_coordinates:
                enemies = self.get_enemies_around(Checker(cell.coordinates, self.BOT_IS_WHITE))
                if len(enemies) > 0:
                    self.add_checker(cell.coordinates, self.BOT_IS_WHITE)
                    self.pass_turn()
                    return cell.coordinates
        self.pass_turn()
        return None

    def normal_bot_turn(self):
        max_enemies = []
        best_position = Point(0, 0)
        for cell in self.__game_map:
            if cell.coordinates not in self.__occupied_coordinates:
                enemies = self.get_enemies_around(Checker(cell.coordinates, self.BOT_IS_WHITE))
                if len(enemies) >= len(max_enemies):
                    max_enemies = enemies
                    best_position = cell.coordinates
        self.pass_turn()
        if len(max_enemies) == 0:
            return None
        self.add_checker(best_position, self.BOT_IS_WHITE)
        return best_position

    def hard_bot_turn(self):
        map_copy = self.copy_current_state()
        possible_turns = self.get_possible_turns()
        best_variant_score = 0
        best_turn = None
        for turn in possible_turns:
            score = self.check_bot_turn(turn)
            self.use_copy(map_copy)
            if score > best_variant_score:
                best_variant_score = score
                best_turn = turn
        self.pass_turn()
        return best_turn

    def check_bot_turn(self, turn, turn_number=0):
        turn_number += 1
        bot_color = self.WHITE if self.BOT_IS_WHITE else self.BLACK
        map_copy = self.copy_current_state()
        self.make_turn(turn)
        possible_turns = self.get_possible_turns()
        if turn_number == (self.HARD_BOT_INTELLIGENCE - 1) * 2 or len(possible_turns) == 0:
            return self.__score[bot_color]
        best_variant_score = 0
        for turn in possible_turns:
            score = self.check_bot_turn(turn, turn_number)
            self.use_copy(map_copy)
            if score > best_variant_score:
                best_variant_score = score
        return best_variant_score

    def copy_current_state(self):
        return copy.deepcopy([copy.deepcopy(self.__game_map),
                              self.__score,
                              self.__occupied_coordinates,
                              self.__checkers,
                              self.__colored_checkers,
                              self.__white_turn])

    def use_copy(self, map_copy):
        self.__game_map = map_copy[0]
        self.__score = map_copy[1]
        self.__occupied_coordinates = map_copy[2]
        self.__checkers = map_copy[3]
        self.__colored_checkers = map_copy[4]
        self.__white_turn = map_copy[5]

    def get_possible_turns(self):
        possible_turns = []
        for cell in self.__game_map:
            if cell.coordinates not in self.__occupied_coordinates and self.check_turn(cell.coordinates):
                possible_turns.append(cell.coordinates)
        return possible_turns

    def get_enemies_around(self, checker):
        enemies = []
        for direction in Point.get_directions():
            enemies += self.get_enemies(checker, direction)
        return enemies

    def add_checker(self, coordinates, is_white):
        color = self.WHITE if is_white else self.BLACK
        checker = Checker(coordinates, is_white)
        self.__score[color] += 1
        self.__occupied_coordinates.append(coordinates)
        self.__checkers[coordinates.to_tuple()] = checker
        if is_white:
            self.__colored_checkers[self.WHITE].append(checker)
        else:
            self.__colored_checkers[self.BLACK].append(checker)
        self.change_enemies_color(checker)

    def get_checker_at(self, coordinates):
        key = coordinates.to_tuple()
        if key in self.__checkers:
            return self.__checkers[key]
        return None

    def get_enemies(self, checker, direction):
        enemies = []
        enemy_coordinates = checker.coordinates + direction
        while self.is_inside_field(enemy_coordinates) and self.get_checker_at(enemy_coordinates) is not None \
                and self.get_checker_at(enemy_coordinates).is_white != checker.is_white:
            enemies.append(self.get_checker_at(enemy_coordinates))
            enemy_coordinates += direction
        return enemies if self.is_inside_field(enemy_coordinates) and \
                          self.get_checker_at(enemy_coordinates) is not None else []

    def change_enemies_color(self, checker):
        color = self.WHITE if checker.is_white else self.BLACK
        enemy_color = self.WHITE if not checker.is_white else self.BLACK
        for enemy in self.get_enemies_around(checker):
            self.__colored_checkers[enemy_color].remove(enemy)
            self.__colored_checkers[color].append(enemy)
            self.update_score()
            enemy.change_color()

    def update_score(self):
        self.__score[self.WHITE] = len(self.__colored_checkers[self.WHITE])
        self.__score[self.BLACK] = len(self.__colored_checkers[self.BLACK])
