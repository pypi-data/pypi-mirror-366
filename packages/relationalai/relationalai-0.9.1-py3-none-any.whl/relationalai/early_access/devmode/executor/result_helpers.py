import pandas as pd
import datetime

def format_columns(result_frame:pd.DataFrame):
    for col in result_frame.columns:
        if result_frame[col].apply(lambda x: isinstance(x, (datetime.date, datetime.datetime))).any():
            result_frame[col] = pd.to_datetime(result_frame[col], errors='coerce')
    return result_frame