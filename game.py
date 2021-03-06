#!/usr/bin/env python3

#
# TODO:
# - logging
# - Asset match kind
# - Fix reject_wild, is_wild
# - Evaluate return on wild
#

import collections
import enum
import functools
import itertools
import logging
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
    # Kind, value, count
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
        return type(self) == type(other) and self.kind == other.kind

    def __hash__(self):
        return hash(self.kind)

    def __repr__(self):
        return str(self)


class Action:
    """
    Encapsulates player's possible actions, to use with a given strategy.
    """

    def __init__(self, game, player, use_wild=False):
        self.game = game
        self.player = player
        self.use_wild = use_wild

    def evaluate(self):
        pass

    def value(self):
        pass

    def execute(self):
        pass


class StealAction(Action):

    def evaluate(self):
        self.other = None
        candidates = [p for p in self.game.players 
                      if p.available_asset() and 
                      p != self.player and
                      (self.player.hand[p.available_asset()[0]] or 
                       (self.use_wild and any(self.player.wild_cards())))]
        if candidates:
            self.other = max(candidates, key=lambda p: p.available_asset()[1])
            return True
        return False

    def value(self):
        return self.other.available_asset()[1]

    def execute(self):
        kind = self.other.available_asset()[0]
        logging.info(f"\tSteal {kind} from {self.other}")
        match = None
        while True:
            card = None
            if self.player.hand[kind]:
                card = self.player.hand[kind].pop()
            else:
                wild = next(self.player.wild_cards(), None)
                if wild:
                    card = self.player.hand[wild.kind].pop()
            if card is None:
                break
            if not self.other.defend(card):
                match = self.other.steal_from()
                break

        return match


class MatchHandAction(Action):

    def evaluate(self):
        self.pairs = []
        for k, l in self.player.hand.items():
            if not l or l[0].is_wild():
                continue
            if len(l) > 1:
                self.pairs.append(l[0:2])
            elif self.use_wild and any(self.player.wild_cards()):
                self.pairs.append([l[0], next(self.player.wild_cards())])
        return len(self.pairs) > 0

    def pairs_by_value(self):
        return map(lambda cs: (sum(map(op.attrgetter('value'), cs)), cs), self.pairs)

    def value(self):
        return max(self.pairs_by_value(), key=op.itemgetter(0))[0]

    def execute(self):
        pair = max(self.pairs_by_value(), key=op.itemgetter(0))[1]
        match = [self.player.hand[card.kind].pop() for card in pair]
        logging.info(f"\tPlay {match} from hand")
        return match


class MatchDiscardAction(Action):

    def evaluate(self):
        d = self.game.discard_top()
        self.kind = None
        if d:
            if d.is_wild():
                eligible = list(self.player.reject_wild(self.player.hand_cards()))
                if any(eligible):
                    card = max(eligible, key=op.attrgetter('value'))
                    if card:
                        self.kind = card.kind
            elif self.player.hand[d.kind]:
                self.kind = d.kind
            elif self.use_wild and any(self.player.wild_cards()):
                self.kind = next(self.player.wild_cards()).kind
        return bool(self.kind)

    def value(self):
        return self.game.discard_top().value + self.player.hand[self.kind][0].value

    def execute(self):
        match = [self.game.discard.pop(), self.player.hand[self.kind].pop()]
        logging.info(f"\tPlay {match} using discard")
        return match


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
        return sum(map(lambda c: c.value, self.asset_cards()))

    def asset_cards(self) -> typing.List:
        return itertools.chain(*self.assets)

    def hand_cards(self):
        return itertools.chain(*self.hand.values())

    def wild_cards(self):
        return itertools.chain(self.hand.get(AssetKind.SILVER, []), 
                               self.hand.get(AssetKind.GOLD, []))

    def can_steal(self):
        return len(self.assets) > 1

    def available_asset(self) -> Card:
        if self.can_steal():
            assert None not in self.assets[-1]
            card = next(self.reject_wild(self.assets[-1]), None)
            assert card, str(self.assets[-1])
            return (card.kind, sum(c.value for c in self.assets[-1]))
        return None

    @staticmethod
    def reject_wild(cards):
        return itertools.filterfalse(op.methodcaller('is_wild'), cards)

    #
    # Actions
    # 
    def defend(self, acard):
        a = self.available_asset()
        assert a
        k, v = a
        self.assets[-1].append(acard)

        #
        # Find a card to defend
        # TODO: policy.  Don't use gold to defend low value.
        #
        dcard = None
        if self.hand[k]:
            dcard = self.hand[k].pop()
        elif any(self.wild_cards()):
            wild = next(self.wild_cards())
            dcard = self.hand[wild.kind].pop()
        if dcard:
            self.assets[-1].append(dcard)
            return True
        return False

    def steal_from(self) -> typing.List[Card]:
        return self.assets.pop()

    def replenish(self, game):
        while len(list(self.hand_cards())) < HAND_SIZE and game.deck:
            self.deal(game.deck.pop())

    def play_card(self, game):
        #
        # Enumerate actions.
        #
        possible = [MatchHandAction, MatchDiscardAction]
        if self.can_steal():
            possible.append(StealAction)
        for wild in [False, True]:
            actions = [cls(game, self, wild) for cls 
                       in possible]
            available = [a for a in actions if a.evaluate()]
            if available:
                choice = max(available, key=op.methodcaller('value'))
                match = choice.execute()
                if match:
                    self.assets.append(match)
                return True
        return False


    def discard(self, game):
        # TODO: be more intelligent about discard.
        if any(self.hand_cards()):
            c = min(self.hand_cards(), key=lambda c: c.value)
            c = self.hand[c.kind].pop()
            logging.info(f"\tDiscard {c}")
            game.discard.append(c)


    def turn(self, game):
        hand = list(map(str, self.hand_cards()))
        logging.info("%s hand %s; discard: %s" % (self, hand, game.discard_top()))
        if not any(self.hand_cards()):
            return False

        played = self.play_card(game)
        if not played:
            self.discard(game)

        logging.info("\t%s stack %s" % (self, self.assets))
        self.replenish(game)
        return True


def GreedyPlayer(Player):
    pass


class Game:

    def __init__(self, n_players=5, verbose=False):
        sets = [list(itertools.repeat(Card(k, amt), n)) for k, amt, n in CARDS]
        self.deck = functools.reduce(op.add, sets)
        random.shuffle(self.deck)
        self.discard = []
        self.players = [Player(i) for i in range(n_players)]
        random.shuffle(self.players)

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
            if not any(played):
                break

        s = sum(map(lambda c: c.value, self.discard))
        logging.info(f"Discard pile {s} ({self.discard})")
        for p in self.players:
            t = p.total_assets()
            logging.info(f"{p}: {t}")
            s += t

        assert s == 1360, s

        # Make sure we didn't lose any cards
        c = sum([len(list(p.asset_cards())) for p in self.players]) + len(self.discard)
        assert c == 110, c

        return {p.player_id : p.total_assets() for p in self.players}


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    gm = Game()
    gm.play()
