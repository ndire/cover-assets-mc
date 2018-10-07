#!/usr/bin/env python3

import collections
import enum
import functools
import itertools
import operator as op
import random
import typing

import game

if __name__ == "__main__":
    wins = collections.defaultdict(lambda: 0)
    for i in range(500):
        gm = game.Game()
        results = gm.play()
        m, w = max([(m, i) for i,m in results.items()])
        wins[w] += 1
    print(wins)

