import streamlit as st
from swiss_real_estate_agent import SwissPropertyAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_property_agent():
    if 'property_agent' not in st.session_state:
        st.session_state.property_agent = SwissPropertyAgent(
            firecrawl_api_key=os.getenv('FIRECRAWL_API_KEY'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            model_id="gpt-4o"
        )

def main():
    st.set_page_config(page_title="Swiss Real Estate Agent", page_icon="🏡", layout="wide")
    
    with st.sidebar:
        st.title("🔑 Configuration")
        st.info("API keys are now loaded from environment variables.")
        
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
        if not all([os.getenv('FIRECRAWL_API_KEY'), os.getenv('OPENAI_API_KEY')]):
            st.error("⚠️ API keys not found in environment variables!")
            return
        
        create_property_agent()
        with st.spinner("🔍 Searching..."):
            results = st.session_state.property_agent.find_properties(city, max_price, property_type)
            st.markdown(results)
        
        with st.spinner("📊 Analyzing Trends..."):
            trends = st.session_state.property_agent.get_location_trends(city)
            with st.expander("📈 Market Trends"):
                st.markdown(trends)

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
