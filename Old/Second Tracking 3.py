import time
import csv
from moomoo import *
from datetime import datetime
from apscheduler.schedulers.background import *
from apscheduler.triggers.interval import *
import pandas as pd

code_list=['US.SPY','US.QQQ','US.NVDA','US.AAPL','US.IWM','US.SMCI']
start_time_str = "2025-1-31 09:30:00"
end_time_str = "2025-1-31 16:00:00"
is_init=True
start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
file_name = end_time_str[:10]+'.csv'

csvfile = open(file_name, 'a', newline='')
writer = csv.writer(csvfile)

def option_selector_V6(option_chain, current_stock_price, call_position, put_position):
    # for ITM n-th position selection
    call_position-=1
    put_position-=1
    df = pd.DataFrame(option_chain)
    df['strike_time'] = pd.to_datetime(df['strike_time']).dt.date
    closest_date = df['strike_time'].min()
    df_calls = df[(df['strike_time'] == closest_date) & 
                  (df['option_type'] == 'CALL') & 
                  (df['strike_price'] < current_stock_price)]
    df_calls = df_calls.sort_values(by='strike_price', ascending=False)
    df_puts = df[(df['strike_time'] == closest_date) & 
                 (df['option_type'] == 'PUT') & 
                 (df['strike_price'] > current_stock_price)]
    df_puts = df_puts.sort_values(by='strike_price', ascending=True)
    selected_call = None
    selected_put = None
    if call_position < len(df_calls):
        selected_call = df_calls.iloc[call_position]
    if put_position < len(df_puts):
        selected_put = df_puts.iloc[put_position]
    selected_call_name=selected_call['code']
    selected_put_name=selected_put['code']
    return selected_call_name, selected_put_name

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

def initialize():
    global quote_ctx
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    global code_list
    call_list=[]
    put_list=[]
    for code in code_list:
        ret,data=quote_ctx.get_market_snapshot(code)
        if ret==RET_OK:
            current_stock_price=data['last_price'].iloc[0]
        ret,data=quote_ctx.get_option_chain(code)
        if ret==RET_OK:
            option_chain=data
        selected_call_code1,selected_put_code1=option_selector_V6(option_chain,current_stock_price,1,1)
        selected_call_code2,selected_put_code2=option_selector_V6(option_chain,current_stock_price,2,2)
        selected_call_code3,selected_put_code3=option_selector_V6(option_chain,current_stock_price,5,5)
        call_list.append(selected_call_code1)
        put_list.append(selected_put_code1)
        call_list.append(selected_call_code2)
        put_list.append(selected_put_code2)
        call_list.append(selected_call_code3)
        put_list.append(selected_put_code3)
    code_list.extend(call_list)
    code_list.extend(put_list)
    code_list=sorted(list(set(code_list)))
    header_row = ['Time']
    for code in code_list:
        header_row.extend([code[3:]+'Last',code[3:]+'Bid',code[3:]+'Ask'])
    writer.writerow(header_row)
    ret_sub,msg = quote_ctx.subscribe(code_list, [SubType.ORDER_BOOK, SubType.QUOTE], subscribe_push=False)
    if ret_sub != RET_OK:
        print("Subscription failed.")
        print(msg)
        quote_ctx.close()
        exit()
    csvfile.flush()
    print(header_row)

def wait_until_start(start_time):
    while True:
        now = datetime.now()
        if now >= start_time:
            print("Start time reached. Starting the scheduler...")
            initialize()
            break
        remaining = (start_time - now).total_seconds()
        print(f"Waiting for start time. Remaining seconds: {remaining:.1f}")
        time.sleep(min(remaining, 1))  # Sleep for the smaller of remaining time or 1 second

def collect_market_data():
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [current_time_str]
    for code in code_list:
        price = get_last_price(code)
        bid, ask = get_bid_and_ask(code)
        row.extend([price, bid, ask])
    print(row)
    writer.writerow(row)
    csvfile.flush()

scheduler = BackgroundScheduler()
scheduler.add_job(collect_market_data, IntervalTrigger(seconds=1), start_date=start_time, end_date=end_time)

try:
    wait_until_start(start_time)
    scheduler.start()

    # Keep the script running
    while True:
        now = datetime.now()
        if now >= end_time:
            print("End time reached. Shutting down the scheduler...")
            scheduler.shutdown()
            quote_ctx.close()
            csvfile.close()
            exit()
            break
        time.sleep(0.5)

except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    quote_ctx.close()
    csvfile.close()
    print("Scheduler stopped, quote context and CSV file closed.")
    exit()