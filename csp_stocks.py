import csp
from csp import ts
import pandas as pd
from datetime import timedelta
from perspective.widget import PerspectiveWidget
from perspective import table as PerspectiveTable
from typing import List

__all__ = (
    "load_stock_data",
    "stock_data_stream",
    "push_to_perspective",
    "push_to_perspective_table",
    "STOCKS_SCHEMA"
)

STOCKS_SCHEMA = {
    'date': 'date', 
    'year': 'integer', 
    'ticker': 'string', 
    'adj_close': 'float', 
    'close': 'float', 
    'high': 'float', 
    'low': 'float', 
    'open': 'float', 
    'volume': 'integer', 
    'current_shares': 'float', 
    'daily_trades': 'float', 
    'trade_price': 'float', 
    'trade_value': 'float', 
    'cash_reserves': 'float', 
    'portfolio_value': 'float'
}


# Load the stock data from a CSV file
def load_stock_data(csv_path):
    df = pd.read_csv(csv_path, header=0)
    # df = df.sort_values(by='date').reset_index(drop=True)
    return df


# Define a CSP node that simulates a stock data stream by outputting rows as dictionaries
@csp.node
def stock_data_stream(data: List[dict], interval: timedelta = timedelta(seconds=1)) -> ts[List[dict]]:
    with csp.alarms():
        a_tick = csp.alarm(bool)

    with csp.state():
        s_data = data.copy()
        s_index = 0  # to track the current index in the stream

    with csp.start():
        csp.schedule_alarm(a_tick, timedelta(), True)

    if csp.ticked(a_tick):
        # Output one row of stock data one day at the time
        if s_index >= len(s_data):
            s_index = 0
        # find the slice data just for today's date
        current_date = s_data[s_index]['date']
        last_index = s_index
        while (last_index < len(s_data)) and (current_date == s_data[last_index]['date']):
            last_index += 1
        # slice today's records: from s_index to next_index
        csp.output(s_data[s_index:last_index])
        # shift forward to the next day index
        s_index = last_index
        csp.schedule_alarm(a_tick, interval, True)


# Method to push data to Perspective widget
@csp.node
def push_to_perspective(data: ts[list], widget: PerspectiveWidget):
    if csp.ticked(data):
        widget.update(data)

# Method to push data to a Perspective table
@csp.node
def push_to_perspective_table(data: ts[list], table: PerspectiveTable):
    if csp.ticked(data):
        table.update(data)
