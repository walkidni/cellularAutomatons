# -*- coding: utf-8 -*-
import operator
from enum import Enum
import numpy as np
class Pattern:
    class Neighborhood(Enum):
        MOORE = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                 (0, 1), (1, -1), (1, 0), (1, 1)]
        VON_NEUMANN = [(-1, 0), (0, -1), (0, 1), (1, 0)]

    Neighbors = Neighborhood

    def __init__(self,name, rows=100, cols=100, colors=[(255,255,255),(0,0,0),(140,140,140)], neighborhood='moore'):
        self._rows = rows
        self._cols = cols
        self._grid = np.zeros((rows, cols), dtype=np.int8)
        self._neighbors = self.Neighbors.VON_NEUMANN.value if neighborhood == 'vonNeumann' else self.Neighbors.MOORE.value
        self.colors = colors
        self.name = name


    def update(self):
        return

    def to_numpy(self, verbose=False):
        if verbose:
            self.print()
        return self._grid

    def print(self):
        print(self._grid)


class SquaredCellularPattern(Pattern):

    def __init__(self, rows, cols, rule_number=60, init_cond='impulse', impulse_pos='hl'):
        super().__init__('SquaredCellularPattern', rows, cols)

        assert 0 <= rule_number <= 255
        assert init_cond in ['random', 'impulse']
        assert impulse_pos in ['hl', 'hr', 'hc', 'c', 'lc', 'll', 'lr']

        rule_binary_str = np.binary_repr(rule_number, width=8)
        self._rule_binary = np.array(
            [int(ch) for ch in rule_binary_str], dtype=np.int8)
        self._counter = 0
        self._powers_of_two = np.array([[4], [2], [1]])  # shape (3, 1)

        if init_cond == 'impulse':  # starting with an initial impulse
            if impulse_pos == 'hl':
                self._grid[0, 0] = 1
            elif impulse_pos == 'hr':
                self._grid[0, cols - 1] = 1
            elif impulse_pos == 'hc':
                self._grid[0, cols // 2] = 1
            elif impulse_pos == 'c':
                self._grid[rows // 2, cols // 2] = 1
            elif impulse_pos == 'lc':
                self._grid[rows // 2, 0] = 1
            elif impulse_pos == 'll':
                self._grid[rows - 1, 0] = 1
            elif impulse_pos == 'lr':
                self._grid[rows - 1, cols - 1] = 1
        elif init_cond == 'random':  # random init of the first step
            self._grid[0, :] = np.array(
                np.random.rand(cols) < 0.5, dtype=np.int8)

    def update(self):
        pattern = self._grid

        if self._counter < self._rows - 1:
            pattern[self._counter + 1,
                    :] = self._step(pattern[self._counter, :])
            self._counter += 1
        else:
            pattern = np.roll(pattern, -1, 0)
            pattern[-1, :] = self._step(pattern[-2, :])

        self._grid = pattern

        return pattern

    def _step(self, row):
        # circular shift to left and right
        row_shift_right = np.roll(row, 1)
        row_shift_left = np.roll(row, -1)

        # stack row-wise, shape (3, cols)
        y = np.vstack((row_shift_right, row, row_shift_left)).astype(np.int8)

        # LCR pattern as number
        z = np.sum(self._powers_of_two * y, axis=0).astype(np.int8)

        return self._rule_binary[7 - z]


class FireForestPattern(Pattern):
    class FFState(Enum):
        BURN = 2
        ALIVE = 1
        DEAD = 0

    STATE = FFState

    def __init__(self, rows, cols, fire_p=0.0000005, grow_p=0.05, burn_ratio=0.005, dead_ratio=0.5):
        super().__init__('FireForestPattern', rows, cols, neighborhood='vonNeumann')

        self._grid = self._grid_init(burn_ratio, dead_ratio)
        self._fire_p = fire_p
        self._grow_p = grow_p
        self.colors = [(50,50,50),(0,90,0),(255,0,0)]

    def _grid_init(self, burn_ratio, dead_ratio):
        # Define the initial state of the grid
        initial_state = np.zeros((self._rows, self._cols),
                                 dtype=int)

        initial_state[:] = self.STATE.ALIVE.value

        num_burning = int(self._rows * self._cols * burn_ratio)
        burn_indices = np.random.choice(
            initial_state.size, size=num_burning, replace=False)

        num_dead = int(self._rows * self._cols * dead_ratio)
        dead_indices = np.random.choice(
            initial_state.size, size=num_dead, replace=False)

        initial_state.flat[dead_indices] = self.STATE.DEAD.value
        initial_state.flat[burn_indices] = self.STATE.BURN.value

        return initial_state

    def update(self):
        pattern = np.zeros_like(self._grid)

        for i in range(pattern.shape[0]):
            for j in range(pattern.shape[1]):
                pattern[i, j] = self._rules((i, j))

        self._grid = pattern

    def _rules(self, coord):
        if self._grid[coord] == self.STATE.BURN.value:
            # 1.  A burning tree turns into an empty cell.
            return self.STATE.DEAD.value
        elif self._grid[coord] == self.STATE.ALIVE.value:
            # 2.  A non-burning tree with one burning neighbour turns into a burning tree.
            for neighbor in self._neighbors:
                ncoord = tuple(map(operator.add, coord, neighbor))
                if ncoord[0] < 0 or ncoord[0] > self._rows - 1:
                    continue
                if ncoord[1] < 0 or ncoord[1] > self._cols - 1:
                    continue

                if self._grid[ncoord] == self.STATE.BURN.value:
                    return self.STATE.BURN.value

            # 3.  A tree with no burning neighbour ignites with probability f due to lightning.
            return np.random.choice([self.STATE.ALIVE.value, self.STATE.BURN.value], size=1, p=[1-self._fire_p, self._fire_p])
        else:
            # 4.  An empty space grows a new tree with probability p.
            return np.random.choice([self.STATE.DEAD.value, self.STATE.ALIVE.value], size=1, p=[1-self._grow_p, self._grow_p])

