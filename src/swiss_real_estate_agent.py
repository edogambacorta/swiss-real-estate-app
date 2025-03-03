from typing import Dict, List, Optional, Tuple
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
    listing_url: Optional[str] = Field(description="URL of the original property listing")

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

    def find_properties(self, city: str, min_price: float, max_price: float, property_type: str = "Apartment", canton: Optional[str] = None, num_results: int = 10) -> Optional[List[Dict]]:
        formatted_city = city.lower().replace(" ", "-")
        canton_code = get_canton_code(canton) if canton else None
        
        urls = [
            f"https://www.homegate.ch/buy/{property_type.lower()}/city-{formatted_city}",
            f"https://www.immoscout24.ch/en/real-estate/buy/city-{formatted_city}",
            f"https://www.comparis.ch/immobilien/marktplatz/{formatted_city}/kaufen",
        ]
        
        try:
            prompt = f"Extract at least {num_results * 2} property listings in {city} between {min_price} and {max_price} CHF, including image URLs and original listing URLs"
            if canton_code:
                prompt += f" in the canton of {get_canton_name(canton_code)}"
            
            print(f"API Request - URLs: {urls}, Prompt: {prompt}")  # Debug log
            response = self.firecrawl.extract(urls, {
                'prompt': prompt,
                'schema': PropertiesResponse.model_json_schema(),
            })
            print(f"Raw API Response: {response}")  # Debug log
            
            properties = response['data']['properties']
            print(f"Number of properties before filtering: {len(properties)}")  # Debug log
            
            # Process properties to ensure image URLs and listing URLs are present and filter by price range
            filtered_properties = []
            for prop in properties:
                if 'image_url' not in prop or not prop['image_url'] or 'listing_url' not in prop or not prop['listing_url']:
                    prop['image_url'], prop['listing_url'] = self._extract_urls(prop)
                price = self._parse_price(prop['price'])
                if min_price <= price <= max_price:
                    filtered_properties.append(prop)
                if len(filtered_properties) >= num_results:
                    break
            
            if canton_code:
                filtered_properties = [prop for prop in filtered_properties if prop['canton'] == canton_code][:num_results]
            
            print(f"Number of properties after filtering: {len(filtered_properties)}")  # Debug log
            
            if len(filtered_properties) < num_results:
                print(f"Warning: Only found {len(filtered_properties)} properties matching the criteria")
            
            return filtered_properties[:num_results]
        except Exception as e:
            error_message = f"Error finding properties: {str(e)}"
            print(error_message)
            if hasattr(e, 'response'):
                print(f"API Response: {e.response.text}")
            return None

    def _extract_urls(self, property_data: Dict) -> Tuple[Optional[str], Optional[str]]:
        try:
            # Extract image URL and listing URL from the property data
            return property_data.get('image_url'), property_data.get('listing_url')
        except Exception as e:
            print(f"Error extracting image URL or listing URL: {str(e)}")
            return None, None

    def filter_properties_by_canton(self, properties: List[Dict], canton: str) -> List[Dict]:
        canton_code = get_canton_code(canton)
        return [prop for prop in properties if prop['canton'] == canton_code]

    def get_location_trends(self, city: str, canton: Optional[str] = None) -> Dict:
        formatted_city = city.lower().replace(' ', '-')
        canton_code = get_canton_code(canton) if canton else None
        canton_name = get_canton_name(canton_code) if canton_code else None
        
        default_item = {"header": "Data Unavailable", "subheader": "Unable to retrieve information"}
        
        try:
            urls = [f"https://www.homegate.ch/market-analysis/{formatted_city}"]
            if canton_code:
                urls.append(f"https://www.homegate.ch/market-analysis/canton-{canton_code.lower()}")
            
            prompt = f"Extract price trends, demand, supply, rental yield, and future outlook for {city}"
            if canton_code:
                prompt += f" and the canton of {canton_name}"
            
            print(f"Location Trends API Request - URLs: {urls}, Prompt: {prompt}")  # Debug log
            response = self.firecrawl.extract(urls, {
                'prompt': prompt,
                'schema': LocationsResponse.model_json_schema(),
            })
            print(f"Location Trends Raw API Response: {response}")  # Debug log
            
            trends = response['data']['locations']
            
            # Process the trends data into a structured format
            city_data = next((loc for loc in trends if loc['location'].lower() == city.lower()), None)
            
            market_trends = [
                {"header": "Price Trends", "subheader": f"Average price: CHF {city_data['price_per_sqm']:,.2f} per m²" if city_data and city_data.get('price_per_sqm') else "Data not available"},
                {"header": "Demand", "subheader": "High demand in urban areas" if city_data else "Unable to assess demand"},
                {"header": "Supply", "subheader": "Limited supply in popular areas" if city_data else "Unable to assess supply"},
                {"header": "Rental Yield", "subheader": f"{city_data['rental_yield']:.2f}% average rental return" if city_data and city_data.get('rental_yield') else "Data not available"},
                {"header": "Future Outlook", "subheader": f"Annual increase: {city_data['annual_increase']:.2f}%" if city_data and city_data.get('annual_increase') else "Unable to predict future trends"}
            ]
            
            return {"market_trends": market_trends}
        
        except Exception as e:
            print(f"Error getting location trends: {str(e)}")
            return {"market_trends": [default_item] * 5}

    def _parse_price(self, price_str: str) -> float:
        try:
            # Remove 'CHF', commas, and any other non-numeric characters (except '.')
            cleaned_price = ''.join(char for char in price_str if char.isdigit() or char == '.')
            return float(cleaned_price)
        except ValueError:
            print(f"Unable to parse price: {price_str}")  # Debug log
            return float('inf')  # Return infinity for unparseable prices

    def test_api_connection(self):
        try:
            # Make a simple API call to test the connection
            response = self.firecrawl.extract(["https://www.example.com"], {
                'prompt': "Extract the title of the page",
                'schema': {"type": "object", "properties": {"title": {"type": "string"}}}
            })
            print("API connection successful")
            return True
        except Exception as e:
            print(f"API connection failed: {str(e)}")
            return False

    def analyze_properties(self, properties: List[Dict], city: str, min_price: float, max_price: float, canton: Optional[str] = None) -> str:
        canton_name = get_canton_name(get_canton_code(canton)) if canton else None
        context = f"from {city} with prices between {min_price} and {max_price} CHF" + (f" in the canton of {canton_name}" if canton_name else "")
        return self.agent.run(f"Analyze these properties {context} and provide recommendations, considering the specified price range and any canton-specific factors:\n{properties}")

    def get_canton_statistics(self, canton: str) -> Dict:
        canton_code = get_canton_code(canton)
        canton_name = get_canton_name(canton_code)
        
        default_item = {"header": "Data Unavailable", "subheader": "Unable to retrieve information"}
        
        try:
            urls = [f"https://www.homegate.ch/market-analysis/canton-{canton_code.lower()}"]
            
            prompt = f"Extract information on property types, price ranges, market activity, construction projects, and key regulations for the canton of {canton_name}"
            
            response = self.firecrawl.extract(urls, {
                'prompt': prompt,
                'schema': LocationsResponse.model_json_schema(),
            })
            stats = response['data']['locations']
            
            canton_data = next((loc for loc in stats if loc['location'].lower() == canton_name.lower()), None)
            
            real_estate_statistics = [
                {"header": "Property Types", "subheader": "Mix of apartments and houses" if canton_data else "Data not available"},
                {"header": "Price Range", "subheader": f"Average: CHF {canton_data['price_per_sqm']:,.2f} per m²" if canton_data and canton_data.get('price_per_sqm') else "Data not available"},
                {"header": "Market Activity", "subheader": "Moderate transaction volume" if canton_data else "Unable to assess market activity"},
                {"header": "Construction", "subheader": "Ongoing development in urban areas" if canton_data else "No information on construction projects"},
                {"header": "Regulations", "subheader": "Standard Swiss property regulations apply" if canton_data else "Unable to provide regulation information"}
            ]
            
            return {"canton_name": canton_name, "real_estate_statistics": real_estate_statistics}
        
        except Exception as e:
            print(f"Error getting canton statistics: {str(e)}")
            return {"canton_name": canton_name, "real_estate_statistics": [default_item] * 5}
