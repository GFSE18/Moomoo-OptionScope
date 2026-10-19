from moomoo import *
import pandas as pd

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

def option_selector(code_list):
    selected_call_list = []
    selected_put_list = []
    for code in code_list:
        ret, data = quote_ctx.get_option_chain(code)
        if ret != RET_OK:
            print("Failed to retrieve data:", data)
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
                    selected_call_list.append(selected_call_code.iloc[0])
            if code_list_puts:
                ret, snapshot_puts = quote_ctx.get_market_snapshot(code_list_puts)
                if ret == RET_OK:
                    df_puts_snapshot = pd.DataFrame(snapshot_puts)
                    df_puts_snapshot = df_puts_snapshot[(df_puts_snapshot['last_price'] > 0.5) & (df_puts_snapshot['last_price'] < 3)]
                    highest_volume = df_puts_snapshot['volume'].max()
                    selected_put_code = df_puts_snapshot[df_puts_snapshot['volume'] == highest_volume]['code']
                    selected_put_list.append(selected_put_code.iloc[0])
            selected_list=[]
            for i in range(len(selected_call_list)):
                selected_list.append(selected_call_list[i])
                selected_list.append(selected_put_list
        [i])
    return selected_list

def option_selector_V2(code_list, price_lower_limit, price_upper_limit):
    # for close-price dual leg option selection
    selected_call_list = []
    selected_put_list = []
    for code in code_list:
        ret,data=quote_ctx.get_market_snapshot(code)
        if ret==RET_OK:
            current_stock_price=data['last_price'].iloc[0]
        ret, data = quote_ctx.get_option_chain(code)
        if ret != RET_OK:
            print("Failed to retrieve data:", data)
        else:
            df = pd.DataFrame(data)
            df['strike_time'] = pd.to_datetime(df['strike_time']).dt.date
            closest_date = df['strike_time'].min()
            df_calls = df[(df['strike_time'] == closest_date) & (df['option_type'] == 'CALL') & (abs(df['strike_price']-current_stock_price)<0.2*current_stock_price)]
            df_puts = df[(df['strike_time'] == closest_date) & (df['option_type'] == 'PUT') & (abs(df['strike_price']-current_stock_price)<0.2*current_stock_price)]
            code_list_calls = df_calls['code'].to_list()
            code_list_puts = df_puts['code'].to_list()
            if code_list_calls:
                ret, snapshot_calls = quote_ctx.get_market_snapshot(code_list_calls)
                if ret == RET_OK:
                    df_calls_snapshot = pd.DataFrame(snapshot_calls)
                    df_calls_snapshot = df_calls_snapshot[(df_calls_snapshot['last_price'] > price_lower_limit) & (df_calls_snapshot['last_price'] < price_upper_limit)]
                    highest_volume = df_calls_snapshot['volume'].max()
                    selected_call = df_calls_snapshot[df_calls_snapshot['volume'] == highest_volume]
                    selected_call_code = selected_call['code']
                    selected_call_price = selected_call['last_price'].iloc[0]
                    selected_call_list.append(selected_call_code.iloc[0])
            if code_list_puts:
                ret, snapshot_puts = quote_ctx.get_market_snapshot(code_list_puts)
                if ret == RET_OK:
                    df_puts_snapshot = pd.DataFrame(snapshot_puts)
                    df_puts_snapshot = df_puts_snapshot[(df_puts_snapshot['last_price'] > price_lower_limit) & (df_puts_snapshot['last_price'] < price_upper_limit)]
                    df_puts_snapshot['price_diff'] = abs(df_puts_snapshot['last_price'] - selected_call_price)
                    min_price_diff=df_puts_snapshot['price_diff'].min()
                    selected_put=df_puts_snapshot[df_puts_snapshot['price_diff'] == min_price_diff]
                    selected_put_code = selected_put['code']
                    selected_put_list.append(selected_put_code.iloc[0])
    selected_list = []
    for call, put in zip(selected_call_list, selected_put_list):
        selected_list.append(call)
        selected_list.append(put)
    return selected_list

def option_selector_V3(code_list):
    # for ATM option selection
    selected_call_list = []
    selected_put_list = []
    for code in code_list:
        ret,data=quote_ctx.get_market_snapshot(code)
        if ret==RET_OK:
            current_stock_price=data['last_price'].iloc[0]
        ret, data = quote_ctx.get_option_chain(code)
        if ret != RET_OK:
            print("Failed to retrieve data:", data)
        else:
            df = pd.DataFrame(data)
            df['strike_time'] = pd.to_datetime(df['strike_time']).dt.date
            closest_date = df['strike_time'].min()
            df_calls = df[(df['strike_time'] == closest_date) & (df['option_type'] == 'CALL') & (abs(df['strike_price']-current_stock_price)<0.05*current_stock_price)].copy()
            df_puts = df[(df['strike_time'] == closest_date) & (df['option_type'] == 'PUT') & (abs(df['strike_price']-current_stock_price)<0.05*current_stock_price)].copy()
            df_calls['strike_price_diff']=abs(df_calls['strike_price']-current_stock_price)
            min_strike_price_diff=df_calls['strike_price_diff'].min()
            selected_call=df_calls[df_calls['strike_price_diff']==min_strike_price_diff]
            selected_call_code=selected_call['code']
            selected_strike_price=selected_call['strike_price'].iloc[0]
            selected_put=df_puts[df_puts['strike_price']==selected_strike_price]
            selected_put_code=selected_put['code']
            selected_call_list.append(selected_call_code.iloc[0])
            selected_put_list.append(selected_put_code.iloc[0])
    selected_list = []
    for call, put in zip(selected_call_list, selected_put_list):
        selected_list.append(call)
        selected_list.append(put)
    return selected_list

def option_selector_V4(option_chain,current_stock_price):
    # for close delta dual leg option selection
    df = pd.DataFrame(option_chain)
    df['strike_time'] = pd.to_datetime(df['strike_time']).dt.date
    closest_date = df['strike_time'].min()
    df_calls = df[(df['strike_time'] == closest_date) & (df['option_type'] == 'CALL') & (abs(df['strike_price']-current_stock_price)<0.2*current_stock_price)]
    df_puts = df[(df['strike_time'] == closest_date) & (df['option_type'] == 'PUT') & (abs(df['strike_price']-current_stock_price)<0.2*current_stock_price)]
    code_list_calls = df_calls['code'].to_list()
    code_list_puts = df_puts['code'].to_list()
    ret, snapshot_calls = quote_ctx.get_market_snapshot(code_list_calls)
    if ret==RET_OK:
        df_calls_snapshot = pd.DataFrame(snapshot_calls)
        df_calls_snapshot = df_calls_snapshot[(df_calls_snapshot['last_price'] > 0.5) & (df_calls_snapshot['last_price'] < 1.5)]
        highest_volume = df_calls_snapshot['volume'].max()
        selected_call = df_calls_snapshot[df_calls_snapshot['volume'] == highest_volume]
        selected_call_code = selected_call['code'].iloc[0]
        selected_call_delta=selected_call['option_delta'].iloc[0]
    ret, snapshot_puts = quote_ctx.get_market_snapshot(code_list_puts)
    if ret==RET_OK:
        df_puts_snapshot = pd.DataFrame(snapshot_puts)
        df_puts_snapshot = df_puts_snapshot[(df_puts_snapshot['last_price'] > 0.5) & (df_puts_snapshot['last_price'] < 1.5)]
        df_puts_snapshot['delta_diff']=abs(abs(df_puts_snapshot['option_delta'])-selected_call_delta)
        min_delta_diff=df_puts_snapshot['delta_diff'].min()
        selected_put=df_puts_snapshot[df_puts_snapshot['delta_diff']==min_delta_diff]
        selected_put_code=selected_put['code'].iloc[0]
    return selected_call_code,selected_put_code

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

# code_list=['US.SPY','US.QQQ','US.NVDA','US.IWM','US.AVGO','US.PLTR','US.AMD','US.MU','US.SOXL']
code_list=['US.SPY','US.QQQ','US.IWM']
for code in code_list:
    ret,data=quote_ctx.get_market_snapshot(code)
    if ret==RET_OK:
        current_stock_price=data['last_price'].iloc[0]
    ret,data=quote_ctx.get_option_chain(code)
    if ret==RET_OK:
        option_chain=data
    print(option_selector_V6(option_chain,current_stock_price,1,1))
    print(option_selector_V6(option_chain,current_stock_price,2,2))
    print(option_selector_V6(option_chain,current_stock_price,5,5))
quote_ctx.close()