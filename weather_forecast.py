import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# OpenWeatherMap API Key
API_KEY = '30e1266dfef92833645973c5f023d79e'

# Function to get weather data
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to get 5-day weather forecast
def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to convert UNIX timestamp to readable time
def convert_time(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')

# Streamlit web app
def main():
    st.title("Weather Forecasting")

    # Initialize session state for recent searches
    if 'recent_searches' not in st.session_state:
        st.session_state['recent_searches'] = []

    # Display recent searches in the sidebar
    st.sidebar.header("Recent Searches")
    if st.session_state['recent_searches']:
        for city in st.session_state['recent_searches']:
            if st.sidebar.button(city):
                st.session_state['city'] = city
    else:
        st.sidebar.write("No recent searches")

    city = st.text_input("Enter city name", st.session_state.get('city', ""))

    if st.button("Get Weather"):
        data = get_weather(city)
        if data:
            st.write(f"**City**: :red[{data['name']}]")
            st.write(f"**Temperature**: :red[{data['main']['temp']} °C]")
            st.write(f"**Weather**: :red[{data['weather'][0]['description'].capitalize()}]")
            st.write(f"**Humidity**: :red[{data['main']['humidity']} %]")
            st.write(f"**Wind Speed**: :red[{data['wind']['speed']} m/s]")
            st.write(f"**Sunrise**: :red[{convert_time(data['sys']['sunrise'] + data['timezone'])}]")
            st.write(f"**Sunset**: :red[{convert_time(data['sys']['sunset'] + data['timezone'])}]")
            st.image(f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png")

            # Store the city in recent searches
            if city not in st.session_state['recent_searches']:
                st.session_state['recent_searches'].append(city)
                if len(st.session_state['recent_searches']) > 5:  # Limit to 5 recent searches
                    st.session_state['recent_searches'].pop(0)

            # Create columns for map and forecast
            col1, col2 = st.columns([1, 2])

            # Displaying the map in the first column
            with col1:
                st.subheader("Location on Map")
                lat = data['coord']['lat']
                lon = data['coord']['lon']
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))

            # Displaying 5-day weather forecast in the second column using tabs
            with col2:
                forecast_data = get_forecast(city)
                if forecast_data:
                    st.subheader("5-Day Weather Forecast")
                    tabs = st.tabs([forecast['dt_txt'].split()[0] for forecast in forecast_data['list'][::8]])
                    for tab, forecast in zip(tabs, forecast_data['list'][::8]):  # Get forecast every 24 hours
                        with tab:
                            st.write(f"**Temperature**: :red[{forecast['main']['temp']} °C]")
                            st.write(f"**Weather**: :red[{forecast['weather'][0]['description'].capitalize()}]")
                            st.write(f"**Humidity**: :red[{forecast['main']['humidity']} %]")
                            st.image(f"http://openweathermap.org/img/wn/{forecast['weather'][0]['icon']}@2x.png")
                            st.write("---")
        else:
            st.error("City not found!")

if __name__ == "__main__":
    main()
