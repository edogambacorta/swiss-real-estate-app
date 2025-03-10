# Technical Context

## Technologies Used

- Python 3.10+
- Streamlit: For building the web application interface
- OpenAI API: For AI-powered property analysis and recommendations
- Firecrawl API: For web scraping real estate websites
- python-dotenv: For loading environment variables
- pydantic: For data validation and settings management
- Watchdog: For monitoring file system events and automating tasks

## Development Setup

- Virtual environment is used for package management
- Requirements are listed in requirements.txt

## API Key Management

- API keys (Firecrawl and OpenAI) are stored as environment variables
- A .env file in the root directory is used to store these variables locally
- python-dotenv is used to load these variables in the application
- Error handling is implemented for missing or invalid API keys

## Security Considerations

- The .env file is included in .gitignore to prevent accidental commits of sensitive information
- API keys are never exposed in the UI or client-side code
- Users are advised to follow best practices for API key security, including regular rotation and appropriate permissions
- Error messages related to API keys are designed to provide useful information without exposing sensitive data

## Project Structure

- main.py: Entry point of the application
- src/
  - ui.py: Contains the Streamlit UI code and error handling for user interactions
  - swiss_real_estate_agent.py: Contains the core logic for property search and analysis, including API key management and error handling
  - swiss_cities_database.py: Implements SwissCitiesDatabase class for storing and managing city information
- requirements.txt: Lists all Python package dependencies
- .env: Stores API keys (not tracked in version control)
- .env.example: Template for .env file (safe to include in version control)
- README.md: Provides detailed setup instructions and guidance on API key management

## Data Flow

1. Environment variables are loaded at application start
2. SwissPropertyAgent is initialized with error handling for API keys
3. SwissCitiesDatabase is initialized with pre-populated city information
4. User inputs are collected through the Streamlit UI
5. City overview is fetched from SwissCitiesDatabase or fallback methods
6. Property search is performed using the Firecrawl API with error handling
7. Results or error messages are displayed to the user in the Streamlit interface

## Error Handling

- Comprehensive error handling is implemented throughout the application
- API-related errors (missing keys, invalid keys, API call failures) are caught and reported to the user
- User-friendly error messages are displayed in the Streamlit interface
- Fallback methods are implemented for city information when not found in SwissCitiesDatabase

This structure ensures a separation of concerns, maintains security best practices for handling API keys, provides a robust error handling system, and incorporates a local database for improved performance and reliability in retrieving city information.
