"""Step 4: the order with no price. A market order takes whatever the book holds, so a bigger order pays more."""
from book import Book, money
from save import save


def ladder():
    """Ten sell prices three cents apart with 500 shares at each, and one buyer."""
    book = Book()
    for k in range(10):
        book.submit('sell', 500, 4002 + 3 * k)
    book.submit('buy', 500, 3998)
    return book


if __name__ == '__main__':
    rows = []
    print('buy at any price   shares bought   average price   last share cost   paid above $40.02')
    for want in (100, 1000, 5000, 8000):
        book = ladder()
        book.submit('buy', want)
        got = sum(t.qty for t in book.trades)
        paid = sum(t.qty * t.price for t in book.trades)
        rows.append([want, got, paid / got, book.trades[-1].price, paid - got * 4002])
        print('%15d %15d %15s %17s %19s' % (want, got, '$%.3f' % (paid / got / 100), money(book.trades[-1].price), money(paid - got * 4002)))
    print('the order for 8,000 found only 5,000 shares. The other 3,000 found no seller and were dropped.')

    book = ladder()
    id = book.submit('sell', 300, 4000)
    print('\na new seller at $40.00: best seller %s' % money(book.best_ask()))
    book.cancel(id)
    print('the seller cancels:     best seller %s, trades: %d' % (money(book.best_ask()), len(book.trades)))
    book.cancel(book.bids[0].id)
    n = len(book.trades)
    book.submit('sell', 100)
    print('the only buyer cancels, then somebody sells 100 at any price: %d trades. There is nobody to sell to.' % (len(book.trades) - n))
    save(4, rows=rows)
