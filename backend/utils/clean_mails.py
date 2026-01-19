import re
from bs4 import BeautifulSoup
import html

def html_to_clean_text(html_content: str)-> str:
    if not html_content:
        return ""
    
    #Decode HTML entities
    html_content = html.unescape(html_content)
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    #Remove scripts, styles, meta , head junk
    for tag in soup(["script", "style", "meta","noscript","head"]):
        tag.decompose()
        
    text = soup.get_text(seperator=" ")
    
    # Remove URLs
    text = re.sub(r"http\S+", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove common footer noise
    blacklist = [
        "unsubscribe",
        "do not reply",
        "terms and conditions",
        "privacy policy",
        "all rights reserved",
        "copyright",
    ]

    lowered = text.lower()
    for word in blacklist:
        idx = lowered.find(word)
        if idx != -1:
            text = text[:idx]
            break

    return text.strip()

def clean_email_text(text: str) -> str:
    if not text:
        return ""
    
    #Remove urls
    text = re.sub(r"http\S+","",text)
    
    #Replace multiple whitespace/newlines/tabs with single space
    text = re.sub(r"\s+"," ",text)
    
    #Remove marketing footers keywords
    blacklist = [
        "unsubscribe",
        "do not reply",
        "terms and conditions",
        "copyright",
        "all rights reserved",
        "image simulated"
    ]
    
    lowered = text.lower()
    for word in blacklist:
        idx = lowered.find(word)
        if idx != -1:
            text = text[:idx]
            break
    return text.strip()