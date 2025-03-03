from typing import Dict, List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
import streamlit as st

# Swiss-specific property data schema
class PropertyData(BaseModel):
    building_name: str = Field(description="Name of the building/property")
    property_type: str = Field(description="Type (e.g., apartment, chalet, house)")
    location_address: str = Field(description="Address including city/canton")
    price: str = Field(description="Price in CHF")
    description: str = Field(description="Property details")

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
    def __init__(self, firecrawl_api_key: str, openai_api_key: str, model_id: str = "gpt-4o"):
        self.agent = Agent(
            model=OpenAIChat(id=model_id, api_key=openai_api_key),
            markdown=True,
            description="I am a Swiss real estate expert assisting with property search and analysis."
        )
        self.firecrawl = FirecrawlApp(api_key=firecrawl_api_key)

    def find_properties(self, city: str, max_price: float, property_type: str = "Apartment") -> str:
        formatted_city = city.lower().replace(" ", "-")
        urls = [
            f"https://www.homegate.ch/buy/{property_type.lower()}/city-{formatted_city}",
            f"https://www.immoscout24.ch/en/real-estate/buy/city-{formatted_city}",
            f"https://www.comparis.ch/immobilien/marktplatz/{formatted_city}/kaufen",
        ]
        
        response = self.firecrawl.extract(urls, {
            'prompt': f"Extract property listings in {city} under {max_price} CHF.",
            'schema': PropertiesResponse.model_json_schema(),
        })
        
        properties = response['data']['properties']
        return self.agent.run(f"Analyze these properties from {city} and provide recommendations:\n{properties}")

    def get_location_trends(self, city: str) -> str:
        urls = [f"https://www.homegate.ch/market-analysis/{city.lower().replace(' ', '-')}" ]
        response = self.firecrawl.extract(urls, {
            'prompt': f"Extract price trends for {city}.",
            'schema': LocationsResponse.model_json_schema(),
        })
        trends = response['data']['locations']
        return self.agent.run(f"Provide investment insights based on these trends:\n{trends}")
