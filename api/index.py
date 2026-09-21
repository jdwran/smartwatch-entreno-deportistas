import sys
import os

# Ensure the repository root is in sys.path for Vercel serverless execution
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.main import app

# Vercel looks for the ASGI application callable 'app'
__all__ = ["app"]
