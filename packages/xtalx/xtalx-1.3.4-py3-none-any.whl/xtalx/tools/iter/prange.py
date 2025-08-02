# Copyright (c) 2020 Phase Advanced Sensor Systems, Inc.
import sys
import math


FRAC_LUT = [
    '\u2500',
    '\u258F',
    '\u258E',
    '\u258D',
    '\u258C',
    '\u258B',
    '\u258A',
    '\u2589',
    ]


class piter:
    '''
    Iterator class that also displays a progress bar.
    '''
    def __init__(self, seq, width=40, verbose=True, clear_line=False):
        self.seq        = seq
        self.width      = width
        self.verbose    = verbose
        self.clear_line = clear_line
        self.end        = len(seq)
        self._iter      = iter(seq)
        self.v          = 0

    def __repr__(self):
        if self.end:
            frac, n_star = math.modf(self.v * self.width / self.end)
        else:
            frac, n_star = 0, self.width
        frac         = int(frac * 8)
        n_star       = int(n_star)
        n_space      = self.width - n_star - 1

        s = '\r\u2503' + '\u2588'*n_star
        if n_space >= 0:
            s += FRAC_LUT[frac] + '\u2500'*n_space
        s += ('\u2503 [%u / %u]' % (self.v, self.end))

        return s

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.verbose:
            sys.stdout.write(repr(self))

        try:
            self.v += 1
            return next(self._iter)
        except StopIteration:
            if self.verbose:
                if self.clear_line:
                    sys.stdout.write('\r\x1B[0K')
                else:
                    print()
            raise


def prange(*args, **kwargs):
    return piter(range(*args), **kwargs)
