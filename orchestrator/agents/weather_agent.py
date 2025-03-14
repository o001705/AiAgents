from phidata.agent import Agent
import requests
import spacy
import datetime

class WeatherAgent(Agent):
    def __init__(self, api_key: str, history_api_key: str = None, retrieval_agent=None):
        super().__init__()
        self.api_key = api_key
        self.history_api_key = history_api_key
        self.retrieval_agent = retrieval_agent
        self.current_weather_url = "http://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        self.history_url = "https://api.weatherapi.com/v1/history.json"
        self.geo_url = "http://ip-api.com/json/"
        self.nlp = spacy.load("en_core_web_sm")

    def generate_response(self, question: str, context=None):
        location = self.extract_location(question)
        if not location and self.retrieval_agent:
            location = self.retrieval_agent.infer_location(question)
        
        if not location:
            location = self.get_approx_location()
        
        if not location:
            location = "London, UK"
        
        timeframe, days = self.classify_timeframe(question)
        
        if timeframe == "current":
            weather_data = self.get_weather(location)
        elif timeframe == "future":
            weather_data = self.get_forecast(location, days)
        elif timeframe == "past":
            weather_data = self.get_past_weather(location, question)
        else:
            return "I couldn't determine the timeframe."
        
        if weather_data:
            return self.format_weather_response(weather_data, timeframe)
        else:
            return "I couldn't retrieve the weather details at the moment."
    
    def extract_location(self, question: str):
        doc = self.nlp(question)
        locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]  # GPE: Geo-Political Entity
        return locations[0] if locations else None
    
    def classify_timeframe(self, question: str):
        keywords = {
            "current": ["now", "currently", "at the moment"],
            "future": ["tomorrow", "next", "this weekend", "in a few days"],
            "past": ["yesterday", "last week", "last month", "previous days", "last year", "last 3 years"]
        }
        
        for timeframe, words in keywords.items():
            if any(word in question.lower() for word in words):
                days = self.extract_days(question) if timeframe == "future" else 1
                return timeframe, days
        
        return "current", 1  # Default to current weather
    
    def extract_days(self, question: str):
        doc = self.nlp(question)
        for token in doc:
            if token.like_num:
                return int(token.text)
        return 1  # Default to 1 day if no specific number is found
    
    def get_approx_location(self):
        response = requests.get(self.geo_url)
        if response.status_code == 200:
            data = response.json()
            return data.get("city")
        return None
    
    def get_weather(self, location: str):
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"
        }
        response = requests.get(self.current_weather_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    
    def get_forecast(self, location: str, days: int):
        params = {
            "q": location,
            "cnt": days * 8,  # 8 forecasts per day (3-hour intervals)
            "appid": self.api_key,
            "units": "metric"
        }
        response = requests.get(self.forecast_url, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_past_weather(self, location: str, question: str):
        if not self.history_api_key:
            return None
        
        target_date = (datetime.datetime.utcnow() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        
        params = {
            "key": self.history_api_key,
            "q": location,
            "dt": target_date
        }
        response = requests.get(self.history_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
