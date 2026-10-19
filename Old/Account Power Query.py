from moomoo import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US, host='127.0.0.1', port=11111, security_firm=SecurityFirm.FUTUINC)
ret, data = trd_ctx.accinfo_query(currency=Currency.USD)
if ret == RET_OK:
    print(data)
    print(data['us_cash'][0])  # 取第一行的购买力
else:
    print('accinfo_query error: ', data)
trd_ctx.close()  # 关闭当条连接
