import pandas as pd

# Add filepath
def load_csv_file(filepath):
    """
    Reads a CSV file into a pandas DataFrame and converts specific columns 
    into appropriate datetime or time-of-day formats. It assumes the following columns 
    are present in the CSV: 'start_time', 'end_time', 'start_date', 'end_date', 
    'start_time_of_day', and 'end_time_of_day'.

    Parameters:
        filepath (str): Path to the CSV file.
    Returns:
        pd.DataFrame: DataFrame with parsed datetime, date, and time-of-day columns.
    
    Notes:
        - Datetime conversion uses `errors="coerce"` for 'start_time' and 'end_time',
          so invalid values will become NaT.
        - 'start_date' and 'end_date' are converted to `datetime.date` objects.
        - 'start_time_of_day' and 'end_time_of_day' must follow the format '%H:%M:%S'.
    """
    df = pd.read_csv(filepath)
    # Converting into datetime
    df = df.drop_duplicates()
    df['start_time'] = pd.to_datetime(df['start_time'], errors="coerce")
    df['end_time'] = pd.to_datetime(df['end_time'], errors="coerce")
    # Keep as dates
    df['start_date'] = pd.to_datetime(df['start_date']).dt.date
    df['end_date'] = pd.to_datetime(df['end_date']).dt.date
    # Show only time of day (hour, min, sec)
    df['start_time_of_day'] = pd.to_datetime(df['start_time_of_day'], format = '%H:%M:%S').dt.time
    df['end_time_of_day'] = pd.to_datetime(df['end_time_of_day'], format = '%H:%M:%S').dt.time

    
    return df