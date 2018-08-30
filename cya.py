#!/usr/bin/env python3

import collections
import enum
import functools
import itertools
import operator
import random

#
# Labels don't really matter, but helpful for debugging.
#
AssetKind = enum.Enum('AssetKind', [
    'GOLD', 'SILVER', 
    'HOUSE', 'BASEBALL', 'JEWEWLS', 'BANK', 
    'CARS', 'COINS', 'CASH', 'STOCKS', 'PIGGY', 'STAMPS'
])

CARDS = [
    (AssetKind.GOLD, 50, 4),
    (AssetKind.SILVER, 25, 8),
    (AssetKind.HOUSE, 20, 8),
    (AssetKind.JEWEWLS, 15, 10),
    (AssetKind.CARS,15, 10),
    (AssetKind.STOCKS, 10, 10),
    (AssetKind.BANK, 10, 10),
    (AssetKind.COINS, 10, 10),
    (AssetKind.BASEBALL, 5, 10),
    (AssetKind.CASH, 5, 10),
    (AssetKind.STAMPS, 5, 10),
    (AssetKind.PIGGY, 5, 10),
]

HAND_SIZE = 5

class Card:

    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

    def is_wild(self):
        return self.kind in [AssetKind.GOLD, AssetKind.SILVER]

    def __str__(self):
        return self.kind.name

    def __eq__(self, other):
        return self.kind == other.kind

    def __hash__(self):
        return hash(self.kind)

    def __repr__(self):
        return str(self)


class Player:

    def __init__(self, player_id):
        self.hand = collections.defaultdict(list)
        self.player_id = player_id
        self.assets = []

    def deal(self, card):
        self.hand[card.kind].append(card)

    def __str__(self):
        return "Player " + str(self.player_id)

    def hand_cards(self):
        return itertools.chain(*self.hand.values())

    def replenish(self, game):
        while len(list(self.hand_cards())) < HAND_SIZE and game.deck:
            self.deal(game.deck.pop())

    def total(self):
        return sum(map(lambda c: c.value, itertools.chain(*self.assets)))

    #
    # TODO: make this rule based
    #
    def turn(self, game):
        hand = list(map(str, self.hand_cards()))
        print("%s hand %s, %s" % (self, hand, game.discard_top()))
        if not any(self.hand_cards()):
            return False

        match = None

        # First match in hand.
        for k, l in self.hand.items():
            if len(l) > 1:
                match = [l.pop(), l.pop()]
                print(f"Play {match} from hand")
                break

        # Next check discard.
        if not match:
            d = game.discard_top()
            if d and self.hand[d.kind]:
                match = [game.discard.pop(), self.hand[d.kind].pop()]
                print(f"Play {match} using discard")

        # Consider stealing.

        if match:
            self.assets.append(match)
        elif any(self.hand_cards()):
            c = min(self.hand_cards(), key=lambda c: c.value)
            c = self.hand[c.kind].pop()
            print(f"Discard {c}")
            game.discard.append(c)

        print("%s stack %s" % (self, self.assets))
        self.replenish(game)
        return True

class Game:

    def __init__(self, n_players=5):
        sets = [list(itertools.repeat(Card(k, amt), n)) for k, amt, n in CARDS]
        self.deck = functools.reduce(operator.add, sets)
        random.shuffle(self.deck)
        self.discard = []
        self.players = [Player(i) for i in range(n_players)]

    def deal_hands(self):
        for i in range(HAND_SIZE):
            for p in self.players:
                p.deal(self.deck.pop())

    def discard_top(self):
        if self.discard:
            return self.discard[-1]

    def play(self):
        self.deal_hands()
        self.discard.append(self.deck.pop())
        while True:
            if not any(p.turn(self) for p in self.players):
                break
        s = sum(map(lambda c: c.value, self.discard))
        print(f"Discard pile {s}")
        for p in self.players:
            t = p.total()
            print(f"{p}: {t}")
            s += t
        print(s)

if __name__ == "__main__":
    game = Game()
    game.play()
