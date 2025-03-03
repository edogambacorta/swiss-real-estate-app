# Technical Context

## Technologies Used

- Python 3.10+
- Streamlit: For building the web application interface
- OpenAI API: For AI-powered property analysis and recommendations
- Firecrawl API: For web scraping real estate websites
- python-dotenv: For loading environment variables

## Development Setup

- Virtual environment is used for package management
- Requirements are listed in requirements.txt

## API Key Management

- API keys (Firecrawl and OpenAI) are stored as environment variables
- A .env file in the root directory is used to store these variables locally
- python-dotenv is used to load these variables in the application

## Security Considerations

- The .env file is included in .gitignore to prevent accidental commits of sensitive information
- API keys are never exposed in the UI or client-side code
- Users are advised to follow best practices for API key security, including regular rotation and appropriate permissions

## Project Structure

- main.py: Entry point of the application
- src/
  - ui.py: Contains the Streamlit UI code
  - swiss_real_estate_agent.py: Contains the core logic for property search and analysis
- requirements.txt: Lists all Python package dependencies
- .env: Stores API keys (not tracked in version control)
- .env.example: Template for .env file (safe to include in version control)

## Data Flow

1. Environment variables are loaded at application start
2. User inputs are collected through the Streamlit UI
3. Property search is performed using the Firecrawl API
4. Property analysis is conducted using the OpenAI API
5. Results are displayed to the user in the Streamlit interface

This structure ensures a separation of concerns and maintains security best practices for handling API keys.
