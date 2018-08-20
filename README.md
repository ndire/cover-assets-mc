# Cover Your Assets

## Overview

[Cover Your Assets](https://www.grandpabecksgames.com/products---cover-your-assets) is a card game published by Grampa Beck Games.  Here are the [rules](https://www.grandpabecksgames.com/rules-cya).  This project uses a Monte Carlo simulation in python in order to identify optimal strategies. 

The game involves building a stack of matched asset cards.  At the end of the game the player's score is based on the amount of money in the stack.  Asset card matches may be formed from the player's hand, the discard pile, or by stealing the top match from another player's stack.

## Strategy

Each hand, a player must choose from:

1.  Make a paired match from his hand.

2.  Pick up the top of the discard pile to make a pair.

3.  Steal another player's top match using a matching card or Silver/Gold.

4.  Discard and draw a new card.

The question is how to prioritize these actions.
