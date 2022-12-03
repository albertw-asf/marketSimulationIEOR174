from collections import defaultdict
from agents import *

class Exchange():
    def __init__(self):
        self.tick_size = 1

        self.bids = defaultdict(lambda:0)
        self.asks = defaultdict(lambda:0)

        self.bid_customers = {}
        self.ask_customers = {}

        self.timestamp = 0
        self.transactions = []

        self.orders = {}
        # add fields to store transactions

    def match_bid(self, bpx, bqty, bcid, agent):        
        # get better ask prices on the market 
        best_asks = [x for x in self.asks if x <= bpx]
        original_bqty = bqty

        # iterate through best ask prices on the market
        for apx in best_asks:

            # get customer ids corresponding to current ask price,
            # should already be in ascending order by timestamp
            a_cids = [cid for cid in self.ask_customers if self.ask_customers[cid][0] == apx]
            for a_cid in a_cids:
                customer_aqty = self.ask_customers[a_cid][2]
                curr_agent = self.ask_customers[a_cid][3]

                if bqty >= customer_aqty:
                    bqty -= customer_aqty

                    # destroys acid in the loop?
                    self.remove_ask(a_cid)
                elif bqty < customer_aqty and bqty > 0:
                    self.asks[apx] -= bqty
                    if curr_agent is not None:
                        curr_agent.quantity -= bqty
                    self.ask_customers[a_cid] = (self.ask_customers[a_cid][0], self.ask_customers[a_cid][1], customer_aqty - bqty, curr_agent)
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
            self.add_bid(bpx, bqty, bcid, agent)

    def match_ask(self, apx, aqty, acid, agent):
        # get better ask prices on the market 
        best_bids = [x for x in self.bids if x >= apx]
        original_aqty = aqty

        # iterate through best bid prices on the market
        for bpx in best_bids:

            # get customer ids corresponding to current ask price,
            # should already be in ascending order by timestamp
            b_cids = [cid for cid in self.bid_customers if self.bid_customers[cid][0] == bpx]
            for b_cid in b_cids:
                customer_bqty = self.bid_customers[b_cid][2]
                curr_agent = self.bid_customers[b_cid][3]

                if aqty >= customer_bqty:
                    aqty -= customer_bqty
                    self.remove_bid(b_cid)
                elif aqty < customer_bqty and aqty > 0:
                    self.bids[bpx] -= aqty
                    if curr_agent is not None:
                        curr_agent.quantity -= aqty
                    self.bid_customers[b_cid] = (self.bid_customers[b_cid][0], self.bid_customers[b_cid][1], customer_bqty - aqty, curr_agent)
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
            self.add_ask(apx, aqty, acid, agent)

    # add bid to exchange
    def add_bid(self, price, quantity, customer_id, agent):
        # tob_bid = max(self.bids)
        tob_ask = min(self.asks) if len(self.asks) != 0 else float("inf")
        if price >= tob_ask:
            self.match_bid(price, quantity, customer_id, agent)

        else: 
            self.bids[price] += quantity
            self.bid_customers[customer_id] = (price, self.get_timestamp(), quantity, agent)
            
        self.bids = defaultdict(lambda:0, sorted(self.bids.items(), reverse=True))
        self.bid_customers = dict(sorted(self.bid_customers.items(), key=lambda item: (item[1][0], -item[1][1]), reverse=True))

    # add ask to exchange
    def add_ask(self, price, quantity, customer_id, agent):
        tob_bid = max(self.bids) if len(self.bids) != 0 else 0
        if price <= tob_bid:
            self.match_ask(price, quantity, customer_id, agent)

        else: 
            self.asks[price] += quantity
            self.ask_customers[customer_id] = (price, self.get_timestamp(), quantity, agent)
            # self.increment_timestamp()
        self.asks = defaultdict(lambda:0, sorted(self.asks.items()))
        self.ask_customers = dict(sorted(self.ask_customers.items(), key=lambda item: (item[1][0], item[1][1])))

    # remove bid from exchange
    def remove_bid(self, customer_id):
        assert customer_id in self.bid_customers
        price, timestamp, quantity, _ = self.bid_customers.pop(customer_id)

        if self.bids[price] == quantity: 
            self.bids.pop(price)
        else: 
            self.bids[price] -= quantity

        # self.increment_timestamp()
        return price, quantity

    # remove ask from exchange
    def remove_ask(self, customer_id):
        assert customer_id in self.ask_customers
        price, timestamp, quantity, _ = self.ask_customers.pop(customer_id)
        
        if self.asks[price] == quantity: 
            self.asks.pop(price)
        else: 
            self.asks[price] -= quantity
        
        # self.increment_timestamp()
        return price, quantity

    def increment_timestamp(self, amt):
        self.timestamp += amt
    
    def get_timestamp(self):
        return self.timestamp

    def get_transactions(self):
        return self.transactions

    def add_order(self, a):
        side = a.get_side()
        if side == "AB":
            bid = a.get_theo() - a.get_spread()
            ask = a.get_theo() + a.get_spread()
            self.add_bid(bid, a.get_order_quantity(), a.get_cid(), a)
            self.add_ask(ask, a.get_order_quantity(), a.get_cid(), a)
            self.orders[a.get_cid()] = {"bid": (bid, a.get_order_quantity()), "ask": (ask, a.get_order_quantity())}
        
        elif side == "A":
            self.add_ask(a.get_theo(), a.get_order_quantity(), a.get_cid(), a)
            self.orders[a.get_cid()] = {"ask": (a.get_theo(), a.get_order_quantity())}
        elif side == "B":
            self.add_bid(a.get_theo(), a.get_order_quantity(), a.get_cid(), a)
            self.orders[a.get_cid()] = {"bid": (a.get_theo(), a.get_order_quantity())}

    def check_cancelled_orders(self):
        to_cancel = []
        for cid in self.ask_customers.keys():
            curr_time = self.get_timestamp()
            curr_agent = self.ask_customers[cid][3]
            order_time = self.ask_customers[cid][1]
            if curr_time > curr_agent.get_order_duration() + order_time:
                to_cancel.append(cid)
        for cid in to_cancel:
            self.remove_ask(cid)

        to_cancel = []
        for cid in self.bid_customers.keys():
            curr_time = self.get_timestamp()
            curr_agent = self.bid_customers[cid][3]
            order_time = self.bid_customers[cid][1]
            if curr_time > curr_agent.get_order_duration() + order_time:
                to_cancel.append(cid)
        for cid in to_cancel:
            self.remove_bid(cid)
