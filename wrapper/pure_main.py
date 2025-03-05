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
# def get_news():
#     user_prompt = "Explain to me AI"
#     prompt = user_prompt + ". The previous sentence(s) are the user's initial prompt. Rewrite your response to make it more engaging and relatable for a novice CS student in college. Be creative and modern in your explanation. Include a relevant diagram, table, or other visual representation to enhance understanding, and provide a concise walkthrough explaining its significance and how it relates to the user's question. "
#     original_result = model.generate_content([prompt], generation_config=config)
#     # print(result.text)
    
#     prompt = original_result.text + ". The previous sentences are your response to the initial query. Pick a key word/phrase from the response which you feel would be beneficial to include the latest news about. I will be making an API to call get the latest news about this word/phrase. The goal for this news is to allow the user to connect CS concepts with things they see in real life or in the industry. Only return those the word/phrase. "
#     result = model.generate_content([prompt], generation_config=config)
#     # print(result.text)

#     newsapi = NewsApiClient(api_key=news_api_key)

#     word = result.text
#     targetedArticles = newsapi.get_everything(q=word)
#     articles = targetedArticles["articles"]
#     news = ""
#     for article in articles:
#         news += f"Title: {article['title']}" + f"Description: {article['description']}\n" + f"Content: {article['content']}\n\n"
    
#     # main idea + Gemini original response + news 
#     prompt = "Given the user's original query and your initial response, identify a recent real-world event, example, or development from the provided news articles that illustrates or connects to the topic. Summarize the example and explain how it relates to the user's query and your response. The following was your original response: " + original_result.text + " The following was the main concept from your response: " + word + " . The following is the news: " + news
   
#     # main idea + user initial query + Gemini original response + news
#     # prompt = "Given the user's original query and your initial response, identify a recent real-world event, example, or development from the provided news articles that illustrates or connects to the topic. Summarize the example and explain how it relates to the user's query and your response. Here is the user's original question: " + user_prompt + " The following is your response: " + original_result.text + "The following is the main concept from the user's question: " + word + " . The following is the news: " + news
#     result = model.generate_content([prompt], generation_config=config)
#     print(result.text)
    
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
    deepseek_with_news()