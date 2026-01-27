import re
from bs4 import BeautifulSoup
import html

def html_to_clean_text(html_content: str)-> str:
    if not html_content:
        return ""
    
    html_content = html.unescape(html_content)
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    for tag in soup(["script", "style", "meta","noscript","head"]):
        tag.decompose()
        
    text = soup.get_text(separator=" ")
    
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


def extract_sender(user_input : str):
    text = user_input.lower()
    
    if "from" in text:
        return text.split('from', 1)[1].strip()
    
    return None

import re

NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3",
    "four": "4", "five": "5", "six": "6", "seven": "7",
    "eight": "8", "nine": "9"
}

def normalize_username(text: str | None):
    if not text:
        return None

    t = text.lower()

    # remove punctuation Deepgram adds
    t = re.sub(r"[^\w\s]", "", t)

    # numbers
    for word, digit in NUMBER_WORDS.items():
        t = re.sub(rf"\b{word}\b", digit, t)

    # remove spaces
    t = t.replace(" ", "")

    print(" NORMALIZED USERNAME:", t)

    # username must be alphanumeric, min length
    if re.fullmatch(r"[a-z0-9]{3,}", t):
        return t

    return None

def preserve_email_state(state):
    return {
        "to": state.get("to"),
        "to_local": state.get("to_local"),
        "email_provider": state.get("email_provider"),
        "subject": state.get("subject"),
        "body": state.get("body"),
    }

