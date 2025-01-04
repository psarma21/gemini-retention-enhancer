# wrapper/main.py
import google.generativeai as genai
import os
from newsapi import NewsApiClient
import requests

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
        return prompt + "Here is additional context about the query: The last user prompt was " + u1 + " and the last Gemini response was " + g1
    else:
        return prompt + "Here is additional context about the query: The last two users prompts were " + u1 + " and " + u2 + " , and the last Gemini response was " + g1

def get_gemini_response(text, topic, last_user_prompt, last_gemini_response, second_to_last_user_prompt):
    # enhancement #1 - modernization of language
    # modified query: vanilla query + modernization of vocabulary/language + customizable response (optional) + previous context to query
    try:
        if topic != "none":
            prompt = text + ". The previous sentence(s) are the user's initial prompt. Rewrite your response to make it more engaging and relatable for a novice CS student in college who is interested in " + topic + " . Be creative and modern in your explanation. Include a relevant diagram, table, or other visual representation to enhance understanding, and provide a concise walkthrough explaining its significance and how it relates to the user's question.  "
            prompt_with_context = add_context_to_prompt(prompt, u1=last_user_prompt, g1=last_gemini_response, u2=second_to_last_user_prompt)
            response =  model.generate_content([prompt_with_context], generation_config=config)  
        else:
            prompt = text + ". The previous sentence(s) are the user's initial prompt. Rewrite your response to make it more engaging and relatable for a novice CS student in college. Be creative and modern in your explanation. Include a relevant diagram, table, or other visual representation to enhance understanding, and provide a concise walkthrough explaining its significance and how it relates to the user's question. "
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
    
    summarize_news_prompt = "Using the user's original query and your initial response, analyze the provided news articles to identify a real-world event, example, or application that connects to the concept discussed (e.g., linked lists). Summarize this connection in a concise and user-friendly manner, emphasizing how it relates to the user's question. If no relevant articles are available, reference a well-known real-world scenario or example to illustrate the concept. Bold key terms or highlight notable examples to make the connection stand out and enhance user engagement. For instance, if a technology like blockchain or a company like Google uses linked lists in practice, emphasize this in your explanation."
    context = " The following was the user query: " + last_user_query + ". The following was your response: " + last_gemini_response + ". The following is the news: " + news
    result = model.generate_content([summarize_news_prompt+context], generation_config=config)
    return result.text

def get_image_description_and_image(last_gemini_response, last_user_query, key_word):
    # Call Gemini to generate a description for the bolded word
    image_query_prompt = "Given the user's question, your response, and specific word in your response, provide a detailed description of an image that would visually represent that word that also enhances the understanding of the overlying concept discussed. The image should be creative, colorful, and engaging, designed to help a novice computer science learner grasp the concept intuitively. For example, if the word is 'linked list', the description might include visual metaphors or illustrative elements, such as 'a chain of nodes connected by arrows, each node containing a small icon of data inside.' The goal is to create a vivid and imaginative representation that bridges theory with an accessible visual analogy."
    context = " Here is the user's query: " + last_user_query + " . Here is your response: " + last_gemini_response + ' . Here is the key word: ' + key_word
    image_description_response = model.generate_content([image_query_prompt + context], generation_config=config)
    
    print(image_description_response.text)

    url = f"https://pollinations.ai/p/{image_description_response.text}"
    response = requests.get(url)
    return response.url
    
    
    