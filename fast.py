"""The same book with faster shelves. Same orders in, same trades out.

Every price has its own queue. Two heaps remember which prices are in use, an index finds any order by its id.
"""
import heapq
from collections import deque

from book import Order, Trade


class FastBook:
    def __init__(self):
        self.queue = {'buy': {}, 'sell': {}}        # price -> the orders waiting at that price, earliest first
        self.heap = {'buy': [], 'sell': []}         # the prices in use; the best one is on top
        self.index = {}                             # order id -> order, for cancel
        self.trades = []
        self.next_id = 1

    def best(self, side):
        heap, queue = self.heap[side], self.queue[side]
        while heap:
            price = -heap[0] if side == 'buy' else heap[0]
            line = queue.get(price)
            while line and line[0].qty == 0:        # filled or cancelled orders leave when they reach the front
                line.popleft()
            if line:
                return line[0]
            heapq.heappop(heap)
            queue.pop(price, None)
        return None

    def submit(self, side, qty, price=None):
        order = Order(self.next_id, side, price, qty)
        self.next_id += 1
        other = 'sell' if side == 'buy' else 'buy'
        while order.qty:
            best = self.best(other)
            if best is None:
                break
            if price is not None and (best.price > price if side == 'buy' else best.price < price):
                break
            qty = min(order.qty, best.qty)
            buy, sell = (order, best) if side == 'buy' else (best, order)
            self.trades.append(Trade(best.price, qty, buy.id, sell.id))
            order.qty -= qty
            best.qty -= qty
            if best.qty == 0:
                del self.index[best.id]
        if order.qty and price is not None:
            line = self.queue[side].get(price)
            if line is None:
                line = self.queue[side][price] = deque()
                heapq.heappush(self.heap[side], -price if side == 'buy' else price)
            line.append(order)
            self.index[order.id] = order
        return order.id

    def cancel(self, id):
        order = self.index.pop(id, None)
        if order is None:
            return False
        order.qty = 0                               # it stays in its queue as an empty order until it reaches the front
        return True

    def best_bid(self):
        best = self.best('buy')
        return best.price if best else None

    def best_ask(self):
        best = self.best('sell')
        return best.price if best else None
