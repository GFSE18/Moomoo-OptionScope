import time
import csv
from moomoo import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
track_code = 'US.QQQ241203C515000'
start_time_str = "2024-12-03 09:30:00"
end_time_str = "2024-12-03 16:00:00"
file_name = start_time_str[:10]+' '+track_code+'.csv'
is_buy_signal_cur=False
is_buy_signal_prev=False

def get_MA(num_cycle):
    ret,data=quote_ctx.get_cur_kline(track_code,10,KLType.K_1M)
    if ret==RET_OK:
        close_prices=data['close']
        close_prices=close_prices.to_list()
        return sum(close_prices[-num_cycle:])/num_cycle
    else:
        print("Failed to get MA")
        return None

def get_bid_ask(code):
    ret,data=quote_ctx.get_order_book(code)
    if ret==RET_OK:
        bid=float(data['Bid'][0][0])
        ask=float(data['Ask'][0][0])
        return bid,ask
    else:
        print("Failed to get bid & ask")
        return None,None
    
def get_timestamp(time_str):
    time_tuple=time.strptime(time_str,"%Y-%m-%d %H:%M:%S")
    timestamp=time.mktime(time_tuple)
    return timestamp

def get_action(is_buy_signal_cur,is_buy_signal_prev):
    if is_buy_signal_cur==is_buy_signal_prev:
        return None
    elif is_buy_signal_cur!=is_buy_signal_prev and is_buy_signal_cur==True:
        return 'Buy'
    else:
        return 'Sell'

# start_timestamp=get_timestamp(start_time_str)
# end_timestamp=get_timestamp(end_time_str)
# ret_sub_kl=quote_ctx.subscribe(track_code,SubType.K_1M,subscribe_push=False)[0]
# ret_sub_orderbook=quote_ctx.subscribe(track_code,SubType.ORDER_BOOK,subscribe_push=False)[0]
# if ret_sub_kl==RET_OK:
#     with open(file_name, 'a', newline='') as csvfile:
#         writer=csv.writer(csvfile)
#         writer.writerow(['Time','MA5','MA10','Bid','Ask','Action','Action Price'])
#         while True:
#             current_time=time.localtime()
#             current_time_str=time.strftime("%Y-%m-%d %H:%M:%S",current_time)
#             current_timestamp=time.mktime(current_time)
#             if current_timestamp>=start_timestamp and current_timestamp<=end_timestamp:
#                 ma5=get_MA(5)
#                 ma10=get_MA(10)
#                 bid,ask=get_bid_ask(track_code)
#                 action=None
#                 action_price=None
#                 if ma5 > ma10:
#                     is_buy_signal_cur = True
#                 else:
#                     is_buy_signal_cur = False

#                 action = get_action(is_buy_signal_cur, is_buy_signal_prev)  # Determine action based on the transition
#                 if action == 'Buy':
#                     action_price = ask
#                 elif action == 'Sell':
#                     action_price = bid
#                 else:
#                     action_price = None

#                 writer.writerow([current_time_str,ma5,ma10,bid,ask,action,action_price])
#                 print("Data written at: "+current_time_str)
#                 print("MA5: "+str(ma5)+" MA10: "+str(ma10)+" Bid: "+str(bid)+" Ask: "+str(ask)+" Action: "+str(action)+" Action Price: "+str(action_price))
#                 is_buy_signal_prev = is_buy_signal_cur
#             else:
#                 print("Time range exceeded, stopping...")
#                 break
#             time.sleep(60)
# else:
#     print("Subscription failed")
# quote_ctx.close()

start_timestamp=get_timestamp(start_time_str)
end_timestamp=get_timestamp(end_time_str)
with open(file_name, 'a', newline='') as csvfile:
    writer=csv.writer(csvfile)
    writer.writerow(['Time','MA5','MA10','Bid','Ask','Action','Action Price'])
    ret_sub_kl=quote_ctx.subscribe(track_code,SubType.K_1M,subscribe_push=False)[0]
    ret_sub_orderbook=quote_ctx.subscribe(track_code,SubType.ORDER_BOOK,subscribe_push=False)[0]
    if ret_sub_kl==RET_OK:
        while True:
            current_time=time.localtime()
            current_time_str=time.strftime("%Y-%m-%d %H:%M:%S",current_time)
            current_timestamp=time.mktime(current_time)
            if current_timestamp>=start_timestamp and current_timestamp<=end_timestamp:
                ma5=get_MA(5)
                ma10=get_MA(10)
                bid,ask=get_bid_ask(track_code)
                action=None
                action_price=None
                if ma5 > ma10:
                    is_buy_signal_cur = True
                else:
                    is_buy_signal_cur = False

                action = get_action(is_buy_signal_cur, is_buy_signal_prev)  # Determine action based on the transition
                if action == 'Buy':
                    action_price = ask
                elif action == 'Sell':
                    action_price = bid
                else:
                    action_price = None

                writer.writerow([current_time_str,ma5,ma10,bid,ask,action,action_price])
                print("Data written at: "+current_time_str)
                print("MA5: "+str(ma5)+" MA10: "+str(ma10)+" Bid: "+str(bid)+" Ask: "+str(ask)+" Action: "+str(action)+" Action Price: "+str(action_price))
                is_buy_signal_prev = is_buy_signal_cur
            else:
                print("Time range exceeded, stopping...")
                break
            time.sleep(60)
quote_ctx.close()