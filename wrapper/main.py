# wrapper/main.py
from google import genai
from google.genai import types
import os
from newsapi import NewsApiClient
import requests
import json

# configure the API key and initialize the model
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
response_config=types.GenerateContentConfig(
    temperature=2.0,
    system_instruction="""Be engaging and hip in your response while maintaining high technical strength. If applicable, return .svg or Mermaid code to create 
        an engaging, basic, and simple diagram which would help me visually understand my question better. Provide a concise walkthrough of it. If applicable, give simple code 
        with helpful comments that provides an engaging and interactive output such that I can compile separately to help me understand my question better. 
        Provide a concise walkthrough of it. If applicable, ask a question at the end of your response if the user wants to learn about something deeper within the topic. 
        Bold key concepts and engaging words to highlight their significance and capture the user's attention respectively. Avoid empty new lines, try not to make sentences 
        too long in your response, and include relevant emojis in your response to capture the reader's attention."""
)
model = "gemini-2.0-flash"

news_api_key = os.getenv("NEWS_API_KEY")

# add_context_to_prompt adds previous chat history to the prompt as context for Gemini
def add_context_to_prompt(prompt, u1, g1, u2):
    contents = []
    if u2:
        contents.append({
            "role": "user",
            "parts": [{"text": u2}]
        })
    if u1:
        contents.append({
            "role": "user",
            "parts": [{"text": u1}]
        })
    if g1:
        contents.append({
            "role": "model",
            "parts": [{"text": g1}]
        })
    if prompt:
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
    return contents


# enhancement #1 - modernization of language
# modified query: vanilla query + modernization of vocabulary/language + customizable response (optional) + previous context to query
def get_gemini_response(text, topic, last_user_prompt, last_gemini_response, second_to_last_user_prompt):
    try:
        if topic != "none":
            prompt = text + """. The previous sentence(s) are the user's initial prompt. Rewrite your response to make it more engaging and 
            relatable for a novice CS student in college who is interested in """ + topic + """ . Be creative and modern in your 
            explanation. Include a relevant diagram or other visual representation to enhance understanding, and provide a 
            concise walkthrough explaining its significance and how it relates to the user's question. Only do this if a visual 
            representation is needed. If applicable, ask a follow-up question at the end of your response that encourages deeper exploration 
            of the topic, such as reviewing related code, learning a subtopic, or applying the concept practically. Avoid empty new lines in your response."""
            prompt_with_context = add_context_to_prompt(prompt, u1=last_user_prompt, g1=last_gemini_response, u2=second_to_last_user_prompt)
            response =  client.models.generate_content(model=model, contents=[prompt_with_context], config=response_config)  
        else:
            prompt = text + ". I am a novice CS student in college."   
            chat_history = add_context_to_prompt(prompt, last_user_prompt, last_gemini_response, second_to_last_user_prompt)       
            response = client.models.generate_content(
                model=model,
                contents=chat_history,
                config=response_config
            )
        return response.text
    except Exception as e:
        return f"Error: {e}"
    
# enhancement #2 - provided latest technology news most relevant to last user-Gemini interaction
def get_related_news(last_gemini_response, last_user_query):
    newsapi = NewsApiClient(api_key=news_api_key)
    key_word = "technology"
    targetedArticles = newsapi.get_everything(q=key_word)
    # targetedArticles = newsapi.get_top_headlines()
    articles = targetedArticles["articles"]
    news = ""
    for article in articles:
        news += f"Title: {article['title']}" + f"Description: {article['description']}\n" + f"Content: {article['content']}\n"
        
    print(news)
            
    # original query + Gemini original response + news 
    summarize_news_prompt = """Using the user's original query and your initial response, analyze the provided news articles to 
    identify real-world events, companies/technologies/products, or people that connect to the concept discussed. List 5 
    connections in a bullet point manner with a one-sentence-maximum explanation emphasizing how it relates to the user's question. 
    If no relevant articles are available, mention that in a sentence, and instead reference real-world events, technologies, or people 
    you know to illustrate the concept. Bold key words like company or product names to enhance user engagement. Include the news title at 
    the beginning of each bullet point."""
    context = " The following was the user query: " + last_user_query + ". The following was your response: " + last_gemini_response + ". The following is the news: " + news
    result =  client.models.generate_content(model=model, contents=[summarize_news_prompt+context], config=config)  
    return result.text

# enhancement 3 - call Gemini to generate a description for the bolded word
def get_image_description_and_image(last_gemini_response, last_user_query, key_word):
    image_query_prompt = """Given the user's question, your response, and specific word in your response, provide detailed steps to 
    create an image that would visually represent that word that also enhances the understanding of the overlying concept discussed. 
    These steps will be directly passed to an AI image generator so the steps need to be clear. The image should be creative and engaging, 
    designed to help a novice computer science learner grasp the concept intuitively. For example, if the word is 'linked list', the description 
    might include visual metaphors or illustrative elements, such as 'a long chain of nodes connected by arrows, each node containing a small icon of 
    data inside. The goal is to create a vivid and imaginative representation that bridges theory with an accessible visual analogy. The AI generator 
    cannot create text well so ideally the description should not ask to generate any text in the image. The image should be able to explain that word 
    without any caption or text."""
    caption_json_prompt = """Additionally, generate a concise and engaging caption that a novice learner can use to interpret and connect with the image
    . For the entire response, use this JSON schema: {'image_description': str, 'caption': str}"""
    context = " Here is the user's query: " + last_user_query + " . Here is your response: " + last_gemini_response + ' . Here is the key word: ' + key_word
    image_description_response = client.models.generate_content(model=model, contents=[image_query_prompt + caption_json_prompt + context], config=config)
    
    image_description_response_text = image_description_response.text
    cleaned_text = image_description_response_text.replace("```json", "").replace("```", "").strip()
    print(image_description_response.text)
    
    try:
        response_json = json.loads(cleaned_text)
        image_description = response_json.get("image_description", "")
        caption = response_json.get("caption", "")
    except json.JSONDecodeError as e:
        return None
    

    url = f"https://pollinations.ai/p/{image_description}"
    response = requests.get(url)
    return response.url, caption
    
    
    