from collections import defaultdict
from re import A

class Exchange():
    def __init__(self):
        self.bids = defaultdict(0)
        self.asks = defaultdict(0)

        self.bid_customers = {}
        self.ask_customers = {}

    # add bid to exchange
    def add_bid(self, price, quantity, customer_id):
        # tob_bid = max(self.bids)
        tob_ask = min(self.asks)
        if price <= tob_ask:
            match_bid(price, quantity, customer_id)
            ... # TODO: matching algorithm
        else: 
            self.bids[price] += quantity
            self.bid_customers[customer_id] = (price, quantity)

    # add ask to exchange
    def add_ask(self, price, quantity, customer_id):
        tob_bid = max(self.bids)
        if price >= tob_bid:
            match_ask(price, quantity, customer_id)
            ... # TODO: matching algorithm
        else: 
            self.asks[price] += quantity
            self.ask_customers[customer_id] = (price, quantity)

    # remove bid from exchange
    def remove_bid(self, customer_id):
        assert customer_id in self.bid_customers
        price, quantity = self.bid_customers.pop(customer_id)
        self.bids[price] -= quantity
        return price, quantity

    # remove ask from exchange
    def remove_ask(self, customer_id):
        assert customer_id in self.ask_customers
        price, quantity = self.bid_customers.pop(customer_id)
        self.asks[price] -= quantity
        return price, quantity

    def match_bid(self, bpx, bqty, cid):
        best_asks = [x for x in self.asks if x <= bpx]
        
        bid_transactions = []
        ask_transactions = []

        for apx in best_asks:
            aqty = self.asks[apx]

            a_cids = [cid for cid in self.ask_customers if self.ask_customers[cid][0] == apx]

            if bqty >= aqty:
                bqty -= aqty
                for a_cid in a_cids:
                    self.remove_ask(a_cid)
            else: 

    def match_ask(self, px, qty, cid):
