from moomoo import *
track_code='US.QQQ241203C515000'
track_set=['US.QQQ','US.SPY','US.IWM']
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
start_time_str = "2024-12-09 09:30:00"
print(start_time_str[:10])
quote_ctx.close()