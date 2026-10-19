import os
from moomoo import *
pwd_unlock = os.environ.get('MOOMOO_TRADING_PASSWORD', '')
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUINC)
trd_code='US.MLGO'
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret_sub = quote_ctx.subscribe(trd_code, [SubType.ORDER_BOOK], subscribe_push=False)[0]
if ret_sub == RET_OK:  # 订阅成功
    ret, data = quote_ctx.get_order_book(trd_code)  # 获取一次 3 档实时摆盘数据
    if ret == RET_OK:
        print(data['Ask'][0][0])
        price=data['Ask'][0][0]
    else:
        print('error:', data)
else:
    print('subscription failed')
quote_ctx.close()

ret, data = trd_ctx.unlock_trade(pwd_unlock)
if ret == RET_OK:
    ret, data = trd_ctx.place_order(price=0.01, qty=1, code=trd_code, trd_side=TrdSide.BUY, trd_env=TrdEnv.REAL)
    if ret == RET_OK:
        print(data)
        print(data['order_id'][0])  # 获取下单的订单号
        print(data['order_id'].values.tolist())  # 转为 list
    else:
        print('place_order error: ', data)
else:
    print('unlock_trade failed: ', data)
trd_ctx.close()