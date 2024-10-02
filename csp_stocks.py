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
    df = pd.read_csv(csv_path, parse_dates=['date'])
    df = df.sort_values(by='date').reset_index(drop=True)
    return df


# # TODO: change to use a List[ts] series instead of df argument

# Define a CSP node that simulates a stock data stream by outputting rows as dictionaries
@csp.node
def stock_data_stream(data: pd.DataFrame, interval: timedelta = timedelta(seconds=1)) -> ts[dict]:
    with csp.alarms():
        a_tick = csp.alarm(bool)

    with csp.state():
        s_data = data.to_dict(orient='records')  # Convert the DataFrame to a list of dictionaries (hashable)
        s_index = 0  # to track the current index in the stream

    with csp.start():
        csp.schedule_alarm(a_tick, timedelta(), True)

    if csp.ticked(a_tick):
        # Output one row of stock data at a time as a dictionary
        if s_index < len(s_data):
            current_day_data = s_data[s_index]
            csp.output([current_day_data])  # Output as a list of one dict to match Perspective's format
            # TODO: loop back to the beginning
            s_index += 1
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
