#!/usr/bin/env python
"""
bir grubun icinde iki kareden biri mutlaka 3 ise, ve o iki kare ayni sirada ise
o siradaki diger 3 ihtimalleri elenmeli
"""


from itertools import combinations, product
from operator import itemgetter
import numpy as np


__author__ = 'taylanbil'


def subgroups_helper(triple):
    ans = [''.join(i) for i in list(combinations(triple, 2))]
    # No need for the  + list(triple) because fitted single cells are already
    # picked up by the other groups.
    return set(ans)


MEANINGFUL_SUBGROUPS = {
    'row': set(['123', '456', '789']),
    'column': set(['123', '456', '789']),
    'square': set(['123', '456', '789', '147', '258', '369'])
}
for key in MEANINGFUL_SUBGROUPS.keys():
    tmp = set([])
    for triple in MEANINGFUL_SUBGROUPS[key]:
        tmp.update(subgroups_helper(triple))
    MEANINGFUL_SUBGROUPS[key].update(tmp)


class SudokuCell(object):

    def __init__(self, val=None):
        self.set_value(val)
        self.set_possible_vals(val)
        # self.is_set = False if val is None else True
        self.is_set = False

    def set_value(self, val):
        self.val = val
        if val is not None:
            self.set_possible_vals(val)
            # self.is_set = True

    def set_possible_vals(self, possible_vals):
        if possible_vals is None:
            self.possible_vals = set(range(1, 10))
        elif isinstance(possible_vals, int):
            self.possible_vals = set([possible_vals])
        else:
            self.possible_vals = set(possible_vals)
        # if len(self.possible_vals) == 1:
        #     self.is_set = True

    def eliminate_possibilities(self, val):
        if isinstance(val, int):
            val = [val]
        self.possible_vals.difference_update(set(val))
        # if len(self.possible_vals) == 1:
        #     self.is_set = True

    def check_possibility(self, val):
        return val in self.possible_vals


class SudokuGroup(object):

    def __init__(self, cells, group_kind, id_num):
        assert len(cells) == 9
        self.cells = zip(range(1, 10), cells)  # [(1, sq1), (2, sq2), ...]
        self.settled_combinations = set([])
        self.spotted_vals = set([])
        self.places = set(xrange(1, 10))
        self.meaningful_subgroups = MEANINGFUL_SUBGROUPS[group_kind]
        self.group_kind = group_kind
        self.id_num = id_num

    def settle_combination(self, nuple, fitted_cells, settle_type,
                           explain=True):
        not_this_nuple = self.places.difference(nuple)
        fitted_cell_list = map(itemgetter(1), fitted_cells)
        for i, cell in self.cells:
            if cell in fitted_cell_list:
                cell.eliminate_possibilities(not_this_nuple)
            else:
                cell.eliminate_possibilities(nuple)
        self.settled_combinations.add(nuple)
        # Explanation
        if explain and len(nuple) == 1:
            cell = fitted_cell_list[0]
            if not cell.is_set:
                cell.is_set = True
                other_group_kinds = {'square', 'row', 'column'}.difference(
                    set([self.group_kind]))
                other_group_kinds = list(other_group_kinds)
                args = (list(nuple)[0], self.group_kind, self.id_num + 1,
                        other_group_kinds[0], other_group_kinds[1])
                print(('There is only one cell that can contain the value %s in'
                       ' %s #%s! Adjusting the appropriate %s and %s'
                       ' accordingly.' % args))
        elif explain and settle_type == 'fit':
            print(('In %s #%s, there are %s cells with only possible values'
                   ' %s, so the other cells in this %s cannot contain any of'
                   ' %s' % (self.group_kind, self.id_num+1, len(nuple),
                            list(nuple), self.group_kind, list(nuple))))
        elif explain:
            print(('In %s #%s, the values %s can only be in %s cells. So those'
                   ' cells cannot contain any other value'
                   % (self.group_kind, self.id_num+1, list(nuple), len(nuple))))

    def could_relate(self, n):
        container = ''.join(map(str, [i for i, cell in self.cells
                                      if n in cell.possible_vals]))
        if container in self.meaningful_subgroups:
            return container, n
        return False, None

    def fit_combination(self, nuple, explain=True):
        fitted_cells = [(i, cell) for i, cell in self.cells
                        if nuple.issuperset(cell.possible_vals)]
        if len(fitted_cells) == len(nuple):
            # settled
            self.settle_combination(nuple, fitted_cells, 'fit')

    def fit(self, n, explain=True):
        """
        This should be called with n <= 4
        """
        for nuple in combinations(xrange(1, 10), n):
            if self.to_fit(nuple):
                self.fit_combination(frozenset(nuple), explain=True)

    def spot(self, n, explain=True):
        for nuple in combinations(xrange(1, 10), n):
            if self.to_fit(nuple):
                self.spot_combination(frozenset(nuple), explain=True)

    def spot_combination(self, nuple, explain=True):
        disjoint_cells = [(i, cell) for i, cell in self.cells
                          if nuple.isdisjoint(cell.possible_vals)]
        disjoint_indices = map(itemgetter(0), disjoint_cells)
        overlapping_cells = [(i, cell) for i, cell in self.cells
                             if i not in disjoint_indices]
        if len(disjoint_cells) + len(nuple) == 9:
            self.settle_combination(nuple, overlapping_cells, 'spot')

    def to_fit(self, nuple):
        return not any(settled_comb.issubset(nuple)
                       for settled_comb in self.settled_combinations)

    def is_solved(self):
        return all([len(cell.possible_vals) == 1
                    for cell in map(itemgetter(1), self.cells)])


class SudokuTable(object):

    def __init__(self, table):
        """
        squares must be a 9 by 9 nested array
        """
        self.line = '-' * 73
        self.table = np.array(table)
        assert self.table.shape == (9, 9)
        self.groupify()
        self.solved = False

    def groupify(self):
        self.rows = []
        self.columns = []
        self.sq3 = []
        # rows
        for row in xrange(9):
            group_row = SudokuGroup(self.table[row, :].ravel(), 'row', row)
            self.rows.append(group_row)
        # columns
        for col in xrange(9):
            group_col = SudokuGroup(self.table[:, col].ravel(), 'column', col)
            self.columns.append(group_col)
        # 3by3 squares
        for i, j in product(range(3), range(3)):
            # order:
            # (0, 0), (0, 1), (0, 2), (1, 0), ..., (2, 1), (2, 2)
            group_sq3 = SudokuGroup(self.table[3*i:3*i+3, 3*j:3*j+3].ravel(),
                                    'square', i*3+j)
            self.sq3.append(group_sq3)
        self.groups = self.rows + self.columns + self.sq3

    def to_string(self):
        ans = []
        for row_num, row in enumerate(self.table):
            ans.append(self.line)
            if not row_num % 3:
                ans.append(self.line)
            for i in xrange(3):
                ans.append(self.get_line_i(i, row))
        ans.append(self.line)
        ans.append(self.line)
        return '\n'.join(ans)

    def get_line_i(self, i, cells):
        assert i in [0, 1, 2]
        assert len(cells) == 9
        ans = []
        for v, cell in enumerate(cells):
            if not v % 3:
                ans.append(' | ')
            tmp = []
            for j in range(3*i+1, 3*i+4):
                tmp.append('%s' % j if j in cell.possible_vals else ' ')
            ans.append(''.join(tmp))
        return '%s%s' % (' ', ' - '.join(ans))

    def solve(self, explain=True):
        old_outer, old = None, None
        new = ''
        i = 0
        if explain:
            print('INITIAL PROBLEM')
            print(self.to_string())
        while old_outer != new and not self.solved:
            while old != new and not self.solved:
                i += 1
                old = new
                self.solve_single_pass_no_relating(explain)
                new = self.to_string()
                if explain:
                    print new
                if all([row.is_solved() for row in self.rows]):
                    self.solved = True
                    print('SOLVED!')
                    break
            else:
                old_outer = new
                self.relate_groups()
                new = self.to_string()
                if all([row.is_solved() for row in self.rows]):
                    break
                elif explain:
                    print new
        if not explain:
            print(self.to_string())

    def identify_group(self, i):
        return i // 9, i % 9

    def get_related_group(self, gtype, num, relation):
        relation = set(relation)
        if gtype == 'sq3' and \
                any([relation.issubset(tmp)
                     for tmp in [set('123'), set('456'), set('789')]]):
            # row
            ans = (num // 3) * 3 + relation.issubset(set('456')) + \
                2 * relation.issubset(set('789'))
            return ans
        elif gtype == 'sq3':
            # column
            ans = 9 + (num % 3) * 3 + relation.issubset(set('258')) + \
                2 * relation.issubset(set('369'))
            return ans
        elif gtype == 'row':
            # square
            ans = 18 + (num // 3) * 3
            ans += relation.issubset(set('456')) + \
                2 * relation.issubset(set('789'))
            return ans
        else:  # column
            # square
            ans = 18 + (num // 3) + 3 * (
                relation.issubset(set('456')) +
                2 * relation.issubset(set('789')))
            return ans

    def clean_related_group(self, related_group, group, val):
        donottouch = map(itemgetter(1), group.cells)
        for i, cell in related_group.cells:
            if cell not in donottouch:
                cell.eliminate_possibilities(val)

    def relate_groups(self):
        for i, group in enumerate(self.groups):
            for n in xrange(1, 10):
                relation, n = group.could_relate(n)
                if not relation:
                    continue
                # grab what squares it relates to and eliminate possibilites
                gtype, num = self.identify_group(i)
                gtype = {0: 'row', 1: 'col', 2: 'sq3'}[gtype]
                related_index = self.get_related_group(gtype, num, relation)
                # print ('I am %s number %s, interesting value is %s'
                #        ' and it relates to group %s') % (gtype, num + 1, n,
                #                                          related_index)
                related_group = self.groups[related_index]
                self.clean_related_group(related_group, group, n)

    def solve_single_pass_no_relating(self, explain=True):
        for group in self.groups:
            for n in xrange(1, 4):
                group.fit(n, explain)
                group.spot(n, explain)


def get_sudoku_table(table):
    sudoku = []
    for row in table:
        sudoku.append([])
        for val in row:
            sudoku[-1].append(SudokuCell(val))
    return SudokuTable(sudoku)


if __name__ == '__main__':
    easy = [
        [None, None, 5, None, None, 3, 1, 4, None],
        [None, 7, None, None, 2, None, None, None, 5],
        [None, None, 2, None, None, 1, None, None, None],
        [2, None, None, None, 3, None, None, 5, None],
        [9, 6, None, None, None, None, None, 2, 8],
        [None, 5, None, None, 7, None, None, None, 3],
        [None, None, None, 3, None, None, 6, None, None],
        [4, None, None, None, 5, None, None, 8, None],
        [None, 8, 1, 4, None, None, 5, None, None]
    ]
    extreme = [
        [2, None, None, None, 9, None, None, None, 1],
        [None, None, 8, 1, None, 7, 2, None, None],
        [None, None, None, None, None, None, None, None, None],
        [4, 8, None, 6, None, 3, None, 1, 9],
        [None, None, 3, None, None, None, 7, None, None],
        [9, 2, None, 7, None, 1, None, 4, 6],
        [None, None, None, None, None, None, None, None, None],
        [None, None, 2, 8, None, 5, 1, None, None],
        [7, None, None, None, 4, None, None, None, 8],
    ]
    extreme2 = [
        [None, None, 1, None, None, None, 3, None, None],
        [None, None, 3, None, 7, None, 8, None, None],
        [6, 7, None, None, None, None, None, 9, 4],
        [2, None, None, None, 5, None, None, None, 3],
        [None, 5, None, 9, None, 3, None, 8, None],
        [7, None, None, None, 6, None, None, None, 9],
        [8, 2, None, None, None, None, None, 3, 7],
        [None, None, 5, None, 8, None, 6, None, None],
        [None, None, 7, None, None, None, 9, None, None],
    ]

    S = get_sudoku_table(extreme2)
    S.solve()
