import sys
import os

# Ensure the project root is on sys.path so that pytest can import
# top-level modules like `app` and `nlp_model` from the tests/ subdirectory.
sys.path.insert(0, os.path.dirname(__file__))
