import time
import csv
from moomoo import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
code_list=['US.QQQ','US.SPY','US.IWM','US.NVDA','US.TSLA','US.AMD','US.AAPL','US.PLTR']

start_time_str = "2024-12-16 06:45:00"
end_time_str = "2024-12-16 13:00:00"
start_time = time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
end_time = time.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
start_timestamp = time.mktime(start_time)
end_timestamp = time.mktime(end_time)
file_name = start_time_str[:10]+'.csv'

def get_bid_and_ask(code):
    ret, data = quote_ctx.get_order_book(code)
    if ret != RET_OK:
        print("Failed to get ask and bid:", data)
        exit()
        return None, None
    return data['Bid'][0][0], data['Ask'][0][0]

def get_last_price(code):
    ret, data = quote_ctx.get_stock_quote(code)
    if ret != RET_OK:
        print("Failed to get current price:", data)
        exit()
        return None
    return float(data['last_price'][0])

def option_selector(code_list):
    selected_calls = []
    selected_puts = []
    for code in code_list:
        ret, data = quote_ctx.get_option_chain(code)
        if ret != RET_OK:
            print("Failed to retrieve data:", data)
            exit()
        else:
            df = pd.DataFrame(data)
            df['strike_time'] = pd.to_datetime(df['strike_time']).dt.date
            closest_date = df['strike_time'].min()
            df_calls = df[(df['strike_time'] == closest_date) & (df['option_type'] == 'CALL')]
            df_puts = df[(df['strike_time'] == closest_date) & (df['option_type'] == 'PUT')]
            code_list_calls = df_calls['code'].to_list()
            code_list_puts = df_puts['code'].to_list()
            if code_list_calls:
                ret, snapshot_calls = quote_ctx.get_market_snapshot(code_list_calls)
                if ret == RET_OK:
                    df_calls_snapshot = pd.DataFrame(snapshot_calls)
                    df_calls_snapshot = df_calls_snapshot[(df_calls_snapshot['last_price'] > 0.5) & (df_calls_snapshot['last_price'] < 3)]
                    highest_volume = df_calls_snapshot['volume'].max()
                    selected_call_code = df_calls_snapshot[df_calls_snapshot['volume'] == highest_volume]['code']
                    selected_calls.append(selected_call_code.iloc[0])
            if code_list_puts:
                ret, snapshot_puts = quote_ctx.get_market_snapshot(code_list_puts)
                if ret == RET_OK:
                    df_puts_snapshot = pd.DataFrame(snapshot_puts)
                    df_puts_snapshot = df_puts_snapshot[(df_puts_snapshot['last_price'] > 0.5) & (df_puts_snapshot['last_price'] < 3)]
                    highest_volume = df_puts_snapshot['volume'].max()
                    selected_put_code = df_puts_snapshot[df_puts_snapshot['volume'] == highest_volume]['code']
                    selected_puts.append(selected_put_code.iloc[0])
    return selected_calls, selected_puts

with open(file_name,'a') as csvfile:
    writer=csv.writer(csvfile)
    header_row=['Time']
    calls,puts=option_selector(code_list)
    code_list.extend(calls)
    code_list.extend(puts)
    print(code_list)
    for code in code_list:
        header_row.extend([code[3:]+'Last',code[3:]+'Bid',code[3:]+'Ask'])
    writer.writerow(header_row)
    ret_sub,msg = quote_ctx.subscribe(code_list, [SubType.ORDER_BOOK, SubType.QUOTE], subscribe_push=False)
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
            row=[current_time_str]
            for code in code_list:
                price=get_last_price(code)
                bid,ask=get_bid_and_ask(code)
                row.extend([price,bid,ask])
            print(row)
            writer.writerow(row)
            csvfile.flush()
        else:
            print("Time out")
            break
        time.sleep(1)
quote_ctx.close()