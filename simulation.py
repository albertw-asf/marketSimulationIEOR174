import pandas as pd
import numpy as np

from exchange import *
from agents import *

import matplotlib.pyplot as plt
import random
from scipy.stats import bernoulli

def simulate(price_fnc, policy_fnc, policy_number=3, agent_arrival_rate=0.1, taker_probability=0.4, n=10000):
    # pre-determine some true price curve as a function of time
    # can begin as uniform
    e = Exchange()

    ### defining hyperparameters ###
    agent_arrival_rate = 0.1
    taker_probability = 0.4

    price_function = price_fnc
    customer_id = 1

    while e.get_timestamp() < n:     
        # agents arrive at same rate, some probability they are maker vs taker
        agent_arrival_time = random.expovariate(agent_arrival_rate)
        policy_fnc(e, price_fnc, policy_number)

        e.increment_timestamp(agent_arrival_time)
        e.check_cancelled_orders()

        order_duration_sd = 0.0 # placeholder
        theo_sd = 2.5
        agent_is_taker = random.random() < taker_probability
        if not agent_is_taker:
            mvn_skews = [8, 0]
            mvn_means = [2, 0]
            mvn_cov = [[9, -5.625], [-5.625, 6.25]]

            a = Maker((mvn_skews, mvn_means, mvn_cov), order_duration_sd, theo_sd, price_function(e.get_timestamp() - 5), customer_id)
        
        else: 
            mvn_skews = [8, 0]
            mvn_means = [2, 0]
            mvn_cov = [[9, -9], [-9, 16]]
            
            a = Taker((mvn_skews, mvn_means, mvn_cov), order_duration_sd, theo_sd, price_function(e.get_timestamp() - 3), customer_id)

        e.add_order(a)
        customer_id += 1
    print("total simulation time:", e.get_timestamp())
    print("total agents:", customer_id)
    return e

# function to parse transactions from exchange
def summarize_transactions(ex: Exchange, price_function, num_agents=10):
    arr = ex.get_transactions()
    # arr

    df = pd.DataFrame(arr)
    long = df[["bid_customerid", "price", "quantity", "timestamp", "aggressor_side"]]
    long["customer_side"] = ["bid"] * len(long)
    long = long.rename(columns={"bid_customerid": "customer_id"})
    short = df[["ask_customerid", "price", "quantity", "timestamp", "aggressor_side"]]
    short["customer_side"] = ["ask"] * len(long)
    short = short.rename(columns={"ask_customerid": "customer_id"})
    short.loc[:, "quantity"] = -1 * short["quantity"]

    summary = pd.concat([long, short], axis=0).sort_values("timestamp")
    summary["transaction_value"] = -1 * summary["price"] * summary["quantity"]

    summary["mod_customer_id"] = summary["customer_id"] % num_agents
    profit = summary.groupby("mod_customer_id").sum()[["transaction_value", "quantity"]]
    profit["profit"] = profit["quantity"] * price_function(ex.get_timestamp()) + profit["transaction_value"]
    profit = profit.sort_values("profit", ascending=False)
    return summary, profit