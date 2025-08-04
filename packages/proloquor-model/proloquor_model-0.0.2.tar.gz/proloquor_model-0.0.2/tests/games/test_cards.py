import sys
if 'src' not in sys.path:
    sys.path.insert(0, 'src')

from proloquor_model.games.cards import Rank, Suit, Card, PokerDeck

def test_card():
    c = Card(Rank.NINE, Suit.DIAMONDS)

    assert str(c) == "NINE of DIAMONDS"
    
def test_PokerDeck():
    pd = PokerDeck().shuffle()

    assert len(pd) == 52