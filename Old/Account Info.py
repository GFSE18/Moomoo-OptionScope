from moomoo import *
trd_ctx = OpenSecTradeContext(filter_trdmarket=TrdMarket.US,host='127.0.0.1',port=11111,security_firm=SecurityFirm.FUTUINC)
ret1, data1 = trd_ctx.get_acc_list()
ret2, data2 = trd_ctx.accinfo_query()
if ret1 == RET_OK:
    print(data1)
    #print(data['acc_id'][0])  # 取第一个账号
    #print(data['acc_id'].values.tolist())  # 转为 list
else:
    print('get_acc_list error: ', data1)
trd_ctx.close()