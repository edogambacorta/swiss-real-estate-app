import streamlit as st
from src.swiss_real_estate_agent import SwissPropertyAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_property_agent():
    if 'property_agent' not in st.session_state:
        try:
            st.session_state.property_agent = SwissPropertyAgent(model_id="gpt-4o")
        except ValueError as e:
            st.error(f"Error initializing SwissPropertyAgent: {str(e)}")
            st.session_state.property_agent = None

def display_property(property):
    with st.expander(f"{property['building_name']} - {property['price']}"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Location:** {property['location_address']}")
            st.write(f"**Type:** {property['property_type']}")
        with col2:
            st.write(f"**Size:** {property.get('size', 'N/A')}")
            st.write(f"**Rooms:** {property.get('rooms', 'N/A')}")
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
    
    canton = st.selectbox("Canton", ["All"] + ["Zurich", "Geneva", "Bern", "Vaud", "Valais", "St. Gallen", "Ticino", "Basel-Stadt", "Lucerne", "Aargau"])

    if st.button("🔍 Search Properties"):
        create_property_agent()
        if st.session_state.property_agent is None:
            return
        
        with st.spinner("🔍 Searching..."):
            properties = st.session_state.property_agent.find_properties(city, max_price, property_type)
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
                    display_property(property)
                
                st.write(f"Showing {start_idx + 1}-{min(end_idx, len(properties))} of {len(properties)} properties")
                
                # Property analysis
                if st.button("Analyze Properties"):
                    with st.spinner("Analyzing properties..."):
                        analysis = st.session_state.property_agent.analyze_properties(properties, city)
                        st.markdown("## Property Analysis")
                        st.markdown(analysis)
            else:
                st.error("No properties found or an error occurred while searching. Please try again.")
        
        with st.spinner("📊 Analyzing Trends..."):
            trends = st.session_state.property_agent.get_location_trends(city)
            if trends:
                with st.expander("📈 Market Trends"):
                    st.markdown(trends)
            else:
                st.error("An error occurred while analyzing market trends. Please try again.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Swiss Real Estate Regulations")
    if st.sidebar.button("Show Regulations"):
        # This is a placeholder. In a real application, you would fetch this data from a reliable source.
        st.sidebar.markdown("""
        - Non-residents need a permit (Lex Koller) to buy property
        - Annual property tax varies by canton
        - Rental properties: Landlords can only increase rent with interest rate changes
        """)

if __name__ == "__main__":
    main()
