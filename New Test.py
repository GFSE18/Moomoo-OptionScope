import time
from datetime import datetime
from moomoo import OpenQuoteContext, RET_OK, SubType
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# ========== USER INPUT ==========
OPTION_CODE = "US.SPY251222C680000"   # <-- put your option ticker/code here
REFRESH_SEC = 1
HOST, PORT = "127.0.0.1", 11111

quote_ctx = None


def get_last_price(code: str):
    ret, data = quote_ctx.get_stock_quote(code)
    if ret != RET_OK:
        return None
    return float(data["last_price"].iloc[0])


def get_best_bid_ask(code: str):
    ret, data = quote_ctx.get_order_book(code)
    if ret != RET_OK:
        return None, None
    bid = data["Bid"][0][0]
    ask = data["Ask"][0][0]
    return bid, ask


def tick():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last = get_last_price(OPTION_CODE)
    bid, ask = get_best_bid_ask(OPTION_CODE)
    print(f"[{ts}] {OPTION_CODE} | last={last} bid={bid} ask={ask}")


def main():
    global quote_ctx
    quote_ctx = OpenQuoteContext(host=HOST, port=PORT)

    # subscribe once (recommended)
    ret, msg = quote_ctx.subscribe([OPTION_CODE], [SubType.QUOTE, SubType.ORDER_BOOK], subscribe_push=False)
    if ret != RET_OK:
        print("Subscribe failed (will still poll):", msg)

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        tick,
        IntervalTrigger(seconds=REFRESH_SEC),
        max_instances=1,
        coalesce=True,
        misfire_grace_time=1,
    )
    scheduler.start()

    try:
        while True:
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown(wait=False)
        quote_ctx.close()
        print("Closed.")


if __name__ == "__main__":
    main()
