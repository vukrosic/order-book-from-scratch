"""Step 5: speed. The same 100,000 orders through the book with plain lists and the book with one queue per price."""
import hashlib
import random
import time

from book import Book
from fast import FastBook
from save import save


def stream(n, seed=5):
    """n events: 65 % orders with a price, 10 % market orders, 25 % cancels of an order that may still wait."""
    r = random.Random(seed)
    out, sent = [], 0
    for _ in range(n):
        u = r.random()
        if u < 0.25 and sent:
            out.append(('cancel', r.randint(max(1, sent - 3000), sent)))
        else:
            side = r.choice(('buy', 'sell'))
            price = None if u < 0.35 else 4000 + int(r.gauss(0, 40)) + (-20 if side == 'buy' else 20)
            out.append((side, r.randrange(1, 6) * 100, price))
            sent += 1
    return out


def play(book, events):
    start = time.time()
    for e in events:
        if e[0] == 'cancel':
            book.cancel(e[1])
        else:
            book.submit(*e)
    seconds = time.time() - start
    tape = hashlib.sha256(repr(book.trades).encode()).hexdigest()[:12]
    return seconds, tape


if __name__ == '__main__':
    events = stream(100000)
    slow, fast = Book(), FastBook()
    s1, tape1 = play(slow, events)
    s2, tape2 = play(fast, events)
    print('100,000 events          seconds   events per second   trades   fingerprint of all trades')
    print('plain lists          %10.2f %19s %8d   %s' % (s1, format(int(100000 / s1), ','), len(slow.trades), tape1))
    print('one queue per price  %10.2f %19s %8d   %s' % (s2, format(int(100000 / s2), ','), len(fast.trades), tape2))
    print('same trades: %s. %d times faster (the seconds change with the machine).' % (tape1 == tape2, round(s1 / s2)))
    print('orders waiting in the plain book at the end: %s' % format(len(slow.bids) + len(slow.asks), ','))
    save(5, slow=s1, fast=s2, trades=len(slow.trades), same=tape1 == tape2, tape=tape1, waiting=len(slow.bids) + len(slow.asks))
