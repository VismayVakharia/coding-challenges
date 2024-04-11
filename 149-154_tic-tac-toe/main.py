#!/usr/bin/env python3.8

import pyglet
from itertools import product
from random import choice
from enum import IntEnum

WIN_W = 600
WIN_H = 600


class Cross(object):
    def __init__(self, cen_x: float, cen_y: float, size_: float = 20):
        self.x = cen_x
        self.y = cen_y
        length = size_ / 2
        self.shapes = [
            pyglet.shapes.Line(self.x - length, self.y - length, self.x + length, self.y + length,
                               color=(0, 0, 0), width=3),
            pyglet.shapes.Line(self.x - length, self.y + length, self.x + length, self.y - length,
                               color=(0, 0, 0), width=3)
        ]

    def draw(self):
        for shape in self.shapes:
            shape.draw()


class Circle(object):
    def __init__(self, cen_x: float, cen_y: float, size_: float = 20):
        self.x = cen_x
        self.y = cen_y
        radius = size_ / 2
        self.shapes = [
            pyglet.shapes.Circle(self.x, self.y, radius + 3, color=(0, 0, 0)),
            pyglet.shapes.Circle(self.x, self.y, radius, color=(225, 225, 225))
        ]

    def draw(self):
        for shape in self.shapes:
            shape.draw()


class Status(IntEnum):
    RUNNING = -1
    CROSS = 0
    CIRCLE = 1
    TIE = 2

    def __repr__(self):
        return self.name


Scores = {"X": {"X": 1, "O": -1, "Tie": 0}, "O": {"X": -1, "O": 1, "Tie": 0}}


class Board(object):
    def __init__(self):
        self.states = [["" for i in range(3)] for j in range(3)]
        self.available = list(product(range(3), repeat=2))
        self.players = {"X": Cross, "O": Circle}
        self.toggle = {"X": "O", "O": "X"}
        self.currentPlayer = "X"
        self.status = Status.RUNNING

        self.background = pyglet.graphics.Batch()
        self.box = pyglet.shapes.Rectangle(x=X, y=Y, width=size, height=size, color=(225, 225, 225),
                                           batch=self.background)
        self.partitions = [pyglet.shapes.Line(X + sep, Y, X + sep, Y + sep * 3,
                                              color=(0, 0, 0), width=3, batch=self.background),
                           pyglet.shapes.Line(X + sep * 2, Y, X + sep * 2, Y + sep * 3,
                                              color=(0, 0, 0), width=3, batch=self.background),
                           pyglet.shapes.Line(X, Y + sep, X + sep * 3, Y + sep,
                                              color=(0, 0, 0), width=3, batch=self.background),
                           pyglet.shapes.Line(X, Y + sep * 2, X + sep * 3, Y + sep * 2,
                                              color=(0, 0, 0), width=3, batch=self.background)]
        self.shapes = []
        self.label = pyglet.text.Label('',
                                       font_name="Ubuntu Mono", font_size=size/8, bold=True,
                                       x=X+size/2, y=Y+size/2, color=(225, 55, 25, 255),
                                       anchor_x='center', anchor_y='center')

    def draw(self):
        self.box.draw()
        if self.status == Status.RUNNING:
            for partition in self.partitions:
                partition.draw()
            # self.background.draw()
            for shape in self.shapes:
                shape.draw()
        else:
            for partition in self.partitions:
                partition.opacity = 100
                partition.draw()
            # self.background.draw()
            for shape in self.shapes:
                for item in shape.shapes:
                    item.opacity = 100
                shape.draw()
            if self.status == Status.CROSS:
                self.label.text = "Cross Won!"
            elif self.status == Status.CIRCLE:
                self.label.text = "Circle Won!"
            elif self.status == Status.TIE:
                self.label.text = "Tie!"
            self.label.draw()

    def randomTurn(self):
        if len(self.available) > 0 and self.status is Status.RUNNING:
            i, j = choice(self.available)
            offset = sep / 2
            shape = self.players[self.currentPlayer]
            self.states[i][j] = self.currentPlayer
            self.shapes.append(shape(X + offset * (2 * i + 1), Y + offset * (2 * j + 1), sep / 2))
            self.currentPlayer = self.toggle[self.currentPlayer]
            self.available.remove((i, j))
            self.checkWinner()

    def humanTurn(self, i: int, j: int):
        if (i, j) in self.available and self.status is Status.RUNNING:
            offset = sep / 2
            shape = self.players[self.currentPlayer]
            self.states[i][j] = self.currentPlayer
            self.shapes.append(shape(X + offset * (2 * i + 1), Y + offset * (2 * j + 1), sep / 2))
            self.currentPlayer = self.toggle[self.currentPlayer]
            self.available.remove((i, j))
            self.checkWinner()
            self.bestTurn()

    def bestTurn(self):
        if len(self.available) > 0 and self.status is Status.RUNNING:
            best_score = -100
            best_move = None
            offset = sep / 2
            player = self.players[self.currentPlayer]

            for i, j in self.available:
                self.states[i][j] = self.currentPlayer
                score = self.minimax(current_player=self.currentPlayer, max_flag=1)
                self.states[i][j] = ""
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
            i, j = best_move
            self.states[i][j] = self.currentPlayer
            self.shapes.append(player(X + offset * (2 * i + 1), Y + offset * (2 * j + 1), sep / 2))
            self.currentPlayer = self.toggle[self.currentPlayer]
            self.available.remove((i, j))
            self.checkWinner()

    def checkWinner(self, update_states: bool = True):
        winner = None
        is_filled = True
        for i in range(3):
            if "" in self.states[i]:
                is_filled = False
        if is_filled:
            winner = "Tie"
        for i in range(3):
            if self.states[i][0] == self.states[i][1] == self.states[i][2]:
                if self.states[i][0] != "":
                    winner = self.states[i][0]
        for i in range(3):
            if self.states[0][i] == self.states[1][i] == self.states[2][i]:
                if self.states[0][i] != "":
                    winner = self.states[0][i]
        if self.states[0][0] == self.states[1][1] == self.states[2][2]:
            if self.states[0][0] != "":
                winner = self.states[0][0]
        if self.states[2][0] == self.states[1][1] == self.states[0][2]:
            if self.states[2][0] != "":
                winner = self.states[2][0]

        if update_states:
            if winner == "X":
                self.status = Status.CROSS
            elif winner == "O":
                self.status = Status.CIRCLE
            elif winner == "Tie":
                self.status = Status.TIE
        return winner

    def minimax(self, current_player, max_flag: int = 1, depth: int = 1):
        result = self.checkWinner(update_states=False)
        if result is not None:
            return Scores[current_player][result]

        player = current_player if max_flag == -1 else self.toggle[current_player]
        best_score = 100 * max_flag
        fun = min if max_flag == 1 else max

        for i, j in product(range(3), repeat=2):
            if self.states[i][j] == "":
                self.states[i][j] = player
                score = self.minimax(current_player, max_flag * -1, depth + 1)
                self.states[i][j] = ""
                best_score = fun(best_score, score)
        return best_score


if __name__ == "__main__":
    window = pyglet.window.Window(WIN_W, WIN_H)

    size = 2 * min(WIN_W, WIN_H) // 3
    X = (WIN_W - size) // 2
    Y = (WIN_H - size) // 2
    sep = size / 3

    game = Board()
    # game.bestTurn()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if game.status is Status.RUNNING:
            i = int((x - X)//sep)
            j = int((y - Y) // sep)
            game.humanTurn(i, j)
        else:
            game.__init__()
            # game.bestTurn()

    @window.event
    def on_draw():
        window.clear()
        # pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        game.draw()

    pyglet.app.run()
