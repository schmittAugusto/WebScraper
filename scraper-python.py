## scraper-python.py
# To run this script, paste `python scraper-python.py` in the terminal

import requests
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
from bs4 import BeautifulSoup
import re  # Add import for regular expressions
import imaplib
import email
from email.header import decode_header
import html2text

#setup the client (secret key) and the service (deepseek)

load_dotenv()
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY") 
client = OpenAI(api_key = os.environ["OPENAI_API_KEY"], base_url="https://api.deepseek.com")

#I think I have now fully cleaned my local repo history as well as the remote one. This push is intended to test that.

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



def scrape_email_content(email_address, password, sender_filter=None, imap_server="imap.gmail.com", max_emails=5):
    """
    Connects to an email account via IMAP and scrapes content from emails.
    Args:
        email_address: The email address to connect to
        password: The password or app-specific password
        sender_filter: Email address to filter by sender (optional)
        imap_server: IMAP server address (default is Gmail)
        max_emails: Maximum number of recent emails to scrape
    Returns:
        A list of dictionaries containing email data
    """
    try:
        # Connect to the IMAP server
        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(email_address, password)
        
        # Select the mailbox (inbox by default)
        imap.select("INBOX")
        
        # Search for emails with optional sender filter
        if sender_filter:
            _, message_numbers = imap.search(None, f'FROM "{sender_filter}"')
        else:
            _, message_numbers = imap.search(None, "ALL")
            
        email_ids = message_numbers[0].split()
        
        # Get the last max_emails number of emails
        email_ids = email_ids[-max_emails:] if len(email_ids) > max_emails else email_ids
        
        # List to store email data
        emails_data = []
        
        # HTML to text converter
        h = html2text.HTML2Text()
        h.ignore_links = True
        
        for email_id in email_ids:
            # Fetch the email data
            _, msg_data = imap.fetch(email_id, "(RFC822)")
            email_body = msg_data[0][1]
            message = email.message_from_bytes(email_body)
            
            # Get subject
            subject = decode_header(message["subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            # Get sender
            from_ = decode_header(message["from"])[0][0]
            if isinstance(from_, bytes):
                from_ = from_.decode()
            
            # Get date
            date = message["date"]
            
            # Get content
            content = ""
            if message.is_multipart():
                # Handle multipart messages
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        content += part.get_payload(decode=True).decode()
                    elif part.get_content_type() == "text/html":
                        html_content = part.get_payload(decode=True).decode()
                        content += h.handle(html_content)
            else:
                # Handle plain text emails
                content = message.get_payload(decode=True).decode()
            
            email_data = {
                "subject": subject,
                "from": from_,
                "date": date,
                "content": content
            }
            
            emails_data.append(email_data)
            
        imap.close()
        imap.logout()
        
        print(f"Successfully scraped {len(emails_data)} emails" + 
              (f" from sender {sender_filter}" if sender_filter else ""))
        return emails_data
        
    except Exception as e:
        print(f"Error scraping emails: {str(e)}")
        return []

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
    #chatResponse = chat_with_deepseek(prompt)
    #riteTextFile(chatResponse)
    #rint(chatResponse)

    #email information to test the email scraping function
    email_address = "fact.bridge.extract@gmail.com"
    password = "awpaovraofzcfldt"
    emails_data = scrape_email_content(email_address, password, "vspipano@gmail.com")
    for email in emails_data:
        print(f"Email content: {email['content']}\n")
    print("End of email scraping.")