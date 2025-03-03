# Technical Context

## Technologies Used

- Python 3.10+
- Streamlit: For building the web application interface
- OpenAI API: For AI-powered property analysis and recommendations
- Firecrawl API: For web scraping real estate websites
- python-dotenv: For loading environment variables
- pydantic: For data validation and settings management

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
- requirements.txt: Lists all Python package dependencies
- .env: Stores API keys (not tracked in version control)
- .env.example: Template for .env file (safe to include in version control)
- README.md: Provides detailed setup instructions and guidance on API key management

## Data Flow

1. Environment variables are loaded at application start
2. SwissPropertyAgent is initialized with error handling for API keys
3. User inputs are collected through the Streamlit UI
4. Property search is performed using the Firecrawl API with error handling
5. Property analysis is conducted using the OpenAI API with error handling
6. Results or error messages are displayed to the user in the Streamlit interface

## Error Handling

- Comprehensive error handling is implemented throughout the application
- API-related errors (missing keys, invalid keys, API call failures) are caught and reported to the user
- User-friendly error messages are displayed in the Streamlit interface

This structure ensures a separation of concerns, maintains security best practices for handling API keys, and provides a robust error handling system for a better user experience.
