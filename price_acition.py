from time import sleep

from common_utils.read_data import *

stock = Stock("^DJI")
first_candle = stock.get_first_candle(interval='15m')
print(first_candle)

while True:
    current_price = stock.get_current_price()
    print(current_price)
    # print(nyc_datetime.isoformat())
    if current_price > first_candle.High:
        print("********* BUY ************")
    elif current_price < first_candle.Low:
        print("********* SELL ************")
    sleep(30)
