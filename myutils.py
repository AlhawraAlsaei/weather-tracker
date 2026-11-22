
# Import pandas
import pandas as pd


# Calculate temperature statistics
def calculate_temperature_stats(df):
    """Calculate the average, minimum, and maximum temperatures."""

    avg_temp = df["Temperature"].mean()
    min_temp = df["Temperature"].min()
    max_temp = df["Temperature"].max()

    return avg_temp, min_temp, max_temp


# Filter weather observations by date
def filter_weather_by_date(df, selected_date):
    """Return weather observations matching the selected date."""

    df = df.copy()
    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%Y-%m-%d"
    )

    filtered_data = df[df["Date"].dt.date == selected_date]

    return filtered_data
