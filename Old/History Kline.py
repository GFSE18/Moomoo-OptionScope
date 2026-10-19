import matplotlib.pyplot as plt
import numpy as np
from moomoo import *

# Initialize the connection
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# Fetch data
ret, data, page_req_key = quote_ctx.request_history_kline(
    'US.SPY241224C596000', '2024-12-24', '2024-12-25', KLType.K_1M, fields=KL_FIELD.CLOSE, extended_time=False
)
if ret == RET_OK:
    call_close_prices = data['close'].tolist()

ret, data, page_req_key = quote_ctx.request_history_kline(
    'US.SPY241224P597000', '2024-12-24', '2024-12-25', KLType.K_1M, fields=KL_FIELD.CLOSE, extended_time=False
)
if ret == RET_OK:
    put_close_prices = data['close'].tolist()

ret, data, page_req_key = quote_ctx.request_history_kline(
    'US.SPY', '2024-12-24', '2024-12-25', KLType.K_1M, fields=KL_FIELD.CLOSE, extended_time=False
)
if ret == RET_OK:
    underlying_close_prices = data['close'].tolist()

# Composite close prices
composite_close_prices = [call + put for call, put in zip(call_close_prices, put_close_prices)]

# Close the connection
quote_ctx.close()

# Generate the exponential function values
time_steps = np.arange(len(composite_close_prices))
exp_function = np.exp(-0.04335 * time_steps) + 21

# Plotting
fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
fig.suptitle("Option and Underlying Prices")

# Call close prices
axes[0].plot(call_close_prices, label='Call Close Prices', color='blue')
axes[0].set_ylabel("Call Prices")
axes[0].legend()

# Put close prices
axes[1].plot(put_close_prices, label='Put Close Prices', color='orange')
axes[1].set_ylabel("Put Prices")
axes[1].legend()

# Underlying close prices
axes[2].plot(underlying_close_prices, label='Underlying Close Prices', color='green')
axes[2].set_ylabel("Underlying Prices")
axes[2].legend()

# Composite close prices and exponential function
axes[3].plot(composite_close_prices, label='Composite Close Prices', color='red')
axes[3].plot(exp_function, label=r'exponential function', color='purple', linestyle='--')
axes[3].set_ylabel("Composite Prices")
axes[3].set_xlabel("Time Step")
axes[3].legend()

# Adjust layout
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()
