from collections import defaultdict
from re import A

class Exchange():
    def __init__(self):
        self.tick_size = 1

        self.bids = defaultdict(lambda:0)
        self.asks = defaultdict(lambda:0)

        self.bid_customers = {}
        self.ask_customers = {}

        self.timestamp = 0
        self.transactions = []
        # add fields to store transactions

    def match_bid(self, bpx, bqty, bcid):
        '''
        summary: 
        - given bid as taker side, go through ask side of book and get better asks
        - start at best (lowest) ask and go up if the order still has more qty to be filled
        - allow all partial filling; match by price then timestamp
        '''
        
        # get better ask prices on the market 
        best_asks = [x for x in self.asks if x <= bpx]
        original_bqty = bqty

        # iterate through best ask prices on the market
        for apx in best_asks:
            total_aqty = self.asks[apx]

            # get customer ids corresponding to current ask price,
            # should already be in ascending order by timestamp
            a_cids = [cid for cid in self.ask_customers if self.ask_customers[cid][0] == apx]
            for a_cid in a_cids:
                customer_aqty = self.ask_customers[a_cid][2]
                if bqty >= customer_aqty:
                    bqty -= customer_aqty
                    self.remove_ask(a_cid)
                elif bqty < customer_aqty and bqty > 0:
                    self.asks[apx] -= bqty
                    self.ask_customers[a_cid] = (self.ask_customers[a_cid][0], self.ask_customers[a_cid][1], customer_aqty - bqty)
                    bqty = 0
                else:
                    break
                self.transactions.append({"bid_customerid": bcid, 
                                                "ask_customerid": a_cid, 
                                                "price": bpx, 
                                                "quantity": min(original_bqty, customer_aqty), 
                                                "timestamp": self.timestamp, 
                                                "aggressor_side": "bid", 
                                                "aggressor_id": bcid
                                            })
            if bqty == 0:
                break
        # new
        if bqty != 0:
            self.add_bid(bpx, bqty, bcid)

    def match_ask(self, apx, aqty, acid):
        # get better ask prices on the market 
        best_bids = [x for x in self.bids if x >= apx]
        original_aqty = aqty

        # iterate through best ask prices on the market
        for bpx in best_bids:

            # get customer ids corresponding to current ask price,
            # should already be in ascending order by timestamp
            b_cids = [cid for cid in self.bid_customers if self.bid_customers[cid][0] == bpx]
            for b_cid in b_cids:
                customer_bqty = self.bid_customers[b_cid][2]
                if aqty >= customer_bqty:
                    aqty -= customer_bqty
                    self.remove_bid(b_cid)
                elif aqty < customer_bqty and aqty > 0:
                    self.bids[bpx] -= aqty
                    self.bid_customers[b_cid] = (self.bid_customers[b_cid][0], self.bid_customers[b_cid][1], customer_bqty - aqty)
                    aqty = 0
                else:
                    break

                self.transactions.append({"bid_customerid": b_cid, 
                                                "ask_customerid": acid, 
                                                "price": apx, 
                                                "quantity": min(original_aqty, customer_bqty), 
                                                "timestamp": self.timestamp, 
                                                "aggressor_side": "ask", 
                                                "aggressor_id": acid
                                            })
            
            if aqty == 0:
                break
        # new
        if aqty != 0:
            self.add_ask(apx, aqty, acid)

    # add bid to exchange
    def add_bid(self, price, quantity, customer_id):
        # tob_bid = max(self.bids)
        tob_ask = min(self.asks) if len(self.asks) != 0 else float("inf")
        if price >= tob_ask:
            self.match_bid(price, quantity, customer_id)
            # ... # TODO: matching algorithm
        else: 
            self.bids[price] += quantity
            self.bid_customers[customer_id] = (price, self.get_timestamp(), quantity)
            self.increment_timestamp()
        self.bids = defaultdict(lambda:0, sorted(self.bids.items(), reverse=True))
        self.bid_customers = dict(sorted(self.bid_customers.items(), key=lambda item: (item[1][0], -item[1][1]), reverse=True))

    # add ask to exchange
    def add_ask(self, price, quantity, customer_id):
        tob_bid = max(self.bids) if len(self.bids) != 0 else 0
        if price <= tob_bid:
            self.match_ask(price, quantity, customer_id)
            # ... # TODO: matching algorithm
        else: 
            self.asks[price] += quantity
            self.ask_customers[customer_id] = (price, self.get_timestamp(), quantity)
            self.increment_timestamp()
        self.asks = defaultdict(lambda:0, sorted(self.asks.items()))
        self.ask_customers = dict(sorted(self.ask_customers.items(), key=lambda item: (item[1][0], item[1][1])))

    # remove bid from exchange
    def remove_bid(self, customer_id):
        assert customer_id in self.bid_customers
        price, timestamp, quantity = self.bid_customers.pop(customer_id)

        if self.bids[price] == quantity: 
            self.bids.pop(price)
        else: 
            self.bids[price] -= quantity

        self.increment_timestamp()
        return price, quantity

    # remove ask from exchange
    def remove_ask(self, customer_id):
        assert customer_id in self.ask_customers
        price, timestamp, quantity = self.ask_customers.pop(customer_id)
        
        if self.asks[price] == quantity: 
            self.asks.pop(price)
        else: 
            self.asks[price] -= quantity
        
        self.increment_timestamp()
        return price, quantity

    def increment_timestamp(self):
        self.timestamp += 1
    
    def get_timestamp(self):
        return self.timestamp

    def get_transactions(self):
        return self.transactions