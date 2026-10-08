"""Step 8: the band. The same crash again with one rule added: no trade more than 5 % from the last five minutes."""
from step7_crash import report, show
from market import run
from save import save

if __name__ == '__main__':
    out = {}
    for name, band in (('no band', False), ('with the band', True)):
        book, tape, log = run(seller_at=1800, band=band)
        out[name] = res = report(book, tape, log, 1800)
        print('--- ' + name)
        show(res)
        print('pauses: %d%s\n' % (len(res['pauses']), ''.join(', %d seconds after the seller starts' % p for p in res['pauses'])))
    a, b = out['no band'], out['with the band']
    print('the large seller got %.1f times more money with the band' % (b['seller_money'] / a['seller_money']))
    save(8, **{'none': a, 'band': b})
