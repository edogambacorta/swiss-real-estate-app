import os
import sys

required_env_vars = [
    "FIRECRAWL_API_KEY",
    "OPENAI_API_KEY"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print("Error: The following required environment variables are not set:")
    for var in missing_vars:
        print(f"- {var}")
    print("Please set these variables before running the application.")
    sys.exit(1)
else:
    print("All required environment variables are set.")
    sys.exit(0)
