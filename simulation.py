import pandas as pd
import numpy as np

from exchange import *
from agents import *

import matplotlib.pyplot as plt
import random
from scipy.stats import bernoulli

def execute_policy(e: Exchange):
    # a = SimplePolicy(100)
    a = TightPolicy(100)
    e.add_order(a)

# pre-determine some true price curve as a function of time
# can begin as uniform
e = Exchange()

### defining hyperparameters ###
agent_arrival_rate = 0.1
taker_probability = 0.4

price_function = lambda t: 100
# future price functions can incorporate like lagged information when the agents read it 
# true_price_func = lambda t: np.sin(t / 5*60)
customer_id = 1
count = 0

while e.get_timestamp() < 1000:     
    ### pseudo code this ###

    # agent arrives by some exponential inter-arrival time simulating poisson
    # increment timestamp by exponential variable
    # calculate agent's characteristics (aggression level, theo value, cancel duration)
    # first check existing cancel queue, remove orders if necessary
    # add agent's bid/asks to exchange
    # plot exchange
    # sidenote: also need to increment customerids

    # add in own policy logic 

    ### ------------------------------------------------------------ ###

    # agents arrive at same rate, some probability they are maker vs taker
    agent_arrival_time = random.expovariate(agent_arrival_rate)
    execute_policy(e)

    e.increment_timestamp(agent_arrival_time)
    e.check_cancelled_orders()

    order_duration_sd = 0.0 # placeholder
    theo_sd = 2.5
    agent_is_taker = random.random() < taker_probability
    if not agent_is_taker:
        mvn_skews = [8, 0]
        mvn_means = [2, 10]
        mvn_cov = [[9, -5.625], [-5.625, 6.25]]

        a = Maker((mvn_skews, mvn_means, mvn_cov), order_duration_sd, theo_sd, price_function(e.get_timestamp()), customer_id)
    
    else: 
        mvn_skews = [8, 0]
        mvn_means = [2, 20]
        mvn_cov = [[9, -9], [-9, 16]]
        
        a = Taker((mvn_skews, mvn_means, mvn_cov), order_duration_sd, theo_sd, price_function(e.get_timestamp()), customer_id)

    e.add_order(a)

    print(e.get_timestamp())
    customer_id += 1