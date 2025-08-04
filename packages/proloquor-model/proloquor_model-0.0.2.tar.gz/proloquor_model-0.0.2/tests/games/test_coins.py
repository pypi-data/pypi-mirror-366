import sys
if 'src' not in sys.path:
    sys.path.insert(0, 'src')
    
from proloquor_model.games.coins import Coin, CoinSide

def test_coin():
    c =  Coin()
    assert str(c) == "HEADS"

def test_coinFlip():
    c = Coin()
    heads = 0
    for i in range(1000):
        heads = heads + 1 if str(c.flip()) == 'HEADS' else heads

    assert 400 < heads < 600