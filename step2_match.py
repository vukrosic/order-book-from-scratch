"""Step 2: a match. A buyer arrives who accepts the sellers' price, and the first trades happen."""
from book import money, show
from save import save
from step1_book import book, names


def send(name, side, qty, price=None):
    n = len(book.trades)
    names[book.submit(side, qty, price)] = name
    limit = 'at any price' if price is None else ('up to ' if side == 'buy' else 'down to ') + money(price)
    print('%s: %s %d %s' % (name, side, qty, limit))
    for t in book.trades[n:]:
        print('   TRADE %d shares at %s   (%s buys from %s)' % (t.qty, money(t.price), names[t.buy_id], names[t.sell_id]))
    return book.trades[n:]


if __name__ == '__main__':
    first = send('Ivy', 'buy', 250, 4005)
    paid = sum(t.qty * t.price for t in first)
    print('   Ivy was ready to pay %s and paid %s: %s less' % (money(250 * 4005), money(paid), money(250 * 4005 - paid)))
    second = send('Jon', 'buy', 400, 4003)
    print('   Jon got %d shares; his other %d wait in the book\n' % (sum(t.qty for t in second), book.bids[0].qty))
    show(book, names)
    print('\nlast price %s, best buyer %s, best seller %s' % (money(book.trades[-1].price), money(book.best_bid()), money(book.best_ask())))
    save(2, first=[list(t) for t in first], second=[list(t) for t in second], paid=paid, saved=250 * 4005 - paid,
         jon_rest=book.bids[0].qty, last=book.trades[-1].price, best_bid=book.best_bid(), best_ask=book.best_ask())
