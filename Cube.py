# First edge color will be on <UDFB> and second color will be on <RL>
# Order for corner colors is U/D, F/B, then R/L
import re
import abc
import time
from math import ceil

YEL = 0
GRE = 1
ORA = 2
BLU = 3
RED = 4
WHI = 5
TOP = 0
FRONT = 1
SIDE = 2


class Cubie:
    def __init__(self, position=None, real_pos=None, colors=None):
        self.position = position
        self.real_pos = real_pos
        self.colors = colors
        self.org_colors = colors
        self.twist_dir = 0

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    def get_real_pos(self):
        return self.real_pos

    def set_real_pos(self, real_pos):
        self.real_pos = real_pos

    def get_color(self, orientation):
        return self.colors[orientation]

    def set_colors(self, colors):
        self.colors = colors

    @abc.abstractmethod
    def get_side(self, color):
        pass

    def is_solved(self):
        return True if self.real_pos == self.position else False

    @abc.abstractmethod
    def is_twisted(self):
        pass

    @abc.abstractmethod
    def set_twist_dir(self):
        pass

    def get_twist_dir(self):
        return self.twist_dir

    def get_org_color(self, sticker):
        return self.org_colors[sticker]

    def set_org_colors(self):
        self.org_colors = tuple(self.colors)

    def __str__(self):
        is_center = False
        if self.colors is None:
            is_center = True
        # return str(self.position) + " " + str(self.colors) if not is_center else "CENTER"
        return str(self.position)


class Corner(Cubie):
    def __init__(self, position=None, real_pos=None, colors=None):
        super().__init__(position, real_pos, colors)

    def get_side(self, color):
        color_map = {YEL: 0, WHI: 0, ORA: 1, RED: 1, GRE: 2, BLU: 2}
        return color_map.get(color)

    def is_twisted(self):
        condition = self.colors[TOP] not in (YEL, WHI)
        return condition

    def set_twist_dir(self):
        top_dir = self.colors.index(self.get_org_color(TOP))
        dir1 = ([0, 0, 0], [0, 2, 2], [2, 2, 0], [2, 0, 2])
        if self.is_twisted():
            if top_dir == FRONT:
                self.twist_dir = 0 if self.real_pos in dir1 else 1
            elif top_dir == SIDE:
                self.twist_dir = 1 if self.real_pos in dir1 else 0
        else:
            self.twist_dir = -1

    def __str__(self):
        color_map = {0: "YEL", 1: "GRE", 2: "ORA", 3: "BLU", 4: "RED", 5: "WHI"}
        return color_map.get(self.colors[0]) + "/ " + color_map.get(self.colors[1]) + "/ " + color_map.get(
            self.colors[2])


class Edge(Cubie):
    def __init__(self, position=None, real_pos=None, colors=None):
        super().__init__(position, real_pos, colors)

    def get_side(self, color):
        color_map = {YEL: 0, WHI: 0, ORA: 0, RED: 0, GRE: 1, BLU: 1}
        return color_map.get(color)

    def is_twisted(self):
        condition = False
        if self.position in ([0, 1, 0], [1, 2, 0], [2, 1, 0], [1, 0, 0], [0, 1, 2], [1, 2, 2], [2, 1, 2], [1, 0, 2]):
            condition = False if self.colors[FRONT] in (GRE, BLU) else True
        elif self.position in ([0, 0, 1], [0, 2, 1], [2, 2, 1], [2, 0, 1]):
            condition = False if self.colors[TOP] in (WHI, YEL) else True
        return condition

    def set_twist_dir(self):
        pass

    def __str__(self):
        color_map = {0: "YEL", 1: "GRE", 2: "ORA", 3: "BLU", 4: "RED", 5: "WHI"}
        return color_map.get(self.colors[0]) + "/ " + color_map.get(self.colors[1])


class Cube:
    def __init__(self):
        self.cubie_array = [[[Cubie() for i in range(3)] for j in range(3)] for k in range(3)]
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    if i % 2 == 0 and j % 2 == 0 and k % 2 == 0:
                        self.cubie_array[i][j][k] = Corner([i, j, k], [i, j, k])
                    elif ((i % 2) + (j % 2) + (k % 2)) > 1:
                        pass
                    else:
                        self.cubie_array[i][j][k] = Edge([i, j, k], [i, j, k])

        self.traced_pieces = []
        self.traced_edges = []
        self.twists = []
        self.flips = []
        self.parity = False

        # U layer corners
        self.cubie_array[0][0][0].set_colors([YEL, RED, GRE])
        self.cubie_array[0][0][2].set_colors([YEL, RED, BLU])
        self.cubie_array[0][2][0].set_colors([YEL, ORA, GRE])
        self.cubie_array[0][2][2].set_colors([YEL, ORA, BLU])

        # D layer corners
        self.cubie_array[2][0][0].set_colors([WHI, RED, GRE])
        self.cubie_array[2][0][2].set_colors([WHI, RED, BLU])
        self.cubie_array[2][2][0].set_colors([WHI, ORA, GRE])
        self.cubie_array[2][2][2].set_colors([WHI, ORA, BLU])

        # U layer edges
        self.cubie_array[0][0][1].set_colors([YEL, RED])
        self.cubie_array[0][1][0].set_colors([YEL, GRE])
        self.cubie_array[0][1][2].set_colors([YEL, BLU])
        self.cubie_array[0][2][1].set_colors([YEL, ORA])

        # E layer edges
        self.cubie_array[1][0][0].set_colors([RED, GRE])
        self.cubie_array[1][0][2].set_colors([RED, BLU])
        self.cubie_array[1][2][0].set_colors([ORA, GRE])
        self.cubie_array[1][2][2].set_colors([ORA, BLU])

        # D layer edges
        self.cubie_array[2][0][1].set_colors([WHI, RED])
        self.cubie_array[2][1][0].set_colors([WHI, GRE])
        self.cubie_array[2][1][2].set_colors([WHI, BLU])
        self.cubie_array[2][2][1].set_colors([WHI, ORA])

        for layer in self.cubie_array:
            for column in layer:
                for piece in column:
                    if type(piece) == Corner or type(piece) == Edge:
                        piece.set_org_colors()

    ###############################################################

    def update_pos(self):
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    self.cubie_array[i][j][k].set_real_pos([i, j, k])

    def scramble(self, scramble):
        moves = scramble.split()
        for move in moves:
            self.move(move)

    def move(self, move):
        move_map = {
            "U": self.u,
            "U'": self.ui,
            "U2": self.u2,
            "D": self.d,
            "D'": self.di,
            "D2": self.d2,
            "L": self.l,
            "L'": self.li,
            "L2": self.l2,
            "R": self.r,
            "R'": self.ri,
            "R2": self.r2,
            "F": self.f,
            "F'": self.fi,
            "F2": self.f2,
            "B": self.b,
            "B'": self.bi,
            "B2": self.b2,
        }
        meth = move_map.get(move)
        meth()

    ###############################################################

    def u(self):
        topleft = self.cubie_array[0][0][0]
        topright = self.cubie_array[0][0][2]
        bottomright = self.cubie_array[0][2][2]
        bottomleft = self.cubie_array[0][2][0]

        topleft.set_colors([topleft.get_color(TOP), topleft.get_color(SIDE), topleft.get_color(FRONT)])
        topright.set_colors([topright.get_color(TOP), topright.get_color(SIDE), topright.get_color(FRONT)])
        bottomright.set_colors([bottomright.get_color(TOP), bottomright.get_color(SIDE), bottomright.get_color(FRONT)])
        bottomleft.set_colors([bottomleft.get_color(TOP), bottomleft.get_color(SIDE), bottomleft.get_color(FRONT)])

        temp = self.cubie_array[0][0][0]
        self.cubie_array[0][0][0] = self.cubie_array[0][2][0]
        self.cubie_array[0][2][0] = self.cubie_array[0][2][2]
        self.cubie_array[0][2][2] = self.cubie_array[0][0][2]
        self.cubie_array[0][0][2] = temp

        temp = self.cubie_array[0][0][1]
        self.cubie_array[0][0][1] = self.cubie_array[0][1][0]
        self.cubie_array[0][1][0] = self.cubie_array[0][2][1]
        self.cubie_array[0][2][1] = self.cubie_array[0][1][2]
        self.cubie_array[0][1][2] = temp

        self.update_pos()

    def ui(self):
        topleft = self.cubie_array[0][0][0]
        topright = self.cubie_array[0][0][2]
        bottomright = self.cubie_array[0][2][2]
        bottomleft = self.cubie_array[0][2][0]

        topleft.set_colors([topleft.get_color(TOP), topleft.get_color(SIDE), topleft.get_color(FRONT)])
        topright.set_colors([topright.get_color(TOP), topright.get_color(SIDE), topright.get_color(FRONT)])
        bottomright.set_colors([bottomright.get_color(TOP), bottomright.get_color(SIDE), bottomright.get_color(FRONT)])
        bottomleft.set_colors([bottomleft.get_color(TOP), bottomleft.get_color(SIDE), bottomleft.get_color(FRONT)])

        temp = self.cubie_array[0][0][0]
        self.cubie_array[0][0][0] = self.cubie_array[0][0][2]
        self.cubie_array[0][0][2] = self.cubie_array[0][2][2]
        self.cubie_array[0][2][2] = self.cubie_array[0][2][0]
        self.cubie_array[0][2][0] = temp

        temp = self.cubie_array[0][0][1]
        self.cubie_array[0][0][1] = self.cubie_array[0][1][2]
        self.cubie_array[0][1][2] = self.cubie_array[0][2][1]
        self.cubie_array[0][2][1] = self.cubie_array[0][1][0]
        self.cubie_array[0][1][0] = temp

        self.update_pos()

    def u2(self):
        self.u()
        self.u()

        self.update_pos()

    ################################################################

    def d(self):
        topleft = self.cubie_array[2][0][0]
        topright = self.cubie_array[2][0][2]
        bottomright = self.cubie_array[2][2][2]
        bottomleft = self.cubie_array[2][2][0]

        topleft.set_colors([topleft.get_color(TOP), topleft.get_color(SIDE), topleft.get_color(FRONT)])
        topright.set_colors([topright.get_color(TOP), topright.get_color(SIDE), topright.get_color(FRONT)])
        bottomright.set_colors([bottomright.get_color(TOP), bottomright.get_color(SIDE), bottomright.get_color(FRONT)])
        bottomleft.set_colors([bottomleft.get_color(TOP), bottomleft.get_color(SIDE), bottomleft.get_color(FRONT)])

        temp = self.cubie_array[2][0][0]
        self.cubie_array[2][0][0] = self.cubie_array[2][0][2]
        self.cubie_array[2][0][2] = self.cubie_array[2][2][2]
        self.cubie_array[2][2][2] = self.cubie_array[2][2][0]
        self.cubie_array[2][2][0] = temp

        temp = self.cubie_array[2][0][1]
        self.cubie_array[2][0][1] = self.cubie_array[2][1][2]
        self.cubie_array[2][1][2] = self.cubie_array[2][2][1]
        self.cubie_array[2][2][1] = self.cubie_array[2][1][0]
        self.cubie_array[2][1][0] = temp

        self.update_pos()

    def di(self):
        topleft = self.cubie_array[2][0][0]
        topright = self.cubie_array[2][0][2]
        bottomright = self.cubie_array[2][2][2]
        bottomleft = self.cubie_array[2][2][0]

        topleft.set_colors([topleft.get_color(TOP), topleft.get_color(SIDE), topleft.get_color(FRONT)])
        topright.set_colors([topright.get_color(TOP), topright.get_color(SIDE), topright.get_color(FRONT)])
        bottomright.set_colors([bottomright.get_color(TOP), bottomright.get_color(SIDE), bottomright.get_color(FRONT)])
        bottomleft.set_colors([bottomleft.get_color(TOP), bottomleft.get_color(SIDE), bottomleft.get_color(FRONT)])

        temp = self.cubie_array[2][0][0]
        self.cubie_array[2][0][0] = self.cubie_array[2][2][0]
        self.cubie_array[2][2][0] = self.cubie_array[2][2][2]
        self.cubie_array[2][2][2] = self.cubie_array[2][0][2]
        self.cubie_array[2][0][2] = temp

        temp = self.cubie_array[2][0][1]
        self.cubie_array[2][0][1] = self.cubie_array[2][1][0]
        self.cubie_array[2][1][0] = self.cubie_array[2][2][1]
        self.cubie_array[2][2][1] = self.cubie_array[2][1][2]
        self.cubie_array[2][1][2] = temp

        self.update_pos()

    def d2(self):
        self.d()
        self.d()

        self.update_pos()

    ##########################################################################

    def l(self):
        topleft = self.cubie_array[0][0][0]
        topright = self.cubie_array[0][2][0]
        bottomright = self.cubie_array[2][2][0]
        bottomleft = self.cubie_array[2][0][0]

        topleft.set_colors([topleft.get_color(FRONT), topleft.get_color(TOP), topleft.get_color(SIDE)])
        topright.set_colors([topright.get_color(FRONT), topright.get_color(TOP), topright.get_color(SIDE)])
        bottomright.set_colors([bottomright.get_color(FRONT), bottomright.get_color(TOP), bottomright.get_color(SIDE)])
        bottomleft.set_colors([bottomleft.get_color(FRONT), bottomleft.get_color(TOP), bottomleft.get_color(SIDE)])

        temp = self.cubie_array[0][0][0]
        self.cubie_array[0][0][0] = self.cubie_array[2][0][0]
        self.cubie_array[2][0][0] = self.cubie_array[2][2][0]
        self.cubie_array[2][2][0] = self.cubie_array[0][2][0]
        self.cubie_array[0][2][0] = temp

        temp = self.cubie_array[0][1][0]
        self.cubie_array[0][1][0] = self.cubie_array[1][0][0]
        self.cubie_array[1][0][0] = self.cubie_array[2][1][0]
        self.cubie_array[2][1][0] = self.cubie_array[1][2][0]
        self.cubie_array[1][2][0] = temp

        self.update_pos()

    def li(self):
        topleft = self.cubie_array[0][0][0]
        topright = self.cubie_array[0][2][0]
        bottomright = self.cubie_array[2][2][0]
        bottomleft = self.cubie_array[2][0][0]

        topleft.set_colors([topleft.get_color(FRONT), topleft.get_color(TOP), topleft.get_color(SIDE)])
        topright.set_colors([topright.get_color(FRONT), topright.get_color(TOP), topright.get_color(SIDE)])
        bottomright.set_colors([bottomright.get_color(FRONT), bottomright.get_color(TOP), bottomright.get_color(SIDE)])
        bottomleft.set_colors([bottomleft.get_color(FRONT), bottomleft.get_color(TOP), bottomleft.get_color(SIDE)])

        temp = self.cubie_array[0][0][0]
        self.cubie_array[0][0][0] = self.cubie_array[0][2][0]
        self.cubie_array[0][2][0] = self.cubie_array[2][2][0]
        self.cubie_array[2][2][0] = self.cubie_array[2][0][0]
        self.cubie_array[2][0][0] = temp

        temp = self.cubie_array[0][1][0]
        self.cubie_array[0][1][0] = self.cubie_array[1][2][0]
        self.cubie_array[1][2][0] = self.cubie_array[2][1][0]
        self.cubie_array[2][1][0] = self.cubie_array[1][0][0]
        self.cubie_array[1][0][0] = temp

        self.update_pos()

    def l2(self):
        self.l()
        self.l()

        self.update_pos()

    ####################################################################

    def r(self):
        topleft = self.cubie_array[0][2][2]
        topright = self.cubie_array[0][0][2]
        bottomright = self.cubie_array[2][0][2]
        bottomleft = self.cubie_array[2][2][2]

        topleft.set_colors([topleft.get_color(FRONT), topleft.get_color(TOP), topleft.get_color(SIDE)])
        topright.set_colors([topright.get_color(FRONT), topright.get_color(TOP), topright.get_color(SIDE)])
        bottomright.set_colors([bottomright.get_color(FRONT), bottomright.get_color(TOP), bottomright.get_color(SIDE)])
        bottomleft.set_colors([bottomleft.get_color(FRONT), bottomleft.get_color(TOP), bottomleft.get_color(SIDE)])

        temp = self.cubie_array[0][0][2]
        self.cubie_array[0][0][2] = self.cubie_array[0][2][2]
        self.cubie_array[0][2][2] = self.cubie_array[2][2][2]
        self.cubie_array[2][2][2] = self.cubie_array[2][0][2]
        self.cubie_array[2][0][2] = temp

        temp = self.cubie_array[0][1][2]
        self.cubie_array[0][1][2] = self.cubie_array[1][2][2]
        self.cubie_array[1][2][2] = self.cubie_array[2][1][2]
        self.cubie_array[2][1][2] = self.cubie_array[1][0][2]
        self.cubie_array[1][0][2] = temp

        self.update_pos()

    def ri(self):
        topleft = self.cubie_array[0][2][2]
        topright = self.cubie_array[0][0][2]
        bottomright = self.cubie_array[2][0][2]
        bottomleft = self.cubie_array[2][2][2]

        topleft.set_colors([topleft.get_color(FRONT), topleft.get_color(TOP), topleft.get_color(SIDE)])
        topright.set_colors([topright.get_color(FRONT), topright.get_color(TOP), topright.get_color(SIDE)])
        bottomright.set_colors([bottomright.get_color(FRONT), bottomright.get_color(TOP), bottomright.get_color(SIDE)])
        bottomleft.set_colors([bottomleft.get_color(FRONT), bottomleft.get_color(TOP), bottomleft.get_color(SIDE)])

        temp = self.cubie_array[0][0][2]
        self.cubie_array[0][0][2] = self.cubie_array[2][0][2]
        self.cubie_array[2][0][2] = self.cubie_array[2][2][2]
        self.cubie_array[2][2][2] = self.cubie_array[0][2][2]
        self.cubie_array[0][2][2] = temp

        temp = self.cubie_array[0][1][2]
        self.cubie_array[0][1][2] = self.cubie_array[1][0][2]
        self.cubie_array[1][0][2] = self.cubie_array[2][1][2]
        self.cubie_array[2][1][2] = self.cubie_array[1][2][2]
        self.cubie_array[1][2][2] = temp

        self.update_pos()

    def r2(self):
        self.r()
        self.r()

        self.update_pos()

    ##########################################################################

    def f(self):
        topleft = self.cubie_array[0][2][0]
        topright = self.cubie_array[0][2][2]
        bottomright = self.cubie_array[2][2][2]
        bottomleft = self.cubie_array[2][2][0]

        topleft.set_colors([topleft.get_color(SIDE), topleft.get_color(FRONT), topleft.get_color(TOP)])
        topright.set_colors([topright.get_color(SIDE), topright.get_color(FRONT), topright.get_color(TOP)])
        bottomright.set_colors([bottomright.get_color(SIDE), bottomright.get_color(FRONT), bottomright.get_color(TOP)])
        bottomleft.set_colors([bottomleft.get_color(SIDE), bottomleft.get_color(FRONT), bottomleft.get_color(TOP)])

        temp = self.cubie_array[0][2][0]
        self.cubie_array[0][2][0] = self.cubie_array[2][2][0]
        self.cubie_array[2][2][0] = self.cubie_array[2][2][2]
        self.cubie_array[2][2][2] = self.cubie_array[0][2][2]
        self.cubie_array[0][2][2] = temp

        top = self.cubie_array[0][2][1]
        right = self.cubie_array[1][2][2]
        bottom = self.cubie_array[2][2][1]
        left = self.cubie_array[1][2][0]

        top.set_colors([top.get_color(FRONT), top.get_color(TOP)])
        right.set_colors([right.get_color(FRONT), right.get_color(TOP)])
        bottom.set_colors([bottom.get_color(FRONT), bottom.get_color(TOP)])
        left.set_colors([left.get_color(FRONT), left.get_color(TOP)])

        temp = self.cubie_array[0][2][1]
        self.cubie_array[0][2][1] = self.cubie_array[1][2][0]
        self.cubie_array[1][2][0] = self.cubie_array[2][2][1]
        self.cubie_array[2][2][1] = self.cubie_array[1][2][2]
        self.cubie_array[1][2][2] = temp

        self.update_pos()

    def fi(self):
        topleft = self.cubie_array[0][2][0]
        topright = self.cubie_array[0][2][2]
        bottomright = self.cubie_array[2][2][2]
        bottomleft = self.cubie_array[2][2][0]

        topleft.set_colors([topleft.get_color(SIDE), topleft.get_color(FRONT), topleft.get_color(TOP)])
        topright.set_colors([topright.get_color(SIDE), topright.get_color(FRONT), topright.get_color(TOP)])
        bottomright.set_colors([bottomright.get_color(SIDE), bottomright.get_color(FRONT), bottomright.get_color(TOP)])
        bottomleft.set_colors([bottomleft.get_color(SIDE), bottomleft.get_color(FRONT), bottomleft.get_color(TOP)])

        temp = self.cubie_array[0][2][0]
        self.cubie_array[0][2][0] = self.cubie_array[0][2][2]
        self.cubie_array[0][2][2] = self.cubie_array[2][2][2]
        self.cubie_array[2][2][2] = self.cubie_array[2][2][0]
        self.cubie_array[2][2][0] = temp

        top = self.cubie_array[0][2][1]
        right = self.cubie_array[1][2][2]
        bottom = self.cubie_array[2][2][1]
        left = self.cubie_array[1][2][0]

        top.set_colors([top.get_color(FRONT), top.get_color(TOP)])
        right.set_colors([right.get_color(FRONT), right.get_color(TOP)])
        bottom.set_colors([bottom.get_color(FRONT), bottom.get_color(TOP)])
        left.set_colors([left.get_color(FRONT), left.get_color(TOP)])

        temp = self.cubie_array[0][2][1]
        self.cubie_array[0][2][1] = self.cubie_array[1][2][2]
        self.cubie_array[1][2][2] = self.cubie_array[2][2][1]
        self.cubie_array[2][2][1] = self.cubie_array[1][2][0]
        self.cubie_array[1][2][0] = temp

        self.update_pos()

    def f2(self):
        self.f()
        self.f()

        self.update_pos()

    #######################################################################3

    def b(self):
        topleft = self.cubie_array[0][0][0]
        topright = self.cubie_array[0][0][2]
        bottomright = self.cubie_array[2][0][2]
        bottomleft = self.cubie_array[2][0][0]

        topleft.set_colors([topleft.get_color(SIDE), topleft.get_color(FRONT), topleft.get_color(TOP)])
        topright.set_colors([topright.get_color(SIDE), topright.get_color(FRONT), topright.get_color(TOP)])
        bottomright.set_colors([bottomright.get_color(SIDE), bottomright.get_color(FRONT), bottomright.get_color(TOP)])
        bottomleft.set_colors([bottomleft.get_color(SIDE), bottomleft.get_color(FRONT), bottomleft.get_color(TOP)])

        temp = self.cubie_array[0][0][0]
        self.cubie_array[0][0][0] = self.cubie_array[0][0][2]
        self.cubie_array[0][0][2] = self.cubie_array[2][0][2]
        self.cubie_array[2][0][2] = self.cubie_array[2][0][0]
        self.cubie_array[2][0][0] = temp

        top = self.cubie_array[0][0][1]
        right = self.cubie_array[1][0][2]
        bottom = self.cubie_array[2][0][1]
        left = self.cubie_array[1][0][0]

        top.set_colors([top.get_color(FRONT), top.get_color(TOP)])
        right.set_colors([right.get_color(FRONT), right.get_color(TOP)])
        bottom.set_colors([bottom.get_color(FRONT), bottom.get_color(TOP)])
        left.set_colors([left.get_color(FRONT), left.get_color(TOP)])

        temp = self.cubie_array[0][0][1]
        self.cubie_array[0][0][1] = self.cubie_array[1][0][2]
        self.cubie_array[1][0][2] = self.cubie_array[2][0][1]
        self.cubie_array[2][0][1] = self.cubie_array[1][0][0]
        self.cubie_array[1][0][0] = temp

        self.update_pos()

    def bi(self):
        topleft = self.cubie_array[0][0][0]
        topright = self.cubie_array[0][0][2]
        bottomright = self.cubie_array[2][0][2]
        bottomleft = self.cubie_array[2][0][0]

        topleft.set_colors([topleft.get_color(SIDE), topleft.get_color(FRONT), topleft.get_color(TOP)])
        topright.set_colors([topright.get_color(SIDE), topright.get_color(FRONT), topright.get_color(TOP)])
        bottomright.set_colors([bottomright.get_color(SIDE), bottomright.get_color(FRONT), bottomright.get_color(TOP)])
        bottomleft.set_colors([bottomleft.get_color(SIDE), bottomleft.get_color(FRONT), bottomleft.get_color(TOP)])

        temp = self.cubie_array[0][0][0]
        self.cubie_array[0][0][0] = self.cubie_array[2][0][0]
        self.cubie_array[2][0][0] = self.cubie_array[2][0][2]
        self.cubie_array[2][0][2] = self.cubie_array[0][0][2]
        self.cubie_array[0][0][2] = temp

        top = self.cubie_array[0][0][1]
        right = self.cubie_array[1][0][2]
        bottom = self.cubie_array[2][0][1]
        left = self.cubie_array[1][0][0]

        top.set_colors([top.get_color(FRONT), top.get_color(TOP)])
        right.set_colors([right.get_color(FRONT), right.get_color(TOP)])
        bottom.set_colors([bottom.get_color(FRONT), bottom.get_color(TOP)])
        left.set_colors([left.get_color(FRONT), left.get_color(TOP)])

        temp = self.cubie_array[0][0][1]
        self.cubie_array[0][0][1] = self.cubie_array[1][0][0]
        self.cubie_array[1][0][0] = self.cubie_array[2][0][1]
        self.cubie_array[2][0][1] = self.cubie_array[1][0][2]
        self.cubie_array[1][0][2] = temp

        self.update_pos()

    def b2(self):
        self.b()
        self.b()

        self.update_pos()

    ##################################################################

    def __str__(self):
        string = ""
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    string += self.cubie_array[i][j][k].__str__() + ", "
                string += "\n"
            string += "\n"
        return string

    ##########################################################################

    def alg_count(self):
        self.update_tp()
        self.check_twists()
        corner_targets = self.trace([0, 2, 2], self.traced_pieces)
        self.parity = corner_targets % 2 != 0
        # edge_buffer = [0, 2, 1]
        edge_buffer = [0, 1, 2] if self.parity else [0, 2, 1]
        if self.parity:
            temp = self.cubie_array[0][2][1]
            self.cubie_array[0][2][1] = self.cubie_array[0][1][2]
            self.cubie_array[0][1][2] = temp
            self.update_pos()
            self.update_tp()
            self.flips = []
            self.check_twists()
        #edge_algs = int(self.trace(edge_buffer, self.traced_edges) / 2)
        edge_algs = ceil(self.trace(edge_buffer, self.traced_edges) / 2)
        corner_algs = ceil(corner_targets / 2)
        algs = edge_algs + corner_algs
        # print("Parity:", self.parity)
        # print("Corner Comms:", corner_algs)
        # print("Edge Comms:", edge_algs)
        algs += self.num_twist_algs()
        # print("Twist Algs:", self.num_twist_algs())
        algs += self.num_flip_algs()
        # print("Flip Algs:", self.num_flip_algs())
        return algs

    def num_twist_algs(self):
        algs = 0
        cc_twists = []
        c_twists = []
        for twist in self.twists:
            if twist.get_twist_dir() == 1:
                cc_twists.append(twist)
            elif twist.get_twist_dir() == 0:
                c_twists.append(twist)
        other_twists = abs(len(cc_twists) - len(c_twists))
        two_twists = min(len(c_twists), len(cc_twists))
        algs += two_twists + other_twists
        return algs

    def num_flip_algs(self):
        return ceil(len(self.flips) / 2)

    def check_twists(self):
        for cubie in self.traced_pieces:
            if cubie.is_solved() and cubie.is_twisted() and cubie not in self.twists:
                if cubie == self.cubie_array[0][2][2]:
                    continue
                cubie.set_twist_dir()
                self.twists.append(cubie)
        for cubie in self.traced_edges:
            if cubie.is_solved() and cubie.is_twisted() and cubie not in self.flips:
                if self.parity:
                    if cubie == self.cubie_array[0][1][2]:
                        continue
                else:
                    if cubie == self.cubie_array[0][2][1]:
                        continue
                self.flips.append(cubie)

    def update_tp(self):
        for layer in self.cubie_array:
            for column in layer:
                for cubie in column:
                    if type(cubie) == Corner:
                        if cubie.is_solved() and cubie not in self.traced_pieces:
                            self.traced_pieces.append(cubie)
                    elif type(cubie) == Edge:
                        if cubie.is_solved() and cubie not in self.traced_edges:
                            self.traced_edges.append(cubie)

    def trace(self, passed_buffer, traced_things):
        buffer = self.cubie_array[passed_buffer[0]][passed_buffer[1]][passed_buffer[2]]
        buffer_location = passed_buffer
        piece_type = type(buffer)
        piece_count = 8 if piece_type == Corner else 12
        counter = 0
        side = TOP

        while len(traced_things) < piece_count:
            temp = self.retrieve_next_piece(buffer, side)
            if temp[0] not in traced_things:
                traced_things.append(temp[0])
                counter += 1
            if temp[0].get_position() == buffer_location:
                if self.cubie_array[buffer_location[0]][buffer_location[1]][buffer_location[2]] not in traced_things:
                    traced_things.append(self.cubie_array[buffer_location[0]][buffer_location[1]][buffer_location[2]])
                if len(traced_things) < piece_count:
                    #if counter % 2 != 0:
                    #    counter += 2
                    #elif piece_type == Corner and temp[0].get_color(temp[1]) not in (WHI, YEL):
                    #    counter += 2
                    #elif piece_type == Edge and temp[0].get_color(temp[1]) not in (WHI, YEL, RED, ORA):
                    #    counter += 2
                    buffer = self.break_cycle(piece_type)
                    buffer_location = buffer.get_real_pos()
                    side = TOP
                    counter += 2
                else:
                    break
                continue
            buffer = temp[0]
            side = temp[1]
        return counter

    def retrieve_next_piece(self, cubie, sticker):
        pos = cubie.get_position()
        next_cubie = self.cubie_array[pos[0]][pos[1]][pos[2]]
        return [next_cubie, cubie.get_side(cubie.get_color(sticker))]

    def break_cycle(self, piece_type):
        for layer in self.cubie_array:
            for column in layer:
                for cubie in column:
                    if type(cubie) == piece_type == Corner and cubie not in self.traced_pieces:
                        return cubie
                    elif type(cubie) == piece_type == Edge and cubie not in self.traced_edges:
                        return cubie
        return None


start_time = time.time()
alg_distribution = {5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
total = 0
file = "Scrambles.txt"
count = 0
cube = Cube()
with open(file) as fp:
    for scramble in fp:
        count += 1
        scramble = re.sub('(\\d+\\))', '', scramble)
        scramble = re.sub('(.w.*)', '', scramble)
        cube.scramble(scramble)
        algs = cube.alg_count()
        total += algs
        alg_distribution[algs] += 1
        cube = Cube()
for (key, value) in alg_distribution.items():
    print(str(key) + ": ", '{0:.3g}'.format(value / count * 100), "%")
print("Total:", count)
print("Average:", '{0:.4g}'.format(total / count))
print("{:.3f}".format(time.time() - start_time), "seconds")
# some brand new risky code


