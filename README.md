# Swiss Real Estate App

An AI-powered real estate application focused on the Swiss market, built with Streamlit and leveraging OpenAI and Firecrawl APIs.

## Features

- Property search across major Swiss real estate websites
- AI-powered property analysis and recommendations
- Location trend analysis and investment insights
- Multilingual support (English, German, French, Italian)
- Canton-specific filtering
- Integration of Swiss real estate regulations

## Prerequisites

- Python 3.10+
- Firecrawl API key
- OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/swiss-real-estate-app.git
   cd swiss-real-estate-app
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your API keys:
   ```
   FIRECRAWL_API_KEY=your_firecrawl_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

   IMPORTANT: Keep your `.env` file secure and never commit it to version control. It's added to `.gitignore` by default.

## Usage

1. Ensure your `.env` file is set up correctly with your API keys.

2. Run the Streamlit app:

   ```
   streamlit run main.py
   ```

3. Open your web browser and go to `http://localhost:8501` to use the Swiss Real Estate App.

4. If you encounter any errors related to API keys, check your `.env` file and ensure the keys are correct.

## API Key Security and Error Handling

This application uses environment variables to securely store API keys and includes error handling for API-related issues. Always follow these best practices:

1. Never share your API keys publicly or commit them to version control.
2. Use environment variables or secure secret management systems in production.
3. Regularly rotate your API keys, especially if you suspect they've been compromised.
4. Set appropriate permissions and rate limits on your API keys when possible.
5. If you encounter errors related to API keys or API calls, check the error messages in the application for guidance.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
