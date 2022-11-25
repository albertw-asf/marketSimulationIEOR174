import numpy as np
import random
from scipy.stats import skewnorm, norm
from exchange import *
from multivariate_skewnorm import multivariate_skewnorm

class Agent():
    def __init__(self, aggression_params, order_time_sd, theo_sd, true_value, customerid):

        self.true_value = true_value

        # calculate agent cahracteristics
        self.theo_value = round(true_value + norm.rvs(scale=theo_sd, size=1)[0])

        self.order_duration = 1800
        self.cid = customerid

    def get_theo(self):
        return self.theo_value
    
    def get_order_duration(self):
        return self.order_duration

    def get_cid(self):
        return self.cid

    def get_true_value(self):
        return self.true_value

class Maker(Agent):
    def __init__(self, aggression_params, order_time_sd, theo_sd, true_value, cid):
        super().__init__(aggression_params, order_time_sd, theo_sd, true_value, cid)

        mvn_skews, mvn_means, mvn_cov = aggression_params

        self.spread, self.quantity = multivariate_skewnorm(mvn_skews, mvn_means, mvn_cov).rvs(size=1)
        self.spread = round(self.spread)
        self.quantity = round(self.quantity)
        if self.spread < 1:
            self.spread = 1
        if self.quantity < 1:
            self.quantity = 1

        self.side = "AB"

    # def add_order(self):
    #     bid = self.theo_value - self.spread
    #     ask = self.theo_value + self.spread
    #     self.exchange.add_bid(bid, self.quantity, self.cid)
    #     self.exchange.add_ask(ask, self.quantity, self.cid)

    def get_spread(self):
        return self.spread
    
    def get_order_quantity(self):
        return self.quantity
    
    def get_side(self):
        return self.side

class Taker(Agent):
    def __init__(self, aggression_params, order_time_sd, theo_sd, true_value, cid):
        super().__init__(aggression_params, order_time_sd, theo_sd, true_value, cid)
    
        mvn_skews, mvn_means, mvn_cov = aggression_params

        self.spread, self.quantity = multivariate_skewnorm(mvn_skews, mvn_means, mvn_cov).rvs(size=1)
        self.spread = round(self.spread)
        self.quantity = round(self.quantity)
        if self.spread < 1:
            self.spread = 1
        if self.quantity < 1:
            self.quantity = 1

        bid_p = 0.5
        if random.random() < bid_p:
            self.side = "B"
        else: 
            self.side = "A"

    # def add_order(self):

    #     if self.side == "B":
    #         # bid = self.theo_value - self.spread
    #         self.exchange.add_bid(self.theo_value, self.quantity, self.cid)
    #     else: 
    #         # ask = self.theo_value + self.spread
    #         self.exchange.add_ask(self.theo_value, self.quantity, self.cid)
    
    def get_order_quantity(self):
        return self.quantity

    def get_side(self):
        return self.side