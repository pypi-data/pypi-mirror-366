from enum import Enum
import numpy as np

class Suit(Enum):
    CLUBS    = 1
    DIAMONDS = 2
    HEARTS   = 3
    SPADES   = 4

class Rank(Enum):
    TWO   = 2
    THREE = 3
    FOUR  = 4
    FIVE  = 5
    SIX   = 6
    SEVEN = 7
    EIGHT = 8
    NINE  = 9
    TEN   = 10
    JACK  = 11
    QUEEN = 12
    KING  = 13
    ACE   = 14

class Card:
    def __init__(self, rank = Rank.ACE, suit = Suit.SPADES):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank.name} of {self.suit.name}"
    
class Deck:
    def __init__(self):
        self.cards = []

    def __str__(self):
        return ", ".join([str(c) for c in self.cards])
    
    def __len__(self):
        return len(self.cards)
    
    def add(self, card: Card):
        self.cards.append(card)
        return self
    
    def draw(self, replace = False):
        if replace:
            return self.cards[0]
        return self.cards.pop(0)
    
    def shuffle(self):
        np.random.shuffle(self.cards)
        return self
    
class PokerDeck(Deck):
    def __init__(self):
        super().__init__()
        for rank in Rank:
            for suit in Suit:
                self.add(Card(rank, suit))