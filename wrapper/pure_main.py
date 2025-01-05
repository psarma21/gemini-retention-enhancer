# wrapper/main.py
import google.generativeai as genai
import os
from pathlib import Path
from newsapi import NewsApiClient
import requests

# Configure the API key and initialize the model
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
config = genai.GenerationConfig(
    temperature=2.0, # increasing response creativity
)

news_api_key = os.getenv("NEWS_API_KEY")

# get latest news
def get_news():
    user_prompt = "Explain to me AI"
    prompt = user_prompt + ". The previous sentence(s) are the user's initial prompt. Rewrite your response to make it more engaging and relatable for a novice CS student in college. Be creative and modern in your explanation. Include a relevant diagram, table, or other visual representation to enhance understanding, and provide a concise walkthrough explaining its significance and how it relates to the user's question. "
    original_result = model.generate_content([prompt], generation_config=config)
    # print(result.text)
    
    prompt = original_result.text + ". The previous sentences are your response to the initial query. Pick a key word/phrase from the response which you feel would be beneficial to include the latest news about. I will be making an API to call get the latest news about this word/phrase. The goal for this news is to allow the user to connect CS concepts with things they see in real life or in the industry. Only return those the word/phrase. "
    result = model.generate_content([prompt], generation_config=config)
    # print(result.text)

    newsapi = NewsApiClient(api_key=news_api_key)

    word = result.text
    targetedArticles = newsapi.get_everything(q=word)
    articles = targetedArticles["articles"]
    news = ""
    for article in articles:
        news += f"Title: {article['title']}" + f"Description: {article['description']}\n" + f"Content: {article['content']}\n\n"
    
    # main idea + Gemini original response + news 
    prompt = "Given the user's original query and your initial response, identify a recent real-world event, example, or development from the provided news articles that illustrates or connects to the topic. Summarize the example and explain how it relates to the user's query and your response. The following was your original response: " + original_result.text + " The following was the main concept from your response: " + word + " . The following is the news: " + news
   
    # main idea + user initial query + Gemini original response + news
    # prompt = "Given the user's original query and your initial response, identify a recent real-world event, example, or development from the provided news articles that illustrates or connects to the topic. Summarize the example and explain how it relates to the user's query and your response. Here is the user's original question: " + user_prompt + " The following is your response: " + original_result.text + "The following is the main concept from the user's question: " + word + " . The following is the news: " + news
    result = model.generate_content([prompt], generation_config=config)
    print(result.text)
 
def get_image_from_pollinator():
    query="an apple under the moonlight"
    
    url = f"https://pollinations.ai/p/{query.text}"
    response = requests.get(url)
    with open('generated_image.jpg', 'wb') as file:
        file.write(response.content)
    print('Image downloaded!')
    
            
if __name__ == "__main__":
    get_image_from_pollinator()
