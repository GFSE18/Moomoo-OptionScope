import time
import csv
from moomoo import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
track_code1 = 'US.QQQ241204C520000'
track_code2 = 'US.QQQ241204P520000'

start_time_str = "2024-12-04 09:30:00"
end_time_str = "2024-12-04 16:00:00"
start_time = time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
end_time = time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
start_timestamp = time.mktime(start_time)
end_timestamp = time.mktime(end_time)
file_name = 'QQQ241204CP520000' + '.csv'

def get_bid_and_ask(code):
    ret, data = quote_ctx.get_order_book(code)
    if ret != RET_OK:
        print("Failed to get ask and bid:", data)
        return None, None
    return data['Bid'][0][0], data['Ask'][0][0]

def get_last_price(code):
    ret, data = quote_ctx.get_stock_quote(code)
    if ret != RET_OK:
        print("Failed to get current price:", data)
        return None
    return data['last_price'][0]

with open(file_name,'a') as csvfile:
    writer=csv.writer(csvfile)
    writer.writerow(['Time', 'Last Price C', 'Bid C', 'Ask C','Last Price P','Bid P','Ask P'])
    ret_sub,msg = quote_ctx.subscribe([track_code1,track_code2], [SubType.ORDER_BOOK, SubType.QUOTE], subscribe_push=False)
    if ret_sub != RET_OK:
        print("Subscription failed.")
        print(msg)
        quote_ctx.close()
        exit()
    while True:
        current_time=time.localtime()
        current_timestamp=time.mktime(current_time)
        current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
        if current_timestamp>=start_timestamp and current_timestamp<=end_timestamp:
            last_price1=get_last_price(track_code1)
            bid1,ask1=get_bid_and_ask(track_code1)
            last_price2=get_last_price(track_code2)
            bid2,ask2=get_bid_and_ask(track_code2)
            writer.writerow([current_time_str,last_price1,bid1,ask1,last_price2,bid2,ask2])
            print(f"Data written at {current_time_str}: Price C={last_price1}, Bid C={bid1}, Ask C={ask1} Price P={last_price2}, Bid P={bid2}, Ask P={ask2}")
            #csvfile.flush()
        else:
            print("Time out")
            break
        time.sleep(1)
quote_ctx.close()