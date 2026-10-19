from moomoo import *
from datetime import datetime
from Option_Selector import option_selector_V6

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
code_list=['US.IONQ']
code_list=['US.SPY','US.QQQ','US.IWM']
for code in code_list:
    ret,data=quote_ctx.get_market_snapshot(code)
    if ret==RET_OK:
        current_stock_price=data['last_price'].iloc[0]
    ret,data=quote_ctx.get_option_chain(code)
    if ret==RET_OK:
        option_chain=data
    print(option_selector_V6(option_chain,current_stock_price,1,1))
quote_ctx.close()