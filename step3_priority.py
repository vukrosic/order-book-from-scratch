"""Step 3: who goes first. Best price first; at the same price, whoever came first. Then a referee checks it."""
import random

from book import Book
from save import save


class QueueJumper(Book):
    """The same book with one character changed: > and < instead of >= and <=. Now the newest order goes first."""

    def rest(self, order):
        mine = self.bids if order.side == 'buy' else self.asks
        i = 0
        while i < len(mine) and (mine[i].price > order.price if order.side == 'buy' else mine[i].price < order.price):
            i += 1
        mine.insert(i, order)


def referee(book, orders, seed=3):
    """Sends random orders and keeps its own plain record of who waits. Counts every broken rule."""
    r = random.Random(seed)
    waiting = {}                                    # id -> [side, price, qty], written by the referee itself
    jumps = crossed = lost = 0
    for _ in range(orders):
        side = r.choice(('buy', 'sell'))
        price = 4000 + r.randint(-15, 15) + (-4 if side == 'buy' else 4)
        qty = r.randrange(1, 6) * 100
        n = len(book.trades)
        id = book.submit(side, qty, price)
        for t in book.trades[n:]:
            maker = t.sell_id if side == 'buy' else t.buy_id
            other = [(p if side == 'buy' else -p, i) for i, (s, p, q) in waiting.items() if s != side]
            if min(other)[1] != maker:              # somebody with a better price, or the same price and earlier, was skipped
                jumps += 1
            waiting[maker][2] -= t.qty
            if waiting[maker][2] == 0:
                del waiting[maker]
            qty -= t.qty
        if qty:
            waiting[id] = [side, price, qty]
        if book.best_bid() is not None and book.best_ask() is not None and book.best_bid() >= book.best_ask():
            crossed += 1                            # a buyer and a seller who agree must never both be waiting
        if sum(q for s, p, q in waiting.values()) != sum(o.qty for o in book.bids + book.asks):
            lost += 1                               # shares appeared or disappeared
    return dict(orders=orders, trades=len(book.trades), jumps=jumps, crossed=crossed, lost=lost)


if __name__ == '__main__':
    book = Book()
    ana = book.submit('sell', 100, 4002)
    ben = book.submit('sell', 100, 4002)
    book.submit('buy', 150, 4002)
    names = {ana: 'Ana', ben: 'Ben'}
    print('Ana and Ben both sell 100 at $40.02, Ana first. A buyer takes 150:')
    for t in book.trades:
        print('   %s sells %d' % (names[t.sell_id], t.qty))
    right = referee(Book(), 10000)
    wrong = referee(QueueJumper(), 10000)
    print('\nreferee, 10,000 random orders        trades   queue jumps   crossed book   lost shares')
    for name, res in (('the book', right), ('one character changed', wrong)):
        print('%-28s %14d %13d %14d %13d' % (name, res['trades'], res['jumps'], res['crossed'], res['lost']))
    save(3, demo=[[names[t.sell_id], t.qty] for t in book.trades], right=right, wrong=wrong)
