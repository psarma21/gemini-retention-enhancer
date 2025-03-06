# wrapper/main.py
from google import genai
from google.genai import types
from openai import OpenAI
import os
from newsapi import NewsApiClient
import requests

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
    
def experiment():
    prompt = "tell me the news today"
    original_result = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt], config=config)
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
    # newsapi = NewsApiClient(api_key=news_api_key)
    # key_word = "technology"
    # targetedArticles = newsapi.get_everything(q=key_word, page=1)
    # articles = targetedArticles["articles"]
    # news = ""
    # for article in articles:
    #     news += f"Title: {article['title']}" + f"Description: {article['description']}\n" + f"Content: {article['content']}\n"
        
    # print(news)
    
#     news = """Title: Cellebrite Suspends Serbia as Customer After Claims Police Used Firm's Tech To Plant SpywareDescription: Cellebrite says it has stopped Serbia from using its technology following allegations that Serbian police and intelligence used Cellebrite's technology to unlock the phones of a journalist and an activist, and then plant spyware. From a report: In December 20…
# Content: In December 2024, Amnesty International published a report that accused Serbian police of using Cellebrite's forensics tools to hack into the cellphones of a local journalist and an activist. Once th… [+481 chars]
# Title: Software Firm Bird To Leave Europe Due To Onerous Regulations in AI Era, Says CEODescription: Cloud communications software firm Bird, one of the Netherlands' most prominent tech startups, plans to move most of its operations out of Europe, its CEO said, citing restrictive regulations and difficulties hiring skilled technology workers. From a report: …
# Content: Never heard of them (I'm Dutch). When I google search on "bird ai dutch" all I get are news headlines and somewhere on the second page I find a couple of companies which have 'bird' in their name and… [+92 chars]
# Title: Trump stands to gain $250 million with social media expansion into financial servicesDescription: Trump Media & Technology Group's share value surged following the announcement it's expanding into financial services.
# Content: One week into Donald Trump's presidency, his multi-billion-dollar social media company announced its expansion into the financial services industry.
# In partnership with Charles Schwab, Trump Media &… [+1379 chars]"""
    
    client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are trying to teach a CS student in college a concept"},
            {"role": "user", "content": "tell me the news today"},
        ],
        stream=False
    )
    print(response.choices[0].message.content) 
    
if __name__ == "__main__":
    get_news()