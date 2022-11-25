import pandas as pd
import numpy as np

from exchange import *
from agents import *

import matplotlib.pyplot as plt
import random
from scipy.stats import bernoulli


# pre-determine some true price curve as a function of time
# can begin as uniform
random.seed(88)
e = Exchange()

### defining hyperparameters ###
agent_arrival_rate = 10
taker_probability = 0.4
true_price_func = lambda t: np.sin(t / 5*60)
temp_true_val = 100

while e.get_timestamp() < 100: 
    customer_id = 1
    
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

    order_duration_sd = 0.0 # placeholder
    theo_sd = 2.5
    agent_is_taker = random.random() < taker_probability
    if not agent_is_taker:
        mvn_skews = [8, 0]
        mvn_means = [2, 10]
        mvn_cov = [[9, -5.625], [-5.625, 6.25]]

        a = Maker((mvn_skews, mvn_means, mvn_cov), order_duration_sd, theo_sd, temp_true_val, customer_id)
    
    else: 
        mvn_skews = [8, 0]
        mvn_means = [2, 20]
        mvn_cov = [[9, -9], [-9, 16]]
        
        a = Taker((mvn_skews, mvn_means, mvn_cov), order_duration_sd, theo_sd, temp_true_val, customer_id)

    print("side", a.get_side())
    print("order", a.get_theo(), a.get_order_quantity())
    if not agent_is_taker:
        print("spread", a.get_spread())
    print("\n")
    e.add_order(a)

    # show_exchange(e)

    # check cancelled orders
    for cid in e.ask_customers.keys():
        curr_time = e.get_timestamp()
        curr_agent = e.ask_customers[cid][3]
        order_time = e.ask_customers[cid][1]
        if curr_time > curr_agent.get_order_duration() + order_time:
            e.remove_ask(cid)
        
    for cid in e.bid_customers.keys():
        curr_time = e.get_timestamp()
        curr_agent = e.bid_customers[cid][3]
        order_time = e.bid_customers[cid][1]
        if curr_time > curr_agent.get_order_duration() + order_time:
            e.remove_bid(cid)

    customer_id += 1
    e.increment_timestamp(agent_arrival_time)