import numpy as np
import random
from scipy.stats import skewnorm, norm
from exchange import *
from multivariate_skewnorm import multivariate_skewnorm

#####################################
#### global variable definitions ####
#####################################

order_duration = 500

class Agent():
    def __init__(self, theo_sd, true_value, customerid):

        self.true_value = true_value

        # calculate agent cahracteristics
        self.theo_value = round(true_value + norm.rvs(scale=theo_sd, size=1)[0])

        self.order_duration = order_duration
        self.cid = customerid

    def get_theo(self):
        return self.theo_value
    
    def get_order_duration(self):
        return self.order_duration

    def get_cid(self):
        return self.cid

    def get_true_value(self):
        return self.true_value

class MainCharacter(Agent):
    # simple policy always quotes 97@10, 103@10 for bid-ask
    def __init__(self, true_value, quantity, side, spread, cid):
        theo_sd = 0
        super().__init__(theo_sd, true_value, cid)
        self.quantity = quantity
        self.side = side
        self.spread = spread

    def get_spread(self):
        return self.spread
    
    def get_order_quantity(self):
        return self.quantity
    
    def get_side(self):
        return self.side
        
class SimpleTightPolicy(Agent):
    # tight policy always quotes 99@10, 101@10 for bid-ask
    def __init__(self, true_value):
        theo_sd = 0
        cid = -2
        super().__init__(theo_sd, true_value, cid)
        self.quantity = 10
        self.side = "AB"
        self.spread = 1

    def get_spread(self):
        return self.spread
    
    def get_order_quantity(self):
        return self.quantity

    def get_side(self):
        return self.side

class SimpleSmallPolicy(Agent):
    def __init__(self, true_value):
        theo_sd = 0
        cid = -2
        super().__init__(theo_sd, true_value, cid)
        self.quantity = 1
        self.side = "AB"
        self.spread = 1

# class: Arbtrageur
# can give perfect information or imperfect information, spread out between taking and asking based on where the top of book is

# class: regression to mean -er

# these classes don't have to be special designations, because 
class LaggedPolicy(Agent):
    # reading x ticks behind
    pass

class PsychicPolicy(Agent):
    # reading x ticks into the future
    pass 

## adversarial classes ##

class Maker(Agent):
    def __init__(self, aggression_params, order_time_sd, theo_sd, true_value, cid):
        super().__init__(theo_sd, true_value, cid)

        mvn_skews, mvn_means, mvn_cov = aggression_params

        self.spread, self.quantity = multivariate_skewnorm(mvn_skews, mvn_means, mvn_cov).rvs(size=1)
        self.spread = round(self.spread)
        self.quantity = round(abs(self.quantity))
        if self.spread < 1:
            self.spread = 1
        if self.quantity < 1:
            self.quantity = 1

        self.side = "AB"

    def get_spread(self):
        return self.spread
    
    def get_order_quantity(self):
        return self.quantity
    
    def get_side(self):
        return self.side

class Taker(Agent):
    def __init__(self, aggression_params, order_time_sd, theo_sd, true_value, cid):
        super().__init__(theo_sd, true_value, cid)
    
        mvn_skews, mvn_means, mvn_cov = aggression_params

        self.spread, self.quantity = multivariate_skewnorm(mvn_skews, mvn_means, mvn_cov).rvs(size=1)
        self.spread = round(self.spread)
        self.quantity = round(abs(self.quantity))
        if self.spread < 1:
            self.spread = 1
        if self.quantity < 1:
            self.quantity = 1

        bid_p = 0.5
        if random.random() < bid_p:
            self.side = "B"
        else: 
            self.side = "A"
    
    def get_order_quantity(self):
        return self.quantity

    def get_side(self):
        return self.side