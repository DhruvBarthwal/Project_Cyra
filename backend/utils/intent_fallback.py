def fallback_intent(text: str) -> str:
    text = (text or "").lower().strip()
    
    if "next" in text:
        return "NEXT_EMAIL"
    if "previous" in text or "prev" in text:
        return "PREV_EMAIL"
    
    if any(k in text for k in ["confirm", "yes", "send it", "go ahead", "okay"]):
        return "CONFIRM_SEND"
    
    if any(k in text for k in [
        "undo delete",
        "restore email",
        "untrash",
        "bring it back",
        "recover email"
        "restore"
    ]):
        return "UNTRASH_EMAIL"
    if any(k in text for k in [
        "no",
        "nope",
        "cancel",
        "don't",
        "do not",
        "stop",
        "leave it",
        "never mind"
    ]):
        return "CANCEL_DELETE"

    if any(k in text for k in ["delete", "remove", "trash", "discard"]):
        return "DELETE_EMAIL"

    if any(k in text for k in ["create","write", "compose", "send", "send mail", "send email", "compose email"]):
        return "COMPOSE_EMAIL"

    if any(k in text for k in ["read", "open", "check", "show", "inbox"]):
        return "READ_EMAIL"
    
    if any(k in text for k in [
        "unstar",
        "remove star",
        "clear star",
        "not important",
        "remove important"
    ]):
        return "UNSTAR_EMAIL"
    
    
    if any(k in text for k in [
        "star",
        "star this",
        "mark important",
        "add star",
        "mark star",
        "important email",
        "star email"
    ]):
        return "STAR_EMAIL"
    
    return "UNKNOWN"

