# wrapper/main.py
import google.generativeai as genai
import os

# Configure the API key and initialize the model
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_gemini_response(text):
    try:
        # prompt 1 - vanilla query
        prompt = "What is a binary tree?"
        response = model.generate_content([text])  

        # prompt 2 - modernization of language
        prompt = response.text + "From the previous sentences, modernize the language to be more understandable to a novice developer." 
        response = model.generate_content([prompt]) 
        return response.text
    except Exception as e:
        return f"Error: {e}"