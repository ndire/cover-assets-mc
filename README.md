# Cover Your Assets

## Overview

[Cover Your Assets](https://www.grandpabecksgames.com/products---cover-your-assets) 
is a card game published by Grampa Beck Games.  Here are the
[rules](https://www.grandpabecksgames.com/rules-cya).  This project uses a
Monte Carlo simulation in python in order to identify optimal strategies.
My intent is for the same framework to be reused for other analysis.

The game involves building a stack of matched asset cards.  There are 10 types
of asset cards in various denominations.  At the end of the game the player's
score is based on the amount of money in the stack.  Asset card matches may be
formed from the player's hand, the discard pile, or by stealing the top match
from another player's stack.

## Strategic Analysis

Each hand, a player must choose from:

1.  Make a paired match from her hand.

2.  Pick up the top of the discard pile to make a pair.

3.  Steal another player's top match using a matching card or Silver/Gold.

4.  Discard and draw a new card.

In addition, the player must decide how many cards to commit to defending the
top of her own stack. A player may choose to keep a Silver or Gold for later
stealing or defense.

The question is how to prioritize these actions. If a player has a pair that
matches the top of another user's stack, should they play that pair, or use it
to steal? In my experience playing with humans, people tend to have the
intuition that they should commit more to stealing and defending when the match
group is more than say, $50K.

## Approach

### Assumptions

These are basic assumptions that we will be unlikely to revisit:
* Silver and Gold are equal except for their value in the stack.
* Players have perfect memory of match values within each others' stacks.  It's
  not realistic to intentionally go deep in another player's stack, but players
  will notice high value matches in the top 5, which is realistic in my
  experience.

Simplifying assumptions which may not reflect reality:
* Discarding is avoided if at all possible.  Later we'll revisit whether it
  ever makes sense to discard lower value cards instead of stealing.
* Decisions are only made on current game state; there is no attempt to count
  cards and/or infer other player's hands based on past plays.  Ie, no
  "card-counting".  This mostly comes into play at the end of the game when
  some cards have been played out.  This is probably wise for a human player,
  but we'll ignore it for now.

### Strategic Parameters

We will start by simplifying the strategies using some parameters.

* *Defense*.
    * Never defend.  Don't block steal attempts.  Note that 
    * Defend value.
    * Always defend.
* *Stealing*
    * Never steal.
    * Steal above a certain value (say, 50-100).
    * Always steal if no match to play.
    * Always steal if possible.

## Installation

## TODO: 

* PyLint
* PyUnit
