#!/usr/bin/env python3

import collections
import enum
import functools
import itertools
import operator as op
import random
import typing

import numpy as np
from scipy.stats import chi2_contingency

import game

if __name__ == "__main__":
    iters = 1000
    wins = collections.defaultdict(lambda: 0)
    for i in range(iters):
        gm = game.Game()
        results = gm.play()
        m, w = max([(m, i) for i,m in results.items()])
        wins[w] += 1
    print(sorted([(i, w / iters) for i, w in wins.items()]))
    table = np.array([list(wins.values()), [iters - w for w in wins.values()]])
    chi2, p, dof, ex = chi2_contingency(table)
    print(round(p, 4))

