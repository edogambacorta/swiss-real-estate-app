from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
import os
from dotenv import load_dotenv

# Swiss-specific property data schema
class PropertyData(BaseModel):
    building_name: str = Field(description="Name of the building/property")
    property_type: str = Field(description="Type (e.g., apartment, chalet, house)")
    location_address: str = Field(description="Address including city/canton")
    price: str = Field(description="Price in CHF")
    description: str = Field(description="Property details")
    size: Optional[str] = Field(description="Size of the property in square meters")
    rooms: Optional[str] = Field(description="Number of rooms")

class PropertiesResponse(BaseModel):
    properties: List[PropertyData] = Field(description="List of properties")

# Location trends schema
class LocationData(BaseModel):
    location: str
    price_per_sqm: float  # Swiss standard: price per square meter
    annual_increase: float
    rental_yield: float

class LocationsResponse(BaseModel):
    locations: List[LocationData] = Field(description="List of location data")

class SwissPropertyAgent:
    def __init__(self, model_id: str = "gpt-4o"):
        load_dotenv()
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        if not self.firecrawl_api_key or not self.openai_api_key:
            raise ValueError("Missing API keys. Please check your .env file.")

        try:
            self.agent = Agent(
                model=OpenAIChat(id=model_id, api_key=self.openai_api_key),
                markdown=True,
                description="I am a Swiss real estate expert assisting with property search and analysis."
            )
            self.firecrawl = FirecrawlApp(api_key=self.firecrawl_api_key)
        except Exception as e:
            raise ValueError(f"Error initializing APIs: {str(e)}")

    def find_properties(self, city: str, max_price: float, property_type: str = "Apartment") -> Optional[List[Dict]]:
        formatted_city = city.lower().replace(" ", "-")
        urls = [
            f"https://www.homegate.ch/buy/{property_type.lower()}/city-{formatted_city}",
            f"https://www.immoscout24.ch/en/real-estate/buy/city-{formatted_city}",
            f"https://www.comparis.ch/immobilien/marktplatz/{formatted_city}/kaufen",
        ]
        
        try:
            response = self.firecrawl.extract(urls, {
                'prompt': f"Extract property listings in {city} under {max_price} CHF.",
                'schema': PropertiesResponse.model_json_schema(),
            })
            
            properties = response['data']['properties']
            return properties
        except Exception as e:
            print(f"Error finding properties: {str(e)}")
            return None

    def get_location_trends(self, city: str) -> Optional[str]:
        urls = [f"https://www.homegate.ch/market-analysis/{city.lower().replace(' ', '-')}" ]
        try:
            response = self.firecrawl.extract(urls, {
                'prompt': f"Extract price trends for {city}.",
                'schema': LocationsResponse.model_json_schema(),
            })
            trends = response['data']['locations']
            return self.agent.run(f"Provide investment insights based on these trends:\n{trends}")
        except Exception as e:
            print(f"Error getting location trends: {str(e)}")
            return None

    def analyze_properties(self, properties: List[Dict], city: str) -> str:
        return self.agent.run(f"Analyze these properties from {city} and provide recommendations:\n{properties}")
