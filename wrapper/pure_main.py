# wrapper/main.py
import google.generativeai as genai
from pathlib import Path
import os

# Configure the API key and initialize the model
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------------------------------------------------------------------------------------------------------

# Read an image
# media = Path("/Users/pawansarma/Documents/Pawan/SJSU/masters-thesis/code/wrapper")

# apple = PIL.Image.open(media / "apple.jpeg")

# response = model.generate_content(["Tell me about this apple", apple])
# print(response.text)

# Pass pdf file contexts as part of the API --> convert to .txt file
# pdf_path = Path("/Users/pawansarma/Documents/Pawan/SJSU/masters-thesis/cs297-proposal-updated.pdf")

# with pdfplumber.open(pdf_path) as pdf:
#     text = ''
#     for page in pdf.pages:
#         text += page.extract_text()

# text_file_path = Path("/Users/pawansarma/Documents/Pawan/SJSU/masters-thesis/cs297-proposal-updated.txt")
# with open(text_file_path, "w") as text_file:
#     text_file.write(text)
    
# prompt = f"Explain to me this proposal\n\n{text[:1500]}"  # Limiting to 1500 characters for brevity
# response = model.generate_content([prompt])

# print(response.text)

# ---------------------------------------------------------------------------------------------------------------

# pass text file contents to Gemini
# text_file_path = Path("/Users/pawansarma/Documents/Pawan/SJSU/masters-thesis/code/wrapper/mappings.txt")
# with open(text_file_path, "r") as text_file:
#     text = text_file.read()  
    
# prompt = f"Each line in this file represents a pair of traditional word, modern day equivalent. Explain to me a buying a stock in one paragraph using these modern words when appropriate. Do not use them if they are not needed:\n\n{text[:1500]}"
# prompt = "What is a binary tree?" + "The previous sentence(s) are the user's initial prompt. If the prompt is related to computer science, modernize the language of your response to be more understandable to a novice developer. If not, respond as you normally would." # TODO: more interesting?
# mapping file - ask LLM to do this, do it daily maybe? "understandable" - it should be already!
# response = model.generate_content([prompt]) 
# print(response.text)

# ---------------------------------------------------------------------------------------------------------------

# actually upload a file and read it from it
# media = Path("/Users/pawansarma/Documents/Pawan/SJSU/masters-thesis/code/wrapper")
# result = model.generate_content(["Give summary of this file.", genai.upload_file(media / "mappings.txt")])
# print(result.text)

# ---------------------------------------------------------------------------------------------------------------------

# experiment
prompt = "What is a binary tree? The previous sentence(s) are the user's initial prompt. If the prompt is related to computer science, modernize the language of your response to be more interesting to a novice developer.  If not, respond as you normally would."
result = model.generate_content([prompt])
print(result.text)
