"""Step 6: a market. An hour of trading by makers and takers. Nobody in this program sets the price."""
import time

from book import money
from market import run
from save import save

if __name__ == '__main__':
    start = time.time()
    book, tape, log = run()
    seconds = time.time() - start
    prices = [t.price for t in book.trades]
    gaps = [row[3] - row[2] for row in tape if row[2] and row[3]]
    volume = sum(t.qty for t in book.trades)
    print('one hour, 20 makers, takers arriving at random')
    print('orders sent %s, trades %s, shares traded %s' % (format(book.next_id - 1, ','), format(len(prices), ','), format(volume, ',')))
    print('lowest trade %s, highest %s, last %s' % (money(min(prices)), money(max(prices)), money(prices[-1])))
    print('average gap between best buyer and best seller: %.1f cents' % (sum(gaps) / len(gaps)))
    print('stop-loss orders fired: %d' % log['stops_fired'])
    print('the whole hour took %.2f seconds to run' % seconds)
    save(6, orders=book.next_id - 1, trades=len(prices), volume=volume, low=min(prices), high=max(prices), last=prices[-1],
         gap=sum(gaps) / len(gaps), stops=log['stops_fired'], seconds=seconds)
