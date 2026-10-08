"""Step 1: the book. Eight people want to trade and nobody agrees on a price, so all eight orders wait."""
from book import Book, money, show
from save import save

book, names = Book(), {}
orders = [('Ana', 'sell', 100, 4002), ('Eve', 'buy', 200, 3998), ('Ben', 'sell', 200, 4002), ('Fay', 'buy', 100, 3997),
          ('Cy', 'sell', 300, 4005), ('Gus', 'buy', 400, 3995), ('Di', 'sell', 500, 4010), ('Hal', 'buy', 300, 3990)]
for name, side, qty, price in orders:
    names[book.submit(side, qty, price)] = name

if __name__ == '__main__':
    show(book, names)
    spread = book.best_ask() - book.best_bid()
    print('\nbest buyer %s, best seller %s, gap %d cents, trades so far: %d'
          % (money(book.best_bid()), money(book.best_ask()), spread, len(book.trades)))
    save(1, orders=orders, best_bid=book.best_bid(), best_ask=book.best_ask(), spread=spread, trades=len(book.trades))
