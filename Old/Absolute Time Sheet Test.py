import time
import csv
from moomoo import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
track_code = 'US.QQQ241203C515000'

start_time_str = "2024-12-03 09:00:00"
end_time_str = "2024-12-03 16:00:00"
start_time = time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
end_time = time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
start_timestamp = time.mktime(start_time)
end_timestamp = time.mktime(end_time)

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
    return data['last_price'][0]  # Access the correct price

file_name = start_time_str[:10] + ' ' + track_code + '.csv'
with open(file_name, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Time', 'Last Price', 'Bid', 'Ask'])
    ret_sub,msg = quote_ctx.subscribe(track_code, [SubType.ORDER_BOOK, SubType.QUOTE], subscribe_push=False)
    if ret_sub != RET_OK:
        print("Subscription failed.")
        print(msg)
        quote_ctx.close()
        exit()
    while True:
        current_time = time.localtime()
        current_timestamp = time.mktime(current_time)

        if start_timestamp <= current_timestamp <= end_timestamp:
            current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
            bid, ask = get_bid_and_ask(track_code)
            price = get_last_price(track_code)

            if bid is not None and ask is not None and price is not None:
                writer.writerow(['1', '2', '3', '4'])
                print(f"Data written at {current_time_str}: Price={price}, Bid={bid}, Ask={ask}")
            else:
                print(f"Skipping row due to missing data at {current_time_str}")
        else:
            print("Time out. Exiting...")
            break
        time.sleep(5)
quote_ctx.close()

