import os

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key_here")  # Use environment variables!
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expires in 30 minutes
