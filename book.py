"""The order book: two lists and one loop.

Prices are whole cents, so 4002 means $40.02. An order with price None is a market order: it takes any price.
"""
from collections import namedtuple

Trade = namedtuple('Trade', 'price qty buy_id sell_id')


class Order:
    __slots__ = ('id', 'side', 'price', 'qty')

    def __init__(self, id, side, price, qty):
        self.id, self.side, self.price, self.qty = id, side, price, qty


def money(cents):
    return '$%.2f' % (cents / 100)


class Book:
    def __init__(self):
        self.bids = []          # buy orders that wait, best first: highest price, then earliest
        self.asks = []          # sell orders that wait, best first: lowest price, then earliest
        self.trades = []
        self.next_id = 1

    def submit(self, side, qty, price=None):
        order = Order(self.next_id, side, price, qty)
        self.next_id += 1
        other = self.asks if side == 'buy' else self.bids
        while order.qty and other:
            best = other[0]
            if price is not None and (best.price > price if side == 'buy' else best.price < price):
                break                                   # the best waiting price is not good enough
            qty = min(order.qty, best.qty)
            buy, sell = (order, best) if side == 'buy' else (best, order)
            self.trades.append(Trade(best.price, qty, buy.id, sell.id))    # the waiting order's price
            order.qty -= qty
            best.qty -= qty
            if best.qty == 0:
                other.pop(0)
        if order.qty and price is not None:
            self.rest(order)                            # what is left waits in the book
        return order.id

    def rest(self, order):
        mine = self.bids if order.side == 'buy' else self.asks
        i = 0
        while i < len(mine) and (mine[i].price >= order.price if order.side == 'buy' else mine[i].price <= order.price):
            i += 1                                      # walk past every better price, and every equal price that came first
        mine.insert(i, order)

    def cancel(self, id):
        for mine in (self.bids, self.asks):
            for i, order in enumerate(mine):
                if order.id == id:
                    del mine[i]
                    return True
        return False

    def best_bid(self):
        return self.bids[0].price if self.bids else None

    def best_ask(self):
        return self.asks[0].price if self.asks else None

    def levels(self, side, n=5):
        """The first n prices of one side with the shares waiting at each."""
        out = []
        for order in (self.bids if side == 'buy' else self.asks):
            if out and out[-1][0] == order.price:
                out[-1][1] += order.qty
            elif len(out) < n:
                out.append([order.price, order.qty])
            else:
                break
        return out


def show(book, names=None):
    """Print the book the way a trading screen does: sellers on top, buyers below, best prices in the middle."""
    def who(order):
        return (names[order.id] + ' ') if names else ''
    for order in reversed(book.asks):
        print('   sell  %s  %s%d' % (money(order.price), who(order), order.qty))
    print('   ----')
    for order in book.bids:
        print('   buy   %s  %s%d' % (money(order.price), who(order), order.qty))
