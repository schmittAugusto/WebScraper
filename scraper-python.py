## scraper-python.py
# To run this script, paste `python scraper-python.py` in the terminal

import requests
from datetime import datetime
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
    

    return text

#function that checks if a file already exists, writing a new one if it doesn't, or appending if it does
def writeTextFile(string):
    with open("textLog.txt", "a") as file:
        now = datetime.now()
        file.write("Entry time: " + now.strftime("%d/%m/%Y %H:%M:%S") + '\n')
        file.write(string + '\n\nEnd of response\n\n')


if __name__ == '__main__':

    #defining different URLs
    urlEN = 'https://en.wikipedia.org/wiki/Folha_de_S.Paulo'
    urlPT = 'https://pt.wikipedia.org/wiki/Folha_de_S.Paulo'

    #evokes the scrape function and stores the return text into a variable
    messageEN = scrape(urlEN)
    messagePT = scrape(urlPT)
       
    #defines the prompt with a simple order and the text that was scraped
    prompt = f"""I extracted two texts from different sources, but regarding the same topic: the Brazilian Newspaper "Folha de São Paulo". I want you to process these texts and output the following:
    A- a summary of the processed content, which should be of neutral tone and provide only the consensual aspects and points of view between the different sources. This summary should be limited to 300 words
    B- a brief description of additions from source 1 that are not presented by source 2. This should be limited to 100 words
    C- a brief description of additions from source 2 that are not presented by source 1. This should be limited to 100 words

    Please restrain from being repetitive and keep neutral tone throughout your answer. 

    These are the mentioned texts:

    Text 1 (Source 1): <<<{messageEN}>>>;

    Text 2 (Source 2): <<<{messagePT}>>>."""

    

    #prints the response of the AI chat
    chatResponse = chat_with_deepseek(prompt)
    writeTextFile(chatResponse)
    print(chatResponse)