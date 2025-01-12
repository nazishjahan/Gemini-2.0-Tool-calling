from dotenv import load_dotenv
import os
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
import streamlit as st

load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")



@tool
def calculator(expression):
    """
    A calculator function to evaluate mathematical expressions.

    Parameters:
        expression (str): A string containing a mathematical expression to evaluate.

    Returns:
        float or str: The result of the evaluated expression, or an error message if invalid.
    """
    try:
        # Evaluate the expression safely using eval with restricted globals and locals
        result = eval(expression, {"__builtins__": None}, {})
        return result
    except Exception as e:
        return f"Error: {str(e)}"



import requests
@tool
def fetch_stock_price(api_key, symbol):
    """
    Fetch the latest stock price using a stock API.

    Parameters:
        api_key (str): Your API key for the stock data service.
        symbol (str): The stock ticker symbol (e.g., 'AAPL', 'GOOGL').

    Returns:
        dict: A dictionary containing the stock price or an error message.
    """
    base_url = f"https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",
        "apikey": "4XLBNQWHUU50M3B5"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if "Time Series (1min)" not in data:
            return {"error": "Failed to fetch stock data. Check symbol or API key."}

        # Extract the latest price
        latest_time = sorted(data["Time Series (1min)"].keys())[0]
        latest_data = data["Time Series (1min)"][latest_time]
        price = latest_data["1. open"]

        return {
            "symbol": symbol,
            "price": price,
            "time": latest_time
        }

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


import requests
@tool
def get_weather(city, api_key):
    """
    Fetch weather information for a given city.
    
    Args:
        city (str): Name of the city.
        api_key (str): OpenWeatherMap API key.
        
    Returns:
        dict: Weather information including temperature, weather condition, and humidity.
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": "30e76dc18ed2ac7d93c461ada59cee43",
        "units": "metric"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        weather = {
            "City": data["name"],
            "Temperature": data["main"]["temp"],
            "Weather": data["weather"][0]["description"],
            "Humidity": data["main"]["humidity"]
        }
        
        return weather
    
    except requests.exceptions.HTTPError as errh:
        return f"HTTP Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return f"Connection Error: {errc}"
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return f"Error: {err}"


import shutil
@tool


def get_disk_usage(path='/'):
    """
    Display the current disk usage for a given path.
    
    Args:
        path (str): The file system path to check disk usage (default is root '/').
    
    Returns:
        dict: Disk usage statistics including total, used, free space, and usage percentage.
    """
    try:
        usage = shutil.disk_usage(path)
        disk_info = {
            "Path": path,
            "Total Space (GB)": round(usage.total / (1024 ** 3), 2),
            "Used Space (GB)": round(usage.used / (1024 ** 3), 2),
            "Free Space (GB)": round(usage.free / (1024 ** 3), 2),
            "Usage Percentage (%)": round((usage.used / usage.total) * 100, 2)
        }
        return disk_info
    
    except Exception as e:
        return f"Error: {e}"


import requests
@tool


def search_images(keyword, api_key, per_page=5):
    """
    Search for images based on a keyword using Unsplash API.
    
    Args:
        keyword (str): Search term for the images.
        api_key (str): Unsplash API access key.
        per_page (int): Number of image results to retrieve (default is 5).
        
    Returns:
        list: A list of image URLs matching the search keyword.
    """
    base_url = "https://api.unsplash.com/search/photos"
    params = {
        "query": keyword,
        "client_id": api_key,
        "per_page": per_page
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        image_urls = [result['urls']['regular'] for result in data['results']]
        return image_urls if image_urls else ["No images found."]
    
    except requests.exceptions.HTTPError as errh:
        return f"HTTP Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return f"Connection Error: {errc}"
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return f"Error: {err}"


tools = [calculator,get_weather,get_disk_usage,fetch_stock_price]

llm = ChatGoogleGenerativeAI(model= "gemini-2.0-flash-exp",api_key = GOOGLE_API_KEY )



agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=False)


# Styling for the sidebar and submit button
st.markdown("""
<style>
    .stSidebar {
        background-color: #f0f0f0;
        padding: 1em;
        border-radius: 10px;
    }
    .tool-item {
        font-size: 1.1em;
        margin-bottom: 0.5em;
        color: #333;
    }
    .stButton button {
        background-color: green;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5em 1em;
    }
</style>
""", unsafe_allow_html=True)

# Add a sidebar menu
with st.sidebar:
    # Using markdown with custom CSS to make the header red
    st.markdown("<h1 style='color: red;'>Available Tools</h1>", unsafe_allow_html=True)
   
    st.markdown("""
    <div class="stSidebar">
        <div class="tool-item">1. Calculator</div>
        <div class="tool-item">2. Weather Information</div>
        <div class="tool-item">3. Disk Usage</div>
        <div class="tool-item">4. Stock Price Fetcher</div>
    </div>
    """, unsafe_allow_html=True)

# Main app interface
st.title("Gemini Tool Calling")
st.write("Welcome to Nazish's Agentic App!")

# Input and processing
user_input = st.text_input("Enter your prompt")
if st.button("Submit"):
    response = agent.invoke(user_input)
    st.write(response["output"])
