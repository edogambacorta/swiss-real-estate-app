import streamlit as st
from src.swiss_real_estate_agent import SwissPropertyAgent
from src.cantons import get_all_canton_names, get_canton_name, get_canton_code
import os
from dotenv import load_dotenv
from PIL import Image
import requests
from io import BytesIO

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
            display: flex;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin-bottom: 20px;
        }
        .property-thumbnail {
            width: 200px;
            height: 100%;
            object-fit: cover;
        }
        .property-content {
            flex: 1;
            padding: 20px;
            position: relative;
        }
        .property-title {
            font-size: 24px;
            font-weight: bold;
            color: #1e3a8a;
            margin-bottom: 10px;
        }
        .property-price {
            font-size: 20px;
            font-weight: bold;
            color: #059669;
            margin-bottom: 15px;
        }
        .property-details {
            font-size: 16px;
            margin-bottom: 10px;
        }
        .property-details strong {
            font-weight: bold;
            color: #1e3a8a;
        }
        .property-expand {
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            cursor: pointer;
            color: #2563eb;
            font-size: 24px;
        }
        .property-description {
            font-size: 14px;
            color: #4b5563;
            margin-top: 15px;
        }
        .property-image-large {
            width: 100%;
            max-height: 400px;
            object-fit: cover;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .view-listing-button {
            background-color: #2563eb;
            color: white !important;
            padding: 10px 15px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin-top: 15px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s;
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

def load_image(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None

def display_property(property):
    st.markdown(f"""
    <div class="property-card">
        <img src="{property.get('image_url', 'https://via.placeholder.com/200x300?text=No+Image')}" alt="Property Image" class="property-thumbnail">
        <div class="property-content">
            <div class="property-title">{property['building_name']}</div>
            <div class="property-price">{property['price']}</div>
            <div class="property-details">📍 <strong>Location:</strong> {property['location_address']}</div>
            <div class="property-details">🏠 <strong>Type:</strong> {property['property_type']}</div>
            <div class="property-details">📐 <strong>Size:</strong> {property.get('size', 'N/A')}</div>
            <div class="property-details">🛏️ <strong>Rooms:</strong> {property.get('rooms', 'N/A')}</div>
            <div class="property-expand">▼</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("View Details"):
        st.image(property.get('image_url', 'https://via.placeholder.com/800x600?text=No+Image'), use_column_width=True, caption="Property Image")
        st.markdown(f"<div class='property-description'>{property['description']}</div>", unsafe_allow_html=True)
        st.markdown(f"<a href='{property['listing_url']}' target='_blank' class='view-listing-button'>View Listing</a>", unsafe_allow_html=True)

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

def display_market_trends(trends_data):
    display_bullet_points(trends_data["market_trends"], "📈 Market Trends Summary")

def display_canton_statistics(canton_data):
    display_bullet_points(canton_data["real_estate_statistics"], f"📊 {canton_data['canton_name']} Real Estate Statistics")

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

    if st.button("🔍 Search Properties"):
        create_property_agent()
        if st.session_state.property_agent is None:
            return
        
        if debug_mode:
            st.write("Testing API connection...")
            api_test_result = st.session_state.property_agent.test_api_connection()
            st.write(f"API Test Result: {'Success' if api_test_result else 'Failed'}")
        
        if min_price >= max_price:
            st.error("Minimum price must be less than maximum price.")
        else:
            with st.spinner("🔍 Searching..."):
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
            
            with st.spinner("📊 Analyzing Market Insights..."):
                trends = st.session_state.property_agent.get_location_trends(city, selected_canton)
                canton_stats = st.session_state.property_agent.get_canton_statistics(selected_canton) if selected_canton else None
                
                if trends or canton_stats:
                    with st.expander("📈 Market Insights", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            if trends:
                                st.write(f"Market Trends for properties between {min_price} and {max_price} CHF:")
                                display_market_trends(trends)
                        with col2:
                            if selected_canton and canton_stats:
                                st.write(f"Canton Statistics for properties between {min_price} and {max_price} CHF:")
                                display_canton_statistics(canton_stats)
                else:
                    st.error("An error occurred while analyzing market insights. Please try again.")
                    if debug_mode:
                        st.write("Debug information:")
                        st.write(f"City: {city}")
                        st.write(f"Canton: {selected_canton}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Swiss Real Estate Regulations")
    if st.sidebar.button("Show Regulations"):
        # This is a placeholder. In a real application, you would fetch this data from a reliable source.
        st.sidebar.markdown("""
        - Non-residents need a permit (Lex Koller) to buy property
        - Annual property tax varies by canton
        - Rental properties: Landlords can only increase rent with interest rate changes
        """)
        
        if selected_canton:
            st.sidebar.markdown(f"### {selected_canton} Specific Regulations")
            # Placeholder for canton-specific regulations
            st.sidebar.markdown(f"Displaying regulations specific to {selected_canton}...")
            # In a real application, you would fetch canton-specific regulations here

if __name__ == "__main__":
    main()
