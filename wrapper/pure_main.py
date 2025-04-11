# wrapper/main.py
from google import genai
from google.genai import types
from openai import OpenAI
import os
from newsapi import NewsApiClient

# Configure the API key and initialize the model
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)
config=types.GenerateContentConfig(
    temperature=2.0
)

news_api_key = os.getenv("NEWS_API_KEY")

# get latest news
def get_news():
    newsapi = NewsApiClient(api_key=news_api_key)
    key_word='technology'
    # url = "https://newsapi.org/v2/everything"
    # params = {
    #     "q": key_word,
    #     "apiKey": news_api_key,
    # }
    
    # response = requests.get(url, params=params)
    
    # if response.status_code == 200:
    #     data = response.json()
    #     for article in data["articles"][:5]:  # Print top 5 articles
    #         print(f"Title: {article['title']}")
    #         print(f"Source: {article['source']['name']}")
    #         print(f"URL: {article['url']}\n")
    # else:
    #     print(f"Error: {response.status_code}, {response.text}")
    
    targetedArticles = newsapi.get_everything(q=key_word)
    articles = targetedArticles["articles"]
    news = ""
    for article in articles:
        news += f"Title: {article['title']}" + f"Description: {article['description']}\n" + f"Content: {article['content']}\n\n"
        
    print(news)
    
# Gemini 2.0 Flash
def gemini_2_flash():
    prompt = "can you return emojis?"
    original_result = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt], config=config)
    print(original_result.text)
    
# Gemini 2.0 Flash Lite
def gemini_2_flash_lite():
    prompt = "tell me the news today in nba"
    original_result = client.models.generate_content(model="gemini-2.0-flash-lite", contents=[prompt], config=config)
    print(original_result.text)
    
def deepseek():
    client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "tell me the news today"},
        ],
        stream=False
    )
    print(response.choices[0].message.content) 
    
def deepseek_with_news():
    client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are trying to teach a CS student in college a concept"},
            {"role": "user", "content": "tell me the news today regarding it"},
        ],
        stream=False
    )
    print(response.choices[0].message.content) 
    
if __name__ == "__main__":
    gemini_2_flash()