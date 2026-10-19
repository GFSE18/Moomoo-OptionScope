class Ticker():
    def __init__(self,code,history_size):
        self.code=code
        self.cost=None
        self.price=None
        self.past_prices=[]
        self.indicator1=None
        self.indicator2=None
        self.indicator3=None
        self.history_size=history_size
        self.has_asset=False
        self.is_buy_cur=False
        self.is_buy_prev=False
        self.is_sell_cur=False
        self.is_sell_prev=False
        self.action=None

    def add_data(self,price):
        self.price=price
        if len(self.past_prices)>=self.history_size:
            self.past_prices.pop(0)
        self.past_prices.append(self.price)
    
    def update_indicators(self,in1,in2,in3):
        self.indicator1=in1
        self.indicator2=in2
        self.indicator3=in3

    def get_SMA(self,data):
        return sum(data)/len(data)

    def get_LMA(self,data):
        weights=list(range(1,self.history_size+1))
        weighted_sum=sum(data[i]*weights[i] for i in range(len(weights)))
        return weighted_sum/sum(weights)
    
    def get_SqMA(self, data):
        weights = list(range(1, self.history_size + 1))
        weights = [w**2 for w in weights]
        weighted_sum = sum(data[i] * weights[i] for i in range(len(weights)))
        return weighted_sum / sum(weights)

    def get_SMMA(self,data,smma_prev):
        if len(data)<self.history_size:
            return self.get_SMA(data)
        return ((self.history_size-1)*smma_prev+data[-1])/self.history_size
    
    def signal_check(self):
        return True
    
    def gain_loss_check(self):
        if not self.has_asset:
            return None
        return (self.price-self.cost)/self.cost

    def update_action(self):
        if self.is_buy_cur and not self.is_buy_prev and not self.has_asset:
            self.is_buy_prev=self.is_buy_cur
            self.is_sell_prev=self.is_sell_cur
            return True
        elif self.is_sell_cur and not self.is_sell_prev and self.has_asset:
            self.is_buy_prev=self.is_buy_cur
            self.is_sell_prev=self.is_sell_cur
            return False
        else:
            self.is_buy_prev=self.is_buy_cur
            self.is_sell_prev=self.is_sell_cur
            return None