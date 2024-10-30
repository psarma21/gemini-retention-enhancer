# wrapper/main.py
import PIL
import google.generativeai as genai
from pathlib import Path
import os
import pdfplumber

# Configure the API key and initialize the model
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Read a text file
# media = Path("/Users/pawansarma/Documents/Pawan/SJSU/masters-thesis/code/wrapper")

# sample_pdf = genai.upload_file(media / "mappings.txt")

# prompt = f"Read the contents of this text file: {sample_pdf}"
# response = model.generate_content(prompt)
# print(response.text)

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

# pass text file contents to Gemini
text_file_path = Path("/Users/pawansarma/Documents/Pawan/SJSU/masters-thesis/code/wrapper/mappings.txt")
with open(text_file_path, "r") as text_file:
    text = text_file.read()  
    
# prompt = f"Each line in this file represents a pair of traditional word, modern day equivalent. Explain to me a buying a stock in one paragraph using these modern words when appropriate. Do not use them if they are not needed:\n\n{text[:1500]}"
prompt = "What is a binary tree?"
response = model.generate_content([prompt])  

prompt = response.text + "From the previous sentences, modernize the language to be more understandable to a novice developer." # TODO: more interesting?
# mapping file - ask LLM to do this, do it daily maybe? "understandable" - it should be already!
response = model.generate_content([prompt]) 
print(response.text)



# media = Path("/Users/pawansarma/Documents/Pawan/SJSU/masters-thesis/code/wrapper")
# result = model.generate_content([genai.upload_file(media / "mappings.txt"), "Give summary of this file."])
# print(result.text)