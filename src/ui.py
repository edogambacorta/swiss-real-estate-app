import streamlit as st
from src.swiss_real_estate_agent import SwissPropertyAgent
from src.cantons import get_all_canton_names, get_canton_name, get_canton_code
import os
from dotenv import load_dotenv
from PIL import Image
import requests
from io import BytesIO

# Load environment variables
load_dotenv()

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
    with st.expander(f"{property['building_name']} - {property['price']}"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Location:** {property['location_address']}")
            st.write(f"**Type:** {property['property_type']}")
            st.write(f"**Size:** {property.get('size', 'N/A')}")
            st.write(f"**Rooms:** {property.get('rooms', 'N/A')}")
        with col2:
            if property.get('image_url'):
                img = load_image(property['image_url'])
                if img:
                    st.image(img, use_column_width=True)
                else:
                    st.write("Image not available")
            else:
                st.write("No image available")
        st.write("**Description:**")
        st.write(property['description'][:200] + "..." if len(property['description']) > 200 else property['description'])

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
    st.set_page_config(page_title="Swiss Real Estate Agent", page_icon="🏡", layout="wide")
    
    with st.sidebar:
        st.title("🔑 Configuration")
        st.info("API keys are loaded from environment variables.")
        
        language = st.selectbox("Language / Sprache / Langue / Lingua", ["English", "Deutsch", "Français", "Italiano"])
        
    st.title("🏠 Swiss Property Finder")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.text_input("City", placeholder="e.g., Zurich, Geneva")
    with col2:
        max_price = st.number_input("Max Price (CHF)", min_value=0.0, step=100000.0)
    with col3:
        property_type = st.selectbox("Property Type", ["Apartment", "House", "Chalet"])
    
    canton = st.selectbox("Canton", ["All"] + get_all_canton_names())

    if st.button("🔍 Search Properties"):
        create_property_agent()
        if st.session_state.property_agent is None:
            return
        
        with st.spinner("🔍 Searching..."):
            selected_canton = None if canton == "All" else canton
            properties = st.session_state.property_agent.find_properties(city, max_price, property_type, selected_canton)
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
                
                # Pagination
                items_per_page = 5
                page_number = st.number_input("Page", min_value=1, max_value=(len(properties) - 1) // items_per_page + 1, value=1)
                start_idx = (page_number - 1) * items_per_page
                end_idx = start_idx + items_per_page
                
                for property in properties[start_idx:end_idx]:
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if property.get('image_url'):
                            img = load_image(property['image_url'])
                            if img:
                                st.image(img, width=100)
                            else:
                                st.write("Thumbnail not available")
                        else:
                            st.write("No thumbnail")
                    with col2:
                        display_property(property)
                
                st.write(f"Showing {start_idx + 1}-{min(end_idx, len(properties))} of {len(properties)} properties")
                
                # Property analysis
                if st.button("Analyze Properties"):
                    with st.spinner("Analyzing properties..."):
                        analysis = st.session_state.property_agent.analyze_properties(properties, city, selected_canton)
                        st.markdown("## Property Analysis")
                        st.markdown(analysis)
            else:
                st.error("No properties found or an error occurred while searching. Please try again.")
        
        with st.spinner("📊 Analyzing Market Insights..."):
            trends = st.session_state.property_agent.get_location_trends(city, selected_canton)
            canton_stats = st.session_state.property_agent.get_canton_statistics(selected_canton) if selected_canton else None
            
            if trends or canton_stats:
                with st.expander("📈 Market Insights", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        if trends:
                            display_market_trends(trends)
                    with col2:
                        if selected_canton and canton_stats:
                            display_canton_statistics(canton_stats)
            else:
                st.error("An error occurred while analyzing market insights. Please try again.")

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
