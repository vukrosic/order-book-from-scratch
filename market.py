"""A small simulated market on top of the book. One tick is one second.

Who trades here, all by rules I chose:
  makers   20 traders who always keep three buy and three sell orders around the value of the share. Each one
           leaves when it holds too many shares or when the price fell fast, and comes back later.
  takers   people who buy or sell a few hundred shares right now, with market orders.
  stops    300 holders with a stop-loss: "if the price falls to X, sell my shares at any price".
  seller   optional: one large seller who sells 2,000 shares every second, whatever the price.
A maker that has left still shows a buy order at 1 cent and a sell order at $100,000 (stub quotes).

band=True adds the price band: no trade more than 5 % from the average price of the last five minutes; if sellers
or buyers are stopped by the band for 15 seconds in a row, trading pauses for five minutes.
"""
import random

from fast import FastBook

START = 4000            # $40.00
STUB_BID, STUB_ASK = 1, 10_000_000


def run(seconds=3600, seed=7, seller_at=None, band=False, book=None, watch=None):
    r = random.Random(seed)
    book = book or FastBook()
    owner = {}                                          # order id -> maker number
    makers = [dict(inv=0, ids=[], away_until=-1, away=False, since=-60, lean=r.randint(-2, 2)) for _ in range(20)]
    stops = sorted(((START * (1 - r.uniform(0.01, 0.08)), r.randrange(1, 6) * 100) for _ in range(300)), reverse=True)
    value, last, seen = START, START, 0
    to_sell, paused_until, stuck = 0, -1, 0
    recent = []                                         # (second, price, qty) of the last five minutes
    tape = []                                           # one row per second
    log = dict(stops_fired=0, stop_shares=0, stop_money=0, seller_shares=0, seller_money=0, pauses=[],
               held_back=0, left=[])

    def take(side, qty, who=None):
        """A market order. With the band it may not trade outside the band; the rest is cancelled."""
        nonlocal stuck_now
        limit = None
        if band and recent:
            ref = sum(p * q for _, p, q in recent) / sum(q for _, _, q in recent)
            limit = int(ref * 1.05) if side == 'buy' else int(ref * 0.95) + 1
        n = len(book.trades)
        id = book.submit(side, qty, limit)
        if limit is not None and book.cancel(id):
            stuck_now = True
        got = sum(t.qty for t in book.trades[n:])
        paid = sum(t.qty * t.price for t in book.trades[n:])
        return got, paid

    for now in range(seconds):
        stuck_now = False
        if r.random() < 0.1:
            value += r.choice((-1, 1))
        paused = now < paused_until
        # makers
        for k, m in enumerate(makers):
            if m['away'] and now >= m['away_until']:
                m['away'], m['inv'], m['since'] = False, 0, now      # back, with the shares sold somewhere else
                log['left'].append((now, k, 'back'))
            if paused or (r.random() > 0.3 and m['ids']):
                continue
            for id in m['ids']:
                book.cancel(id)
            m['ids'] = []
            if m['away']:
                quotes = [('buy', STUB_BID, 100), ('sell', STUB_ASK, 100)]
            else:
                mid = value + m['lean'] - m['inv'] // 100          # holding more shares -> lower prices
                quotes = [(side, mid + sign * off, r.randrange(2, 6) * 100)
                          for off in (2, 5, 9) for side, sign in (('buy', -1), ('sell', 1))]
            for side, price, qty in quotes:
                id = book.submit(side, qty, max(price, 1))
                owner[id] = k
                m['ids'].append(id)
        if not paused:
            # takers
            for _ in range(r.choice((0, 1, 1, 2))):
                take(r.choice(('buy', 'sell')), r.randrange(1, 5) * 100)
            # stop-loss orders
            while stops and last <= stops[0][0]:
                _, qty = stops.pop(0)
                got, paid = take('sell', qty)
                log['stops_fired'] += 1
                log['stop_shares'] += got
                log['stop_money'] += paid
                log['held_back'] += qty - got
                if got < qty and band:
                    stops.append((10 ** 9, qty - got))   # still wants to sell: tries again next second
                    stops.sort(reverse=True)
                    break
            # the large seller
            if seller_at is not None and now == seller_at:
                to_sell = 120_000
            if to_sell:
                got, paid = take('sell', min(2000, to_sell))
                to_sell -= got
                log['seller_shares'] += got
                log['seller_money'] += paid
        # what happened this second
        new = book.trades[seen:]
        seen = len(book.trades)
        for t in new:
            for id, sign in ((t.buy_id, 1), (t.sell_id, -1)):
                if id in owner:
                    makers[owner[id]]['inv'] += sign * t.qty
        if new:
            last = new[-1].price
            recent.extend((now, t.price, t.qty) for t in new)
        while recent and recent[0][0] <= now - 300:
            recent.pop(0)
        minute_ago = next((row[1] for row in reversed(tape) if row[0] <= now - 60), START)
        for k, m in enumerate(makers):
            fell_fast = last < minute_ago * 0.98 and now - m['since'] >= 60
            if not m['away'] and not paused and (m['inv'] > 3000 or fell_fast):
                m['away'], m['away_until'] = True, now + 180
                for id in m['ids']:
                    book.cancel(id)
                m['ids'] = []
                for side, price in (('buy', STUB_BID), ('sell', STUB_ASK)):
                    id = book.submit(side, 100, price)
                    owner[id] = k
                    m['ids'].append(id)
                log['left'].append((now, k, 'left'))
        if band and not paused:
            stuck = stuck + 1 if stuck_now else 0
            if stuck >= 15:
                paused_until, stuck = now + 300, 0
                log['pauses'].append(now)
        tape.append((now, last, book.best_bid(), book.best_ask(), sum(t.qty for t in new),
                     min((t.price for t in new), default=None), sum(not m['away'] for m in makers), paused))
        if watch:
            watch(now, book, makers, log)            # for drawing: a look at the book once a second
    return book, tape, log
