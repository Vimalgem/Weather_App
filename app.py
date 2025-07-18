import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.tomorrow.io/v4/weather/realtime?location=Chennai&apikey=API_KEY"

# Caching dictionary
cache = {}

# App title
st.title("🌤️ Weather Forecast")
st.write("Get the latest weather updates with caching (10 min)!")

# Input
city = st.text_input("Enter city name")

# On submit
if city:
    city = city.strip().lower()

    # Check cache
    now = datetime.now()
    if city in cache:
        cached_data, timestamp = cache[city]
        if now - timestamp < timedelta(minutes=10):
            st.success(f"✅ Using cached data for {city.title()}")
            data = cached_data
        else:
            del cache[city]  # Expired
            data = None
    else:
        data = None

    # If not in cache, fetch
    if not data:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                cache[city] = (data, now)
            else:
                try:
                    error_data = response.json()
                    st.error(f"❌ {error_data.get('message', 'City not found')}")
                except ValueError:
                    st.error("❌ Invalid response. Please check API key or input.")
        except requests.RequestException as e:
            st.error(f"❌ Network error: {e}")
            data = None

    # Show result
    if data:
        st.markdown(f"### 📍 Weather in {data['name']}")
        st.write(f"**Temperature:** {data['main']['temp']}°C")
        st.write(f"**Description:** {data['weather'][0]['description'].title()}")
        st.write(f"**Humidity:** {data['main']['humidity']}%")
