"""Checks. Run first by run_all.sh."""
import random

from book import Book
from fast import FastBook
from market import run
from step5_fast import play, stream

for Kind in (Book, FastBook):
    # a trade happens at the price of the order that waited, not the price of the order that arrived
    b = Kind()
    b.submit('sell', 100, 4002)
    b.submit('buy', 100, 4010)
    assert [tuple(t) for t in b.trades] == [(4002, 100, 2, 1)]
    assert b.best_bid() is None and b.best_ask() is None

    # price first: the cheaper seller is taken first even though it came later
    b = Kind()
    b.submit('sell', 100, 4005)
    b.submit('sell', 100, 4002)
    b.submit('buy', 100, 4010)
    assert b.trades[0].sell_id == 2

    # then time: at the same price, the earlier order is taken first
    b = Kind()
    b.submit('sell', 100, 4002)
    b.submit('sell', 100, 4002)
    b.submit('buy', 150, 4002)
    assert [(t.sell_id, t.qty) for t in b.trades] == [(1, 100), (2, 50)]

    # an order that is only partly filled waits with what is left
    b.submit('buy', 100, 4002)
    assert b.trades[-1].qty == 50 and b.best_bid() == 4002 and b.best_ask() is None

    # no trade when the prices do not meet
    b = Kind()
    b.submit('sell', 100, 4002)
    b.submit('buy', 100, 4001)
    assert not b.trades and b.best_bid() == 4001 and b.best_ask() == 4002

    # a market order takes any price and never waits
    b.submit('buy', 300)
    assert b.trades[-1].price == 4002 and b.best_ask() is None and b.best_bid() == 4001

    # a cancelled order cannot trade, and cannot be cancelled twice
    id = b.submit('sell', 100, 4005)
    assert b.cancel(id) and not b.cancel(id) and b.best_ask() is None
    b.submit('buy', 100, 4005)
    assert len(b.trades) == 1

    # 20,000 random orders: the book is never crossed, and every trade is inside both orders' limits
    r = random.Random(1)
    b, limit = Kind(), {}
    for _ in range(20000):
        side, price = r.choice(('buy', 'sell')), 4000 + r.randint(-20, 20)
        n = len(b.trades)
        limit[b.submit(side, r.randrange(1, 6) * 100, price)] = price
        for t in b.trades[n:]:
            assert limit[t.sell_id] <= t.price <= limit[t.buy_id]
        assert b.best_bid() is None or b.best_ask() is None or b.best_bid() < b.best_ask()

# the two books give the same trades, with market orders and cancels mixed in
events = stream(20000, seed=9)
assert play(Book(), events)[1] == play(FastBook(), events)[1]

# the market is repeatable: the same seed gives the same trades
a, b = run(seconds=600)[0], run(seconds=600)[0]
assert a.trades == b.trades and len(a.trades) > 1000

# with the band, no trade is more than 5 % from the average of the last five minutes (so never near 1 cent)
book, tape, log = run(seller_at=1800, band=True)
assert min(t.price for t in book.trades) > 3700 and max(t.price for t in book.trades) < 4300 and log['pauses']

print('all checks passed')
