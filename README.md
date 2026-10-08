# Order book from scratch

Eight short Python programs that build the part of a stock exchange that turns orders into trades: the order book and its matching loop. Then they fill it with simulated traders, crash it, and add the rule that stops the crash.

Standard library only. Nothing to install. No real market data, and nothing here is advice about buying or selling anything.

Video: the link is in the description of the film this repo belongs to.

## The question

A price tag in a shop was written by somebody. Nobody writes the price of a share. On 6 May 2010 shares that had opened above $40 traded at one cent for a short time, and nobody had decided that price either. So where does a price come from, and how can it be one cent?

## Run it

```bash
bash run_all.sh
```

Python 3.8 or newer. About 15 seconds. `demo-output.txt` is one saved run, and every number below comes from it. The runs are seeded, so your numbers are the same; only the seconds in step 5 and step 6 change with the machine.

| file | idea | result of the saved run |
| --- | --- | --- |
| `step1_book.py` | orders that wait: two sorted lists | best buyer $39.98, best seller $40.02, gap 4 cents, no trade |
| `step2_match.py` | the matching loop; a trade happens at the price of the order that waited | Ivy was ready to pay $40.05, pays $40.02 and keeps $7.50; Jon gets 50 shares and his other 350 wait |
| `step3_priority.py` | price first, then time; a referee checks 10,000 random orders | the book: 0 queue jumps. One character changed: 1,985 queue jumps, and every other check still passes |
| `step4_market.py` | an order with no price takes whatever the book holds | 100 shares: $40.02 each. 5,000 shares: $40.155 on average, $675 more. 8,000 shares: only 5,000 exist |
| `step5_fast.py` | the same book with one queue per price, a heap of prices and an index of orders | 100,000 events: 6.52 s → 0.06 s, the same 39,992 trades |
| `step6_market.py` | one hour of makers and takers | 133,130 orders, 9,063 trades, price between $39.83 and $40.04, average gap 1.7 cents |
| `step7_crash.py` | one large seller, and makers who leave | 33 seconds after the seller starts the price goes from $39.56 to 1 cent; 74,400 shares sell at 1 cent and 19,900 are bought at $100,000 |
| `step8_band.py` | the same crash with a price band and a pause | lowest trade $39.49, one pause, and the large seller gets $39.73 a share instead of $21.86 |

Shared files: `book.py` (the book with plain lists, about 60 lines), `fast.py` (the same book, faster), `market.py` (the simulated traders and the band), `tests.py` (checks that run first), `save.py` (each step stores its numbers in `runs/`).

## The rules of the book

1. An order is a side (buy or sell), a number of shares and a price limit. A market order has no limit.
2. A new order trades against the best waiting order on the other side for as long as the prices meet.
3. A trade happens at the price of the order that waited.
4. What is left of the new order waits in the book: behind every better price, and behind every order at the same price that came earlier.
5. A waiting order can be cancelled at any time.

## The simulated market (my own rules)

Prices are whole cents. One tick is one second.

- **Makers (20).** Each keeps three buy and three sell orders 2, 5 and 9 cents from the value it believes in, and lowers its prices by one cent for every 100 shares it holds. A maker leaves when it holds more than 3,000 shares, or when the price fell 2 % in a minute. It comes back after 180 seconds. While it is away it shows a buy order at 1 cent and a sell order at $100,000 for 100 shares (stub quotes).
- **Takers.** 0 to 2 market orders a second, 100 to 400 shares, buy or sell at random.
- **Stop-loss holders (300).** Each sells 100 to 500 shares with a market order when the last price falls to its stop, which is 1 % to 8 % below $40.
- **The large seller (steps 7 and 8).** 120,000 shares, 2,000 a second, with market orders, starting at minute 30.
- **The band (step 8).** A market order may not trade more than 5 % from the average trade price of the last five minutes; the part that cannot trade is cancelled. If that happens 15 seconds in a row, trading pauses for five minutes.

## Two things the runs showed that I did not expect

1. **The queue-jump bug is invisible to almost every check.** With `>` in place of `>=` in one line, the newest order goes to the front of its price. All trades still happen at legal prices, the book is never crossed, and no share is lost. Only a check that remembers who came first finds it: 1,985 times in 10,000 orders.
2. **The band helped the seller most.** The large seller received $2,623,451 without the band and $4,767,488 with it, for the same 120,000 shares. With the band, 24 of the 300 stop-loss orders fired instead of all 300.

## What this does not show

- A real market. Every trader rule is mine, including the 180 seconds after which a maker returns. The recovery in step 7 happens because of that rule.
- 6 May 2010. This is not a reconstruction of that day. It has one stock, no futures market and no second exchange.
- The real band rule in full. The real rule has different percentages by kind of stock and time of day.
- Real speed. A Python book that handles 1.8 million events a second in this test is far from an exchange's matching engine.

## Try this (I have not run it)

Some markets do not use "first come, first served". They share an incoming order among all orders at the best price in proportion to their size (pro-rata). Replace the time rule in `rest` and in the loop with that, and run the referee of step 3. Which of its three checks still makes sense?

## Sources for the real events and rules

- Mary L. Schapiro, testimony before the House subcommittee, SEC, 20 May 2010 (the times and index values of 6 May 2010, the cancelled trades, the one-cent trades, stub quotes, stop-loss orders).
- SEC press release 2010-216, 8 November 2010: new rules that prohibit market-maker stub quotes.
- SEC press release 2012-107, 1 June 2012: the Limit Up-Limit Down plan (5 % and 10 % bands around the average price of the last five minutes, 15 seconds, a five-minute pause).
- Wikipedia, "2010 flash crash" and "Order matching system" (secondary).

MIT licence.
