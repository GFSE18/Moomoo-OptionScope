import os
import time
import csv
from moomoo import *
from datetime import datetime
from apscheduler.schedulers.background import *
from apscheduler.triggers.interval import *

code_list=['US.SPY','US.QQQ','US.NVDA','US.IWM','US.AVGO','US.PLTR','US.AMD','US.MU','US.SOXL']
start_time_str = "2024-12-23 06:31:00"
end_time_str = "2024-12-23 13:00:00"
is_init=True
start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
file_name = start_time_str[:10]+'.csv'
pwd_unlock = os.environ.get('MOOMOO_TRADING_PASSWORD', '')

csvfile = open(file_name, 'a', newline='')
writer = csv.writer(csvfile)

def option_selector_V5(option_chain,current_stock_price,price_lower_limit,price_upper_limit,preselect_range=0.2):
    # improved V2 
    df = pd.DataFrame(option_chain)
    df['strike_time'] = pd.to_datetime(df['strike_time']).dt.date
    closest_date = df['strike_time'].min()
    df_calls = df[(df['strike_time'] == closest_date) & (df['option_type'] == 'CALL') & (abs(df['strike_price']-current_stock_price)<preselect_range*current_stock_price)]
    df_puts = df[(df['strike_time'] == closest_date) & (df['option_type'] == 'PUT') & (abs(df['strike_price']-current_stock_price)<preselect_range*current_stock_price)]
    code_list_calls = df_calls['code'].to_list()
    code_list_puts = df_puts['code'].to_list()
    ret, snapshot_calls = quote_ctx.get_market_snapshot(code_list_calls)
    if ret==RET_OK:
        df_calls_snapshot = pd.DataFrame(snapshot_calls)
        df_calls_snapshot = df_calls_snapshot[(df_calls_snapshot['last_price'] > price_lower_limit) & (df_calls_snapshot['last_price'] < price_upper_limit)]
        highest_volume = df_calls_snapshot['volume'].max()
        selected_call = df_calls_snapshot[df_calls_snapshot['volume'] == highest_volume]
        selected_call_code = selected_call['code'].iloc[0]
        selected_call_price = selected_call['last_price'].iloc[0]
        print(selected_call_price)
    ret, snapshot_puts = quote_ctx.get_market_snapshot(code_list_puts)
    if ret==RET_OK:
        df_puts_snapshot = pd.DataFrame(snapshot_puts)
        df_puts_snapshot = df_puts_snapshot[(df_puts_snapshot['last_price'] > price_lower_limit) & (df_puts_snapshot['last_price'] < price_upper_limit)]
        df_puts_snapshot['price_diff'] = abs(df_puts_snapshot['last_price'] - selected_call_price)
        min_price_diff=df_puts_snapshot['price_diff'].min()
        selected_put=df_puts_snapshot[df_puts_snapshot['price_diff'] == min_price_diff]
        selected_put_code=selected_put['code'].iloc[0]
        selected_put_price=selected_put['last_price'].iloc[0]
        print(selected_put_price)
    return selected_call_code,selected_put_code

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

def buy_to_open(code_list):
    for code in code_list:
        bid, ask = get_bid_and_ask(code)
        while ask is None:
            print(f"Ask price for {code} is None. Retrying...")
            bid, ask = get_bid_and_ask(code)
        ret, data = trade_ctx.place_order(price=ask, qty=1, code=code, trd_side=TrdSide.BUY, trd_env=TrdEnv.REAL)
        if ret != RET_OK:
            print(f"Failed to place order for {code}: {data}")

def initialize():
    global quote_ctx
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    global trade_ctx
    trade_ctx= OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUINC)
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
        selected_call_code,selected_put_code=option_selector_V5(option_chain,current_stock_price,0.5,1,0.4)
        call_list.append(selected_call_code)
        put_list.append(selected_put_code)
    option_list=[]
    option_list.extend(call_list)
    option_list.extend(put_list)
    code_list.extend(option_list)
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
    # ret,data=trade_ctx.unlock_trade(pwd_unlock)
    # if ret==RET_OK:
    #     buy_to_open(option_list)
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