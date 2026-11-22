
%%writefile app.py

# Import libraries
import streamlit as st
import pandas as pd
from myutils import calculate_temperature_stats, filter_weather_by_date


# Initialize weather data
if "weather_data" not in st.session_state:
    st.session_state.weather_data = pd.DataFrame(
        columns=["Date", "Temperature", "Conditions", "Humidity", "Wind Speed"]
    )


# Upload an existing weather CSV file
uploaded_file = st.sidebar.file_uploader(
    "Upload Weather Data",
    type="csv"
)


# Load and validate an uploaded CSV file
if uploaded_file is not None:

    # Check if this file has already been loaded
    if st.session_state.get("file_loaded") != uploaded_file.getvalue():

        try:
            # Read the uploaded CSV file
            uploaded_data = pd.read_csv(uploaded_file)

            # Define the required columns
            required_columns = [
                "Date", "Temperature", "Conditions",
                "Humidity", "Wind Speed"
            ]

            # Check if the file is empty
            if uploaded_data.empty:
                st.sidebar.error("The uploaded CSV file is empty.")

            # Check if required columns are missing
            elif not all(col in uploaded_data.columns for col in required_columns):
                st.sidebar.error("The CSV file is missing required columns.")

            else:
                # Convert dates using YYYY-MM-DD format
                uploaded_data["Date"] = pd.to_datetime(
                    uploaded_data["Date"],
                    format="%Y-%m-%d",
                    errors="raise"
                )

                for col in ["Temperature", "Humidity", "Wind Speed"]:
                    uploaded_data[col] = pd.to_numeric(
                        uploaded_data[col], errors="raise"
                    )

                # Check for missing values
                if uploaded_data[required_columns].isna().any().any():
                    st.sidebar.error("The CSV file contains missing values.")

                # Check for invalid temperature
                elif (
                    (uploaded_data["Temperature"] < -90).any()
                    or (uploaded_data["Temperature"] > 60).any()
                ):
                    st.sidebar.error("Temperature must be between -90 and 60 °C.")

                # Check for invalid humidity or wind speed
                elif (
                    (uploaded_data["Humidity"] < 0).any()
                    or (uploaded_data["Humidity"] > 100).any()
                    or (uploaded_data["Wind Speed"] < 0).any()
                ):
                    st.sidebar.error("The CSV file contains invalid weather values.")

                # Check for invalid weather conditions
                elif not uploaded_data["Conditions"].isin(
                    ["Sunny", "Cloudy", "Rainy", "Windy"]
                ).all():
                    st.sidebar.error("The CSV file contains invalid weather conditions.")

                else:
                    # Save the validated weather data
                    st.session_state.weather_data = uploaded_data
                    st.session_state.file_loaded = uploaded_file.getvalue()

                    st.sidebar.success("CSV file uploaded successfully!")

        except (ValueError, TypeError, pd.errors.ParserError, UnicodeError) as error:
            # Display an error message if the CSV file is invalid
            st.sidebar.error(f"Invalid CSV file: {error}")


# Application title
st.title("Weather Tracker")


# Create the sidebar navigation menu
with st.sidebar:
    page = st.radio(
        "MENU",
        ("Log Observation", "Dashboard (Stats)", "Search", "View All Data")
    )


# Page 1: Log Observation
if page == "Log Observation":
    st.header("Log Observation")

    # Create a form that saves only when the button is clicked
    with st.form("weather_form", enter_to_submit=False):

        # Select the observation date
        date = st.date_input("Date")

        # Enter the temperature in Celsius
        temperature = st.number_input("Temperature (°C)")

        # Select the weather conditions
        conditions = st.selectbox(
            "Weather Conditions",
            ("Sunny", "Cloudy", "Rainy", "Windy")
        )

        # Enter humidity percentage
        humidity = st.number_input(
            "Humidity (%)", min_value=0, max_value=100
        )

        # Enter wind speed
        wind_speed = st.number_input(
            "Wind Speed (km/h)", min_value=0.0
        )

        # Submit the weather observation
        submitted = st.form_submit_button("Save Observation")

    # Save the observation when the button is clicked
    if submitted:

        # Validate temperature
        if temperature < -90 or temperature > 60:
            st.error("Please enter a valid temperature between -90 and 60 °C.")

        # Validate humidity
        elif humidity < 0 or humidity > 100:
            st.error("Humidity must be between 0 and 100%.")

        # Validate wind speed
        elif wind_speed < 0:
            st.error("Wind speed cannot be negative.")

        else:
            # Create a DataFrame for the new observation
            new_row = pd.DataFrame({
                "Date": [str(date)],
                "Temperature": [temperature],
                "Conditions": [conditions],
                "Humidity": [humidity],
                "Wind Speed": [wind_speed]
            })

            # Add the new observation to the existing data
            st.session_state.weather_data = pd.concat(
                [st.session_state.weather_data, new_row],
                ignore_index=True
            )

            # Display a success message
            st.success("Weather observation saved successfully!")

            # Display all saved observations
            st.dataframe(st.session_state.weather_data)


# Page 2: Dashboard
elif page == "Dashboard (Stats)":
    st.header("Dashboard (Stats)")
    st.write("Explore weather statistics, temperature trends, and daily insights.")

    # Check if weather data is available
    if not st.session_state.weather_data.empty:

        # Create a copy of the weather data
        df = st.session_state.weather_data.copy()

        # Convert columns to the correct data types
        df["Date"] = pd.to_datetime(df["Date"])
        df["Temperature"] = pd.to_numeric(df["Temperature"])

        # Sort observations by date
        df = df.sort_values("Date")

        # Calculate temperature statistics using myutils
        avg_temp, min_temp, max_temp = calculate_temperature_stats(df)

        # Display temperature statistics in three columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🌡️ Average Temp", f"{avg_temp:.2f} °C")

        with col2:
            st.metric("❄️ Minimum Temp", f"{min_temp:.1f} °C")

        with col3:
            st.metric("🔥 Maximum Temp", f"{max_temp:.1f} °C")

        st.divider()

        # Display temperature trend over time
        st.subheader("Temperature Trend Over Time")

        # Calculate the average temperature for each date
        chart_data = df.groupby("Date")["Temperature"].mean()

        # Display the temperature line chart
        st.line_chart(chart_data)

        st.divider()

        # Record-Breaking Temperatures
        st.subheader("🏆 Record-Breaking Temperatures")

        # Find the hottest and coldest observations
        hottest_row = df.loc[df["Temperature"].idxmax()]
        coldest_row = df.loc[df["Temperature"].idxmin()]

        # Display record temperatures in two columns
        col1, col2 = st.columns(2)

        with col1:
            st.error(
                f"🔥 Hottest Recorded Day\n\n"
                f"**{hottest_row['Temperature']} °C**\n\n"
                f"{hottest_row['Date'].strftime('%Y-%m-%d')}"
            )

        with col2:
            st.info(
                f"❄️ Coldest Recorded Day\n\n"
                f"**{coldest_row['Temperature']} °C**\n\n"
                f"{coldest_row['Date'].strftime('%Y-%m-%d')}"
            )

        st.divider()

        # Student's Choice Innovation: Weather Recommendations
        st.subheader("Weather Insights & Recommendations")

        # Select a date to view weather recommendations
        selected_date = st.date_input(
            "Select a Date",
            value=df["Date"].max().date(),
            key="insights_date"
        )

        # Filter observations by the selected date
        selected_data = df[df["Date"].dt.date == selected_date]

        # Check if observations exist for the selected date
        if not selected_data.empty:

            # Use the last observation recorded for this date
            weather = selected_data.iloc[-1]

            # Get temperature and weather conditions
            selected_temp = weather["Temperature"]
            selected_conditions = weather["Conditions"]

            # Display selected weather information
            st.write("**Weather Conditions:**", selected_conditions)
            st.write("**Temperature:**", selected_temp, "°C")

            # Give recommendations based on weather conditions
            if selected_conditions == "Sunny":
                st.info("☀️ Sunny day! Remember to wear sunscreen.")

            elif selected_conditions == "Rainy":
                st.info("🌧️ Rainy day! Don't forget your umbrella.")

            elif selected_conditions == "Cloudy":
                st.info("☁️ Cloudy day! Enjoy your outdoor activities.")

            elif selected_conditions == "Windy":
                st.info("💨 Windy day! Be careful of strong winds.")

            # Give recommendations based on temperature
            if selected_temp >= 35:
                st.warning(
                    "🔥 High temperature! Stay hydrated and avoid prolonged sun exposure."
                )

            elif selected_temp <= 15:
                st.warning("❄️ Low temperature! Wear warm clothes.")

            else:
                st.success(
                    "🌤️ Temperature is within the selected comfortable range."
                )

        else:
            # Display a message if no data exists for the selected date
            st.warning("No weather observations found for this date.")

    else:
        # Display a message if no observations are available
        st.warning("No weather observations available.")


# Page 3: Search
elif page == "Search":
    st.header("Search Weather Observations")

    # Select a date to search for weather observations
    search_date = st.date_input("Select a Date")

    # Get the saved weather data
    df = st.session_state.weather_data.copy()

    # Check if weather data is available
    if not df.empty:

        # Filter observations using myutils
        search_results = filter_weather_by_date(df, search_date)

        # Display the matching observations
        if not search_results.empty:
            st.success("Weather observations found!")
            st.dataframe(search_results)

        else:
            st.warning("No weather observations found for this date.")

    else:
        st.info("No weather data available. Please add an observation first.")


# Page 4: View All Data
elif page == "View All Data":
    st.header("View All Weather Data")

    # Get all saved weather observations
    df = st.session_state.weather_data

    # Check if weather data is available
    if not df.empty:

        # Display the total number of observations
        st.write("Total Observations:", len(df))

        # Display all weather observations in a sortable table
        st.dataframe(df, use_container_width=True)

        # Edit weather observations
        st.subheader("Edit Weather Data")

        # Display an editable table
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="fixed"
        )

        # Save the edited observations
        if st.button("Save Changes"):

            try:
                # Work on a copy of the edited data
                validated_df = edited_df.copy()

                # Convert columns to the correct data types
                validated_df["Date"] = pd.to_datetime(
                    validated_df["Date"], errors="raise"
                )

                for col in ["Temperature", "Humidity", "Wind Speed"]:
                    validated_df[col] = pd.to_numeric(
                        validated_df[col], errors="raise"
                    )

                # Check for missing values
                if validated_df.isna().any().any():
                    st.error("Please fill in all weather data fields.")

                # Validate temperature
                elif (
                    (validated_df["Temperature"] < -90).any()
                    or (validated_df["Temperature"] > 60).any()
                ):
                    st.error("Temperature must be between -90 and 60 °C.")

                # Validate humidity
                elif (
                    (validated_df["Humidity"] < 0).any()
                    or (validated_df["Humidity"] > 100).any()
                ):
                    st.error("Humidity must be between 0 and 100%.")

                # Validate wind speed
                elif (validated_df["Wind Speed"] < 0).any():
                    st.error("Wind speed cannot be negative.")

                # Validate weather conditions
                elif not validated_df["Conditions"].isin(
                    ["Sunny", "Cloudy", "Rainy", "Windy"]
                ).all():
                    st.error("Please enter valid weather conditions.")

                else:
                    # Save the validated changes
                    st.session_state.weather_data = validated_df.copy()
                    st.success("Weather data updated successfully!")

            except (ValueError, TypeError) as error:
                st.error(f"Invalid weather data: {error}")

    else:
        st.info("No weather data available. Please add an observation first.")


# Convert weather data to CSV format
csv_data = st.session_state.weather_data.to_csv(
    index=False
).encode("utf-8")

# Download the saved weather observations
st.sidebar.download_button(
    label="Download Weather Data",
    data=csv_data,
    file_name="weather_data.csv",
    mime="text/csv"
)
