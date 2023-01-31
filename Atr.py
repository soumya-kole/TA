##RSI NSEBANK
import copy
import os
from datetime import datetime

import pandas as pd
import talib as ta
import yfinance as yf

symbol = "^NSEBANK"
# df=yf.Ticker(symbol).history(period="1mo",interval="15m")
df = yf.Ticker(symbol).history(period="21d", interval="15m")

df["RSI"] = ta.RSI(df["Close"], timeperiod=14)
df['range'] = df['High'] - df['Low']
df['ATR'] = df['range'].rolling(14).mean()

# df["Stoploss"] = 1.0* df['ATR']
# df["Target"] = 2.0 * df['ATR']


df["Stoploss"] = 50
df["Target"] = 100

_intermediate_directory = os.path.join(os.environ['HOME'], 'intermediate')
_final_directory = os.path.join(os.environ['HOME'], 'final')


def _create_if_not_present(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def _handle_date_with_timezone(df: pd.DataFrame, col_name:list) -> pd.DataFrame:
    for c in col_name:
        df[c] = df[c].apply(lambda a: datetime.strftime(a, "%Y-%m-%d %H:%M:%S"))
    return df


def _get_paths():
    _create_if_not_present(_intermediate_directory)
    _create_if_not_present(_final_directory)
    ret = {'_intermediate_csv': os.path.join(_intermediate_directory, 'data.csv'),
            '_final_excel': os.path.join(_final_directory, f"{datetime.today().strftime('%Y_%m_%d_%H_%M_%S')}data.xlsx")}
    print(ret)
    return ret

def check_sl_or_tgt(pos):
    global position
    p = pos
    global trade
    # print("===========================",df['Stoploss'])
    if position:
        for i in range(pos + 1, len(df)):
            # print(trd['Symbol'],pos,trd['Entry Price'])
            if (trade['Buy/Sell'] == "Sell"):
                sl = trade['Entry Price'] + df['Stoploss'][pos]
                tgt = trade['Entry Price'] - df['Target'][pos]

                if (df['Close'][i] > sl) or (df['Close'][i] < tgt):
                    # print("stoploss/tgt hit and pos=",pos)
                    # trade['Exit Price']=df['Close'][i]
                    trade['Exit Price'] = df['Close'][i]
                    trade['Exit Date'] = df.index[i]
                    # traded.clear()
                    position = None
                    p = i
                    traded.append(copy.deepcopy(trade))
                    break

            else:
                sl = trade['Entry Price'] - df['Stoploss'][pos]
                tgt = trade['Entry Price'] + df['Target'][pos]

                if (df['Close'][i] < sl) or (df['Close'][i] > tgt):
                    # print("target/sl hit")
                    # trade['Exit Price']=df['Close'][i]
                    trade['Exit Price'] = df['Close'][i]

                    trade['Exit Date'] = df.index[i]
                    # traded.clear()
                    position = None
                    p = i
                    traded.append(copy.deepcopy(trade))
                    break
    return p


df = df.dropna()
# display first few rows
# print(df.head())
df.to_csv(_get_paths().get('_intermediate_csv'))

trade = {'Symbol': None, 'Buy/Sell': None, 'Entry Price': None, 'Entry Date': None, 'Exit Price': None,
         'Exit Date': None, 'RSI': None}

traded = []

position = None
p = 0

i = 0
print(len(df))
print("=====================start=============================================================")
# for i in range(p,len(df)):
while (i < len(df)):

    # if df['RSI'][i-1] < 60 and df['RSI'][i] > 60:
    if df['RSI'][i] > 60:
        if not position:
            # print("buy at price",df['Close'][i])
            position = "buy"
            trade['Symbol'] = symbol
            trade['Buy/Sell'] = 'Buy'
            trade['Entry Price'] = df['Close'][i]
            trade['Entry Date'] = df.index[i]
            trade['Exit Price'] = None
            trade['Exit Date'] = None
            trade['RSI'] = df['RSI'][i]
            # traded.append(copy.deepcopy(trade))
            # print(trade)

    if df['RSI'][i] < 40:
        if not position:
            # print("sell at price",df['Close'][i])
            position = "sell"
            trade['Symbol'] = symbol
            trade['Buy/Sell'] = 'Sell'
            trade['Entry Price'] = df['Close'][i]
            trade['Entry Date'] = df.index[i]
            trade['Exit Price'] = None
            trade['Exit Date'] = None
            trade['RSI'] = df['RSI'][i]
            # traded.append(copy.deepcopy(trade))
            # print(trade)

    if trade:
        new_pos = check_sl_or_tgt(i)
        i = new_pos

    i = i + 1
# print(traded)

print("End result")
for x in traded:
    print(x['Entry Price'], x['Entry Date'], x['Exit Price'], x['Exit Date'], x['Buy/Sell'])

col_list = ['Entry Price', 'Entry Date', 'Exit Price', 'Exit Date', 'Buy/Sell']

df = pd.DataFrame(traded)
df = _handle_date_with_timezone(df, ['Entry Date', 'Exit Date'])
df.to_excel(_get_paths().get('_final_excel'), columns=col_list, index=False)
# import csv
# csv_columns = ['Symbol','Buy/Sell','Entry Price','Entry Date','Exit Price','Exit Date','RSI']
# csv_file = "Names.csv"
# try:
#     with open(csv_file, 'w') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
#         writer.writeheader()
#         for data in traded:
#             writer.writerow(data)
# except IOError:
#     print("I/O error")
