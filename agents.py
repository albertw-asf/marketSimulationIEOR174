class Agent():
    def __init__(self, exchange, aggression_level, order_time, theo_px):
        self.exchange = exchange
        self.aggression_level = aggression_level
        self.order_time = order_time
        self.theo = theo_px

    def get_theo(self):
        return self.theo
    
    def get_order_time(self):
        return self.order_time

class Maker(Agent):
    def __init__(self, exchange, aggression_level, order_time, theo_px):
        super().__init__(exchange, aggression_level, order_time, theo_px)

class Taker(Agent):
    def __init__(exchange, aggression_level, order_time, theo_px):
        super().__init__(exchange, aggression_level, order_time, theo_px)
    