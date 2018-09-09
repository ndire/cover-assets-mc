#!/usr/bin/env python3

#
# TODO:
# - Fix wild strategy
# - defense
# - Asset match kind
#

import collections
import enum
import functools
import itertools
import operator as op
import random
import typing


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
    (AssetKind.CARS, 15, 10),
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

    def total_assets(self) -> int:
        return sum(map(lambda c: c.value, itertools.chain(*self.assets)))

    def hand_cards(self):
        return itertools.chain(*self.hand.values())

    def wild_cards(self):
        return itertools.chain(self.hand[AssetKind.SILVER], self.hand[AssetKind.GOLD])

    def available_asset(self) -> Card:
        if self.assets:
            card = next(self.reject_wild(self.assets[-1]), None)
            assert card, str(self.assets[-1])
            return (card.kind, sum(c.value for c in self.assets[-1]))
        return None

    @staticmethod
    def hand_match(hand, wild=False):
        for k, l in hand.items():
            if len(l) > 1 and (wild or not l[0].is_wild()):
                return k
        return None

    @staticmethod
    def discard_match(game, hand, wild=False):
        d = game.discard_top()
        if d and hand[d.kind] and (wild or not hand[d.kind][0].is_wild()):
            return d.kind
        return None

    @staticmethod
    def steal_match(game, hand):
        candidates = [p for p in game.players 
                      if p.available_asset() and hand[p.available_asset()[0]]]
        if candidates:
            return max(candidates, key=lambda p: p.available_asset()[1])
        return None

    @staticmethod
    def reject_wild(cards):
        return itertools.filterfalse(op.methodcaller('is_wild'), cards)

    #
    # Actions
    # 

    def steal_from(self) -> typing.List[Card]:
        return self.assets.pop()

    def replenish(self, game):
        while len(list(self.hand_cards())) < HAND_SIZE and game.deck:
            self.deal(game.deck.pop())

    #
    # TODO: make this rule based
    #
    def turn(self, game):
        hand = list(map(str, self.hand_cards()))
        print("%s hand %s; discard: %s" % (self, hand, game.discard_top()))
        if not any(self.hand_cards()):
            return False

        match = None

        # Check for discard wild.

        # First natural match in hand.
        kind = self.hand_match(self.hand)
        if kind:
            match = [self.hand[kind].pop(), self.hand[kind].pop()]
            print(f"\tPlay {match} from hand")

        # Next natural match discard.
        if not match:
            kind = self.discard_match(game, self.hand)
            if kind:
                match = [game.discard.pop(), self.hand[kind].pop()]
                print(f"\tPlay {match} using discard")

        # Consider stealing.
        if not match:
            other = self.steal_match(game, self.hand)
            if other:
                kind = other.available_asset()[0]
                match = other.steal_from()
                print(f"\tSteal {match} from {other}")
                match.append(self.hand[kind].pop())

        # Use wild
        if not match:
            wild = next(self.wild_cards(), None)
            if wild:
                # Make pair from top asset in hand and discard.
                cards = list(self.hand_cards())
                if game.discard_top():
                    cards.append(game.discard_top())
                cards = list(self.reject_wild(cards))
                if cards:
                    best = max(cards, key=op.attrgetter('value'))
                    match = [self.hand[wild.kind].pop()]
                    if self.hand[best.kind]:
                        match.append(self.hand[best.kind].pop())
                    else:
                        match.append(game.discard.pop())
                    print(f"\tPlay {match} using wild")

        if match:
            self.assets.append(match)
        elif any(self.hand_cards()):
            c = min(self.hand_cards(), key=lambda c: c.value)
            c = self.hand[c.kind].pop()
            print(f"\tDiscard {c}")
            game.discard.append(c)

        print("\t%s stack %s" % (self, self.assets))
        self.replenish(game)
        return True

class Game:

    def __init__(self, n_players=5):
        sets = [list(itertools.repeat(Card(k, amt), n)) for k, amt, n in CARDS]
        self.deck = functools.reduce(op.add, sets)
        random.shuffle(self.deck)
        self.discard = []
        self.players = [Player(i) for i in range(n_players)]

    def deal_hands(self):
        for _ in range(HAND_SIZE):
            for p in self.players:
                p.deal(self.deck.pop())

    def discard_top(self) -> Card:
        if self.discard:
            return self.discard[-1]

    def play(self):
        self.deal_hands()
        self.discard.append(self.deck.pop())
        while True:
            played = [p.turn(self) for p in self.players]
            #print(played)
            if not any(played):
                break
            #print(list(map(list, map(op.methodcaller('hand_cards'), self.players))))
        s = sum(map(lambda c: c.value, self.discard))
        print(f"Discard pile {s}")
        for p in self.players:
            t = p.total_assets()
            print(f"{p}: {t}")
            s += t
        print(s)

if __name__ == "__main__":
    gm = Game()
    gm.play()
