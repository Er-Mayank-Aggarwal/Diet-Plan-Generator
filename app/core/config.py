import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
JWT_SECRET = "supersecretkey123"
JWT_ALGO = "HS256"
