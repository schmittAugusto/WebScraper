## scraper-python.py
# To run this script, paste `python scraper-python.py` in the terminal

import requests
import os
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup

#setup the client (secret key) and the service (deepseek)

load_dotenv()
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY") 
client = OpenAI(api_key = os.environ["OPENAI_API_KEY"], base_url="https://api.deepseek.com")

#Sends a string prompt to deepseek and returns its response
def chat_with_deepseek(prompt):
    response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": prompt},
    ],
    stream=False
)
    return response.choices[0].message.content
 


#Scrapes a website using a HTML parser. Reads the <p> elements and returns a 400 character text.
def scrape(inputURL):
    response = requests.get(inputURL)
    soup = BeautifulSoup(response.text, 'html.parser')
    elementList = soup.find_all("p")
    
    #Creates a string variable and feeds the text part of the scraped elements of the URL into that variable
    text = ''
    for element in elementList:
        text += element.get_text()
   
    #terminal feedback
    print(f"Scraper for {inputURL} was successful.")
    
    #takes 400 first characters from that previous string
    #truncatedText = listToText[:400]

    return text

if __name__ == '__main__':

    #defining different URLs
    urlEN = 'https://en.wikipedia.org/wiki/Folha_de_S.Paulo'
    urlPT = 'https://pt.wikipedia.org/wiki/Folha_de_S.Paulo'

    #evokes the scrape function and stores the return text into a variable
    messageEN = scrape(urlEN)
    messagePT = scrape(urlPT)

    #print(messageEN)
    #print("SEGUNDO ARTIGO")
    #print(messagePT)
    
    #defines the prompt with a simple order and the text that was scraped
    prompt = f"""I extracted two texts from different sources, but regarding the same topic: the Brazilian Newspaper "Folha de São Paulo". I want you to process these texts and output the following:
    A- a summary regarding the common topic, which should be neutral and provide a consensus of the points of view between sources. This summary should be limited to 300 words
    B- a brief description of additions and omissions from source 1 in comparison to source 2. This should be limited to 100 words
    C- a brief description of additions and omissions from source 2 in comparison to source 1. This should be limited to 100 words
    These are the mentioned texts:
    Text 1 (Source 1): <<<{messageEN}>>>;
    Text 2 (Source 2): <<<{messagePT}>>>"""

    #prints the response of the AI chat
    
    print(chat_with_deepseek(prompt))