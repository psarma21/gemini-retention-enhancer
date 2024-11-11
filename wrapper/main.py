# wrapper/main.py
import google.generativeai as genai
import os

# Configure the API key and initialize the model
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def add_context_to_prompt(prompt, u1, g1, u2):
    if u1 is None:
        return prompt
    elif u2 is None:
        return prompt + "Here is additional context about the query: The last user prompt was " + u1 + " and the last Gemini response was " + g1
    else:
        return prompt + "Here is additional context about the query: The last two users prompts were " + u1 + " and " + u2 + " , and the last Gemini response was " + g1

def get_gemini_response(text, topic, last_user_prompt, last_gemini_response, second_to_last_user_prompt):
    # prompt 1 - vanilla query + modernization of language + customizable response (optional)
    try:
        config = genai.GenerationConfig(
            temperature=2.0, # increasing response creativity
        )
        if topic != "none":
            prompt = text + ". The previous sentence(s) are the user's initial prompt. Rewrite your response to make it more engaging and relatable for a novice CS student in college who is interested in " + topic + " . Be creative and modern in your explanation. Include a relevant diagram, table, or other visual representation to enhance understanding, and provide a concise walkthrough explaining its significance and how it relates to the user's question.  "
            prompt_with_context = add_context_to_prompt(prompt, u1=last_user_prompt, g1=last_gemini_response, u2=second_to_last_user_prompt)
            print("prompt with context", prompt_with_context)
            response =  model.generate_content([prompt_with_context], generation_config=config)  
        else:
            prompt = text + ". The previous sentence(s) are the user's initial prompt. Rewrite your response to make it more engaging and relatable for a novice CS student in college. Be creative and modern in your explanation. Include a relevant diagram, table, or other visual representation to enhance understanding, and provide a concise walkthrough explaining its significance and how it relates to the user's question. "
            prompt_with_context = add_context_to_prompt(prompt, u1=last_user_prompt, g1=last_gemini_response, u2=second_to_last_user_prompt)
            print("prompt with context",  prompt_with_context)
            response =  model.generate_content([prompt_with_context], generation_config=config)  
        return response.text
    except Exception as e:
        return f"Error: {e}"