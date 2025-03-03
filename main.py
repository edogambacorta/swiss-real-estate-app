import streamlit as st
from src.ui import main
import subprocess
import sys

if __name__ == "__main__":
    # Run the environment variable check
    result = subprocess.run([sys.executable, "check_env.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        sys.exit(1)
    
    # If the check passes, run the main application
    main()
