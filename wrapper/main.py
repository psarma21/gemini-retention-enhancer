# wrapper/main.py
import google.generativeai as genai
import os
from newsapi import NewsApiClient
import requests
import json

# Configure the API key and initialize the model
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

news_api_key = os.getenv("NEWS_API_KEY")

config = genai.GenerationConfig(
    temperature=2.0, # increasing response creativity
)

def add_context_to_prompt(prompt, u1, g1, u2):
    if u1 is None:
        return prompt
    elif u2 is None:
        return prompt + "Here is additional context about the query. If it is unrelated to the current query, disregard it. The last user prompt was " + u1 + " and the last Gemini response was " + g1
    else:
        return prompt + "Here is additional context about the query. If it is unrelated to the current query, disregard it. The last two users prompts were " + u1 + " and " + u2 + " , and the last Gemini response was " + g1

# enhancement #1 - modernization of language
# modified query: vanilla query + modernization of vocabulary/language + customizable response (optional) + previous context to query
def get_gemini_response(text, topic, last_user_prompt, last_gemini_response, second_to_last_user_prompt):
    try:
        if topic != "none":
            prompt = text + """. The previous sentence(s) are the user's initial prompt. Rewrite your response to make it more engaging and 
            relatable for a novice CS student in college who is interested in """ + topic + """ . Be creative and modern in your 
            explanation. Include a relevant diagram, table, or other visual representation to enhance understanding, and provide a 
            concise walkthrough explaining its significance and how it relates to the user's question. Bold key concepts to highlight their 
            significance. """
            prompt_with_context = add_context_to_prompt(prompt, u1=last_user_prompt, g1=last_gemini_response, u2=second_to_last_user_prompt)
            response =  model.generate_content([prompt_with_context], generation_config=config)  
        else:
            prompt = text + """. The previous sentence(s) are the user's initial prompt. Rewrite your response to make it more engaging 
            and relatable for a novice CS student in college. Be creative and modern in your explanation. Include a relevant diagram, 
            table, or other visual representation to enhance understanding, and provide a concise walkthrough explaining its significance 
            and how it relates to the user's question. Bold key concepts to highlight their significance. """
            prompt_with_context = add_context_to_prompt(prompt, u1=last_user_prompt, g1=last_gemini_response, u2=second_to_last_user_prompt)
            response =  model.generate_content([prompt_with_context], generation_config=config)  
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
        
    # print(news)
            
    # original query + Gemini original response + news 
    summarize_news_prompt = """Using the user's original query and your initial response, analyze the provided news articles to 
    identify real-world events, companies/technologies/products, or people that connect to the concept discussed. List 8-10 
    connections in a bullet point manner with a one-sentence-maximum explanation emphasizing how it relates to the user's question. 
    If no relevant articles are available, mention that in a sentence, and instead reference real-world events, technologies, or people 
    you know to illustrate the concept. But try to extract any information from the news first. Bold key words like company or product 
    names to enhance user engagement. """
    context = " The following was the user query: " + last_user_query + ". The following was your response: " + last_gemini_response + ". The following is the news: " + news
    result = model.generate_content([summarize_news_prompt+context], generation_config=config)
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
    image_description_response = model.generate_content([image_query_prompt + caption_json_prompt + context], generation_config=config)
    
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
    
    
    