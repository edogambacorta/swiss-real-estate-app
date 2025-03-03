import streamlit as st
from src.swiss_real_estate_agent import SwissPropertyAgent
from src.cantons import get_all_canton_names, get_canton_name, get_canton_code
import os
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
import requests
from io import BytesIO
from requests.exceptions import RequestException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(page_title="Swiss Real Estate Agent", page_icon="🏡", layout="wide")

# Load environment variables
load_dotenv()

def apply_custom_css():
    st.markdown("""
    <style>
        .app-header {
            text-align: center;
            color: #1e3a8a;
            padding: 20px 0;
            font-size: 2.5em;
        }
        .property-card {
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin-bottom: 20px;
            padding: 20px;
        }
        .property-header {
            display: flex;
            margin-bottom: 20px;
        }
        .property-thumbnail {
            width: 300px;
            height: 225px;
            object-fit: cover;
            border-radius: 5px;
        }
        .property-content {
            flex: 1;
            padding-left: 20px;
        }
        .property-title {
            font-size: 28px;
            font-weight: bold;
            color: #1e3a8a;
            margin-bottom: 10px;
        }
        .property-price {
            font-size: 24px;
            font-weight: bold;
            color: #059669;
            margin-bottom: 15px;
        }
        .property-detail-item {
            font-size: 18px;
            margin-bottom: 10px;
        }
        .property-detail-item strong {
            font-weight: bold;
            color: #1e3a8a;
        }
        .property-description {
            font-size: 16px;
            color: #4b5563;
            margin-top: 15px;
        }
        .view-listing-button {
            background-color: #2563eb;
            color: white !important;
            padding: 12px 20px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin-top: 15px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s;
            font-size: 16px;
            font-weight: bold;
        }
        .view-listing-button:hover {
            background-color: #1d4ed8;
        }
    </style>
    """, unsafe_allow_html=True)

def create_property_agent():
    if 'property_agent' not in st.session_state:
        try:
            st.session_state.property_agent = SwissPropertyAgent(model_id="gpt-4o")
        except ValueError as e:
            st.error(f"Error initializing SwissPropertyAgent: {str(e)}")
            st.session_state.property_agent = None

def load_image(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img.load()  # This will raise an exception for corrupt images
            return img
        except RequestException as e:
            logging.error(f"Network error loading image from {url}: {str(e)}")
        except UnidentifiedImageError:
            logging.error(f"Unidentified image format from {url}")
        except Exception as e:
            logging.error(f"Error loading image from {url}: {str(e)}")
        
        if attempt < max_retries - 1:
            logging.info(f"Retrying image load from {url} (attempt {attempt + 2}/{max_retries})")
    
    logging.warning(f"Failed to load image from {url} after {max_retries} attempts")
    return None  # Return None for failed image loads

def display_property(property):
    price = property['price']
    if not price.startswith('CHF'):
        price = f"CHF {price}"
    
    st.markdown("<div class='property-card'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        image_url = property.get('image_url')
        if image_url is None:
            st.image('https://via.placeholder.com/300x225?text=No+Image+URL', use_container_width=True)
        else:
            if image_url.startswith(('http://', 'https://')):
                image = load_image(image_url)
                if image is not None:
                    st.image(image, use_container_width=True)
                else:
                    st.image('https://via.placeholder.com/300x225?text=Image+Load+Error', use_container_width=True)
            else:
                st.image('https://via.placeholder.com/300x225?text=Invalid+URL', use_container_width=True)
    
    with col2:
        st.markdown(f"<h3 class='property-title'>{property['building_name']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 class='property-price'>{price}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p class='property-detail-item'>📍 <strong>Location:</strong> {property['location_address']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='property-detail-item'>🏠 <strong>Type:</strong> {property['property_type']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='property-detail-item'>📐 <strong>Size:</strong> {property.get('size', 'N/A')}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='property-detail-item'>🛏️ <strong>Rooms:</strong> {property.get('rooms', 'N/A')}</p>", unsafe_allow_html=True)
    
    with st.expander("Description"):
        st.markdown(f"<p class='property-description'>{property['description']}</p>", unsafe_allow_html=True)
    
    st.markdown(f"<a href='{property['listing_url']}' class='view-listing-button' target='_blank'>View Listing</a>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def parse_price(price_str):
    if price_str == 'Price on request':
        return float('inf')
    # Remove 'CHF', commas, and any other non-numeric characters (except '.')
    cleaned_price = ''.join(char for char in price_str if char.isdigit() or char == '.')
    try:
        return float(cleaned_price)
    except ValueError:
        # If we can't parse the price, return infinity so it appears at the end of sorted lists
        return float('inf')

def display_bullet_points(data, title):
    st.subheader(title)
    for item in data:
        st.markdown(f"• **{item['header']}**: {item['subheader']}")

def render_city_overview(city_overview):
    st.subheader("🏙️ City Overview")
    for key, value in city_overview.items():
        st.markdown(f"• **{key}**: {value}")

def search_properties(city, min_price, max_price, property_type, canton, debug_mode):
    selected_canton = None if canton == "All" else canton
    num_results = 10
    properties = st.session_state.property_agent.find_properties(city, min_price, max_price, property_type, selected_canton, num_results=num_results)
    
    if debug_mode:
        st.write(f"Raw properties data: {properties}")
    
    if properties:
        # Sorting options
        sort_option = st.selectbox("Sort by:", ["Price (Low to High)", "Price (High to Low)", "Size (Small to Large)", "Size (Large to Small)"])
        
        if sort_option == "Price (Low to High)":
            properties.sort(key=lambda x: parse_price(x['price']))
        elif sort_option == "Price (High to Low)":
            properties.sort(key=lambda x: parse_price(x['price']), reverse=True)
        elif sort_option == "Size (Small to Large)":
            properties.sort(key=lambda x: float(x.get('size', '0').split()[0]) if x.get('size') else 0)
        elif sort_option == "Size (Large to Small)":
            properties.sort(key=lambda x: float(x.get('size', '0').split()[0]) if x.get('size') else 0, reverse=True)
        
        # Display all properties without pagination
        for property in properties:
            display_property(property)
        
        st.write(f"Showing {len(properties)} properties")
        
        # Property analysis
        if st.button("Analyze Properties"):
            with st.spinner("Analyzing properties..."):
                analysis = st.session_state.property_agent.analyze_properties(properties, city, min_price, max_price, selected_canton)
                st.markdown("## Property Analysis")
                st.markdown(analysis)
    else:
        st.error("No properties found. Please try adjusting your search criteria.")
        if debug_mode:
            st.write("Debug information:")
            st.write(f"City: {city}")
            st.write(f"Price Range: {min_price} - {max_price} CHF")
            st.write(f"Property Type: {property_type}")
            st.write(f"Canton: {canton}")
    
    return selected_canton

def display_city_overview(city, selected_canton, debug_mode):
    with st.spinner("🏙️ Fetching City Overview..."):
        try:
            logging.info(f"Fetching city overview for {city}, {selected_canton}")
            city_overview = st.session_state.property_agent.get_city_overview(city, selected_canton)
            
            if city_overview:
                logging.info(f"City overview fetched successfully for {city}, {selected_canton}")
                with st.expander("🏙️ City Overview", expanded=True):
                    render_city_overview(city_overview)
            else:
                logging.warning(f"No city overview data available for {city}, {selected_canton}")
                st.warning("No city overview data available for the selected city and canton.")
        except Exception as e:
            logging.error(f"Error fetching city overview for {city}, {selected_canton}: {str(e)}")
            st.error("An error occurred while fetching the city overview. Please try again.")
            if debug_mode:
                st.write("Debug information:")
                st.write(f"City: {city}")
                st.write(f"Canton: {selected_canton}")
                st.write(f"Error: {str(e)}")

def main():
    apply_custom_css()
    
    with st.sidebar:
        st.title("🔑 Configuration")
        st.info("API keys are loaded from environment variables.")
        
        language = st.selectbox("Language / Sprache / Langue / Lingua", ["English", "Deutsch", "Français", "Italiano"])
        debug_mode = st.checkbox("Debug Mode")
    
    st.markdown("<h1 class='app-header'>🏠 Swiss Property Finder</h1>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        city = st.text_input("City", placeholder="e.g., Zurich, Geneva")
    with col2:
        min_price = st.number_input("Min Price (CHF)", min_value=0.0, step=100000.0, value=0.0)
    with col3:
        max_price = st.number_input("Max Price (CHF)", min_value=0.0, step=100000.0, value=1000000.0)
    with col4:
        property_type = st.selectbox("Property Type", ["Apartment", "House", "Chalet"])
    
    canton = st.selectbox("Canton", ["All"] + get_all_canton_names())

    selected_canton = None
    if st.button("🔍 Search Properties"):
        logging.info("Search button clicked")
        create_property_agent()
        if st.session_state.property_agent is None:
            logging.error("Failed to create SwissPropertyAgent")
            return
        
        if debug_mode:
            st.write("Testing API connection...")
            api_test_result = st.session_state.property_agent.test_api_connection()
            st.write(f"API Test Result: {'Success' if api_test_result else 'Failed'}")
            logging.info(f"API Test Result: {'Success' if api_test_result else 'Failed'}")
        
        if min_price >= max_price:
            logging.warning(f"Invalid price range: {min_price} - {max_price}")
            st.error("Minimum price must be less than maximum price.")
        else:
            logging.info(f"Searching properties for {city}, {canton}, {property_type}, price range: {min_price} - {max_price}")
            selected_canton = search_properties(city, min_price, max_price, property_type, canton, debug_mode)
            logging.info(f"Displaying city overview for {city}, {selected_canton}")
            display_city_overview(city, selected_canton, debug_mode)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Swiss Real Estate Regulations")
    if st.sidebar.button("Show Regulations"):
        # This is a placeholder. In a real application, you would fetch this data from a reliable source.
        st.sidebar.markdown("""
        - Non-residents need a permit (Lex Koller) to buy property
        - Annual property tax varies by canton
        - Rental properties: Landlords can only increase rent with interest rate changes
        """)
        
        if canton != "All":
            st.sidebar.markdown(f"### {canton} Specific Regulations")
            # Placeholder for canton-specific regulations
            st.sidebar.markdown(f"Displaying regulations specific to {canton}...")
            # In a real application, you would fetch canton-specific regulations here

if __name__ == "__main__":
    main()
