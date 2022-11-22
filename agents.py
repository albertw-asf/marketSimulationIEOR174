from scipy.stats import skewnorm, norm
from exchange import *
import numpy as np

class Agent():
    def __init__(self, exchange: Exchange, aggression_params, order_time_sd, theo_sd, true_value):
        self.exchange = exchange
        self.true_value = true_value

        # calculate agent cahracteristics
        self.theo_value = round(true_value + norm.rvs(scale=theo_sd, size=1)[0])
        self.spread = np.ceil(skewnorm.rvs(a=aggression_params[0], loc=aggression_params[1], scale=aggression_params[2], size=1)[0])
        # joint distribution between spread and quantity, find out how to do this
        # want spread to be inversely correlated with quantity; ie low spread = high quantity typically

        self.order_duration = 180

    def get_theo(self):
        return self.theo
    
    def get_order_time(self):
        return self.order_time

    def get_aggressiveness(self):
        return self.spread

    def get_cancel_duration(self):        
        return self.order_duration

    def get_theo(self):
        return self.theo_value


class Maker(Agent):
    def __init__(self, exchange, aggression_params, order_time_sd, theo_sd):
        super().__init__(exchange, aggression_params, order_time_sd, theo_sd)

    def add_order(self):
        if self.spread < 1:
            self.spread = 1
        bid = self.theo_value - self.spread
        ask = self.theo_value + self.spread
        self.exchange.add_bid(bid, )
        


class Taker(Agent):
    def __init__(exchange, aggression_params, order_time_sd, theo_sd):
        super().__init__(exchange, aggression_params, order_time_sd, theo_sd)
    