# wrapper/main.py
import google.generativeai as genai
import os
from newsapi import NewsApiClient

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
    summarize_news_prompt = "Based on the user's original query and your initial response, analyze the provided news articles to identify a recent real-world event, example, or development that connects to your response. Summarize the event and clearly explain its relevance to the original question and your explanation. If no provided articles are relevant, use a recent real-world example or event you know to establish the connection. The following was the user query: " + last_user_query + ". The following was your response: " + last_gemini_response + ". The following is the news: " + news
    result = model.generate_content([summarize_news_prompt], generation_config=config)
    return result.text
    
    
    