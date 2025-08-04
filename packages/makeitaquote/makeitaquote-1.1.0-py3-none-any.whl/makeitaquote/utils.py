import re


def remove_markdown(text: str) -> str:
    """Remove Discord markdown formatting from text."""
    # Remove bold (**text** or __text__)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    
    # Remove italic (*text* or _text_)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    
    # Remove strikethrough (~~text~~)
    text = re.sub(r'~~(.*?)~~', r'\1', text)
    
    # Remove spoiler (||text||)
    text = re.sub(r'\|\|(.*?)\|\|', r'\1', text)
    
    # Remove code blocks (```text``` or `text`)
    text = re.sub(r'```(.*?)```', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'`(.*?)`', r'\1', text)
    
    # Remove links [text](url)
    text = re.sub(r'\[([^\]]+)\]$$[^)]+$$', r'\1', text)
    
    # Remove mentions <@user_id>, <#channel_id>, <@&role_id>
    text = re.sub(r'<[@#&!][^>]+>', '', text)
    
    # Remove custom emojis <:name:id>
    text = re.sub(r'<:[^:]+:\d+>', '', text)
    
    return text.strip()