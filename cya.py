#!/usr/bin/env python3

import enum
import functools
import itertools
import operator
import random

class CoverYourAssets:

    #
    # Labels don't really matter, but helpful for debugging.
    #
    AssetKind = enum.Enum('AssetKind', ['GOLD', 'SILVER', 'HOUSE', 'BASEBALL', 'JEWEWLS', 'BANK', 'CARS', 'COINS', 'CASH', 'STOCKS', 'PIGGY'])

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
        (AssetKind.PIGGY, 5, 10),
    ]

    class Card:

        def __init__(self, kind, value):
            self.kind = kind
            self.value = self.value = value

        def is_wild(self):
            return self.kind in [AssetKind.GOLD, AssetKind.SILVER]

        def __str__(self):
            return str(self.kind)

    class Deck:

        def __init__(self, card_cls, card_info):
            sets = [list(itertools.repeat(card_cls(k, amt), n)) for k, amt, n in card_info]
            self.cards = functools.reduce(operator.add, sets)

        def shuffle(self):
            random.shuffle(self.cards)

        def take(self):
            return self.cards.pop()

    class Player:

        def __init__(self, player_id):
            self.hand = []
            self.player_id = player_id

        def deal(self, card):
            self.hand.append(card)

        def new_hand(self):
            self.hand = []

        def hand_value(self):
            return sum(map(lambda c: c.value, self.hand))

        def name(self):
            return "Player"

    def __init__(self, n_players=5):
        self.deck = self.Deck(self.Card, self.CARDS)
        self.deck.shuffle()
        self.discard = []
        self.players = [self.Player(i) for i in range(n_players)]

    def deal_hands(self):
        for i in range(5):
            for p in self.players:
                p.deal(self.deck.take())

    def player_turn(self, player):
        hand = list(map(str, player.hand))
        print("%s hand %s" % (player.name(), hand))

    def play(self):
        self.deal_hands()
        while True:
            for p in self.players:
                self.player_turn(p)
            break

if __name__ == "__main__":
    game = CoverYourAssets()
    game.play()
