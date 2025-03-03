from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
import os
from dotenv import load_dotenv
from .cantons import get_canton_code, get_canton_name, get_all_canton_names

# Swiss-specific property data schema
class PropertyData(BaseModel):
    building_name: str = Field(description="Name of the building/property")
    property_type: str = Field(description="Type (e.g., apartment, chalet, house)")
    location_address: str = Field(description="Address including city/canton")
    canton: str = Field(description="Canton code (e.g., ZH for Zurich)")
    price: str = Field(description="Price in CHF")
    description: str = Field(description="Property details")
    size: Optional[str] = Field(description="Size of the property in square meters")
    rooms: Optional[str] = Field(description="Number of rooms")
    image_url: Optional[str] = Field(description="URL of the property image")

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

    def find_properties(self, city: str, max_price: float, property_type: str = "Apartment", canton: Optional[str] = None) -> Optional[List[Dict]]:
        formatted_city = city.lower().replace(" ", "-")
        canton_code = get_canton_code(canton) if canton else None
        
        urls = [
            f"https://www.homegate.ch/buy/{property_type.lower()}/city-{formatted_city}",
            f"https://www.immoscout24.ch/en/real-estate/buy/city-{formatted_city}",
            f"https://www.comparis.ch/immobilien/marktplatz/{formatted_city}/kaufen",
        ]
        
        try:
            prompt = f"Extract property listings in {city} under {max_price} CHF, including image URLs"
            if canton_code:
                prompt += f" in the canton of {get_canton_name(canton_code)}"
            
            response = self.firecrawl.extract(urls, {
                'prompt': prompt,
                'schema': PropertiesResponse.model_json_schema(),
            })
            
            properties = response['data']['properties']
            
            # Process properties to ensure image URLs are present
            for prop in properties:
                if 'image_url' not in prop or not prop['image_url']:
                    prop['image_url'] = self._extract_image_url(prop)
            
            if canton_code:
                properties = [prop for prop in properties if prop['canton'] == canton_code]
            
            return properties
        except Exception as e:
            error_message = f"Error finding properties: {str(e)}"
            print(error_message)
            if hasattr(e, 'response'):
                print(f"API Response: {e.response.text}")
            return None

    def _extract_image_url(self, property_data: Dict) -> Optional[str]:
        try:
            # Extract image URL from the property data
            return property_data.get('image_url')
        except Exception as e:
            print(f"Error extracting image URL: {str(e)}")
            return None

    def filter_properties_by_canton(self, properties: List[Dict], canton: str) -> List[Dict]:
        canton_code = get_canton_code(canton)
        return [prop for prop in properties if prop['canton'] == canton_code]

    def get_location_trends(self, city: str, canton: Optional[str] = None) -> Optional[str]:
        formatted_city = city.lower().replace(' ', '-')
        canton_code = get_canton_code(canton) if canton else None
        
        urls = [f"https://www.homegate.ch/market-analysis/{formatted_city}"]
        if canton_code:
            urls.append(f"https://www.homegate.ch/market-analysis/canton-{canton_code.lower()}")
        
        try:
            prompt = f"Extract price trends for {city}"
            if canton_code:
                prompt += f" and the canton of {get_canton_name(canton_code)}"
            
            response = self.firecrawl.extract(urls, {
                'prompt': prompt,
                'schema': LocationsResponse.model_json_schema(),
            })
            trends = response['data']['locations']
            return self.agent.run(f"Provide investment insights based on these trends, comparing {city} {'to the canton average ' if canton_code else ''}:\n{trends}")
        except Exception as e:
            print(f"Error getting location trends: {str(e)}")
            return None

    def analyze_properties(self, properties: List[Dict], city: str, canton: Optional[str] = None) -> str:
        canton_name = get_canton_name(get_canton_code(canton)) if canton else None
        context = f"from {city}" + (f" in the canton of {canton_name}" if canton_name else "")
        return self.agent.run(f"Analyze these properties {context} and provide recommendations, considering any canton-specific factors:\n{properties}")

    def get_canton_statistics(self, canton: str) -> Optional[str]:
        canton_code = get_canton_code(canton)
        if not canton_code:
            return None
        
        canton_name = get_canton_name(canton_code)
        urls = [f"https://www.homegate.ch/market-analysis/canton-{canton_code.lower()}"]
        
        try:
            response = self.firecrawl.extract(urls, {
                'prompt': f"Extract real estate statistics for the canton of {canton_name}.",
                'schema': LocationsResponse.model_json_schema(),
            })
            stats = response['data']['locations']
            return self.agent.run(f"Provide an overview of the real estate market in the canton of {canton_name} based on these statistics:\n{stats}")
        except Exception as e:
            print(f"Error getting canton statistics: {str(e)}")
            return None
