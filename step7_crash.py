"""Step 7: the crash. The same hour, but at minute 30 one seller starts to sell 2,000 shares a second at any price."""
from book import money
from market import START, run
from save import save


def report(book, tape, log, seller_at):
    prices = [t.price for t in book.trades]
    out = dict(
        low=min(prices), high=max(prices), last=prices[-1],
        penny_shares=sum(t.qty for t in book.trades if t.price == 1),
        top_shares=sum(t.qty for t in book.trades if t.price == 10_000_000),
        far_trades=sum(1 for t in book.trades if t.price < START * 0.4 or t.price > START * 1.6),
        first_left=next((s for s, k, what in log['left'] if what == 'left'), None),
        all_left=next((row[0] for row in tape if row[6] == 0), None),
        first_penny=next((row[0] for row in tape if row[5] == 1), None),
        last_far=max((row[0] for row in tape if row[5] is not None and row[5] < START * 0.4), default=None),
        before_cliff=next((tape[row[0] - 1][1] for row in tape if row[5] == 1), None),
        seller_shares=log['seller_shares'], seller_money=log['seller_money'],
        stops_fired=log['stops_fired'], stop_shares=log['stop_shares'], stop_money=log['stop_money'],
        no_buyer=log['held_back'], pauses=log['pauses'])
    for key in ('first_left', 'all_left', 'first_penny', 'last_far'):
        if out[key] is not None:
            out[key] -= seller_at                       # seconds after the seller starts
    out['pauses'] = [p - seller_at for p in out['pauses']]
    return out


def show(res):
    print('lowest trade %s, highest trade %s, last trade of the hour %s' % (money(res['low']), money(res['high']), money(res['last'])))
    print('shares sold at 1 cent: %s. Shares bought at $100,000: %s' % (format(res['penny_shares'], ','), format(res['top_shares'], ',')))
    print('trades more than 60 %% away from $40: %d' % res['far_trades'])
    print('the large seller: %s shares for %s, %s a share' % (format(res['seller_shares'], ','), money(res['seller_money']),
                                                             money(res['seller_money'] / max(res['seller_shares'], 1))))
    print('stop-loss orders fired: %d. They sold %s shares for %s; %s shares found no buyer' % (
        res['stops_fired'], format(res['stop_shares'], ','), money(res['stop_money']), format(res['no_buyer'], ',')))


if __name__ == '__main__':
    book, tape, log = run(seller_at=1800)
    res = report(book, tape, log, 1800)
    print('seconds after the seller starts: first maker leaves %d, last maker leaves %d, first trade at 1 cent %d (the trade before it: %s)'
          % (res['first_left'], res['all_left'], res['first_penny'], money(res['before_cliff'])))
    print('last trade below $16: %d seconds after the start' % res['last_far'])
    show(res)
    save(7, **res)
